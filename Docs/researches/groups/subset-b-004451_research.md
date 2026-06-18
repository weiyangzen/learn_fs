# subset-b-004451 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/netdev.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/netdev.c

## Purpose
`netdev.c` is the main Linux network-device and PCI driver body for Intel e1000e adapters. It binds PCI device IDs to board variants, creates and registers the `net_device`, wires `net_device_ops`, NAPI, interrupts, power management, PCI error recovery, reset/open/close flows, RX/TX descriptor rings, VLAN/RSS/offload behavior, statistics, hardware timestamping, WoL, S0ix, and module registration. Lower-level MAC/PHY/NVM behavior is delegated through operation tables in `struct e1000_hw`, while this file owns the OS-facing lifecycle and fast paths.

## Important APIs, types, and functions
- Driver entry points: `e1000_init_module()`, `e1000_exit_module()`, `e1000_probe()`, `e1000_remove()`, `e1000_shutdown()`, `e1000_driver`, `e1000_pci_tbl`, `e1000_err_handler`, and `e1000e_pm_ops`.
- Netdev entry points: `e1000e_netdev_ops` binds `ndo_open`, `ndo_stop`, `ndo_start_xmit`, `ndo_get_stats64`, `ndo_set_rx_mode`, `ndo_set_mac_address`, `ndo_change_mtu`, `ndo_eth_ioctl`, `ndo_tx_timeout`, VLAN add/kill, feature negotiation, and hardware timestamp get/set.
- Adapter/ring state: functions operate mainly on `struct e1000_adapter`, `struct e1000_hw`, `struct e1000_ring`, and per-descriptor `struct e1000_buffer` arrays. Ring cursors `next_to_use` and `next_to_clean` form the central producer/consumer state.
- Register access: `__ew32_prepare()` and `__ew32()` wrap MMIO writes and include an ME/PCIM2PCI arbiter workaround. `er32`/`ew32`, descriptor macros, and hardware constants from `e1000.h` drive register programming.
- RX path: buffer allocation helpers `e1000_alloc_rx_buffers()`, `e1000_alloc_rx_buffers_ps()`, `e1000_alloc_jumbo_rx_buffers()` pair with cleaners `e1000_clean_rx_irq()`, `e1000_clean_rx_irq_ps()`, and `e1000_clean_jumbo_rx_irq()`. `e1000_receive_skb()`, `e1000_rx_checksum()`, and `e1000_rx_hash()` hand packets to GRO with checksum, VLAN, RSS, and timestamp metadata.
- TX path: `e1000_xmit_frame()` checks descriptor space, offload requirements, VLAN tags, no-FCS, hardware timestamping, and DMA maps skb data through `e1000_tx_map()` before descriptor programming in `e1000_tx_queue()`. `e1000_tso()` and `e1000_tx_csum()` create context descriptors. `e1000_clean_tx_irq()` completes descriptors and wakes the queue.
- Interrupts and NAPI: `e1000e_set_interrupt_capability()`, `e1000_request_irq()`, `e1000_request_msix()`, `e1000_intr()`, `e1000_intr_msi()`, `e1000_intr_msix_rx()`, `e1000_intr_msix_tx()`, `e1000_msix_other()`, `e1000_irq_enable()`, `e1000_irq_disable()`, and `e1000e_poll()` implement legacy, MSI, and MSI-X paths.
- Configuration and reset: `e1000_sw_init()`, `e1000e_open()`, `e1000e_close()`, `e1000e_up()`, `e1000e_down()`, `e1000e_reinit_locked()`, `e1000e_reset()`, `e1000_configure()`, `e1000_configure_tx()`, `e1000_setup_rctl()`, `e1000_configure_rx()`, and descriptor flush helpers restore a usable hardware state.
- Link, watchdog, and stats: `e1000_watchdog_task()`, `e1000e_has_link()`, `e1000_print_link_info()`, `e1000e_update_stats()`, `e1000e_get_stats64()`, `e1000e_update_phy_stats()`, and PHY work/timers maintain carrier state, counters, hang detection, and periodic recovery.
- PTP/hwtstamp: `e1000e_get_base_timinca()`, `e1000e_config_hwtstamp()`, `e1000e_systim_reset()`, `e1000e_read_systim()`, `e1000e_cyclecounter_read()`, `e1000e_rx_hwtstamp()`, and `e1000e_tx_hwtstamp_work()` integrate with Linux PHC and socket timestamping.
- Power and recovery: `e1000e_pm_freeze()`, `__e1000_shutdown()`, `__e1000_resume()`, runtime PM callbacks, S0ix entry/exit flows, ASPM disable helpers, WoL setup, and PCI AER handlers manage suspend/resume and slot-reset recovery.

## Control flow
Module load registers `e1000_driver` with the PCI core. On match, `e1000_probe()` enables PCI memory resources, establishes DMA, maps MMIO and optional flash BARs, allocates `net_device`, initializes adapter flags from `e1000_info_tbl`, validates module options, installs MAC/NVM/PHY ops, initializes hardware variants, reads and validates NVM/MAC address, sets features, initializes timers/work items/PTP, resets hardware, gives the driver hardware control, and registers the netdev.

Interface bring-up enters `e1000e_open()`: runtime PM is acquired, TX/RX resources are allocated, AMT control and PHY power are established, QoS latency request is added, hardware is configured before IRQ registration, IRQ mode is requested and optionally MSI-tested, NAPI is enabled, interrupts are enabled, and a synthetic link-status change starts watchdog-driven link negotiation. `e1000e_up()` is the shorter post-reset bring-up path: configure, clear the down bit, set MSI-X registers if needed, enable interrupts, and trigger LSC.

RX interrupts schedule NAPI. `e1000e_poll()` cleans TX as needed, calls the current RX cleaner selected by MTU/packet-split mode, and when budget is not exhausted completes NAPI, adjusts dynamic interrupt moderation, and reenables interrupts. RX cleaners consume descriptors with DD set, enforce EOP/fragment rules, unmap DMA, handle CRC stripping/RXFCS/RXALL, mark checksum and RSS state, attach VLAN and hardware timestamps, send the skb through GRO, clear descriptor status, and batch-refill hardware buffers.

TX begins in `e1000_xmit_frame()`. It rejects down or empty skbs, pads minimum frames, accounts for TSO/checksum context descriptors and data descriptors, stops the queue if insufficient ring space remains, extracts VLAN and protocol flags, emits TSO or checksum context descriptors, maps linear and fragmented skb data into DMA descriptors, handles the single outstanding TX hardware timestamp skb, queues descriptors, updates BQL with `netdev_sent_queue()`, and finally writes TDT unless xmit-more batching delays the doorbell. Completion in `e1000_clean_tx_irq()` walks descriptors through their watched EOP, unmaps buffers, updates BQL via `netdev_completed_queue()`, wakes the queue when there is room, and schedules hang diagnostics if a watched buffer times out.

Reset and reconfiguration paths converge on `e1000e_down()` plus `e1000e_reset()` plus `e1000e_up()`. Down sets `__E1000_DOWN`, disables RX/TX, masks interrupts, synchronizes NAPI and timers, snapshots stats, flushes descriptor writebacks, optionally resets hardware or flushes descriptor rings, then frees ring contents. Reset recalculates packet-buffer allocation and flow-control watermarks, disables AIM if jumbo frames cannot fit, handles hardware-specific descriptor flushes and errata, calls hardware reset/init ops, restores manageability VLAN, VLAN ethertype, adaptive state, PTP timestamp state, EEE advertisement, PHY power, smart-power-down, and clock-gating workarounds.

The watchdog work item is the central slow-path state machine. It checks link, transitions carrier up/down, resumes runtime PM on link, programs link-speed dependent TX settings, wakes or stops the queue, schedules PHY info reads, updates stats and adaptive IFS/ITR, requests resets on restart conditions or PHY hangs, clears stuck RX timestamp registers, and reschedules itself.

Suspend and shutdown freeze the netdev, detach and quiesce running interfaces, disable interrupts and PCI master access, program wake filters through MAC or PHY, apply ULP/EEE/S0ix/ASPM workarounds, release hardware to firmware, and clear bus mastering. Resume restores ASPM policy, PCI master, PHY/MAC workarounds, wake status, hardware reset, manageability pass-through, driver-control bits, IRQ resources, and netdev attachment.

## State and persistence behavior
Persistent hardware state is in PCI config, MMIO registers, descriptor memory, MAC/PHY/NVM registers, PHY wake registers, and firmware ownership bits. Software state is concentrated in `struct e1000_adapter`: flags and flags2, ring pointers and DMA addresses, interrupt mode/vectors, NAPI, timers, work items, stats accumulators, link speed/duplex, WoL settings, management VLAN, PTP timecounter/cyclecounter, TX timestamp skb, and EEE settings.

State survives across reset only when explicitly restored. Examples include VLAN filters, manageability VLAN, PTP frequency and hwtstamp config, EEE advertisement, LAA workaround state, WoL, and module option-derived interrupt/ring behavior. Hardware counters are read-to-clear and accumulated into `adapter->stats`. NVM-derived values such as MAC address, WoL defaults, PBA string, and EEPROM version are read at probe.

Concurrency state is guarded by kernel primitives: NAPI serialization, IRQ masking/synchronization, `__E1000_DOWN`, `__E1000_RESETTING`, `__E1000_TESTING` bits, RTNL around resets from work, spinlocks for stats and SYSTIM conversion, DMA barriers before descriptor and buffer observation, and runtime PM references around paths that access powered hardware.

## Dependencies and integration points
This file depends on Linux PCI, netdevice, NAPI, DMA mapping, interrupt, VLAN, checksum/GSO, ethtool, runtime/system PM, PTP, CPU latency QoS, timer/workqueue, and PCI error-recovery APIs. It integrates with e1000e-local headers and modules: `e1000.h`, `e1000e_trace.h`, board info in `80003es2lan.c`, `82571.c`, `ich8lan.c`, MAC/NVM/PHY operation tables, `ethtool.c`, and `ptp.c`.

Important external integration contracts include `register_netdev()`, `netif_napi_add()`, `request_irq()`/MSI-X vector setup, `pci_register_driver()`, `dma_alloc_coherent()` descriptor memory, `dma_map_*()` packet buffers, `skb` offload metadata, Linux PHC registration from `ptp.c`, and firmware/ME ownership through SWSM/CTRL_EXT/H2ME/FWSM registers.

## Risks and edge cases
- Descriptor ring correctness is high risk: incorrect cursor movement, missing DMA barriers, or stale DMA mappings can cause data corruption, leaks, queue stalls, or device hangs.
- Reset and PM paths are tightly coupled to hardware errata. Changes around `e1000_flush_desc_rings()`, S0ix flows, ULP, ASPM, jumbo frame workarounds, and ME/firmware ownership can regress specific chip generations.
- Interrupt fallback logic must remain coherent across legacy, MSI, MSI-X, netpoll, and runtime PM. A missed mask/unmask or stale vector can produce interrupt storms or dead queues.
- Hardware timestamping supports only one outstanding TX timestamp skb. Mismanaging `tx_hwtstamp_skb` can leak skb references or report timestamps to the wrong packet.
- RX CRC stripping, RXFCS, jumbo, packet split, and BMC/management traffic interact. Feature changes can break jumbo support on newer PCH devices or BMC expectations.
- NVM checksum and MAC address validation at probe are hard failure points; transient NVM/ASPM problems are retried, but persistent failure prevents device registration.
- Watchdog resets run from workqueue under RTNL and depend on state bits. Incorrect ordering can race close/suspend/remove.

## Test signals
Useful validation includes kernel build coverage for `drivers/net/ethernet/intel/e1000e`, module load/unload on supported hardware, probe success with valid NVM checksum and MAC, interface up/down cycles, traffic with checksum offload/TSO/TSO6/GRO, VLAN add/remove and promiscuous/all-multicast modes, jumbo MTU changes, MSI/MSI-X fallback, netpoll if enabled, suspend/resume/runtime PM/WoL, PTP timestamp set/get and TX/RX timestamp traffic, ethtool feature toggles, PCI error recovery injection, and stress for TX hangs, RX allocation failures, DMA mapping errors, and link flap watchdog behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.c

## Purpose
`nvm.c` implements generic EEPROM/NVM primitives for the e1000e driver. It provides bit-banged SPI EEPROM clock/data helpers, register-based EERD reads, SPI writes, NVM arbitration, PBA string decoding, MAC address extraction, checksum validation/update, and NVM reload. Board-specific code installs these routines through `hw->nvm.ops`, while callers use wrappers such as `e1000_read_nvm()`, `e1000_write_nvm()`, and `e1000_validate_nvm_checksum()`.

## Important APIs, types, and functions
- Low-level EEPROM signaling: `e1000_raise_eec_clk()`, `e1000_lower_eec_clk()`, `e1000_shift_out_eec_bits()`, and `e1000_shift_in_eec_bits()` manipulate EECD clock, data-in, data-out, and chip-select bits with `udelay(hw->nvm.delay_usec)`.
- NVM arbitration and command framing: `e1000e_acquire_nvm()` requests EECD ownership and waits for grant, `e1000e_release_nvm()` clears the request after `e1000_stop_nvm()`, `e1000_standby_nvm()` toggles SPI chip select, and `e1000_ready_nvm_eeprom()` waits for the SPI status register ready bit.
- Register polling/read: `e1000e_poll_eerd_eewr_done()` waits for EERD/EEWR done, and `e1000e_read_nvm_eerd()` validates bounds then reads words through the EERD register.
- Write path: `e1000e_write_nvm_spi()` validates bounds, acquires NVM, waits for readiness, sends write-enable and write opcodes, streams words byte-swapped into page-sized SPI writes, sleeps for completion, and releases ownership.
- Device data helpers: `e1000_read_pba_string_generic()` reads legacy or pointer-guarded PBA numbers, `e1000_read_mac_addr_generic()` copies RAL/RAH register contents into `hw->mac.perm_addr` and `hw->mac.addr`.
- Integrity and reload: `e1000e_validate_nvm_checksum_generic()` sums words through `NVM_CHECKSUM_REG` and compares with `NVM_SUM`, with a TGP uninitialized-checksum exception; `e1000e_update_nvm_checksum_generic()` recomputes and writes the checksum; `e1000e_reload_nvm_generic()` toggles `CTRL_EXT.EE_RST`.

## Control flow
For register reads, callers pass an offset, word count, and buffer into `e1000e_read_nvm_eerd()`. The function rejects zero-length or out-of-bounds requests, writes the target word index and start bit to EERD, polls `E1000_NVM_RW_REG_DONE`, and extracts the returned 16-bit word from EERD.

For SPI writes, `e1000e_write_nvm_spi()` loops until all requested words are written. Each page transaction acquires NVM ownership, waits until the EEPROM ready bit clears, toggles standby, sends `NVM_WREN_OPCODE_SPI`, sends the write opcode plus address, shifts each word MSB-first after byte swapping, stops at a page boundary, waits 10-11 ms for programming, then releases ownership. Callers are expected to update the NVM checksum afterward.

PBA string reading first reads `NVM_PBA_OFFSET_0` and `NVM_PBA_OFFSET_1`. If the guard word is absent, it decodes a legacy packed hex PBA into a fixed string. If the guard is present, it treats the second word as a pointer, validates the section length, checks caller buffer space, then reads each word as two ASCII bytes.

Checksum validation reads and accumulates NVM words from zero through the checksum word. The result must equal `NVM_SUM`, except Tiger Lake/PCH TGP can ignore an explicitly uninitialized checksum word. Updating sums all words before the checksum, writes `NVM_SUM - checksum` back to `NVM_CHECKSUM_REG`, and returns the write status.

## State and persistence behavior
This file directly mutates EEPROM/NVM contents only in `e1000e_write_nvm_spi()` and `e1000e_update_nvm_checksum_generic()`. It also changes hardware access state through EECD request/grant/chip-select bits and reloads NVM shadow state through `CTRL_EXT.EE_RST`. MAC and PBA helpers read persistent device identity data and place it into `hw->mac` or caller buffers.

NVM access is serialized by hardware grant bits, not by a local mutex in this file. The caller-provided operation table determines whether these generic helpers are combined with board-specific locking. Timing behavior is persistent only insofar as EEPROM commands require precise delays and page-boundary handling.

## Dependencies and integration points
The file includes `e1000.h` and depends on register access macros (`er32`, `ew32`, `e1e_flush`), `struct e1000_hw`, `struct e1000_nvm_info`, `struct e1000_mac_info`, NVM constants and opcodes, Linux delay helpers, error codes, and debug logging. It is used by probe, ethtool/NVM paths, board variant setup, and reset flows that need MAC address, checksum, PBA, or EEPROM reload services.

## Risks and edge cases
- Incorrect bounds checks or word counts could read/write outside the EEPROM word size; this file rejects offset overflow and zero-word requests.
- SPI bit-banging depends on exact EECD transitions and delays. Changes can break EEPROMs with strict timing or address-bit handling.
- `e1000e_write_nvm_spi()` writes persistent NVM and warns that checksum update is required. Interrupted or misordered writes can leave invalid configuration.
- Page-boundary handling is critical; crossing a page without standby/program delay can wrap or corrupt EEPROM data.
- PBA string parsing must validate length and caller buffer size to avoid malformed NVM data overruns.
- TGP checksum exception deliberately accepts an uninitialized value; tests must distinguish intended platform behavior from silent checksum acceptance elsewhere.

## Test signals
Validation signals include successful probe MAC read, NVM checksum validation, PBA string display in device info, ethtool EEPROM read/write behavior where enabled, checksum update after writes, SPI write page-boundary tests, invalid offset/count rejection, NVM grant timeout handling, and hardware reset/NVM reload behavior. Fault injection around EERD done polling, NVM grant timeout, DMA-independent EEPROM reads, malformed PBA sections, and uninitialized TGP checksum would cover the main branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.h

## Purpose
`nvm.h` declares the generic e1000e NVM/EEPROM helper interface used across the driver. It exposes acquisition, polling, read/write, checksum, PBA, MAC address, LED default validation, and release routines implemented in `nvm.c` or related MAC code, and defines `E1000_STM_OPCODE` for NVM command use.

## Important APIs, types, and functions
- Access control: `e1000e_acquire_nvm()` and `e1000e_release_nvm()` bracket exclusive EEPROM access.
- Polling and data movement: `e1000e_poll_eerd_eewr_done()`, `e1000e_read_nvm_eerd()`, and `e1000e_write_nvm_spi()` provide generic read/write mechanisms.
- Identity helpers: `e1000_read_mac_addr_generic()` and `e1000_read_pba_string_generic()` expose persistent MAC/PBA extraction.
- Integrity helpers: `e1000e_validate_nvm_checksum_generic()` and `e1000e_update_nvm_checksum_generic()` expose checksum validation/update.
- LED validation: `e1000e_valid_led_default()` is declared here but implemented in `mac.c`, reflecting a shared NVM-backed LED default contract.
- Constant: `E1000_STM_OPCODE` is defined as `0xDB00`.

## Control flow
This header has no runtime control flow. It is included by driver implementation files that need prototypes for operation tables or direct helper calls. Board-specific initialization can assign these functions into `hw->nvm.ops` and other code can call the exported generic helpers.

## State and persistence behavior
The header itself stores no state. The declared functions operate on `struct e1000_hw`, which carries NVM/MAC/PHY state and hardware register mappings. Some declared functions read or mutate persistent EEPROM content or hardware-shadowed NVM state.

## Dependencies and integration points
The header assumes `struct e1000_hw`, `s32`, `u8`, `u16`, and `u32` are already visible through surrounding e1000e headers. It is part of the e1000e internal API and integrates with `nvm.c`, `mac.c`, board variant files, and callers in probe/ethtool/reset code.

## Risks and edge cases
- Prototype drift between this header and implementations would break operation-table initialization or cross-file calls at build time.
- Because this header declares persistent NVM write/checksum functions, misuse by callers can corrupt EEPROM if acquisition/release and checksum-update contracts are ignored.
- `E1000_STM_OPCODE` has no local context here; changes require checking all command users.

## Test signals
Build coverage is the main direct test signal. Runtime validation comes indirectly from NVM read/write, checksum, MAC/PBA, and LED default paths in the files that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/param.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/param.c

## Purpose
`param.c` defines and validates e1000e module parameters, converting per-board integer arrays and the global `copybreak` value into fields and flags on `struct e1000_adapter`. It centralizes user-configurable interrupt moderation, interrupt mode, PHY workarounds, NVM write protection, smart power down, and CRC stripping behavior used later by `netdev.c`.

## Important APIs, types, and functions
- Module parameters: `copybreak`, `TxIntDelay`, `TxAbsIntDelay`, `RxIntDelay`, `RxAbsIntDelay`, `InterruptThrottleRate`, `IntMode`, `SmartPowerDownEnable`, `KumeranLockLoss`, `WriteProtectNVM`, and `CrcStripping`.
- Parameter macros and limits: `E1000_MAX_NIC`, `OPTION_UNSET`, `OPTION_DISABLED`, `OPTION_ENABLED`, `E1000_PARAM_INIT`, `E1000_PARAM`, and per-option default/min/max constants.
- Validation model: `struct e1000_option` supports `enable_option`, `range_option`, and `list_option`; `e1000_validate_option()` applies defaults, validates ranges/lists/binary enable values, logs accepted settings, and replaces invalid values with defaults.
- Public entry point: `e1000e_check_options(struct e1000_adapter *adapter)` reads module parameter arrays at `adapter->bd_number`, validates values, and writes final settings into adapter fields.

## Control flow
At module load, Linux module-param machinery stores user-provided arrays and counts. During probe, after adapter flags are initialized, `e1000e_check_options()` runs for the adapter board number. If the board index exceeds `E1000_MAX_NIC`, it logs that defaults are used.

For each option, `e1000e_check_options()` builds a local `e1000_option`, checks whether the corresponding `num_*` count covers this board index, and either validates the user value or assigns the default. TX/RX delay options write `adapter->tx_int_delay`, `tx_abs_int_delay`, `rx_int_delay`, and `rx_abs_int_delay`; RX defaults switch to burst values when `FLAG2_DMA_BURST` is set.

`InterruptThrottleRate` has extra mode handling after range validation. Mode `0` disables ITR, `1` becomes dynamic mode with runtime value 20000, invalid special mode `2` falls back to default, `3` becomes dynamic conservative mode at 20000, `4` enables simplified 2000-8000 interrupt mode, and explicit numeric values clear low control bits in `itr_setting`.

`IntMode` chooses the best allowed interrupt mode based on `CONFIG_PCI_MSI` and `FLAG_HAS_MSIX`. With MSI support, it dynamically allocates an error/default string, defaults to MSI-X when hardware supports it and MSI otherwise, validates user input, and stores `adapter->int_mode`. Without MSI support, only legacy mode is valid.

Boolean options then set hardware-behavior flags or call workarounds: smart power down sets `FLAG_SMART_POWER_DOWN` only on capable devices; CRC stripping sets `FLAG2_CRC_STRIPPING` and `FLAG2_DFLT_CRC_STRIPPING`; Kumeran lock-loss calls `e1000e_set_kmrn_lock_loss_workaround_ich8lan()` for ICH8; write-protect NVM sets `FLAG_READ_ONLY_NVM` for ICH devices when enabled.

## State and persistence behavior
Module parameter values persist for the loaded module instance. `copybreak` is global and later used by RX cleaners to copy small packets into smaller skbs. Per-board arrays persist in static storage and are interpreted by board discovery order (`adapter->bd_number`).

The main state mutations are adapter fields and flags consumed by `netdev.c`: interrupt delay fields program hardware registers, `itr`/`itr_setting` control dynamic interrupt moderation, `int_mode` selects interrupt allocation, `FLAG_SMART_POWER_DOWN` affects PHY power behavior, `FLAG2_CRC_STRIPPING` affects RX CRC handling and jumbo support, and `FLAG_READ_ONLY_NVM` prevents writes on ICH paths. No NVM is written directly in this file.

## Dependencies and integration points
The file depends on Linux `module_param`, `module_param_array_named`, `MODULE_PARM_DESC`, PCI/device logging, allocation for dynamic strings, and e1000e internal definitions in `e1000.h`. Its output is consumed by probe, interrupt setup, TX/RX configuration, RX cleaners, reset, PHY workarounds, NVM write-protection code, and feature toggling.

## Risks and edge cases
- Board-number indexing means option arrays map by discovery order, not stable physical slot identity. Systems with more than `E1000_MAX_NIC` adapters silently use defaults for boards beyond the limit.
- Invalid values are logged and replaced with defaults; callers should not assume user input survived validation.
- `IntMode` allocates temporary strings under `CONFIG_PCI_MSI`; allocation failure exits `e1000e_check_options()` early, leaving later options unapplied.
- `InterruptThrottleRate` has special modes outside the normal numeric range, so validation logic deliberately treats values `0-4` differently from ordinary interrupt rates.
- Disabling NVM write protection is explicitly dangerous, because later NVM write paths can persistently corrupt EEPROM.
- CRC stripping interacts with BMC traffic, RXFCS, and jumbo-frame support on newer PCH hardware.

## Test signals
Useful tests include loading the module with valid, unset, and invalid values for every parameter; checking dmesg logs for accepted/defaulted settings; validating interrupt mode fallback on systems with and without MSI-X; verifying ITR dynamic/simple/off behavior through traffic and register inspection; checking `copybreak` effects on small RX packets; confirming CRC stripping/RXFCS/jumbo interactions; and ensuring write-protect flags are applied only to ICH adapters. Build coverage should include both `CONFIG_PCI_MSI` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/param.c -->
