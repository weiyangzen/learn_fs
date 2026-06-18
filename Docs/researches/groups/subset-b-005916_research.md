# Research: subset-b-005916

This grouped report covers Linux header files under `sources/distributed-fs/ceph-client/include/linux/`. Each file section is bounded by the exact reconciliation markers used to split source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_core.h -->
# sources/distributed-fs/ceph-client/include/linux/serial_core.h

## Purpose

`serial_core.h` is the central UART/TTY driver contract for serial drivers in this kernel tree. It defines the `struct uart_ops` hardware callback ABI, the persistent state objects used by the serial core, UART port metadata, locking wrappers, transmit FIFO helpers, console and early-console declarations, registration APIs, power management APIs, and helper paths for modem status, SysRQ, break handling, and RS485 mode discovery.

## Important APIs, Types, And Functions

Key types are `struct uart_ops`, `struct uart_port`, `struct uart_state`, `struct uart_driver`, `struct earlycon_device`, and `struct earlycon_id`. `struct uart_ops` is the lower-level driver vtable, covering transmitter empty checks, modem control, TX/RX start and stop, throttle/unthrottle, high-priority XON/XOFF characters, startup/shutdown, termios changes, power management, resource request/release, port verification, ioctls, and optional console polling. `struct uart_port` combines hardware accessors, IRQ/clock/FIFO properties, flow-control state, port flags, console/sysrq data, RS485/ISO7816 config, and platform-private data.

Important helpers include `uart_port_set_cons()`, the `uart_port_lock*()` and `uart_port_unlock*()` wrappers, `serial_port_in()`, `serial_port_out()`, `uart_xmit_advance()`, `uart_fifo_out()`, `uart_fifo_get()`, `uart_port_tx*()` macros, `uart_update_timeout()`, `uart_get_baud_rate()`, `uart_get_divisor()`, `uart_fifo_timeout()`, `uart_poll_timeout()`, `OF_EARLYCON_DECLARE()`, `EARLYCON_DECLARE()`, `setup_earlycon()`, `uart_parse_options()`, `uart_set_options()`, `uart_console_write()`, `uart_register_driver()`, `uart_add_one_port()`, `uart_suspend_port()`, `uart_resume_port()`, `uart_handle_dcd_change()`, `uart_handle_cts_change()`, `uart_insert_char()`, `uart_xchar_out()`, and `uart_get_rs485_mode()`.

## Control Flow

The header describes the serial core lifecycle: a low-level driver registers a `uart_driver`, adds one or more `uart_port` instances, implements `uart_ops`, and then the TTY layer opens, configures, transmits, receives, suspends, resumes, and removes ports through those callbacks. Startup is expected to acquire hardware resources and enable reception without asserting RTS/DTR; shutdown disables hardware and releases resources after users disappear. `set_termios()` is the primary reconfiguration path for word length, parity, stop bits, input error masks, and flow-control behavior.

Transmit helpers implement a reusable loop: send `x_char` first, stop if `uart_tx_stopped()` reports software or hardware flow stop, pull bytes from `tty_port.xmit_fifo`, run the driver-supplied write expression, update TX accounting, wake writers below `WAKEUP_CHARS`, and optionally call `ops->stop_tx()` when empty. Break handling first calls a driver hook, then toggles the serial SysRQ window for console ports when enabled, and finally performs SAK if `UPF_SAK` is set.

## State And Persistence

`struct uart_state` is explicitly persistent across opens and contains the TTY port, PM state, refcount, remove waitqueue, and current `uart_port`. `struct uart_port` keeps long-lived hardware configuration, counters in `uart_icount`, modem-control state, flags, status bits, sysrq state, console pointer, RS485/ISO7816 settings, and a private pointer. The header documents locking requirements: many `uart_ops` callbacks run under `port->lock` with local interrupts disabled, while configuration calls usually run under `tty_port->mutex` or the port semaphore.

The port lock wrappers also coordinate with nbcon consoles. When a port is the registered non-blocking console with atomic write support, the wrapper acquires or releases the console device context around the spinlock. The `uart_port_set_cons()` helper updates `port->cons` under the port lock to avoid stale console pointers while another context holds the wrapped lock.

## Dependencies And Integration Points

Dependencies include TTY core, console/nbcon, sysrq, kfifo via `tty_port`, termios, UAPI serial flags, device model, interrupt and spinlock primitives, RS485/ISO7816 UAPI structs, early console table sections, and optional `CONFIG_CONSOLE_POLL`, `CONFIG_SERIAL_CORE_CONSOLE`, `CONFIG_SERIAL_EARLYCON`, and `CONFIG_MAGIC_SYSRQ_SERIAL`. Integration points are serial hardware drivers, platform/OF/ACPI early console discovery, KGDB polling, PM suspend/resume, and TTY line discipline behavior.

## Risks And Test Signals

Major risks are incorrect callback locking, sleeping in no-sleep contexts, using raw `port->lock` instead of the UART lock wrappers when nbcon is involved, stale `port->state` use after shutdown, wrong UAPI flag mappings, incorrect FIFO accounting, and mishandled SysRQ/break paths. Test signals include serial console boot, earlycon boot logs, open/close loops, CTS/DCD transitions, XON/XOFF and RTS/CTS flow control, break and SysRQ behavior, suspend/resume, RS485 configuration ioctls, KGDB polling if enabled, and stress tests that force TX FIFO empty and wakeup thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_s3c.h -->
# sources/distributed-fs/ceph-client/include/linux/serial_s3c.h

## Purpose

`serial_s3c.h` defines register offsets, bit masks, default register values, and machine configuration data for Samsung S3C/S5P/Apple S5L style UART controllers. It is an SoC-specific companion to `serial_core.h`, allowing platform setup and the Samsung UART driver to agree on register layout and per-port defaults.

## Important APIs, Types, And Functions

The file exports register offsets such as `S3C2410_ULCON`, `S3C2410_UCON`, `S3C2410_UFCON`, `S3C2410_UTRSTAT`, `S3C2410_UERSTAT`, `S3C2410_UFSTAT`, `S3C2410_UMSTAT`, `S3C2410_UTXH`, `S3C2410_URXH`, `S3C2410_UBRDIV`, and S3C64XX interrupt registers. It defines line-control masks for character size, parity, stop bits, and IR mode; control bits for clock selection, break, IRQ mode, FIFO timeout, loopback, DMA burst/mode, and error interrupts; FIFO trigger/reset/full/count masks for multiple chip families; modem control/status bits; divisor slot register offset; and Apple S5L-specific interrupt/status masks.

The only C type is `struct s3c2410_uartcfg`, available outside assembly. It captures hardware port number, default serial flags, clock selection, fractional divisor support, and default values for `ucon`, `ulcon`, and `ufcon`.

## Control Flow

There is no executable control flow. Driver code uses these macros while probing or configuring a port: choose the SoC-specific clock source and FIFO layout, build line-control values from termios, set or clear break and loopback, enable CPU or DMA modes, reset FIFOs, decode status/error bits during interrupt service, and program default UCON/UFCON values from `struct s3c2410_uartcfg`.

## State And Persistence

State is held by hardware registers and by per-machine `s3c2410_uartcfg` instances, not by this header. Default values such as `S3C2410_UCON_DEFAULT`, `S5PV210_UCON_DEFAULT`, and `APPLE_S5L_UCON_DEFAULT` influence initial persistent UART state until runtime termios or driver operations change it.

## Dependencies And Integration Points

The header depends on `linux/serial_core.h` for `upf_t` and UART core types when not included from assembly. It integrates with ARM Samsung platform initialization, the Samsung serial driver, clock selection logic, FIFO/interrupt handling, DMA-capable UART paths, and SoC-specific device descriptions.

## Risks And Test Signals

Risks are register-bit drift between SoC variants, mismatched FIFO count masks or trigger shifts, using a default UCON/UFCON value on the wrong controller family, and confusing similarly named AFC/RTS macros. Test signals include boot console on each supported SoC, termios parity/size/stop-bit changes, FIFO interrupt thresholds, RX error reporting, break generation, DMA mode TX/RX, and regression tests for Apple S5L timeout and threshold flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_s3c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_sci.h -->
# sources/distributed-fs/ceph-client/include/linux/serial_sci.h

## Purpose

`serial_sci.h` defines platform data for SuperH and Renesas SCI, SCIF, SCIFA, SCIFB, HSCIF, and related serial controllers. It supplies common control-register bits and a compact platform contract for drivers that bind these UART variants to the serial core.

## Important APIs, Types, And Functions

The header defines `SCSCR_*` bits for transmit interrupt, receive interrupt, transmit enable, receive enable, receive-error interrupt, timeout interrupt, and clock enable bits. The anonymous enum lists register layout identifiers such as `SCIx_SCI_REGTYPE`, `SCIx_SCIFA_REGTYPE`, `SCIx_SH4_SCIF_REGTYPE`, `SCIx_HSCIF_REGTYPE`, `SCIx_RZ_SCIFA_REGTYPE`, and `SCIx_RZV2H_SCIF_REGTYPE`.

`struct plat_sci_port_ops` contains an optional `init_pins()` hook. `struct plat_sci_port` carries the SCI type, `UPF_*` serial flags, sampling rate, initial SCSCR value, optional register type override, and optional platform operations.

## Control Flow

There is no code body. During platform setup and driver probe, the SCI driver consumes `plat_sci_port` to select a register map, initialize control register defaults, configure pins through `init_pins()`, and expose the port as a `uart_port`. Runtime control flow in the driver then uses the `SCSCR_*` bits to enable TX, RX, and interrupt sources.

## State And Persistence

Persistent state is external: platform data may be static, and hardware control state lives in SCI registers. The `scscr` field seeds initial receive/transmit and interrupt enable state for each port.

## Dependencies And Integration Points

Dependencies are `linux/bitops.h`, `linux/serial_core.h`, and `linux/sh_dma.h`. Integration points include Renesas/SuperH platform device setup, pin muxing, serial core `UPF_*` flags, and DMA-capable SCI variants.

## Risks And Test Signals

Risks are selecting the wrong register type for a SoC, enabling interrupts before pins or clocks are ready, and using a sampling rate inconsistent with baud calculations. Test signals include probe on each listed register type, TX/RX interrupt enable behavior, pin initialization, DMA-backed transfers, and boot-console operation on SCI/SCIF variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serial_sci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serio.h -->
# sources/distributed-fs/ceph-client/include/linux/serio.h

## Purpose

`serio.h` defines the Linux serio bus contract for low-level serial input ports such as PS/2 keyboard and mouse controllers. It models serio ports, serio drivers, registration helpers, interrupt delivery, driver data access, and RX pause locking.

## Important APIs, Types, And Functions

The core type `struct serio` contains per-port data, names, physical path, firmware ID, manual bind flag, device ID, interrupt-protection spinlock, transport callbacks (`write`, `open`, `close`, `start`, `stop`), hierarchy pointers and child lists, driver pointer protected by `drv_mutex` and `lock`, embedded `struct device`, global list node, and optional shared `ps2_cmd_mutex`.

`struct serio_driver` supplies ID matching, manual binding, `write_wakeup`, interrupt, connect/reconnect/fast_reconnect, disconnect, cleanup, and embedded `device_driver`. APIs include `serio_open()`, `serio_close()`, `serio_rescan()`, `serio_reconnect()`, `serio_interrupt()`, `serio_register_port()`, `serio_unregister_port()`, `serio_unregister_child_port()`, `serio_register_driver()`, `serio_unregister_driver()`, `module_serio_driver()`, `serio_write()`, `serio_drv_write_wakeup()`, `serio_get_drvdata()`, `serio_set_drvdata()`, `serio_pause_rx()`, and `serio_continue_rx()`.

## Control Flow

Port providers register a `struct serio`; drivers register a `struct serio_driver` with an ID table. Bus matching calls driver connect paths, opening the port through `serio_open()`. Hardware interrupt handlers report bytes through `serio_interrupt()`, which dispatches to the bound driver's `interrupt()` callback. Reconnect and rescan paths recover devices after transport disruption. The inline `serio_write()` delegates outbound bytes to the port transport when available.

## State And Persistence

`struct serio` persists for the lifetime of the port and stores hierarchy depth, parent-child links, current driver, and embedded device state. Driver-private state is attached to `serio->dev` through standard device driver data helpers. RX critical sections are protected by `serio->lock`; driver binding is protected by `drv_mutex` plus the spinlock because interrupt handlers read `serio->drv`.

## Dependencies And Integration Points

Dependencies include cleanup guards, interrupt return types, list/spinlock/mutex primitives, the device model, module device tables, and UAPI serio IDs. Integration points are the input subsystem, PS/2 layer, i8042-like shared hardware, module registration, sysfs device binding, and firmware-described input ports.

## Risks And Test Signals

Risks are racing driver unbind with interrupt delivery, failing to pause RX around driver critical sections, hierarchy leaks when unregistering child ports, and shared PS/2 command deadlocks without `ps2_cmd_mutex`. Test signals include hotplug/register/unregister loops, PS/2 interrupt storms, manual bind/unbind, reconnect after suspend, write wakeups, and lockdep coverage around `serio_pause_rx()` sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/serio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/set_memory.h -->
# sources/distributed-fs/ceph-client/include/linux/set_memory.h

## Purpose

`set_memory.h` provides a cross-architecture API for changing kernel page attributes, direct-map validity, machine-check mitigation attributes, and memory encryption state. It supplies real architecture implementations when configured and no-op fallbacks when not supported.

## Important APIs, Types, And Functions

Primary APIs are `set_memory_ro()`, `set_memory_rw()`, `set_memory_x()`, `set_memory_nx()`, `set_memory_rox()`, `set_direct_map_invalid_noflush()`, `set_direct_map_default_noflush()`, `set_direct_map_valid_noflush()`, `kernel_page_present()`, `can_set_direct_map()`, `set_mce_nospec()`, `clear_mce_nospec()`, `set_memory_encrypted()`, and `set_memory_decrypted()`.

When `CONFIG_ARCH_HAS_SET_MEMORY` is enabled, architecture code from `asm/set_memory.h` supplies the core implementations. Otherwise, the page-permission calls return success without changing mappings. `set_memory_rox()` composes read-only and executable transitions unless an architecture overrides it. Direct-map helpers similarly degrade to no-ops unless `CONFIG_ARCH_HAS_SET_DIRECT_MAP` is present.

## Control Flow

The only implemented flow in this header is sequential composition in `set_memory_rox()`: make pages read-only, return any error, then make them executable. Other inline fallbacks immediately return success or default truth values.

## State And Persistence

Real state changes, when supported, are persistent page-table attribute changes owned by architecture code. This header stores no state. The fallback behavior deliberately preserves call-site buildability on unsupported architectures while not enforcing memory permissions.

## Dependencies And Integration Points

Integration points include module text protection, BPF/JIT or generated code permission transitions, direct-map hardening, memory-failure handling on x86, and encrypted memory support. It depends on architecture configuration and `struct page` declarations from surrounding includes.

## Risks And Test Signals

Risks are assuming permission changes occurred on architectures where these are no-ops, ignoring `__must_check` return values, missing TLB/cache flush semantics in architecture implementations, and calling direct-map changes when `can_set_direct_map()` may be false. Test signals include W^X selftests, module load/unload permission checks, x86 MCE nospec tests, encrypted/decrypted memory tests, and architecture boot tests with unsupported configs to verify fallback build behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sfp.h -->
# sources/distributed-fs/ceph-client/include/linux/sfp.h

## Purpose

`sfp.h` defines SFP/SFP+ module EEPROM layouts, SFF-8024/SFF-8472 constants, diagnostics offsets, parsed module capabilities, and the bus API between an SFP socket driver and an upstream network device. It is a packed binary layout header plus a conditional API facade for `CONFIG_SFP`.

## Important APIs, Types, And Functions

Important binary layout types are `struct sfp_eeprom_base`, `struct sfp_eeprom_ext`, `struct sfp_eeprom_id`, and `struct sfp_diag`. They mirror module EEPROM fields, including transceiver compliance bits, connector, encoding, nominal bitrate, link lengths, vendor identity, wavelength or cable compliance, option bits, diagnostic monitor flags, enhanced options, SFF-8472 revision, alarm and warning thresholds, calibration coefficients, and live diagnostic values.

Constants cover SFF-8024 module IDs, encodings, connectors, extended compliance codes, base EEPROM offsets, option bits, diagnostic offsets, status bits, alarm/warn bits, extended status bits, and page selection. `struct sfp_module_caps` carries supported PHY interface bitmap, ethtool link-mode bitmap, possible PHY presence, and parsed port type. `struct sfp_upstream_ops` defines callbacks for upstream attach/detach, module insert/remove/start/stop, link up/down, and PHY connect/disconnect.

When `CONFIG_SFP` is enabled, APIs include `sfp_get_module_caps()`, `sfp_select_interface()`, `sfp_get_module_info()`, `sfp_get_module_eeprom()`, `sfp_get_module_eeprom_by_page()`, `sfp_upstream_start()`, `sfp_upstream_stop()`, `sfp_upstream_set_signal_rate()`, `sfp_bus_put()`, `sfp_bus_find_fwnode()`, `sfp_bus_add_upstream()`, `sfp_bus_del_upstream()`, and `sfp_get_name()`. Disabled stubs return neutral values or `-EOPNOTSUPP`.

## Control Flow

The typical flow is: an upstream network device locates an SFP bus by firmware node, adds itself with `sfp_bus_add_upstream()`, receives attach and module event callbacks, validates inserted module EEPROM through `module_insert()`, starts the module, selects a PHY interface using advertised link modes, handles link up/down, connects any module PHY, and tears down on removal or upstream unregister. EEPROM and diagnostic accessors serve ethtool requests.

## State And Persistence

This header stores no runtime state, but the packed structs define persistent EEPROM interpretation. The SFP bus object owns runtime state in implementation code. `sfp_module_caps` is parsed module state exposed through a const pointer. The endian-specific bitfields and `__packed` attributes are part of the persistent ABI with raw EEPROM bytes.

## Dependencies And Integration Points

Dependencies include PHY interface definitions, ethtool module EEPROM APIs, netlink extended acknowledgements, firmware nodes, and link-mode bitmaps. Integration points are SFP cage/socket drivers, MAC drivers, phylink, PHY devices on module I2C, ethtool EEPROM/dump commands, and network link management.

## Risks And Test Signals

Risks are broken packed layout, endian bitfield mistakes, invalid checksum or offset interpretation, treating `may_have_phy` as certainty, unsupported-module acceptance, and missing `CONFIG_SFP` behavior at call sites. Test signals include EEPROM fixture parsing for little and big endian builds, ethtool module-info and paged EEPROM reads, hot-insert/remove, PHY connect/disconnect, link-mode interface selection, high-power/rate-select options, and disabled-config builds verifying stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_clk.h -->
# sources/distributed-fs/ceph-client/include/linux/sh_clk.h

## Purpose

`sh_clk.h` defines the legacy SuperH clock framework structures, operations, registration helpers, and initializer macros for module-stop clocks, divider clocks, reparentable clocks, and FSIDIV clocks.

## Important APIs, Types, And Functions

Core types are `struct clk_mapping`, `struct sh_clk_ops`, `struct clk`, `struct clk_div_mult_table`, and `struct clk_div_table`. `struct clk` tracks list membership, parent and children, selectable parent table fields, operations, usecount, rate, flags, enable/status registers, enable bit, mapped register, divider mask, arch-private flags, private data, mapping, and CPU frequency table data.

APIs include `followparent_recalc()`, `recalculate_root_clocks()`, `propagate_rate()`, `clk_reparent()`, `clk_register()`, `clk_unregister()`, `clk_enable_init_clocks()`, `clk_rate_table_build()`, `clk_rate_table_round()`, `clk_rate_table_find()`, `clk_rate_div_range_round()`, `clk_rate_mult_range_round()`, `sh_clk_mstp_register()`, deprecated `sh_clk_mstp32_register()`, `sh_clk_div4_register()`, `sh_clk_div4_enable_register()`, `sh_clk_div4_reparent_register()`, `sh_clk_div6_register()`, `sh_clk_div6_reparent_register()`, and `sh_clk_fsidiv_register()`.

Initializer macros include `SH_CLK_MSTP*`, `SH_CLK_DIV4`, `SH_CLK_DIV6_EXT`, `SH_CLK_DIV6`, `SH_CLK_FSIDIV`, and clock lookup helpers `CLKDEV_CON_ID`, `CLKDEV_DEV_ID`, and `CLKDEV_ICK_ID`.

## Control Flow

Board or SoC code statically declares clock arrays using the macros, registers them, and the framework enables initial clocks, recalculates root rates, propagates rate changes to children, handles parent changes, and applies register-level enable/disable or divider updates through `sh_clk_ops`.

## State And Persistence

Clock state persists in `struct clk` instances and hardware registers. `usecount`, `rate`, parent links, child lists, and mapping refcounts are in-memory state; enable bits, status bits, and divider fields are hardware state. Initializer flags such as `CLK_ENABLE_ON_INIT`, access-size flags, and `CLK_MASK_DIV_ON_DISABLE` control persistent behavior after registration.

## Dependencies And Integration Points

Dependencies include list handling, seq files, cpufreq tables, krefs, common clock consumer APIs, and MMIO. Integration points are SuperH CPG/MSTP clock drivers, cpufreq, clkdev lookup, peripheral power gating, and board setup code.

## Risks And Test Signals

Risks are wrong MMIO access width, incorrect divider masks, stale parent/child rate propagation, register mapping lifetime bugs, and usecount imbalance. Test signals include clock enable/disable tests, cpufreq table rate selection, parent reparenting, peripheral probe requiring MSTP clocks, debug clock tree dumps, and suspend/resume of clock-gated devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/sh_dma.h

## Purpose

`sh_dma.h` defines platform data and register bit constants for the SuperH dmaengine driver. It bridges platform descriptions of DMA channels and slave request lines to the generic shdma base library and dmaengine API.

## Important APIs, Types, And Functions

`struct sh_dmae_slave` embeds `struct shdma_slave` for platform-provided slave identifiers. `struct sh_dmae_slave_config` maps a `slave_id` to a device address, CHCR value, and MID/RID request selector. `struct sh_dmae_channel` describes channel register offsets and DMARS/CHCLR bit placement. `struct sh_dmae_pdata` aggregates slave arrays, channel arrays, transfer-size field masks and shifts, DMAOR defaults, CHCR interrupt-enable bit, register-width and feature flags, and whether the controller is slave-only.

Constants include DMAOR flags `DMAOR_AE`, `DMAOR_NMIF`, `DMAOR_DME`, address increment/decrement/fixed fields `DM_*` and `SM_*`, request selector values `RS_AUTO` and `RS_ERS`, and channel control flags `CHCR_DE`, `CHCR_TE`, and `CHCR_IE`.

## Control Flow

There is no executable flow. Driver probe reads `sh_dmae_pdata`, configures DMAOR, allocates channels from `channel`, configures slave routes from `slave`, programs transfer-size fields using the shift/mask data, and uses CHCR/DMAOR flags during prepare, start, interrupt, and reset paths.

## State And Persistence

Persistent state is platform data plus hardware register values. Feature bitfields such as `dmaor_is_32bit`, `needs_tend_set`, `no_dmars`, `chclr_present`, `chclr_bitwise`, and `slave_only` determine how implementation code treats each controller throughout its lifetime.

## Dependencies And Integration Points

Dependencies are dmaengine, list handling, `shdma-base.h`, and fixed-width types. Integration points are SuperH/Renesas platform device descriptions, DMA clients using slave IDs, serial SCI DMA paths, and generic dmaengine channel allocation.

## Risks And Test Signals

Risks are wrong slave ID to request-line mapping, invalid transfer-size encoding, mismatched 16/32-bit DMAOR access, incorrect CHCLR reset semantics, and enabling memcpy on slave-only hardware. Test signals include dmaengine memcpy if supported, slave TX/RX for serial or audio clients, channel reset after error, interrupt completion, and platform variants without DMARS or with bitwise CHCLR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_eth.h -->
# sources/distributed-fs/ceph-client/include/linux/sh_eth.h

## Purpose

`sh_eth.h` defines platform data for the SuperH/Renesas Ethernet driver. It supplies PHY addressing, PHY interrupt, PHY interface mode, optional MDIO gate control, MAC address, and link-polarity flags.

## Important APIs, Types, And Functions

The only type is `struct sh_eth_plat_data`. Fields are `phy`, `phy_irq`, `phy_interface`, `set_mdio_gate`, `mac_addr[ETH_ALEN]`, `no_ether_link`, and `ether_link_active_low`.

## Control Flow

No functions are implemented. Driver probe consumes this platform data to configure PHY attachment, MDIO access, MAC address setup, and link GPIO/polarity handling. If `set_mdio_gate` is supplied, driver code can open or close an MDIO gate around bus transactions.

## State And Persistence

The platform data is static board or firmware state. Runtime link and PHY state are owned by the Ethernet driver and PHY subsystem. The MAC address may become the persistent network identity for the interface if accepted by the driver.

## Dependencies And Integration Points

Dependencies include PHY interface definitions and Ethernet address length. Integration points are the SH Ethernet MAC driver, phylib, MDIO bus access, board files, and platform data instantiation.

## Risks And Test Signals

Risks include wrong PHY address or IRQ, mismatched PHY interface mode, invalid MAC address, and incorrect active-low link interpretation. Test signals include probe and PHY attach, MDIO reads/writes through gate control, link up/down changes, MAC address reporting, and traffic tests across each supported PHY interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_intc.h -->
# sources/distributed-fs/ceph-client/include/linux/sh_intc.h

## Purpose

`sh_intc.h` defines the descriptor format and helper macros for SuperH interrupt controller registration. It maps event codes or IRQ numbers to enum IDs, groups, mask registers, priority registers, sense registers, acknowledgement registers, subgroups, and optional SMP or balancing metadata.

## Important APIs, Types, And Functions

Types include `intc_enum`, `struct intc_vect`, `struct intc_group`, `struct intc_subgroup`, `struct intc_mask_reg`, `struct intc_prio_reg`, `struct intc_sense_reg`, `struct intc_hw_desc`, and `struct intc_desc`. Macros include `evt2irq()`, `irq2evt()`, `INTC_VECT()`, `INTC_IRQ()`, `INTC_GROUP()`, `INTC_SMP_BALANCING()`, `INTC_SMP()`, `INTC_HW_DESC()`, `DECLARE_INTC_DESC()`, and `DECLARE_INTC_DESC_ACK()`.

APIs are `register_intc_controller()`, `intc_set_priority()`, `intc_irq_lookup()`, `intc_finalize()`, and optional `register_intc_userimask()`.

## Control Flow

SoC code declares descriptor tables with vectors, groups, mask registers, priority registers, sense registers, and optional ack registers. `register_intc_controller()` consumes the descriptor and installs irqchip behavior. The code also supports looking up IRQ numbers by chip name and enum ID, setting priorities, finalizing setup, and registering a user interrupt mask register when configured.

## State And Persistence

Descriptor data is usually `__initdata` and describes persistent hardware topology during boot. Runtime IRQ masking, priority, sense, SMP distribution, and acknowledgement state live in hardware registers and irqchip implementation state.

## Dependencies And Integration Points

Dependencies include IO resource descriptors and optional `CONFIG_SUPERH`, `CONFIG_CPU_HAS_INTEVT`, `CONFIG_INTC_BALANCING`, `CONFIG_SMP`, and `CONFIG_INTC_USERIMASK`. Integration points are arch interrupt setup, irqchip core, platform device IRQ numbering, SMP routing, and syscore suspend behavior through `skip_syscore_suspend`.

## Risks And Test Signals

Risks are bad event-to-IRQ conversion, arrays with missing zero terminators or wrong enum IDs, incorrect register width/field width, conflicting force-enable/disable IDs, and wrong SMP stride/count encoding. Test signals include boot IRQ registration, interrupt delivery from each vector group, priority changes, wake/suspend paths, SMP interrupt distribution, and usermask behavior when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_intc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_timer.h -->
# sources/distributed-fs/ceph-client/include/linux/sh_timer.h

## Purpose

`sh_timer.h` is a minimal platform-data header for SuperH timer drivers. It defines which hardware timer channels are available or enabled for a platform instance.

## Important APIs, Types, And Functions

The only type is `struct sh_timer_config` with `channels_mask`.

## Control Flow

There is no executable code. Timer driver probe reads `channels_mask` to decide which timer channels to register, expose as clocksource/clockevent devices, or reserve.

## State And Persistence

State is static platform configuration. Runtime counter, comparator, interrupt, and clockevent state is owned by timer driver implementation code.

## Dependencies And Integration Points

The header has no external include dependencies beyond basic C declarations. It integrates with SuperH timer platform devices and arch timekeeping setup.

## Risks And Test Signals

Risks are a mask that enables nonexistent channels or omits required channels, causing boot-time timer failure or missing clockevents. Test signals include clocksource registration, periodic and oneshot timer interrupts, sched tick operation, suspend/resume, and boot on platforms with different channel masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sh_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shdma-base.h -->
# sources/distributed-fs/ceph-client/include/linux/shdma-base.h

## Purpose

`shdma-base.h` defines the common dmaengine base library contract for SH-based DMA controllers. Controller-specific drivers embed these base structs and implement `struct shdma_ops` so generic queueing, channel management, IRQ request, init, cleanup, and filtering can be shared.

## Important APIs, Types, And Functions

Types include `enum shdma_pm_state`, `struct shdma_slave`, `struct shdma_desc`, `struct shdma_chan`, `struct shdma_ops`, and `struct shdma_dev`. `struct shdma_desc` embeds `dma_async_tx_descriptor`, transfer direction, partial byte count, cookie, chunk count, mark, and cyclic flag. `struct shdma_chan` keeps channel lock, queued and free descriptor lists, embedded `dma_chan`, device pointer, descriptor storage, max transfer length, raw channel ID, IRQ, slave IDs, hardware request line, and PM state.

`struct shdma_ops` supplies controller-specific callbacks for descriptor completion, halting, busy checks, slave address, descriptor setup, slave binding, transfer setup, start, embedded descriptor lookup, IRQ handling, and partial progress. APIs include `shdma_request_irq()`, `shdma_reset()`, `shdma_chan_probe()`, `shdma_chan_remove()`, `shdma_init()`, `shdma_cleanup()`, and conditional `shdma_chan_filter()`. The `shdma_for_each_chan()` macro iterates channels.

## Control Flow

A controller driver allocates and embeds `shdma_dev`/`shdma_chan`, fills `shdma_ops`, initializes channels with `shdma_init()` and `shdma_chan_probe()`, requests IRQs, and services transfers through dmaengine callbacks. Transfer preparation may move PM state through busy and pending phases. IRQ handlers call the controller `chan_irq()` hook and mark descriptors complete. Cleanup removes channels and frees shared state.

## State And Persistence

Persistent runtime state includes descriptor queues, descriptor pools, channel locks, DMA cookies, cyclic flags, partial progress, PM state, and controller operation pointers. Hardware state is controlled by implementation callbacks.

## Dependencies And Integration Points

Dependencies include dmaengine, interrupt handling, list management, and fixed-width types. Integration points are controller-specific SH DMA drivers, platform-specific `sh_dma.h` data, dmaengine clients, IRQ core, and DMA channel filtering for slave requests.

## Risks And Test Signals

Risks include descriptor queue corruption, incorrect PM state transitions when locks are dropped, partial progress misreporting, channel filter mismatches, and IRQ completion races. Test signals include dmaengine async memcpy/slave transfers, cyclic transfers, terminate/reset paths, interrupt storms, descriptor reuse, residue reporting, and disabled `CONFIG_SH_DMAE_BASE` builds where filtering returns false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shdma-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shm.h -->
# sources/distributed-fs/ceph-client/include/linux/shm.h

## Purpose

`shm.h` defines the kernel-side SysV shared-memory hooks stored in tasks and used for attach and exit handling. It provides real declarations under `CONFIG_SYSVIPC` and no-op or `-ENOSYS` stubs otherwise.

## Important APIs, Types, And Functions

`struct sysv_shm` contains `shm_clist` when SysV IPC is enabled and is empty otherwise. APIs are `do_shmat()`, `exit_shm()`, and `shm_init_task()`. `do_shmat()` attaches a SysV shared-memory segment and returns the mapped address via an output pointer. `exit_shm()` releases per-task shared-memory attachments. `shm_init_task()` initializes the per-task list.

## Control Flow

With SysV IPC enabled, fork or task initialization calls `shm_init_task()`, `do_shmat()` handles the attach syscall path, and task exit calls `exit_shm()`. Without SysV IPC, `do_shmat()` fails with `-ENOSYS` and the lifecycle hooks do nothing.

## State And Persistence

Per-task state is the `sysvshm.shm_clist` list, which tracks attachments for cleanup. Persistent shared-memory segment state is owned outside this header by IPC and memory-management implementations.

## Dependencies And Integration Points

Dependencies include basic types, page definitions, architecture `shmparam`, `struct task_struct`, and user pointers. Integration points are SysV IPC syscalls, task lifecycle, mm attach/mmap behavior, and architecture SHMLBA alignment.

## Risks And Test Signals

Risks are task-exit leaks, wrong SHMLBA alignment, and call sites that do not handle `-ENOSYS` in non-SysV builds. Test signals include `shmat()`/`shmdt()` syscall tests, process exit cleanup, fork behavior, namespace interactions, and non-`CONFIG_SYSVIPC` build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shmem_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/shmem_fs.h

## Purpose

`shmem_fs.h` defines tmpfs/shmem internal inode and superblock data, mount quota limits, flags, helper accessors, and the exported API used by mm, VFS, userfaultfd, hugepage, swap, and file setup code.

## Important APIs, Types, And Functions

Important types are `struct shmem_inode_info`, `struct shmem_quota_limits`, `struct shmem_sb_info`, and `enum sgp_type`. `shmem_inode_info` embeds VFS inode state plus shmem-specific locks, seals, flags, allocated and swapped counters, directory offset context or shrink/swap lists, creation time, NUMA policy, xattrs, fallocate end, fs flags, stop-eviction counter, optional quotas, and the embedded `vfs_inode`. `shmem_sb_info` tracks max and used blocks, inode limits, free inode space, mount mode/uid/gid, hugepage policy, swap policy, inode allocation batches, memory policy, shrinklist, and quota defaults.

APIs include `SHMEM_I()`, `shmem_init()`, `shmem_init_fs_context()`, `shmem_file_setup()`, `shmem_kernel_file_setup()`, `shmem_file_setup_with_mnt()`, `shmem_zero_setup()`, `shmem_zero_setup_desc()`, `shmem_get_unmapped_area()`, `shmem_lock()`, `shmem_mapping()`, `shmem_unlock_mapping()`, `shmem_read_mapping_page_gfp()`, `shmem_writeout()`, `shmem_truncate_range()`, `shmem_unuse()`, `shmem_allowable_huge_orders()`, `shmem_hpage_pmd_enabled()`, `shmem_swap_usage()`, `shmem_uncharge()`, `shmem_partial_swap_usage()`, `shmem_get_folio()`, `shmem_read_folio_gfp()`, `shmem_read_folio()`, `shmem_read_mapping_page()`, `shmem_file()`, `shmem_freeze()`, `shmem_fallocend()`, and `shmem_charge()`.

## Control Flow

File setup APIs create anonymous or mounted shmem files. Page lookup/allocation flows through `shmem_get_folio()` with `SGP_READ`, `SGP_NOALLOC`, `SGP_CACHE`, `SGP_WRITE`, or `SGP_FALLOC`, controlling whether holes may allocate pages or exceed size. Swap and reclaim paths call writeout, unuse, swap usage, uncharge, and shrinklist helpers. Truncation and fallocate paths use `shmem_truncate_range()` and `shmem_fallocend()` to preserve required reservations. `shmem_freeze()` toggles a mapping-frozen flag under exclusive inode lock.

## State And Persistence

Persistent in-memory filesystem state is per-inode allocation, swap, seal, policy, xattr, quota, and shrink/swap list membership plus per-superblock accounting counters and policies. `SHMEM_F_NORESERVE`, `SHMEM_F_LOCKED`, and `SHMEM_F_MAPPING_FROZEN` modify allocation, swap, and mapping mutability behavior. Quota limits use signed 64-bit safe maxima despite byte counters being unsigned.

## Dependencies And Integration Points

Dependencies include VFS files and inodes, swap, NUMA mempolicy, pagemap, percpu counters, xattrs, fs parser, userfaultfd, bits, tmpfs quota, transparent hugepage, and shmem config. Integration points include anonymous shared mappings, tmpfs mounts, memfd-like file setup, userfaultfd, THP, swapoff, reclaim, quotas, xattrs, and FS_IOC flags.

## Risks And Test Signals

Risks are accounting mismatches between `alloced`, `swapped`, quotas, and `used_blocks`; freeze flag changes without the inode lock; hugepage truncation around fallocate reservations; wrong behavior under `CONFIG_SHMEM` or `CONFIG_TRANSPARENT_HUGEPAGE` stubs; and quota overflow. Test signals include tmpfs xfstests, memfd and shared anonymous mmap, swapoff/shmem_unuse, THP tmpfs tests, userfaultfd minor faults, quota enforcement, fallocate hole punch/keep-size, and lockdep around inode freeze.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shmem_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shrinker.h -->
# sources/distributed-fs/ceph-client/include/linux/shrinker.h

## Purpose

`shrinker.h` defines the kernel reclaim shrinker API used by caches to expose reclaimable objects to memory pressure. It includes memcg-aware deferred tracking, shrink-control input, shrinker allocation/registration/freeing, refcount lifetime helpers, and optional debugfs renaming.

## Important APIs, Types, And Functions

Types are `struct shrinker_info_unit`, `struct shrinker_info`, `struct shrink_control`, and `struct shrinker`. `shrink_control` carries GFP mask, NUMA node, target scan count, actual scanned count, and current memory cgroup. `struct shrinker` contains `count_objects()` and `scan_objects()` callbacks, batch size, seeks cost, flags, refcount, completion, RCU head, private data, global list node, optional memcg ID, optional debugfs identity, and per-node deferred object counters.

Constants include `SHRINK_STOP`, `SHRINK_EMPTY`, `DEFAULT_SEEKS`, internal flags `SHRINKER_REGISTERED` and `SHRINKER_ALLOCATED`, and public flags `SHRINKER_NUMA_AWARE`, `SHRINKER_MEMCG_AWARE`, and `SHRINKER_NONSLAB`. APIs are `shrinker_alloc()`, `shrinker_register()`, `shrinker_free()`, `shrinker_try_get()`, `shrinker_put()`, and optional `shrinker_debugfs_rename()`.

## Control Flow

A subsystem allocates or embeds a shrinker, fills count and scan callbacks, registers it, and the page reclaim path calls `count_objects()` followed by `scan_objects()` when there is reclaimable work. Callback return values drive control flow: `SHRINK_EMPTY` means no objects, zero means skip or unknown, and `SHRINK_STOP` stops current-context scanning due to possible deadlock. Unregistration drops the initial refcount and waits for concurrent users to release references before RCU freeing.

## State And Persistence

Persistent shrinker state includes callback pointers, flags, private data, refcount, completion, deferred counters, memcg ID, and debugfs metadata. `shrinker_info` stores per-memcg bitmaps and deferred counts indexed by shrinker ID units.

## Dependencies And Integration Points

Dependencies include atomics, refcounts, completions, RCU, optional memcg, optional debugfs, and reclaim code. Integration points are slab and non-slab caches, filesystem inode/dentry caches, driver caches, memcg reclaim, NUMA-aware reclaim, and debugfs diagnostics.

## Risks And Test Signals

Risks are deadlocks in `count_objects()`, failure to return `SHRINK_STOP` when locks cannot be safely acquired, refcount use-after-free during unregistration, wrong memcg-aware flags, and inaccurate `nr_scanned` accounting. Test signals include memory pressure reclaim, memcg reclaim, shrinker debugfs output, unregister under concurrent reclaim, lockdep, and cache-specific object leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/shrinker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/signal.h -->
# sources/distributed-fs/ceph-client/include/linux/signal.h

## Purpose

`signal.h` provides kernel signal helpers built on `signal_types.h`: siginfo copying, sigset manipulation, pending signal initialization, signal delivery declarations, kernel-thread signal policy helpers, default signal-action masks, altstack helpers, proc rendering, and architecture address untagging for signal fault delivery.

## Important APIs, Types, And Functions

Key helpers include `copy_siginfo()`, `clear_siginfo()`, `copy_siginfo_to_external()`, `copy_siginfo_to_user()`, `copy_siginfo_from_user()`, `siginfo_layout()`, `sigaddset()`, `sigdelset()`, `sigismember()`, `sigisemptyset()`, `sigequalsets()`, `sigmask()`, `sigorsets()`, `sigandsets()`, `sigandnsets()`, `signotset()`, `sigemptyset()`, `sigfillset()`, low-32-bit mask helpers, `siginitset()`, `siginitsetinv()`, `init_sigpending()`, `flush_sigqueue()`, `valid_signal()`, `next_signal()`, `do_send_sig_info()`, `group_send_sig_info()`, `send_signal_locked()`, `sigprocmask()`, `set_current_blocked()`, `__set_current_blocked()`, `get_signal()`, `signal_setup_done()`, `exit_signals()`, `kernel_sigaction()`, `allow_signal()`, `allow_kernel_signal()`, `disallow_signal()`, `unhandled_signal()`, `signals_init()`, `restore_altstack()`, `__save_altstack()`, `unsafe_save_altstack()`, `sigaltstack_size_valid()`, `render_sigset_t()`, and `arch_untagged_si_addr()`.

It defines `enum siginfo_layout`, `SIG_KTHREAD`, `SIG_KTHREAD_KERNEL`, default-action masks, `sig_kernel_only()`, `sig_kernel_coredump()`, `sig_kernel_ignore()`, `sig_kernel_stop()`, `sig_specific_sicodes()`, and `sig_fatal()`.

## Control Flow

Sigset helpers manipulate per-task blocked or pending signal masks. Signal send paths select process or thread delivery through the declared APIs. `get_signal()` obtains a deliverable signal for architecture return-to-user paths, after which `signal_setup_done()` completes frame setup. Kernel thread helpers install special handlers so selected signals are not silently dropped or converted. The default-action masks classify whether a signal is uncatchable, stopping, coredumping, ignored, or fatal.

## State And Persistence

Signal state lives in task, sighand, pending queues, sigsets, and altstack fields. This header manipulates bitsets in-place and initializes `struct sigpending` by emptying the mask and list. It also references global policy/debug variables such as `print_fatal_signals`, `show_unhandled_signals`, and `sighand_cachep`.

## Dependencies And Integration Points

Dependencies include bug/build assertions, lists, `signal_types.h`, string/memory helpers, user access through surrounding includes, task structures, pid types, seq files, and architecture overrides. Integration points include syscall signal APIs, return-to-user architecture code, procfs status rendering, coredump/stop/job-control behavior, kernel threads, seccomp/perf/fault siginfo layouts, and tagged address architectures.

## Risks And Test Signals

Risks are off-by-one signal bit handling, unsupported `_NSIG_WORDS` values, copying kernel siginfo without zeroing external expansion bytes, wrong default-action masks, and architecture mismatches in altstack or tagged address handling. Test signals include signal syscall selftests, realtime signal queueing, ptrace/seccomp/fault siginfo tests, job-control tests, coredump tests, kernel-thread signal behavior, dynamic sigframe altstack validation, and procfs signal mask rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/signal_types.h -->
# sources/distributed-fs/ceph-client/include/linux/signal_types.h

## Purpose

`signal_types.h` defines the core kernel signal data structures shared by signal handling code: kernel siginfo, queued realtime signal objects, pending signal sets, sigaction wrappers, delivered signal state, and valid userspace sigaction flags.

## Important APIs, Types, And Functions

Types are `kernel_siginfo_t`, `struct sigqueue`, `struct sigpending`, `struct sigaction`, `struct k_sigaction`, optional `struct old_sigaction`, and `struct ksignal`. `struct sigqueue` stores list linkage, flags, kernel siginfo, and `ucounts` charging. `struct sigpending` stores queued signal list and aggregate signal set. `struct sigaction` is architecture-sensitive around IRIX ordering and optional restorer fields. `struct ksignal` combines selected action, siginfo, and signal number for delivery.

Constants include `SIGQUEUE_PREALLOC`, `SA_IMMUTABLE`, `__ARCH_UAPI_SA_FLAGS`, and `UAPI_SA_FLAGS`.

## Control Flow

There is no executable flow. Signal code allocates and links `sigqueue` objects, accumulates pending masks in `sigpending`, stores user-visible actions in `sigaction`, wraps them as `k_sigaction`, and passes one selected signal as `ksignal` to architecture frame setup.

## State And Persistence

Queued realtime signals persist until delivered or flushed. `sigpending.signal` is the aggregate pending bitset, while `sigpending.list` stores queued detail. `sigaction` state persists in each process signal handler table. `SA_IMMUTABLE` protects forced signal action races.

## Dependencies And Integration Points

Dependencies include kernel types and UAPI signal definitions. Integration points are signal syscalls, realtime signal queues, ucounts resource accounting, architecture signal frame setup, old ABI compatibility, and userspace sigaction flag validation.

## Risks And Test Signals

Risks are ABI layout mismatches across architectures, missing restorer handling, realtime queue accounting leaks, and allowing invalid UAPI sigaction flags. Test signals include ABI build checks, old sigaction compatibility, realtime signal queue limits, forced-signal race tests, and architecture signal frame tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/signal_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/signalfd.h -->
# sources/distributed-fs/ceph-client/include/linux/signalfd.h

## Purpose

`signalfd.h` connects signal delivery with signalfd waiters. It provides a notification hook that wakes signalfd readers when a task receives a signal and a cleanup hook for sighand teardown, with no-op stubs when signalfd is disabled.

## Important APIs, Types, And Functions

The APIs are `signalfd_notify()` and `signalfd_cleanup()`. When `CONFIG_SIGNALFD` is enabled, `signalfd_notify()` checks `tsk->sighand->signalfd_wqh` with `waitqueue_active()` and wakes it if needed. `signalfd_cleanup()` is declared for implementation code. When disabled, both helpers compile to empty inline functions.

## Control Flow

Signal delivery paths call `signalfd_notify()` after signal state changes. If a signalfd reader is sleeping on the sighand waitqueue, the helper wakes the queue so userspace can read signal records. Sighand teardown calls `signalfd_cleanup()` to release signalfd-related state.

## State And Persistence

The waitqueue is stored in `sighand_struct`, not this header. The helper does not modify signal state; it only wakes waiters. Disabled builds preserve call-site behavior without state.

## Dependencies And Integration Points

Dependencies are UAPI signalfd structures and `linux/sched/signal.h` for task and sighand fields. Integration points are signal delivery, signalfd file operations, poll/select wakeups, and sighand lifetime management.

## Risks And Test Signals

Risks are missed wakeups if signal state changes without calling the helper, dereferencing sighand after teardown, and build differences when `CONFIG_SIGNALFD` is disabled. Test signals include signalfd read/poll selftests, signal mask changes with signalfd, multithreaded delivery, sighand cleanup on exit, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/signalfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/simple_ring_buffer.h -->
# sources/distributed-fs/ceph-client/include/linux/simple_ring_buffer.h

## Purpose

`simple_ring_buffer.h` declares a lightweight per-CPU ring-buffer interface backed by tracing ring-buffer page types. It exposes page and per-CPU state structures because callers need allocation sizing for initialization.

## Important APIs, Types, And Functions

`struct simple_buffer_page` stores list linkage, pointer to a `buffer_data_page`, entry count, write offset, and page ID. `struct simple_rb_per_cpu` stores tail, reader, and head page pointers, backing page array, metadata pointer, number of pages, status (`SIMPLE_RB_UNAVAILABLE`, `SIMPLE_RB_READY`, `SIMPLE_RB_WRITING`), overrun and timestamp tracking, and callback pointer.

APIs are `simple_ring_buffer_init()`, `simple_ring_buffer_unload()`, `simple_ring_buffer_reserve()`, `simple_ring_buffer_commit()`, `simple_ring_buffer_enable_tracing()`, `simple_ring_buffer_reset()`, `simple_ring_buffer_swap_reader_page()`, `simple_ring_buffer_init_mm()`, and `simple_ring_buffer_unload_mm()`.

## Control Flow

Callers allocate `simple_rb_per_cpu` and page arrays, initialize them from a `ring_buffer_desc`, optionally map pages through custom MM load/unload hooks, reserve space with a timestamp, write event data into the reservation, commit it, and allow readers to swap the reader page. Tracing can be enabled or disabled and the buffer reset.

## State And Persistence

Persistent buffer state is per CPU: page pointers, write offsets, status, overrun counter, write timestamp, metadata, and callbacks. Page contents persist until consumed, reset, swapped, or unloaded.

## Dependencies And Integration Points

Dependencies include lists, tracing ring-buffer definitions and types, and integer types. Integration points are tracing or instrumentation code that needs a simpler ring-buffer wrapper, per-CPU event storage, and memory-mapped buffer setup.

## Risks And Test Signals

Risks include exposing internal layout to callers, incorrect allocation sizes, status transitions racing reserve/commit/read, overrun accounting errors, and MM load/unload leaks. Test signals include reserve/commit ordering, reader page swaps, tracing enable/disable, reset behavior, overrun tests, MM mapping/unmapping tests, and per-CPU concurrency stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/simple_ring_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/siox.h -->
# sources/distributed-fs/ceph-client/include/linux/siox.h

## Purpose

`siox.h` defines the SIOX device and driver model interface. SIOX devices are attached to a SIOX master, expose status and watchdog statistics through kernfs nodes, and bind to `siox_driver` implementations that exchange cyclic input/output data.

## Important APIs, Types, And Functions

`struct siox_device` stores master membership, embedded device, type, input/output byte sizes, status type, last status values, connection state, watchdog and status error counters, and kernfs nodes for status exposure. `struct siox_driver` provides `probe`, `remove`, `shutdown`, `set_data`, `get_data`, and embedded `device_driver`.

Helpers and APIs include `to_siox_device()`, `siox_device_synced()`, `siox_device_connected()`, `to_siox_driver()`, `__siox_driver_register()`, `siox_driver_register()`, `siox_driver_unregister()`, and `module_siox_driver()`.

## Control Flow

A SIOX driver registers with `siox_driver_register()`. Matching devices call `probe()`. During master cycles, framework code calls `set_data()` with inbound status plus payload space excluding the status byte, and `get_data()` to retrieve outbound data excluding the status byte. Removal and shutdown callbacks handle teardown. Inline register/unregister helpers connect the driver to the generic device model.

## State And Persistence

`siox_device` persists while the physical or logical SIOX device exists. It tracks connection and synchronization status, status bytes across cycles, and cumulative error statistics. Driver-private state is expected to live through the embedded device model.

## Dependencies And Integration Points

Dependencies include the device model, module registration helpers, kernfs, list handling, and integer types. Integration points are SIOX master drivers, sysfs/kernfs status reporting, module loading, and cyclic industrial I/O device drivers.

## Risks And Test Signals

Risks include mismatched in/out byte sizes, drivers treating the framework-managed status byte as payload, stale connection status, and error counter lifetime issues. Test signals include driver probe/remove, cyclic data exchange, status/watchdog error increments, connected/synced reporting, shutdown behavior, and module register/unregister loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/siox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/siphash.h -->
# sources/distributed-fs/ceph-client/include/linux/siphash.h

## Purpose

`siphash.h` declares the kernel SipHash and HalfSipHash APIs. SipHash2-4 is intended as a secure short-input PRF, while HalfSipHash1-3 and SipHash1-3 helpers are documented as insecure PRFs suitable only for hash tables.

## Important APIs, Types, And Functions

Types are `siphash_key_t`, aligned `siphash_aligned_key_t`, and `hsiphash_key_t`. APIs include `siphash_key_is_zero()`, `__siphash_aligned()`, `__siphash_unaligned()`, fixed-argument helpers `siphash_1u64()` through `siphash_4u64()`, `siphash_1u32()`, `siphash_2u32()`, `siphash_3u32()`, `siphash_4u32()`, generic `siphash()`, `__hsiphash_aligned()`, `__hsiphash_unaligned()`, fixed-argument `hsiphash_1u32()` through `hsiphash_4u32()`, and generic `hsiphash()`.

Internal macros expose raw permutations and constants: `SIPHASH_PERMUTATION`, `SIPHASH_CONST_*`, `HSIPHASH_PERMUTATION`, and `HSIPHASH_CONST_*`.

## Control Flow

The generic `siphash()` and `hsiphash()` wrappers choose aligned or unaligned implementations depending on efficient unaligned access support and pointer alignment. Aligned inline helpers use compile-time constant length checks to select specialized fixed-width helpers for 4, 8, 16, 24, and 32 byte SipHash inputs or 4, 8, 12, and 16 byte HalfSipHash inputs; otherwise they call the general aligned implementation.

## State And Persistence

No persistent state is stored in the header. Security depends on callers providing secret, initialized keys. `siphash_key_is_zero()` helps detect uninitialized all-zero keys.

## Dependencies And Integration Points

Dependencies include kernel types, endian conversion, alignment helpers, rotation helpers, and config for efficient unaligned access. Integration points are kernel hash tables, randomized identifiers, networking, filesystem hash salts, and any short-input keyed hash use.

## Risks And Test Signals

Risks are using HalfSipHash for security-sensitive PRF use, using all-zero or predictable keys, alignment-selection regressions, endian mistakes in fixed-width helpers, and direct misuse of raw permutation macros. Test signals include SipHash known-answer tests, unaligned buffer tests, compile-time constant length specialization coverage, big-endian builds, zero-key checks, and hash table collision resistance tests under randomized keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/siphash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sizes.h -->
# sources/distributed-fs/ceph-client/include/linux/sizes.h

## Purpose

`sizes.h` defines standard binary size constants from bytes through terabytes for kernel code and device descriptions. It improves readability and avoids repeated literal hex constants.

## Important APIs, Types, And Functions

The header exports `SZ_1` through `SZ_512`, kilobyte constants from `SZ_1K` through `SZ_512K`, megabyte constants from `SZ_1M` through `SZ_512M`, gigabyte constants from `SZ_1G` through `SZ_512G`, and terabyte constants from `SZ_1T` through `SZ_128T`. Values larger than 32 bits use `_AC(..., ULL)` from `linux/const.h`.

## Control Flow

There is no control flow. The macros are compile-time constants for array sizing, resource lengths, alignment, register windows, memory-region descriptions, and limit checks.

## State And Persistence

No state is stored. The constants become compile-time numeric values in users.

## Dependencies And Integration Points

The only dependency is `linux/const.h`. Integration points include architecture memory maps, drivers, firmware resource parsing, allocator limits, block sizes, and MM code.

## Risks And Test Signals

Risks are type width mistakes if large constants are used in 32-bit contexts, accidental decimal-vs-binary assumptions, and overflow in expressions that combine size constants before widening. Test signals include build coverage on 32-bit and 64-bit targets, sparse/compiler overflow warnings, and resource-size tests using constants above 4 GiB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sizes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skb_array.h -->
# sources/distributed-fs/ceph-client/include/linux/skb_array.h

## Purpose

`skb_array.h` defines a type-safe `struct sk_buff` FIFO wrapper around `ptr_ring`. It provides fixed-size queue operations for network packet buffers, including context-specific locking variants, length peeking with VLAN tag accounting, resizing, unconsume, and cleanup.

## Important APIs, Types, And Functions

The core type is `struct skb_array`, containing `struct ptr_ring ring`. APIs include `__skb_array_full()`, `skb_array_full()`, `skb_array_produce()`, `skb_array_produce_irq()`, `skb_array_produce_bh()`, `skb_array_produce_any()`, `__skb_array_empty()`, `__skb_array_peek()`, `skb_array_empty()`, `skb_array_empty_bh()`, `skb_array_empty_irq()`, `skb_array_empty_any()`, `__skb_array_consume()`, `skb_array_consume()`, batched consume variants for normal/IRQ/BH/any contexts, `skb_array_peek_len*()`, `skb_array_init()`, `skb_array_unconsume()`, `skb_array_resize()`, `skb_array_resize_multiple_bh()`, and `skb_array_cleanup()`.

`__skb_array_len_with_tag()` computes packet length and adds `VLAN_HLEN` when an skb carries a hardware-accelerated VLAN tag. `__skb_array_destroy_skb()` frees leftover ring entries with `kfree_skb()`.

## Control Flow

Producers enqueue SKBs into the underlying ptr ring with the variant matching their locking context. Consumers dequeue one or a batch, optionally peek at the first skb length, and may unconsume a batch back into the ring. Resize operations preserve entries or free overflow through the skb destroy callback. Cleanup drains and frees queued SKBs.

## State And Persistence

Persistent state is the embedded ptr ring: queue array, producer/consumer indexes, locks, and stored skb pointers. SKB ownership transfers to the ring on successful produce and back to the consumer on consume; cleanup and resize own freeing of retained SKBs.

## Dependencies And Integration Points

Dependencies are `ptr_ring`, `skbuff`, VLAN definitions, allocation hook wrappers, and kernel-only networking headers. Integration points are networking drivers and virtio/vhost-style packet queues that need fixed-depth SKB FIFOs.

## Risks And Test Signals

Risks include using `__skb_array_empty()` or `__skb_array_full()` in loops without compiler barriers, wrong context variant leading to IRQ/BH locking bugs, SKB leaks on resize/unconsume, length undercounting when VLAN tags are present, and assumptions that `struct skb_array` can diverge from `struct ptr_ring` layout despite the offset build check. Test signals include enqueue/dequeue ordering, full/empty transitions, IRQ/BH producer-consumer tests, batch consume/unconsume, resize under load, cleanup leak checks, VLAN length peeking, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skb_array.h -->
