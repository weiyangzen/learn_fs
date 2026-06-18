# Research Report: subset-b-004312

This grouped report covers the CAN SJA1000, SLCAN, Softing, and SPI CAN driver files assigned to work item `subset-b-004312`. Each section preserves the original source path and is bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000.c

Purpose: shared SocketCAN netdevice implementation for Philips/NXP SJA1000 Pelican-mode CAN controllers. Bus-specific drivers supply register accessors, IRQ flags, clock, CDR/OCR values, and optional quirks; this file owns CAN frame TX/RX, bittiming programming, interrupt handling, error reporting, and exported allocation/register helpers.

Important APIs/types/functions: `sja1000_bittiming_const` defines core timing limits. `alloc_sja1000dev()`, `free_sja1000dev()`, `register_sja1000dev()`, `unregister_sja1000dev()`, and exported `sja1000_interrupt()` form the module-facing API. `sja1000_priv` from the header carries `read_reg`/`write_reg`, `pre_irq`/`post_irq`, `cmdreg_lock`, register base, quirk flags, and CAN private state. Netdev operations are `sja1000_open()`, `sja1000_close()`, and `sja1000_start_xmit()`.

Control flow: registration probes the chip by reading MOD, sets reset mode, initializes Pelican mode, acceptance masks, OCR/CDR, then calls `register_candev()`. Open resets the chip, calls `open_candev()`, requests a threaded IRQ unless a board provides a custom IRQ handler, starts the controller, and enables the queue. TX stops the queue, encodes SFF/EFF/RTR IDs into SJA1000 transmit registers, stores echo skb slot 0, and issues `CMD_TR`, `CMD_SRR`, or `CMD_AT`. The ISR loops up to `SJA1000_MAX_IRQ`, handles TX complete, drains RX buffers via `sja1000_rx()`, and maps data overrun, bus error, arbitration lost, error passive, and bus-off conditions into SocketCAN error frames. A threaded reset callback can restart controllers that require reset on RX overrun.

State and persistence: state is hardware-register backed and volatile. Persistent kernel state includes `priv->can.state`, error counters read from TXERR/RXERR, netdev statistics, echo skb slot, queue stopped/running state, and quirk flags. `cmdreg_lock` serializes command register writes because writes require a settling read from SR. No disk persistence exists.

Dependencies/integration: integrates with `linux/can/dev.h`, `linux/can/error.h`, netdevice, ethtool timestamp info, and board drivers that fill `sja1000_priv`. It expects SJA1000-compatible register layout and Pelican mode unless `SJA1000_QUIRK_NO_CDR_REG` applies.

Risks: absent hardware is detected by `0xff` reads, but hot-unplug handling remains best-effort. Error skb allocation failure returns `-ENOMEM` after state handling. Reset-on-overrun restarts the device and frees echo skb, which can drop in-flight TX. Board drivers must provide correct clock frequency and register stride/access locking. Interrupt storm prevention is bounded by `SJA1000_MAX_IRQ`.

Test signals: probe with missing hardware should return `-ENODEV`; loopback TX should echo and wake queue; RX should decode SFF/EFF/RTR; bus errors should produce CAN error frames when reporting is enabled; overrun quirk should wake threaded reset path; bittiming writes should match BTR0/BTR1 values for known bitrates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000.h

Purpose: private shared header for SJA1000 SocketCAN drivers. It defines the Pelican-mode register map, command/status/interrupt bit masks, driver quirk flags, the `sja1000_priv` structure, and exported helper prototypes used by ISA, platform, PC/104, and other SJA1000 adapters.

Important APIs/types/functions: `SJA1000_ECHO_SKB_MAX` documents the single hardware TX buffer. Register constants cover MOD, CMR, SR, IR, IER, BTR, OCR, CDR, acceptance filters, error counters, ID/data registers, and CAN RAM. Bit definitions include mode bits, command bits, IRQ masks, status masks, ECC fields, and `SJA1000_CUSTOM_IRQ_HANDLER`, `SJA1000_QUIRK_NO_CDR_REG`, `SJA1000_QUIRK_RESET_ON_OVERRUN`. `struct sja1000_priv` embeds `struct can_priv` first and exposes hardware callback hooks and board configuration.

Control flow: no executable flow, but the structure defines how lower drivers plug into `sja1000.c`: allocate netdev, set register access callbacks, configure clock/OCR/CDR/flags/IRQ, then register. Optional `pre_irq` and `post_irq` are invoked around shared ISR service.

State and persistence: all fields are in-memory kernel device state. `reg_base` points at I/O memory or encoded port base. `priv` is an extension pointer to board-private allocation returned by `alloc_sja1000dev(sizeof_priv)`. There is no persistent storage.

Dependencies/integration: depends on Linux IRQ return types, SocketCAN device core, and platform data from `linux/can/platform/sja1000.h`. Board drivers must honor the locking note for register access and use `cmdreg_lock` only through the core command helper.

Risks: incorrect register definitions or callback implementations corrupt hardware state. Since `can_priv` must be first, changing layout can break SocketCAN assumptions. Quirk flags alter reset/CDR/IRQ behavior and must match hardware exactly.

Test signals: compile coverage from all SJA1000 subdrivers; runtime probe confirms register offsets; custom IRQ users should exercise `sja1000_interrupt()` directly; overrun and absent-controller paths validate quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_isa.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_isa.c

Purpose: legacy ISA-bus wrapper for SJA1000 CAN controllers configured through module parameters. It creates platform devices for up to eight manually described controllers and binds them to the shared SJA1000 core.

Important APIs/types/functions: module parameters `port`, `mem`, `irq`, `clk`, `cdr`, `ocr`, and `indirect` describe hardware. Register accessors cover memory-mapped, port I/O, and two-port indirect address/data access with per-device spinlocks. `sja1000_isa_probe()` allocates/configures/registers a CAN netdev; `sja1000_isa_remove()` releases resources; init/exit create platform devices and register the platform driver.

Control flow: module init scans parameter arrays. Entries with port or mem plus IRQ become `platform_device`s; incomplete first or explicitly configured entries fail. Probe reserves either memory or I/O ports, maps memory as needed, selects register accessor, derives CAN clock from oscillator divided by two, applies OCR/CDR defaults or overrides, and calls `register_sja1000dev()`. Remove unregisters the CAN device and releases I/O or memory regions.

State and persistence: static module parameter arrays and `sja1000_isa_devs[]` persist for module lifetime. Indirect I/O locks are static per index. Hardware state is reset and initialized by the core at register/open time; no disk persistence exists.

Dependencies/integration: depends on platform bus, ISA-style I/O port APIs, io memory mapping, SocketCAN SJA1000 core, and `linux/can/platform/sja1000.h` OCR/CDR constants.

Risks: fully manual resource configuration can collide with other devices. Indirect mode inheritance from `indirect[0]` is subtle. `priv->reg_base` stores port addresses cast through `void __iomem *`, so accessors must remain consistent. Invalid clock/OCR/CDR module params can produce nonfunctional CAN timing or output drive.

Test signals: load with valid `port`/`irq` or `mem`/`irq`; verify region reservation errors on conflicts; test indirect address/data mode; confirm default and indexed parameter fallback; unload should release all platform devices and regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_platform.c

Purpose: platform-bus SJA1000 driver supporting legacy platform data and device tree bindings, including NXP generic, Renesas RZ/N1, and Technologic variants.

Important APIs/types/functions: `struct sja1000_of_data` supplies optional private size and init hook. Accessors support 8/16/32-bit register spacing plus Technologic indirect 16-bit address/data access. `sp_populate()` handles platform data; `sp_populate_of()` parses OF properties `reg-io-width`, `nxp,external-clock-frequency`, `nxp,tx-output-mode`, `nxp,tx-output-config`, `nxp,clock-out-frequency`, and `nxp,no-comparator-bypass`. `sp_probe()`/`sp_remove()` bind to `module_platform_driver()`.

Control flow: probe requires platform data or OF node, maps resource 0 with devm helpers, obtains IRQ, optionally enables a clock for OF devices, allocates SJA1000 netdev with OF-specific private bytes, derives IRQ flags, sets register base/accessors and timing/output registers, applies match-data init hooks, then registers the SJA1000 device. Remove unregisters and frees the CAN device; devm handles mappings/clocks.

State and persistence: runtime state is in `sja1000_priv` plus optional `technologic_priv` spinlock. Renesas match data sets `SJA1000_QUIRK_NO_CDR_REG` and `SJA1000_QUIRK_RESET_ON_OVERRUN`; the intended reset-on-overrun IRQ oneshot flag is checked before OF init, which is a code-detail risk. No persistent storage.

Dependencies/integration: platform resources, OF matching, optional clocks, SocketCAN SJA1000 core, and the Linux CAN platform data ABI. Device tree properties control register stride and output clock behavior.

Risks: incorrect `reg-io-width` selects wrong register stride. Clock frequency is divided by two; missing/zero clock can invalidate bittiming. IRQ trigger/share flags differ between platform data and OF. Quirk initialization order should be reviewed for reset-on-overrun IRQ threading semantics.

Test signals: OF probe for generic, Renesas, and Technologic compatible strings; verify register reads with 1/2/4-byte spacing; check clock-derived bittiming; validate reset-on-overrun behavior on Renesas hardware; remove path should unregister cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/sja1000_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/tscan1.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/tscan1.c

Purpose: ISA driver for Technologic Systems TS-CAN1 PC/104 boards. It probes board PLD registers, determines IRQ from jumper bits, selects an available SJA1000 I/O base, and delegates CAN operation to the SJA1000 core.

Important APIs/types/functions: constants define PLD offsets, ID magic values, jumper masks, PLD base, SJA1000 candidate bases, and 16 MHz crystal. `tscan1_read()`/`tscan1_write()` use port I/O. `tscan1_probe()` performs board detection/resource selection; `tscan1_remove()` disables and releases resources. `module_isa_driver()` registers up to four jumper-selected boards.

Control flow: probe reserves the PLD region for the ISA ID, validates two ID bytes, maps JP4/JP5 jumper state to IRQ 5/6/7, allocates SJA1000 netdev, configures clock/CDR/OCR and port accessors, then scans a list of SJA1000 base addresses. For each free region it enables the PLD mode with address index and calls `register_sja1000dev()`; failures disable mode and try the next base.

State and persistence: device state is held in the netdev private structure and PLD registers. `netdev->base_addr` stores PLD base, while `priv->reg_base` stores SJA1000 port base. The LED is turned off after successful registration. No disk persistence.

Dependencies/integration: ISA driver core, I/O port reservation, SJA1000 core, and TS-CAN1 PLD hardware semantics documented in comments.

Risks: auto-selecting the first free SJA1000 address may choose an electrically invalid address if the PLD/hardware setup is unexpected. Bad jumper state without IRQ fails probe. Cleanup depends on `dev_get_drvdata()` being populated only after success.

Test signals: probe each JP1/JP2 board slot; verify ID mismatch returns `-ENODEV`; test all JP4/JP5 IRQ combinations; force address conflicts to exercise fallback; unload should disable SJA1000 I/O and release both regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/sja1000/tscan1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/slcan/Makefile

Purpose: build rules for the serial line CAN driver.

Important APIs/types/functions: builds `slcan.o` when `CONFIG_CAN_SLCAN` is enabled, with object components `slcan-core.o` and `slcan-ethtool.o`.

Control flow: no runtime flow. Kbuild links the core tty line discipline/netdev code with ethtool private flag support.

State and persistence: no runtime state. Build-time only.

Dependencies/integration: depends on the parent Kconfig selecting `CONFIG_CAN_SLCAN`; the object split requires symbols in `slcan.h` to connect core and ethtool code.

Risks: omitting either object breaks ethtool ops or the line discipline. Since `slcan-objs` starts empty then appends, later edits must preserve both entries.

Test signals: `CONFIG_CAN_SLCAN=m` should produce one `slcan.ko`; modpost should resolve `slcan_ethtool_ops`, `slcan_err_rst_on_open()`, and `slcan_enable_err_rst_on_open()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-core.c

Purpose: SocketCAN tty line discipline for SLCAN ASCII protocol. It creates a CAN netdev per attached tty, converts ASCII SLCAN frames/errors/states to `struct can_frame`/error skbs, converts outgoing CAN frames to ASCII, and sends setup commands to the adapter on open.

Important APIs/types/functions: `struct slcan` embeds `can_priv`, tty/netdev pointers, spinlock, TX work, RX/TX buffers, parser counters, command flags, and command waitqueue. `slcan_open()`/`slcan_close()` are line discipline lifecycle hooks. `slcan_receive_buf()` receives tty bytes; `slcan_unesc()` frames packets; `slcan_bump_frame()`, `slcan_bump_err()`, and `slcan_bump_state()` decode SLCAN messages. Netdev ops are `slcan_netdev_open()`, `slcan_netdev_close()`, and `slcan_netdev_xmit()`. `slcan_transmit_cmd()` synchronously sends adapter commands. Exported-to-compilation-unit helpers support ethtool private flag `err-rst-on-open`.

Control flow: ldisc open requires `CAP_NET_ADMIN`, allocates/registers a CAN netdev, initializes buffers/workqueue, assigns tty `disc_data`, and exposes ethtool ops. Netdev open fakes `CAN_BITRATE_UNKNOWN` if userspace did not request a bitrate, otherwise sends `C`, `S<n>`, optional `F`, and `L` or `O` commands. RX bytes accumulate until CR or BEL, then dispatch based on first byte. TX netdev path stops the queue, encodes one frame into `xbuff`, writes to tty, and relies on write wakeup/workqueue to drain the remainder and wake the queue. Close sends `C` when configured, flushes work, resets counters, and closes CAN state.

State and persistence: all state is per ldisc/netdev lifetime. `rbuff` and `rcount` hold partial input; `xbuff`, `xhead`, and `xleft` hold partial output or command; `SLF_ERROR` drops malformed overlong/tty-error packets until delimiter; `SLF_XCMD` tracks synchronous command completion; `CF_ERR_RST` persists as a private flag while the netdev exists. No disk persistence.

Dependencies/integration: tty line discipline `N_SLCAN`, SocketCAN core, rtnetlink/netdevice lifecycle, ethtool ops in `slcan-ethtool.c`, and userspace tools that set line discipline and CAN bitrate.

Risks: parser mutates `rbuff` to NUL-terminate ID/counter fields, so malformed messages must be carefully bounded by `SLCAN_MTU`. Command completion uses tty write wakeups and a one-second timeout; adapters that do not drain promptly fail open. `receive_buf` ignores input while the netdev is down. Only classic CAN length 0..8 is supported. Locking spans tty pointer and TX state, but ldisc close must flush work before freeing.

Test signals: attach ldisc to pty/serial, open netdev with supported bitrates, verify emitted command strings, inject SFF/EFF/RTR/error/state messages, test malformed hex and overlong input, verify ethtool private flag cannot change while running, and exercise close/hangup with pending TX work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-ethtool.c

Purpose: ethtool integration for SLCAN private flags and timestamp info.

Important APIs/types/functions: defines private flag string `err-rst-on-open`, maps it to bit 0, implements `get_strings`, `get_priv_flags`, `set_priv_flags`, and `get_sset_count`, and exports `slcan_ethtool_ops` with generic timestamp info.

Control flow: ethtool queries copy the private flag name for `ETH_SS_PRIV_FLAGS`; get/set forwards to `slcan_err_rst_on_open()` and `slcan_enable_err_rst_on_open()` implemented in core. Set converts the bit to a boolean and returns core validation, including `-EBUSY` while the device is running.

State and persistence: no local state. It reads and writes `sl->cmd_flags` through core helpers. The setting lasts only for the netdev/ldisc lifetime.

Dependencies/integration: depends on `slcan.h`, netdevice, ethtool, and SocketCAN core includes. It is linked into `slcan.o` by the Makefile.

Risks: private flag bit layout must match the string array. Unknown stringsets fall through without action for `get_strings`; unsupported count returns `-EOPNOTSUPP`.

Test signals: `ethtool --show-priv-flags slcanX` exposes one flag; toggling it while down changes open behavior; toggling while up returns busy; `ethtool -T` returns generic software timestamp capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan.h

Purpose: small internal header joining SLCAN core and ethtool implementation.

Important APIs/types/functions: declares `slcan_err_rst_on_open()`, `slcan_enable_err_rst_on_open()`, and `extern const struct ethtool_ops slcan_ethtool_ops`.

Control flow: no executable flow. The declarations let `slcan-ethtool.c` call core helpers and let core attach ethtool ops during ldisc open.

State and persistence: no state in this header.

Dependencies/integration: requires callers to include netdevice-compatible type declarations before use; both SLCAN objects include it.

Risks: changing prototypes requires synchronized updates to both compilation units. The flag semantics are not visible here beyond helper names.

Test signals: compile/link test of `CONFIG_CAN_SLCAN`; unresolved symbols indicate header/object mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/slcan/slcan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/softing/Kconfig

Purpose: Kconfig menu entries for Softing generic CAN support and Softing PCMCIA bridge support.

Important APIs/types/functions: `CAN_SOFTING` is a tristate depending on `HAS_IOMEM` and describes shared DPRAM platform-device support. `CAN_SOFTING_CS` is a tristate depending on `PCMCIA` and `CAN_SOFTING`, creating PCMCIA platform devices and requiring Softing firmware 4.6 binaries.

Control flow: build-time configuration only. Enabling PCMCIA support also requires the generic support object.

State and persistence: no runtime state. Configuration persists in kernel build config.

Dependencies/integration: integrates Softing source files with kernel CAN and PCMCIA subsystems. Help text documents the card-wide API limitation: actions on one bus can temporarily affect the other.

Risks: firmware dependency is external and runtime-critical. Selecting only generic support is useful for platform providers, but PCMCIA cards need both options. The two-bus coupling affects user expectations for independent netdev operations.

Test signals: Kconfig dependency resolution; module build for `CAN_SOFTING=m` and `CAN_SOFTING_CS=m`; runtime firmware request names should match installed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/softing/Makefile

Purpose: Kbuild rules for Softing CAN drivers.

Important APIs/types/functions: `softing-y := softing_main.o softing_fw.o`; `obj-$(CONFIG_CAN_SOFTING) += softing.o`; `obj-$(CONFIG_CAN_SOFTING_CS) += softing_cs.o`.

Control flow: no runtime flow. The generic Softing module is composed from runtime/netdev logic and firmware-loading logic, while PCMCIA bridge is separate.

State and persistence: build-time only.

Dependencies/integration: requires symbol sharing between `softing_main.o` and `softing_fw.o` through `softing.h`; PCMCIA bridge exports platform data to the `softing` platform driver.

Risks: omitting `softing_fw.o` breaks boot and start/stop paths; omitting `softing_main.o` removes platform driver and netdev ops. Link order is simple but both objects are mandatory.

Test signals: all Softing configs should link; modpost should resolve firmware helper symbols and platform-driver symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing.h

Purpose: shared internal header for Softing DPRAM CAN driver objects. It defines per-bus and per-card state, exported internal functions, and the DPRAM layout/protocol constants used by firmware and runtime paths.

Important APIs/types/functions: `struct softing_priv` embeds `can_priv`, netdev/card pointers, TX echo ring counters, bittiming const, bus index, output mode, and chip ID. `struct softing` owns platform data, two netdev slots, spinlock, timestamp references, firmware lock/up state, IRQ bookkeeping, card-wide TX state, DPRAM mapping, and card identity. Function prototypes cover firmware loading, card power-on, IRQ enablement, bus start/stop, timestamp conversion, RX injection, and default output selection. DPRAM offsets define RX/TX FIFOs, function command mailboxes, reset/IRQ registers, time registers, and firmware command/receipt areas.

Control flow: no executable flow, but this header encodes the contract between `softing_main.c`, `softing_fw.c`, and platform providers. Runtime code uses the DPRAM offsets to queue TX/RX entries and send synchronous firmware functions.

State and persistence: all structs are volatile kernel/card runtime state. DPRAM fields are card-shared memory; host fields track firmware status, TX pending, timestamp overflow, and identity read from firmware. No disk persistence.

Dependencies/integration: depends on netdevice, SocketCAN, ktime, mutex/spinlock, atomic headers, and `softing_platform.h`. Consumers must hold the documented locks around firmware-up state and DPRAM access.

Risks: DPRAM offsets are ABI with firmware; errors cause silent card miscommunication. The card has up to two netdevs but one shared firmware state and TX FIFO, so per-bus operations are coupled. Ring constants determine echo skb capacity.

Test signals: compile both Softing objects; boot card and read identity; RX/TX FIFO offsets verified by traffic; state transitions tested on one and two bus configurations; timestamp conversion tested across overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_cs.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_cs.c

Purpose: PCMCIA bridge driver for Softing/Vector/EDIC CAN cards. It identifies supported card IDs, configures PCMCIA resources, and creates a `softing` platform device with platform data consumed by the generic DPRAM driver.

Important APIs/types/functions: `softingcs_platform_data[]` lists card names, manufacturer/product IDs, generation, bus count, clock/BRP/SJW limits, DPRAM size, boot/load/app firmware paths, and reset/IRQ callbacks. `softingcs_find_platform_data()` matches IDs. `softingcs_reset()` and `softingcs_enable_irq()` write PCMCIA config bytes. `softingcs_probe_config()` requests memory window parameters. `softingcs_probe()` creates a custom platform device with MEM and IRQ resources.

Control flow: PCMCIA probe matches IDs, selects platform data, configures IRQ/IOMEM/VPP/VCC, requests and enables the PCMCIA device, allocates an embedded platform_device plus resources, fills memory and IRQ resources, assigns a unique id, names it `softingcs.N`, and registers it. Remove unregisters the platform device and disables PCMCIA.

State and persistence: static platform data is immutable. `softingcs_index` assigns increasing IDs under spinlock. `pcmcia->priv` stores the platform device. Runtime firmware/card state lives in the generic Softing platform driver.

Dependencies/integration: PCMCIA core, platform bus, Softing platform data ABI, firmware files under `softing-4.6/`, and generic `softing` platform driver.

Risks: memory window size and generation-specific width/wait settings must match cards. `kzalloc_obj()` usage assumes local macro/support in this source tree. Platform device lifetime uses custom release to free the enclosing allocation. Generation 2 cards do not use `enable_irq` callback.

Test signals: insert each supported card ID; verify platform device creation and resource ranges; firmware request should match platform data; removal should unregister platform child and disable PCMCIA; unsupported IDs should return `-ENOTTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_fw.c

Purpose: firmware protocol and card-control implementation for Softing DPRAM CAN cards. It loads boot, loader, and application firmware, sends synchronous firmware commands, powers on chips, converts timestamps, and starts/stops card buses.

Important APIs/types/functions: `_softing_fct_cmd()` and `softing_fct_cmd()` implement firmware mailbox commands through DPRAM function parameters. `softing_bootloader_command()` sends bootloader commands. `fw_parse()` parses little-endian Softing structured binary records with checksum validation. `softing_load_fw()` writes boot/loader records directly to DPRAM and verifies readback. `softing_load_app_fw()` transfers app records through bootloader SRAM commands and checksum receipts. `softing_chip_poweron()` synchronizes and reads identity. `softing_raw2ktime()` converts card raw ticks. `softing_startstop()` performs the card-wide bus restart/start/stop sequence.

Control flow: firmware loading requests named files, validates a Softing header record, iterates data/start/eof records, writes data to DPRAM or bootloader staging, and verifies checksums/readback. Power-on sends sync vectors, resets chips, reads serial/version/license/chip IDs. Start/stop locks firmware state, stops queues for all relevant netdevs, closes active CAN devices, disables IRQ, resets chip, initializes one or both CAN chips with bittiming/filter/output settings, initializes interface/FIFOs/TX ACK, starts chips, initializes timestamps, reopens/wakes active buses, and re-enables IRQ. Failures shut down IRQs, reset chip, unlock, and close all netdevs.

State and persistence: updates `card->fw.up`, `card->id`, `card->ts_ref`, `card->ts_overflow`, card and per-bus TX counters, bus CAN states, and DPRAM mailbox/FIFO/control fields. Firmware files are external persistent inputs, but driver state is runtime only.

Dependencies/integration: Linux firmware loader, DPRAM I/O accessors/barriers, SocketCAN state helpers, Softing platform data firmware offsets/addresses, and `softing_main.c` IRQ/RX helpers.

Risks: firmware ABI is timing-sensitive; command polling timeouts and signal interruption can leave the card reset. `strncmp()` uses firmware-provided length for header comparison, so malformed short/long headers deserve attention. Starting one bus can restart the other because firmware control is card-wide. Error reporting command is disabled with `if (0 && error_reporting)`, so BERR reporting is intentionally not active despite ctrlmode. Timestamp overflow adjustment mutates `ts_ref` while converting.

Test signals: missing/corrupt firmware files; checksum mismatch; DPRAM readback failure; successful boot identity reads; start one bus then both buses; bus-off recovery through `CAN_MODE_START`; verify queues stop/wake and restart error frames on sibling bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_main.c

Purpose: generic platform driver and runtime data path for Softing DPRAM CAN cards. It boots firmware, creates up to two CAN netdevs, handles TX/RX FIFOs, threaded interrupts, sysfs attributes, and platform-device lifecycle.

Important APIs/types/functions: `softing_netdev_start_xmit()` queues CAN frames into the DPRAM TX FIFO. `softing_handle_1()` processes one RX FIFO or status/lost-message event. `softing_irq_v1()`/`softing_irq_v2()` acknowledge hardware IRQ status; `softing_irq_thread()` drains DPRAM and wakes queues. `softing_enable_irq()` requests/frees threaded IRQs. `softing_card_boot()` validates DPRAM, loads firmware, starts app, and powers on chips. `softing_netdev_create()` configures per-bus CAN devices. Platform callbacks `softing_pdev_probe()` and `softing_pdev_remove()` own mapping, boot, sysfs, and registration.

Control flow: platform probe validates platform data, allocates card state, maps DPRAM, records IRQ, boots the card, creates platform sysfs attributes, allocates/registers netdevs for discovered chip IDs, and publishes readiness. Netdev open calls `open_candev()` then `softing_startstop(up=1)`; stop calls card-wide startstop down. TX encodes command flags, bus ID, CAN ID/DLC/data into FIFO slot, advances hardware write pointer, stores echo skb, and may stop all queues if card FIFO is full. IRQ top halves clear generation-specific IRQ flags and wake the thread; thread drains RX/status entries, updates stats/error states, completes TX echoes, and wakes eligible queues.

State and persistence: card state includes firmware up/down, DPRAM mapping, IRQ request state, card-wide and per-bus TX pending rings, timestamp references, identity, sysfs-visible output/chip fields, and netdev stats. Sysfs `output` is mutable only while netdev is down and persists until device removal.

Dependencies/integration: platform bus, firmware helpers in `softing_fw.c`, SocketCAN, DPRAM I/O barriers, threaded IRQs, sysfs, ethtool timestamp info, and platform data from PCMCIA or other bridge drivers.

Risks: TX/RX FIFO pointer arithmetic and shared card spinlock are critical. RX lost-message reporting is broadcast to active buses because the card does not identify the bus. Error state handling manually updates `priv->can.state` and invokes `can_bus_off()`. Probe creates `ARRAY_SIZE(card->net)` netdevs, so platform `nbus` validation and discovered chip IDs must be coherent. Failure paths must avoid double unregister/free after partially registered netdevs.

Test signals: probe with valid platform data and firmware; DPRAM memory self-test failure; RX normal, RTR, EFF, and error status frames; TX ACK echo completion; FIFO full queue stopping/waking; sysfs output write while up/down; generation 1 and 2 IRQ paths; remove with active netdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_platform.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_platform.h

Purpose: platform-data ABI for Softing CAN platform devices.

Important APIs/types/functions: `fw_dir` defines the firmware directory prefix `softing-4.6/`. `struct softing_platform_data` describes manufacturer/product IDs, generation, bus count, controller frequency, bittiming limits, DPRAM size, boot/load/app firmware offset/address/name triples, and optional reset/IRQ-enable callbacks.

Control flow: no executable flow. Bridge drivers populate this data; the generic platform driver uses it during boot, firmware loading, CAN timing setup, IRQ/reset handling, and naming.

State and persistence: platform data is static or device-provided configuration. Firmware filenames refer to persistent files loaded at runtime.

Dependencies/integration: platform device API and Softing generic driver. PCMCIA bridge fills this structure for card variants.

Risks: incorrect offsets/addresses/firmware names can brick boot for a device instance until reload. Generation controls DPRAM reset/IRQ behavior and memory width expectations. `nbus` must fit the generic driver's two-netdev array.

Test signals: platform probe should reject missing/invalid data; each card variant should load expected firmware triplet; reset and enable_irq callbacks should be invoked in boot/shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/softing/softing_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/Kconfig

Purpose: Kconfig menu for SPI-connected CAN controllers.

Important APIs/types/functions: menu depends on `SPI`. `CAN_HI311X` enables Holt HI311x driver. `CAN_MCP251X` enables Microchip MCP251x/MCP25625 classic CAN driver. It sources the MCP251xFD subdirectory Kconfig for CAN FD-capable controllers.

Control flow: build-time configuration only.

State and persistence: selected options persist in kernel config; no runtime state.

Dependencies/integration: SPI core is mandatory. Subdrivers integrate with SocketCAN and their own regulators/clocks/DT bindings at runtime.

Risks: users may confuse classic `CAN_MCP251X` with FD `CAN_MCP251XFD`; both are separate drivers. Missing SPI dependency prevents menu visibility.

Test signals: Kconfig visibility under SPI; module/object generation for each selected driver; MCP251xFD options sourced correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/Makefile

Purpose: Kbuild rules for SPI CAN drivers.

Important APIs/types/functions: builds `hi311x.o` for `CONFIG_CAN_HI311X`, `mcp251x.o` for `CONFIG_CAN_MCP251X`, and always descends into `mcp251xfd/` so that subdir Kbuild can decide based on its config.

Control flow: no runtime flow.

State and persistence: build-time only.

Dependencies/integration: ties parent SPI CAN menu to concrete driver objects and MCP251xFD composite module.

Risks: `obj-y += mcp251xfd/` is intentional for recursive kbuild; removing it hides FD driver builds even when configured.

Test signals: kernel build with each config as built-in/module; verify subdirectory objects are considered when `CONFIG_CAN_MCP251XFD` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/hi311x.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/hi311x.c

Purpose: SocketCAN SPI driver for Holt HI-3110 CAN controller. It handles SPI register/FIFO access, CAN netdev lifecycle, threaded IRQ RX/error/TX completion, regulators/clocks, workqueue-based TX/restart, and suspend/resume.

Important APIs/types/functions: `hi3110_bittiming_const` defines timing limits. `struct hi3110_priv` stores CAN/net/spi pointers, SPI buffers, TX skb, workqueue/work items, suspend/restart flags, `tx_busy`, regulators, and clock. SPI helpers include `hi3110_spi_trans()`, `hi3110_cmd()`, `hi3110_read()`, `hi3110_write()`. Data path functions include `hi3110_hw_tx()`, `hi3110_hw_rx()`, `hi3110_hard_start_xmit()`, `hi3110_tx_work_handler()`, and `hi3110_can_ist()`.

Control flow: probe obtains optional clock or `clock-frequency`, validates max 40 MHz, allocates CAN netdev, enables clock/power, configures SPI, allocates workqueue/buffers, probes reset value, sleeps hardware, and registers CAN device. Open enables transceiver, requests oneshot high-trigger threaded IRQ, resets chip, writes bittiming, enters normal/listen/loopback mode, and wakes queue. TX stops queue and queues work; work writes one frame to FIFO and stores echo skb. IRQ thread drains RX FIFO while nonempty, reads interrupt/error flags, updates CAN state/error frames, handles bus-off and optional bus error reporting, completes TX echo when TX empty, and wakes queue. Stop closes CAN, frees IRQ, disables interrupts/TX, cleans TX, sleeps chip, and disables transceiver.

State and persistence: runtime state includes `force_quit`, `after_suspend` bitmask, `restart_tx`, `tx_skb`, `tx_busy`, CAN state, netdev stats, regulators, clock, and SPI buffers. Suspend records whether interface was up/down/powered and resume queues restart work as needed. No disk persistence.

Dependencies/integration: SPI core, SocketCAN, regulator and clock frameworks, device properties/OF match `holt,hi3110`, workqueues, freezer-aware PM, and ethtool timestamp info.

Risks: SPI errors are mostly logged but not checked on every register access by design. IRQ handler loops under mutex and must observe `force_quit`. `hi3110_set_normal_mode()` compares masked mode bits with the unmasked requested value, which works only because constants occupy the mask bits. Single TX buffer means queue correctness depends on `tx_skb`/`tx_busy`. Suspend disables IRQ without locking based on lifecycle assumptions.

Test signals: probe with valid/invalid clock frequency and reset STATF value; TX/RX SFF/EFF/RTR frames; bus-off and restart; BERR reporting protocol errors; regulator defer and enable failures; suspend/resume while up and down; SPI controller transfer failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/hi311x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251x.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251x.c

Purpose: SocketCAN SPI driver for classic Microchip MCP2510, MCP2515, and MCP25625 CAN controllers. It provides SPI register access, optional GPIO-controller support for chip pins, CAN TX/RX/error handling, power/clock management, and PM restart logic.

Important APIs/types/functions: large register/instruction map covers SPI commands, CANCTRL/CANSTAT, bit timing, interrupt flags, error flags, TX/RX buffer layouts, masks, filters, and GPIO pin registers. `struct mcp251x_priv` stores CAN/net/spi pointers, model, mutex, SPI buffers, TX skb, workqueue/restart state, regulators/clock, and optional `gpio_chip` plus cached `BFPCTRL`. SPI helpers include read/write/bit modify, half-duplex support, and mode polling. GPIO helpers expose TXnRTS inputs and RXnBF outputs when `gpio-controller` property is present. Netdev and CAN helpers include `mcp251x_hw_tx()`, `mcp251x_hw_rx()`, `mcp251x_set_normal_mode()`, `mcp251x_do_set_bittiming()`, `mcp251x_can_ist()`, `mcp251x_open()`, and `mcp251x_stop()`.

Control flow: probe gets clock or `clock-frequency`, validates 1-25 MHz, allocates CAN netdev, enables clock/power, configures SPI speed defaults based on model, allocates workqueue and transfer buffers, resets/probes CANCTRL defaults, sleeps hardware, registers CAN dev, and optionally registers GPIO chip. Open enables transceiver, requests oneshot IRQ (falling if no firmware node), wakes chip to config mode, programs bittiming and RX buffer acceptance-all mode, enters normal/listen/loopback, and wakes queue. TX queues one skb to workqueue, which writes TXB0 and issues RTS. IRQ thread reads CANINTF/EFLG, drains RX buffers, clears flags, handles overrun and CAN state transitions, calls `can_bus_off()` when needed, completes echo on TX interrupts, and wakes queue. Restart work restores after suspend or emits CAN restart error skb.

State and persistence: volatile state includes CAN state/stats, `force_quit`, `after_suspend`, `restart_tx`, `tx_skb`, `tx_busy`, cached GPIO BFPCTRL, power/transceiver state, and one echo skb slot. Suspend powers down chip and records resume actions; resume restores power/transceiver and queues restart work. No disk persistence.

Dependencies/integration: SPI core including half-duplex controllers, SocketCAN, GPIOLIB optionally, regulator/clock frameworks, device properties/OF IDs, workqueues, threaded IRQs, PM ops, and ethtool timestamp info.

Risks: many register accesses intentionally ignore return values after initial probe. MCP2510 has special slow register-by-register paths and manual RX flag clearing. The open failure path avoids deadlock by deferring `free_irq()` until after mutex unlock when IRQ may be waiting on the same lock. Optional GPIO state must be restored after reset. Only classic CAN data length up to 8 is supported; TX clamps oversized frame len defensively.

Test signals: probe each model and half-duplex/full-duplex SPI controller; verify default SPI speed selection; RX0/RX1 drain and race reread path; TX completion and queue wake; error warning/passive/bus-off transitions and overrun counters; GPIO get/set/request/free; suspend/resume with interface up/down; regulator and IRQ failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Kconfig

Purpose: Kconfig entries for Microchip MCP251xFD CAN FD controller family.

Important APIs/types/functions: `CAN_MCP251XFD` is a tristate selecting `CAN_RX_OFFLOAD`, `REGMAP`, `WANT_DEV_COREDUMP`, and `GPIOLIB`. `CAN_MCP251XFD_SANITY` enables optional internal counter sanity checks with runtime overhead.

Control flow: build-time configuration only.

State and persistence: selected options persist in kernel config; no runtime state.

Dependencies/integration: SPI parent menu, SocketCAN RX offload, regmap abstraction, devcoredump, and GPIO library are required by the composite driver.

Risks: sanity option can affect runtime cost. The main option pulls in several frameworks, so build dependency changes need care.

Test signals: Kconfig dependency resolution; build with sanity enabled/disabled; verify selected helper frameworks are available for module and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Makefile

Purpose: Kbuild composition for the MCP251xFD CAN FD driver.

Important APIs/types/functions: builds `mcp251xfd.o` when `CONFIG_CAN_MCP251XFD` is enabled. The module links chip FIFO, core, CRC, ethtool, RAM, regmap, ring, RX, TEF, timestamp, and TX objects; `mcp251xfd-dump.o` is added when `CONFIG_DEV_COREDUMP` is enabled.

Control flow: no runtime flow. Object list defines functional decomposition of the driver.

State and persistence: build-time only.

Dependencies/integration: relies on the parent SPI Makefile descending into this directory. Conditional dump object corresponds to devcoredump support selected in Kconfig.

Risks: missing one object can break runtime paths or unresolved symbols because the driver is highly split. Conditional dump linkage must match config.

Test signals: module link for MCP251xFD with and without devcoredump; modpost symbol resolution across all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-chip-fifo.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-chip-fifo.c

Purpose: FIFO and acceptance-filter initialization for the MCP251xFD CAN FD controller.

Important APIs/types/functions: `mcp251xfd_chip_rx_fifo_init_one()` builds RX FIFO configuration for one RX ring, enabling timestamps, RX overflow interrupt, and not-empty interrupt. `mcp251xfd_chip_rx_filter_init_one()` enables a filter and points it to the ring FIFO. `mcp251xfd_chip_fifo_init()` initializes TEF, TX FIFO, and all RX FIFOs/filters through regmap writes.

Control flow: full init writes TEFCON based on TX ring object count and enables TEF timestamp/overflow/not-empty interrupts. It writes TX FIFOCON with object count, TX enable, transmit-attempt interrupt, payload size 64 for FD mode or 8 for classic mode, and one-shot or unlimited retry policy from CAN ctrlmode. It then iterates RX rings with `mcp251xfd_for_each_rx_ring()`, programming each RX FIFO and filter.

State and persistence: persistent runtime state is in chip registers programmed through `priv->map_reg`. Ring object counts, FIFO numbers, filter numbers, CAN FD mode, and ctrlmode are read from `mcp251xfd_priv` ring structures. No disk persistence.

Dependencies/integration: depends on `mcp251xfd.h`, regmap, bitfield helpers, ring allocation done elsewhere, and CAN ctrlmode. Integrates with RX, TX, TEF, and timestamp submodules through shared FIFO/register layout.

Risks: FIFO object count is programmed as `obj_num - 1`, so zero-sized rings would underflow if ever allowed. RX overflow interrupt is intentionally enabled on all RX FIFOs to detect RX MAB overflow. Filter index/register math must match hardware grouping of four filters per FLTCON register. Payload size must match CAN FD mode or RX/TX layout breaks.

Test signals: initialize in classic and FD modes; verify TEF/TX/RX FIFOCON register values; test one-shot ctrlmode; receive overflow should raise RXOVIF on affected FIFO; filters should route frames to expected RX FIFO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-chip-fifo.c -->
