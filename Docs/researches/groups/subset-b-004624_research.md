# Research: subset-b-004624

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon.c

## Purpose

`falcon.c` is the Falcon/SFC4000 NIC implementation layer for the legacy Solarflare `sfc-falcon` Ethernet driver. It binds the generic `ef4_nic_type` operation table used by the rest of the driver to Falcon A1 and B0 hardware behavior: probing the ASIC, reading NVRAM configuration, setting up SPI and I2C side buses, selecting board and PHY support, managing resets, configuring the XMAC/XAUI data path, exposing stats, handling MDIO access, and publishing revision-specific capabilities.

The file is not a standalone network path implementation. TX/RX/event queues and filters are mostly delegated to `farch.c`; board-specific power and sensor behavior is delegated to `falcon_boards.c`; PHY-specific behavior is delegated to `sfx7101`, `qt202x`, and `txc` PHY operation tables. `falcon.c` is the orchestration point that sequences those pieces around hardware reset, port reconfiguration, monitoring, and `struct ef4_nic_type` callbacks.

## Important APIs, Types, And Functions

The exported integration objects are `falcon_a1_nic_type` and `falcon_b0_nic_type`. They fill the driver core's `struct ef4_nic_type` with Falcon-specific callbacks for probe/remove/init, reset mapping, IRQ handling, queue operations, event processing, filter management, stats, Wake-on-LAN, and optional MTD operations. The A1 table uses `falcon_legacy_interrupt_a1`, limits interrupt mode to MSI, disables RSS, sets A1 register-table bases, and has no RX scatter. The B0 table uses the shared farch legacy interrupt handler, supports MSI-X, RSS, RX hash, ntuple filtering, scatter, and B0 register-table bases.

NVRAM structures (`struct falcon_nvconfig`, `falcon_nvconfig_board_v2`, `falcon_nvconfig_board_v3`) model the first 0x400 bytes of flash/EEPROM board configuration. `falcon_read_nvram()` chooses flash or EEPROM, reads the NVRAM region under `nic_data->spi_lock`, validates magic/version/checksum, and optionally returns a copy. `falcon_probe_nvconfig()` extracts PHY type/address, SPI device descriptions, permanent MAC address, and board revision, then calls `falcon_probe_board()`.

SPI helpers (`falcon_spi_cmd()`, `falcon_spi_read()`, and, under `CONFIG_SFC_FALCON_MTD`, write/erase/sync helpers) operate via Falcon EE/SPI registers. `falcon_spi_device_init()` decodes device geometry from NVRAM bitfields or fallback defaults. MTD wrappers (`falcon_mtd_probe()`, `falcon_mtd_read()`, `falcon_mtd_write()`, `falcon_mtd_erase()`, `falcon_mtd_sync()`) expose the boot ROM and boot config partitions when enabled.

Port and MAC functions include `falcon_probe_port()`, `falcon_reconfigure_port()`, `falcon_reconfigure_xmac()`, `falcon_reconfigure_xmac_core()`, `falcon_reconfigure_xgxs_core()`, `falcon_reset_macs()`, `falcon_reset_xaui()`, `falcon_deconfigure_mac_wrapper()`, and `falcon_reconfigure_mac_wrapper()`. They coordinate PHY polling/reconfiguration, Falcon XMAC setup, XAUI/XGXS loopback state, multicast hash programming, flow control, frame size, MAC address, FIFO drain, and stats suppression around disruptive operations.

Reset and init functions include `falcon_probe_nic()`, `falcon_init_nic()`, `falcon_remove_nic()`, `falcon_reset_hw()`, `__falcon_reset_hw()`, `falcon_reset_sram()`, `falcon_map_reset_reason()`, and `falcon_map_reset_flags()`. These functions allocate `struct falcon_nic_data`, reject unsupported revisions, find A1 secondary PCI function state, reset hardware, allocate the interrupt-status DMA buffer, add the bit-banged I2C bus, initialize board hardware, initialize SRAM/cache/RX/TX global configuration, and release all resources in reverse.

Stats functions (`falcon_stats_request()`, `falcon_stats_complete()`, `falcon_stats_timer_func()`, `falcon_start_nic_stats()`, `falcon_stop_nic_stats()`, `falcon_update_nic_stats()`) drive XMAC statistics DMA into `efx->stats_buffer`, maintain `nic_data->stats`, derive software/core stats, and use `stats_disable_count` to prevent stats DMA while MAC/XAUI state is being reset.

MDIO functions (`falcon_mdio_read()`, `falcon_mdio_write()`, `falcon_gmii_wait()`) expose PHY register access through the Falcon GMII management registers and are installed into `efx->mdio` by `falcon_probe_port()`.

## Control Flow

Probe starts in `falcon_probe_nic()`. It allocates Falcon private state, rejects FPGA/A0/unsupported strap combinations, finds the second PCI function for A1 dual-function reset handling, performs a full reset, allocates the interrupt-status DMA buffer, probes SPI boot devices, reads and validates NVRAM, derives channel/timer limits, constructs the GPIO-backed I2C adapter, and calls the selected board type's `init()` method. Later `falcon_probe_port()` selects a PHY ops table from `efx->phy_type`, wires MDIO access, probes the PHY, initializes flow-control defaults, and allocates the MAC stats buffer.

Device init through `falcon_init_nic()` switches to on-chip SRAM, resets SRAM contents, applies hardware workarounds, configures RX FIFO thresholds/hash insertion, pushes RSS state on B0, sets flush event destination, and delegates common descriptor-cache/interrupt setup to `ef4_farch_init_common()`.

Port reconfiguration first polls loopback or PHY state, stops stats, isolates and drains MAC/RX/TX paths, resets MACs, reconfigures the PHY, reprograms XGXS/XMAC and wrapper registers, restarts stats, and informs the net stack via `ef4_link_status_changed()`. Monitor flow (`falcon_monitor()`) additionally runs board sensor checks and may force PHY low-power mode on board fault.

Reset requests are normalized by `falcon_map_reset_reason()` and ethtool flags by `falcon_map_reset_flags()`. Hardware reset uses `__falcon_reset_hw()`, with `RESET_TYPE_WORLD` preserving/restoring PCI config for both functions and other resets selectively excluding PHY/PCIe/EEPROM blocks. `falcon_reset_hw()` serializes reset against SPI operations with `spi_lock`.

## State And Persistence Behavior

Persistent hardware identity comes from NVRAM: PHY type/address, board revision, MAC address, and SPI flash/EEPROM geometry. The code validates checksum before trusting it and fails probe on invalid NVRAM. Optional MTD support exposes persistent boot flash/config partitions and verifies writes/erases by reading data back.

Runtime state lives mainly in `struct falcon_nic_data` under `efx->nic_data`: board info, SPI flash/EEPROM descriptors, locks, stats timer/state, XAUI poll flag, and A1 secondary PCI device pointer. `efx` carries link state, PHY mode, multicast hash, RSS tables, stats buffer, IRQ status buffer, and filter state. Stats state is long-lived across polls but is not persistent; it is rebuilt from hardware DMA counters and software counters.

Concurrency is explicit: SPI is serialized by `spi_lock`; MDIO by `mdio_lock`; MAC operations expect `mac_lock`; stats use `stats_lock`, barriers, and a timer; reset pending is read with `READ_ONCE()`. Stats are deliberately disabled around MAC and XAUI reset windows to avoid DMA failures or stale done flags.

## Dependencies And Integration Points

The file depends on Linux PCI, I2C, MTD, netdevice, timer, MDIO/MII, and kernel synchronization APIs. Driver-local dependencies include `net_driver.h`, `efx.h`, `nic.h`, `farch_regs.h`, `io.h`, `phy.h`, `workarounds.h`, `selftest.h`, and `mdio_10g.h`.

It integrates directly with `farch.c` through queue/event/filter/IRQ/common-init callbacks, with `falcon_boards.c` through `falcon_probe_board()` and board operation tables, with PHY drivers through `falcon_sfx7101_phy_ops`, `falcon_qt202x_phy_ops`, and `falcon_txc_phy_ops`, with ethtool through stats, reset, WOL, and self-test callbacks, and with optional MTD through `CONFIG_SFC_FALCON_MTD`.

## Risks And Edge Cases

This code is hardware-sequencing heavy. Ordering mistakes around reset, MAC drain, XAUI reset, stats DMA, or interrupt status buffers can produce data-path hangs or false fatal errors. Several paths depend on revision-specific workarounds (`EF4_WORKAROUND_*`) and A1/B0 register differences; applying B0 behavior to A1 or vice versa is a major risk.

NVRAM validation is a hard probe gate; malformed or absent flash/EEPROM leaves the NIC unusable even if hardware might be manually configurable. SPI MTD writes are potentially destructive, so lock coverage, write-enable sequencing, timeout handling, and read-back verification are important. `falcon_spi_read()` and write/erase loops allow interruption and rescheduling, which prevents CPU stalls but requires callers to handle partial lengths.

Stats DMA uses a done flag inside the DMA buffer plus memory barriers. Missing barriers or enabling stats during MAC/XAUI reset can cause stale or timed-out stat reads. `stats_disable_count` underflow would also be dangerous; callers use warnings but correct pairing remains essential.

Board monitor failures intentionally force PHY low power or off modes. That protects hardware but can surprise users if sensor reads fail transiently. Flow-control recovery differs by revision: A1 schedules an invisible reset while B0 drains/reconfigures the EM/MAC path.

## Test Signals

Hardware self-test entry points include `falcon_test_nvram()` and `falcon_b0_test_chip()`, which uses `ef4_farch_test_registers()` over a B0 register mask after forcing a loopback-capable port state. Runtime test signals include SPI timeout and checksum errors, GMII timeout/error logs, XMAC/XAUI reset timeout logs, NVRAM magic/version/checksum failures, stats DMA timeout logs, board sensor shutdown logs, and reset scheduling from global RX recovery events.

Regression coverage should exercise probe/unwind on invalid NVRAM and failed I2C/SPI allocations, reset mapping for invisible/all/world resets, stats start/stop pairing, link reconfiguration with loopback and no-loopback paths, B0 RSS push, MTD read/write/erase verification under `CONFIG_SFC_FALCON_MTD`, and A1-specific legacy interrupt acknowledgement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon_boards.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon_boards.c

## Purpose

`falcon_boards.c` provides board-level support for Falcon/SFC4000 NIC products. It translates the board revision value read from Falcon NVRAM into a `struct falcon_board_type` and supplies per-board hooks for initialization, teardown, PHY LED setup, identify LED control, and hardware-health monitoring.

This file owns the board-specific I2C device interactions that are outside the Falcon ASIC itself: LM87 sensor setup and alarm interpretation, MAX6647 temperature monitoring for SFE4001, PCA9539 I/O expander power sequencing for SFE4001, and LED wiring differences across SFE4002, SFE4003, and SFN4112F. It is called by `falcon.c` during NIC probe, remove, monitor, and ID LED operations.

## Important APIs, Types, And Functions

The public entry point is `falcon_probe_board(struct ef4_nic *efx, u16 revision_info)`. It decodes type/major/minor fields with `FALCON_BOARD_TYPE`, `FALCON_BOARD_MAJOR`, and `FALCON_BOARD_MINOR`, then searches `board_types[]` and installs `falcon_board(efx)->type`.

`board_types[]` maps four supported board IDs to operations:

- SFE4001: `sfe4001_init()`, `sfe4001_fini()`, `tenxpress_set_id_led()`, and `sfe4001_check_hw()`.
- SFE4002: `sfe4002_init()`, `sfe4002_init_phy()`, `ef4_fini_lm87()`, `sfe4002_set_id_led()`, and `sfe4002_check_hw()`.
- SFE4003: `sfe4003_init()`, `sfe4003_init_phy()`, `ef4_fini_lm87()`, `sfe4003_set_id_led()`, and `sfe4003_check_hw()`.
- SFN4112F: `sfn4112f_init()`, `sfn4112f_init_phy()`, `ef4_fini_lm87()`, `sfn4112f_set_id_led()`, and `sfn4112f_check_hw()`.

LM87 support is abstracted by `ef4_init_lm87()`, `ef4_fini_lm87()`, and `ef4_check_lm87()` when `CONFIG_SENSORS_LM87` is enabled, with no-op stubs otherwise. `ef4_poke_lm87()` writes register/value arrays, `falcon_lm87_common_regs[]` installs common board/controller critical temperature thresholds, and board-specific arrays set voltage and temperature limits.

SFE4001 power and reflash support is implemented by `sfe4001_poweron()`, `sfe4001_poweroff()`, sysfs attribute handlers `phy_flash_cfg_show()`/`phy_flash_cfg_store()`, `sfe4001_init()`, `sfe4001_fini()`, and `sfe4001_check_hw()`. This board uses a PCA9539 I/O expander at `0x74` and a MAX6647-compatible temperature monitor at `0x4e`.

PHY LED helpers include `sfe4002_init_phy()`, `sfe4002_set_id_led()`, `sfn4112f_init_phy()`, `sfn4112f_set_id_led()`, `sfe4003_init_phy()`, and `sfe4003_set_id_led()`. These call into PHY-specific helpers such as `falcon_qt202x_set_led()` and `falcon_txc_set_gpio_*()`.

## Control Flow

Board selection happens after NVRAM is validated in `falcon_probe_nvconfig()`. `falcon_probe_board()` only records type/revision and does not touch hardware. Later, `falcon_probe_nic()` creates the Falcon bit-banged I2C adapter and calls `board->type->init(efx)`, which performs I2C client creation and any board-specific power/sensor setup.

For LM87 boards, init creates an I2C client, clears alarm registers by reading them, writes board-specific limits, writes common thermal limits, and stores the client in `board->hwmon_client`. Monitor calls read alarm registers, mask board-specific bad/unused channels, optionally read temperature registers to decide whether alarm bits are truly critical, log a detailed problem/failure message, and return `-ERANGE` for critical/electrical failures.

SFE4001 init creates a MAX6647 or dummy hwmon client, raises the local high limit to 90 C, creates a PCA9539 dummy client, optionally stops MAC stats when entering PHY flash mode, powers on the PHY, and creates the `phy_flash_cfg` sysfs file. Power-on clears over-temperature latch, enables expander outputs, optionally performs a full power-cycle, then sequences 1.2 V/2.5 V/3.3 V/5 V rails before 1.0 V and waits for DSP/AFE readiness. In special reflash mode it holds the 3.3 V flash config line low and waits without requiring AFE startup.

`phy_flash_cfg_store()` serializes with `rtnl_lock()`, refuses changes while the netdevice is running or not ready, toggles `PHY_MODE_SPECIAL`, stops stats entering special mode, power-cycles the PHY, reconfigures the port, and restarts stats leaving special mode. This sysfs path is intentionally mutually exclusive with the normal open device.

During periodic monitoring, `falcon_monitor()` in `falcon.c` calls the installed board `monitor()` hook. For SFE4001, monitoring checks power-good inputs rather than directly reading the MAX6647 alarm because the temperature register is read-to-clear and could trigger unwanted power restoration. On detected power loss or I2C read failure, it powers off the board and forces `PHY_MODE_OFF`.

## State And Persistence Behavior

Persistent input is only the NVRAM board revision value used to select `board_types[]`. The file itself does not persist configuration, but it creates runtime I2C client state in `struct falcon_board` (`hwmon_client`, `ioexp_client`, `i2c_adap`, revision fields, and type pointer). SFE4001 exposes transient PHY reflash mode through `efx->phy_mode & PHY_MODE_SPECIAL`; the sysfs value reflects runtime mode and is not stored permanently.

Hardware state changed by this file includes sensor limit registers, PCA9539 output/config registers, PHY power rails, PHY LED registers/GPIOs, and over-temperature alarm latches. Teardown reverses client creation and powers down SFE4001 rails.

The LM87 path gracefully compiles to no-ops without `CONFIG_SENSORS_LM87`, which means board init and monitor succeed but sensor enforcement is absent. SFE4001 can use either a real LM90/MAX6647 hwmon driver client or a dummy I2C device depending on `CONFIG_SENSORS_LM90`.

## Dependencies And Integration Points

The file depends on Linux RTNL and I2C APIs and driver-local `net_driver.h`, `phy.h`, `efx.h`, `nic.h`, and `workarounds.h`. It is tightly integrated with `falcon.c` through `falcon_board(efx)->type` and with PHY code through `tenxpress_set_id_led()`, `falcon_qt202x_set_led()`, and TXC GPIO helpers. It depends on the I2C adapter being created before board init and removed after board fini.

The monitor return contract matters: `0` means healthy, `-ERANGE` means a hardware fault such as critical temperature/electrical failure, and other negative errors mean monitor I/O failed. `falcon_monitor()` reacts by logging and forcing PHY low power.

## Risks And Edge Cases

Sensor reads can be destructive because some alarm/status registers are read-to-clear. SFE4001 avoids direct MAX6647 status polling after power-on to prevent a thermal latch clear from re-enabling a board that has shut itself down. Changes to monitor logic must preserve that behavior.

Power sequencing is timing-sensitive. `sfe4001_poweron()` uses multiple rail orderings, sleeps, and retries waiting for DSP/AFE readiness; short-circuiting failures or changing active-low expander bit handling can leave the PHY partially powered. `sfe4001_poweroff()` is used both for cleanup and fault handling, so it must tolerate partially initialized clients.

Several board revisions have known bad or unwired sensors/LEDs. SFE4002 A0 and SFE4003 A0-A2 mask external temperature alarms, and SFE4003 LED GPIOs are ignored before A3. Removing these masks would cause false hardware-fault shutdowns.

The `phy_flash_cfg` sysfs mode manipulates PHY mode and stats. Incorrect locking or allowing changes while the interface is running could race the data path or stats DMA. The code uses RTNL and state/netif checks to keep the transition out of normal operation.

## Test Signals

Useful test signals include board probe failure on unknown type, I2C client creation failures, LM87 register-write failures, sensor alarm logs identifying board/controller overheating or electrical faults, SFE4001 "waiting for DSP boot" retry logs, timeout return from SFE4001 power-on, and `phy_flash_cfg` returning `-EBUSY` while the netdevice is running.

Regression tests on real or simulated hardware should cover each board ID, LM87-enabled and LM87-disabled builds, SFE4001 power-on failure unwinding, sysfs special-mode toggling with stats stop/start pairing, board revision-specific alarm masks, and LED behavior for QT202x and TXC-based boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon_boards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch.c

## Purpose

`farch.c` implements Falcon-architecture hardware support shared by Falcon/SFC4000 revisions for descriptor rings, event queues, interrupts, queue flushing, descriptor-cache setup, RX RSS indirection, and hardware filters. It is the low-level data-path engine used by the `falcon_a1_nic_type` and `falcon_b0_nic_type` operation tables in `falcon.c`.

The file translates generic driver objects (`struct ef4_tx_queue`, `struct ef4_rx_queue`, `struct ef4_channel`, `struct ef4_filter_spec`) into Falcon register-table entries and DMA-visible ring formats. It also consumes Falcon event queue entries and dispatches them to the generic TX/RX completion, reset, refill, and filter machinery.

## Important APIs, Types, And Functions

Special-buffer helpers (`ef4_alloc_special_buffer()`, `ef4_init_special_buffer()`, `ef4_fini_special_buffer()`, `ef4_free_special_buffer()`) allocate DMA buffers for descriptor/event rings, reserve buffer-table IDs from `efx->next_buffer_table`, and write/clear Falcon buffer table entries.

TX APIs include `ef4_farch_tx_probe()`, `ef4_farch_tx_init()`, `ef4_farch_tx_write()`, `ef4_farch_tx_limit_len()`, `ef4_farch_tx_fini()`, and `ef4_farch_tx_remove()`. `ef4_farch_tx_write()` converts software TX buffers into hardware qword descriptors, advances `write_count`, uses a write memory barrier, then either pushes the first descriptor or rings the TX doorbell.

RX APIs include `ef4_farch_rx_probe()`, `ef4_farch_rx_init()`, `ef4_farch_rx_write()`, `ef4_farch_rx_fini()`, `ef4_farch_rx_remove()`, and `ef4_farch_rx_defer_refill()`. RX initialization programs descriptor queue table entries with event queue label, buffer base, size, scatter/jumbo behavior, and iSCSI digest bits. RX writes build qword descriptors for newly added buffers and update the hardware write pointer.

Flush and FLR APIs include `ef4_farch_fini_dmaq()`, `ef4_farch_finish_flr()`, `ef4_farch_do_flush()`, `ef4_farch_flush_tx_queue()`, `ef4_farch_flush_rx_queue()`, and helpers for flush wakeup/completion. They coordinate TX and RX descriptor queue flush commands, flush completion events, generated drain events, retry of failed RX flushes, and cleanup after FLR where events may never arrive.

Event APIs include `ef4_farch_ev_probe()`, `ef4_farch_ev_init()`, `ef4_farch_ev_process()`, `ef4_farch_ev_read_ack()`, `ef4_farch_ev_fini()`, `ef4_farch_ev_remove()`, `ef4_farch_ev_test_generate()`, and `ef4_farch_generate_event()`. Event processing decodes RX, TX, generated, driver, and global events, clears consumed events to all-ones, updates `eventq_read_ptr`, and returns RX budget consumption.

Interrupt APIs include `ef4_farch_irq_enable_master()`, `ef4_farch_irq_disable_master()`, `ef4_farch_irq_test_generate()`, `ef4_farch_fatal_interrupt()`, `ef4_farch_legacy_interrupt()`, and `ef4_farch_msi_interrupt()`. These control the top-level interrupt enable register, schedule channel processing, detect fatal/non-event interrupt sources, and disable bus mastering on serious system errors.

Common hardware init functions include `ef4_farch_test_registers()`, `ef4_farch_fpga_ver()`, `ef4_farch_init_common()`, and `ef4_farch_rx_push_indir_table()`. `ef4_farch_init_common()` sets descriptor-cache SRAM bases/sizes, programs the interrupt-status DMA address, enables fatal interrupt sources, and configures TX DMA arbitration/pacing.

Filter support is represented by private `struct ef4_farch_filter_spec`, `struct ef4_farch_filter_table`, and `struct ef4_farch_filter_state`. Public filter operations include `ef4_farch_filter_table_probe()`, `ef4_farch_filter_table_restore()`, `ef4_farch_filter_table_remove()`, `ef4_farch_filter_insert()`, `ef4_farch_filter_remove_safe()`, `ef4_farch_filter_get_safe()`, `ef4_farch_filter_clear_rx()`, `ef4_farch_filter_count_rx_used()`, `ef4_farch_filter_get_rx_id_limit()`, `ef4_farch_filter_get_rx_ids()`, `ef4_farch_filter_update_rx_scatter()`, optional RFS hooks, and `ef4_farch_filter_sync_rx_mode()`.

## Control Flow

Queue setup is probe/init/remove/fini split. Probe allocates host DMA memory for descriptor/event rings. Init pins those buffers into Falcon buffer tables and writes descriptor/event queue pointer tables. Runtime TX/RX writes fill ring memory, issue barriers, and update hardware write pointers. Fini clears hardware tables and buffer-table entries; remove frees host memory.

TX event handling (`ef4_farch_handle_tx_event()`) handles batched completions by label and descriptor pointer, rewrites write pointers when the work-queue FIFO reports full, and schedules DMA-error reset on packet errors. RX event handling (`ef4_farch_handle_rx_event()`) validates descriptor order and start-of-packet state, supports scatter fragments through `scatter_n`, classifies checksum flags, records errors not covered by MAC stats, discards bad or unmatched multicast packets, and hands completed packets to `ef4_rx_packet()`.

Flush flow starts in `ef4_farch_fini_dmaq()`: if not in recovery and bus mastering is enabled, the NIC type's `prepare_flush()` runs, all TX queues get flush commands, RX queues become pending, and `ef4_farch_do_flush()` submits up to four concurrent RX flushes until all active queues drain or a five-second timeout expires. Hardware flush-done events trigger generated drain events so the event queues are drained of residual completions before active queue count reaches zero.

Event processing loops until an all-ones empty event is found or the RX budget is consumed. Generated events implement internal control messages: test event CPU recording, deferred RX refill, RX drain, and TX drain. Driver events cover flush completions, event queue init, SRAM update, wakeup/timer notifications, RX recovery, and descriptor fetch errors. Global events are delegated to the NIC type, which lets `falcon.c` handle PHY/XMAC and RX recovery signals.

Interrupt flow is intentionally thin. Legacy interrupts read/ack the ISR, handle fatal status from the shared interrupt-status buffer, schedule per-channel tasklets for active event queues, and compensate for zero ISR reads by checking event presence. MSI interrupts schedule the context's channel directly and check fatal status only on the selected non-event IRQ level.

Filter insertion converts a generic `ef4_filter_spec` to Falcon format, chooses RX IP/RX MAC/RX default/TX MAC table, searches for replacement and free slots using the Falcon hardware hash/increment sequence, enforces priority and replace semantics, updates software bitmaps/spec arrays, pushes search-limit registers when depth grows, writes the hardware table entry, and returns an encoded filter ID. Removal and get decode user-visible IDs defensively before touching table state.

## State And Persistence Behavior

Descriptor and event ring state is DMA memory owned by queue/channel objects. Hardware persistence consists of buffer-table entries, descriptor queue pointer-table entries, event queue pointer/read-pointer entries, interrupt registers, and filter-table registers. These are volatile and are rebuilt after reset or queue reallocation.

Flush state uses `efx->active_queues`, `efx->rxq_flush_pending`, `efx->rxq_flush_outstanding`, per-RX `flush_pending`, and per-TX `flush_outstanding`. `ef4_farch_finish_flr()` explicitly clears this state after FLR because DMA failures can prevent normal completion events.

Filter state persists across hardware reset in software as `efx->filter_state`: per-table `used_bitmap`, `spec` arrays, `used` counts, and `search_limit[]`. `ef4_farch_filter_table_restore()` replays used entries into hardware and pushes RX/TX search-limit/default-filter configuration after reset. It is not persistent across driver unload.

Runtime multicast and promiscuous mode state is captured by `ef4_farch_filter_sync_rx_mode()` in `efx->unicast_filter` and `efx->multicast_hash`, while actual MAC multicast hash register writes happen in `falcon.c`.

Synchronization uses memory barriers before doorbells/read-pointer acknowledgements, `spin_lock_bh(&efx->filter_lock)` for filter state, atomic counters for flush progress, and wait queues for flush completion. Interrupt handlers use `READ_ONCE(efx->irq_soft_enabled)` and schedule channel work rather than processing full queues in hard IRQ context.

## Dependencies And Integration Points

This file depends on Linux interrupt, PCI, module, seq-file, CRC32, and netdevice primitives plus Falcon driver headers `net_driver.h`, `bitfield.h`, `efx.h`, `nic.h`, `farch_regs.h`, `io.h`, and `workarounds.h`.

It is wired into `falcon.c` through the NIC type operation tables. It calls generic driver services such as `ef4_xmit_done()`, `ef4_rx_packet()`, `ef4_fast_push_rx_descriptors()`, `ef4_schedule_reset()`, `ef4_schedule_channel_irq()`, `ef4_try_recovery()`, `ef4_rss_enabled()`, and the register I/O helpers. Global event handling is delegated back through `efx->type->handle_global_event`.

Filter APIs are consumed by ethtool/RX/RFS paths through generic `ef4_filter_spec` operations. RSS indirection is populated by `falcon_b0_rx_push_rss_config()` in `falcon.c`. Queue sizes, register-table bases, interrupt mode, scatter capability, and filter-table availability depend on the selected Falcon revision in `struct ef4_nic_type`.

## Risks And Edge Cases

Ring and doorbell ordering is critical. Descriptors must be visible to DMA before write-pointer updates; event queue entries must be cleared before read acknowledgements. Missing barriers can produce stale DMA reads or repeated events.

Flush is inherently racy with DMA and reset. RX flush supports only four outstanding commands and may fail due to descriptor fetches, so retry/pending accounting must remain balanced. TX flush completion can be inferred by reading descriptor pointer tables when events are missing; this is essential for timeout recovery. Incorrect active queue accounting can permanently block queue reallocation.

RX event ordering and scatter handling are fragile. Bad indices may be benign partial packet truncations or serious event loss; the code distinguishes those cases and schedules RX recovery/disable when needed. Misclassifying packet-ok and checksum flags can lead to bad skb checksum state.

Fatal interrupt handling disables bus mastering and may disable the NIC after repeated errors within `EF4_INT_ERROR_EXPIRE`. It also handles EEH-style all-ones legacy ISR reads. Changes here can affect recovery from PCI errors and shared IRQ behavior.

Filter table search limits are a correctness and performance boundary. Search depth must be large enough to find installed filters but bounded to avoid hardware timeouts and software infinite loops. Default filters, auto filters, RX-over-auto replacement, priority checks, and encoded filter IDs all need to stay consistent with RX NFC and RFS expectations. The current `ef4_farch_filter_table_probe()` only initializes the RX IP table for Falcon B0 in this source; zero-sized tables intentionally cause unsupported filter classes to return `-EINVAL`.

## Test Signals

Self-test coverage includes `ef4_farch_test_registers()` bit-sweep validation and `ef4_farch_ev_test_generate()` generated event delivery. Runtime diagnostics include TX/RX descriptor fetch error events, dropped RX event logs, RX recovery event logs, fatal interrupt logs including memory parity status, flush timeout logs with active/pending/outstanding counts, and unexpected event-type logs.

Regression coverage should exercise TX descriptor push versus doorbell paths, RX scatter and bad-index paths, flush success/retry/timeout/FLR cleanup, legacy and MSI interrupt scheduling, fatal interrupt rate limiting, RSS indirection programming, filter insert/replace/remove/get/list/clear behavior, RFS expiry when enabled, and filter restore after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch.c -->
