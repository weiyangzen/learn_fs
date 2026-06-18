# Research: subset-b-004309

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan-core.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan-core.c

Purpose: this is the main NXP/Freescale FlexCAN SocketCAN platform driver. It maps the FlexCAN register block, selects SoC-specific quirk data, configures classic CAN or CAN FD timing, manages RX through either hardware FIFO or mailbox offload, handles TX through one message buffer, reports CAN error states, and integrates runtime/system PM plus wakeup stop-mode handling.

Important APIs, types, and functions: the file defines `struct flexcan_mb` and `struct flexcan_regs` for the hardware layout, many register bit definitions, SoC `struct flexcan_devtype_data` tables, classic and FD `can_bittiming_const` values, endian-specific read/write callbacks, and the platform driver. Core paths include `flexcan_probe()`, `register_flexcandev()`, `flexcan_open()`, `flexcan_chip_start()`, `flexcan_irq()`, `flexcan_mailbox_read()`, `flexcan_start_xmit()`, `flexcan_close()`, `flexcan_set_mode()`, and the suspend/resume helpers. `flexcan_rx_offload_setup()` is the bridge into `can_rx_offload`.

Control flow: probe obtains regulator or PHY transceiver resources, clocks or fixed `clock-frequency`, IRQs, MMIO, compatible match data, endian mode, CAN capabilities, and optional secondary/boff/error IRQs. Runtime PM is enabled before `register_flexcandev()`, which powers clocks, verifies FIFO-capable hardware, registers the CAN netdev, then leaves the core disabled. Opening the device validates mode combinations, resumes runtime PM, opens the CAN core, powers the transceiver, configures RX offload, starts the chip, enables offload, requests IRQs, enables hardware interrupts, and starts the netdev queue. TX converts a CAN/CAN FD skb into FlexCAN ID/control/data words, stores an echo skb, activates the TX mailbox, and applies the ERR005829 reserved-mailbox write sequence. RX IRQs feed either timestamped mailbox masks or FIFO events into `can_rx_offload`; TX completion pulls the echo skb and wakes the queue. Error and state IRQs allocate CAN error skbs, update counters, handle bus-off, and use quirk-specific interrupt masking for cores with incomplete warning/passive IRQ behavior.

State and persistence: persistent software state is in `struct flexcan_priv`: register base, selected endianness callbacks, quirk copy, clocks, transceiver handles, mailbox sizing and masks, CAN offload state, cached CTRL defaults, stop-mode data, and IRQ numbers. Hardware state includes MCR/CTRL/CTRL2/CBT/FDCBT/FDCTRL, mailbox RAM, RX masks, MECR, IMASK/IFLAG, and optional stop-mode request bits. Runtime suspend only gates clocks; system suspend either enters wake-capable stop mode or stops the chip, disables interrupts/transceiver, and selects sleep pinctrl. Resume reverses that state and restarts the chip when needed.

Dependencies and integration points: the driver depends on SocketCAN core helpers, `can_rx_offload`, platform/OF match data, clocks, regulators, PHY transceivers, runtime PM, pinctrl, regmap/syscon, i.MX SCU firmware, SCMI/ATF-managed stop-mode assumptions, and `flexcan_ethtool_ops` from the companion file. Device Tree properties include `big-endian`, `clock-frequency`, `fsl,clk-source`, `fsl,stop-mode`, `fsl,scu-index`, and `wakeup-source`.

Risks: most behavior is quirk-driven, so incompatible quirk combinations are dangerous; the probe checks CAN FD against RX-FIFO mode and mailbox RTR support consistency. Mailbox sizing changes with CAN FD payload size, affecting RX/TX mask boundaries. RX FIFO versus mailbox mode changes RTR support and RX overflow semantics. State IRQ handling has workarounds for broken warning/passive interrupts and can change error IRQ masking dynamically. Stop-mode acknowledgement polling is short and board/firmware dependent. ECC memory initialization and MECR programming must happen in freeze mode with exact unlock sequencing. TX relies on a single mailbox plus echo index zero, so queue stopping/waking must remain paired with TX completion.

Test signals: useful validation includes successful probe for each compatible, correct endian access on big-endian SoCs, `ip link set canX up type can bitrate ...` for classic and FD modes, RX FIFO and RX mailbox receive paths, RTR behavior via ethtool `rx-rtr`, TX echo and queue wakeup, bus error reporting, bus-off/restart, warning/passive transitions on broken IRQ cores, suspend/resume with and without wakeup, runtime PM clock gating, secondary mailbox IRQ use on S32G2, and absence of timeout logs from freeze, low-power, and soft-reset polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan-ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan-ethtool.c

Purpose: this companion file exposes FlexCAN ethtool operations. It reports fixed RX/TX ring characteristics and provides one private flag, `rx-rtr`, that selects the receive implementation needed to support or drop remote-transmission-request frames depending on hardware capabilities.

Important APIs, types, and functions: `flexcan_get_ringparam()` reports mailbox counts, RX FIFO depth, and single-buffer TX. `flexcan_get_strings()`, `flexcan_get_sset_count()`, `flexcan_get_priv_flags()`, and `flexcan_set_priv_flags()` implement `ETH_SS_PRIV_FLAGS`. The exported `flexcan_ethtool_ops` also uses `ethtool_op_get_ts_info`. The private flag maps to `FLEXCAN_QUIRK_USE_RX_MAILBOX` through helpers in `flexcan.h`.

Control flow: ethtool ring queries read `struct flexcan_priv` and return `mb_count` maxima, RX pending as mailbox span or fixed FIFO depth six, and TX pending one. Private-flag reads call `flexcan_active_rx_rtr()`. Private-flag writes compute a new quirk set: enabling `rx-rtr` chooses mailbox mode when mailbox RTR is supported, otherwise FIFO if available, otherwise mailbox; disabling chooses mailbox mode when only mailbox RX is supported and FIFO otherwise. If the quirk set would change while the netdev is running, the operation fails with `-EBUSY`; otherwise it updates the private quirk copy.

State and persistence: the only changed state is `priv->devtype_data.quirks`, a per-device copy created at probe time. The setting is runtime state, not persisted to firmware or device tree. It affects the next open/start path because RX offload setup and chip initialization inspect `FLEXCAN_QUIRK_USE_RX_MAILBOX`.

Dependencies and integration points: it depends on `flexcan.h`, Linux ethtool private flags, and the core driver's `struct flexcan_priv` layout. Users interact through `ethtool --show-priv-flags` and `--set-priv-flags`; the core driver consumes the resulting quirk bit during open.

Risks: changing RX mode while up is blocked, but users may still be surprised that disabling `rx-rtr` can force mailbox mode on devices without FIFO support and logs that RTR frames cannot be received. The flag is capability-sensitive, so bad quirk definitions in the core file can expose impossible mode choices.

Test signals: verify `ethtool -g` reports mailbox/FIFO ring values, private flag count/string is stable, `rx-rtr` toggles only while the interface is down, subsequent interface open uses the selected RX mode, and devices without RX RTR support emit the informational warning when appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan.h -->
## sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan.h

Purpose: this header shares FlexCAN private driver definitions between the core and ethtool files. It documents hardware feature flags, defines the per-SoC quirk bits, declares the device private state, and provides small helpers for RX mailbox/FIFO/RTR capability decisions.

Important APIs, types, and functions: `struct flexcan_devtype_data` carries the quirk bitmap selected by platform or OF match data. `struct flexcan_stop_mode` stores a syscon regmap and bit location for GPR stop mode. `struct flexcan_priv` embeds `struct can_priv` and `struct can_rx_offload`, then stores register pointers, mailbox pointers and dimensions, masks, clocks, transceiver resources, stop-mode firmware data, IRQ numbers, and endian read/write callbacks. Inline helpers are `flexcan_supports_rx_mailbox()`, `flexcan_supports_rx_mailbox_rtr()`, `flexcan_supports_rx_fifo()`, and `flexcan_active_rx_rtr()`. The header declares `flexcan_ethtool_ops`.

Control flow: the header itself has no runtime control flow, but its helpers are used by ethtool to decide whether a requested `rx-rtr` private flag means mailbox mode or FIFO mode. The core driver fills `struct flexcan_priv` during probe and open, then reads its quirk and mailbox fields throughout bit timing, RX offload, interrupt, PM, and TX paths.

State and persistence: the header defines the shape of all FlexCAN runtime state. The quirk bitmap is copied from static match data into each device and can be modified by ethtool before the interface is opened. Stop-mode state persists for the lifetime of the platform device and is consumed by suspend/resume.

Dependencies and integration points: it includes `linux/can/rx-offload.h` and assumes Linux CAN, clock, regulator, PHY, regmap, i.MX SCU, and MMIO types are visible through the C files that include it. The exported ethtool ops declaration is the link between `flexcan-core.c` and `flexcan-ethtool.c`.

Risks: quirk bits are a compact contract across files; adding or changing one requires auditing core startup, RX offload, PM, ethtool mode selection, and compatible data. `struct flexcan_priv` exposes direct register access callbacks and hardware mailbox pointers, so invalid `mb_count` or `mb_size` calculations in the core can corrupt MMIO accesses.

Test signals: compile coverage should catch missing type declarations and exported ops mismatches. Runtime signals are correct quirk-derived behavior per compatible, ethtool `rx-rtr` behavior, CAN FD capability gating, stop-mode wakeup, and mailbox/FIFO receive mode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/grcan.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/grcan.c

Purpose: this is the SocketCAN driver for Aeroflex Gaisler GRCAN and GRHCAN GRLIB CAN controllers. It programs a memory-mapped CAN controller with coherent DMA TX/RX circular buffers, exposes module/sysfs configuration for physical interface selection, implements NAPI receive and TX echo catch-up, and works around a known TX hang bug in older GRLIB versions.

Important APIs, types, and functions: `struct grcan_registers` defines the hardware register layout. `struct grcan_dma` and `struct grcan_dma_buffer` describe one coherent allocation split into aligned TX and RX rings. `struct grcan_device_config` stores interface and buffer-size configuration. `struct grcan_priv` holds CAN private state, NAPI, registers, DMA buffers, echo skb array, ring echo pointer `eskbp`, lock, close/reset flags, and TX bug timers. Main functions are `grcan_probe()`, `grcan_setup_netdev()`, `grcan_open()`, `grcan_start()`, `grcan_interrupt()`, `grcan_poll()`, `grcan_receive()`, `grcan_start_xmit()`, `catch_up_echo_skb()`, `grcan_err()`, `grcan_set_bittiming()`, and the running-reset timer callbacks.

Control flow: probe reads AMBA frequency from DT, maps registers, maps the IRQ, checks `/ambapp0` system ID to decide whether the TX bug workaround is needed, sanitizes module parameters, allocates/registers the CAN device, and resets the hardware. Open allocates aligned DMA rings, allocates an echo skb table sized to the TX ring, opens CAN core, requests the shared IRQ, enables NAPI, starts hardware under the spinlock, and starts the TX queue unless listen-only. `grcan_start()` resets the controller, programs DMA base/size registers, enables default interrupts, writes physical interface/listen/sample/one-shot configuration, enables TX/RX channels, and marks CAN active. IRQ acknowledges pending sources, disables RX/TX interrupts and schedules NAPI for traffic, and sends error sources to `grcan_err()`. NAPI drains RX frames from the DMA ring, catches up TX echo skbs to hardware `txrd`, then reenables RX/TX interrupts. TX writes a CAN frame into the DMA TX slot, handles queue stop on low space, optionally invokes the old-core TX bug workaround, stores echo skb by slot index, issues a write memory barrier, and advances `txwr`.

State and persistence: persistent driver state includes module-parameter defaults copied to each device, sysfs-configurable `enable0`, `enable1`, and `select` while down, coherent DMA ring addresses while open, echo skb pointers, ring pointers in hardware, and reset/closing flags. Error state is mirrored in `priv->can.state`; bus-off can stop hardware when automatic restart is disabled. The running-reset path snapshots TX/RX ring registers, resets the hardware, restores ring pointers and `eskbp`, reenables channels, and wakes the queue if possible.

Dependencies and integration points: it uses SocketCAN, NAPI, shared IRQs, Open Firmware match names, DMA coherent allocation, module parameters, sysfs netdev groups, and `ethtool_op_get_ts_info`. It depends on GRLIB AMBA properties such as `freq` and optional `/ambapp0` `systemid` for TX bug detection.

Risks: ring arithmetic is central; `txwr`, `txrd`, and `eskbp` must remain consistent or echo skbs leak or complete incorrectly. The coherent allocation manually aligns two rings inside a larger allocation. Old hardware can hang if TX write/read pointers update in the same clock cycle, so the workaround mixes busy waits, one-shot frame dropping, hang timers, and running resets. Error handling can halt the device on AHB bus errors. NAPI/IRQ/reset interactions rely on `priv->lock` and `closing/resetting` flags to avoid waking the queue during teardown.

Test signals: validate module parameter sanitization, sysfs interface selection while down and `-EBUSY` while up, successful DMA allocation with configured sizes, RX/TX under ring wraparound, one-shot TX loss handling, bus-off/restart behavior, error-counter state transitions, AHB error shutdown, old-GRLIB TX hang recovery, NAPI interrupt reenable, and clean open/close cycles with no echo skb leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/grcan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Kconfig

Purpose: this Kconfig entry exposes the IFI CAN_FD soft-IP SocketCAN driver as `CONFIG_CAN_IFI_CANFD`.

Important APIs, types, and functions: the entry is `tristate "IFI CAN_FD IP"` and depends on `HAS_IOMEM`. Its help text describes an I/F/I CAN_FD soft IP block attached through the Linux platform bus, typically synthesized into FPGA or CPLD logic.

Control flow: the file contributes configuration metadata only. When selected as built-in or module, it enables compilation of the matching object through the directory Makefile.

State and persistence: there is no runtime state. Persistent behavior is the kernel build configuration symbol.

Dependencies and integration points: `HAS_IOMEM` ensures MMIO accessor support, matching the driver's use of `devm_platform_ioremap_resource()` and `readl()/writel()`. The symbol is consumed by `ifi_canfd/Makefile`.

Risks: Kconfig does not express dependencies on OF or platform bus support even though the driver probes through OF-compatible platform devices; builds without useful platform instantiation may compile but never bind.

Test signals: `CONFIG_CAN_IFI_CANFD=m` should produce `ifi_canfd.ko`, `=y` should link the object built-in, and disabling `HAS_IOMEM` should hide or reject the symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Makefile

Purpose: this Makefile wires the IFI CANFD driver source into the kernel build.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_CAN_IFI_CANFD) += ifi_canfd.o`, so the object is included when the Kconfig symbol is built-in or modular.

Control flow: Kbuild expands the conditional object assignment during kernel build. There is no source-level runtime behavior.

State and persistence: state is entirely build configuration. The output is either no object, a built-in object, or a loadable module depending on `CONFIG_CAN_IFI_CANFD`.

Dependencies and integration points: it depends on the sibling Kconfig symbol and the `ifi_canfd.c` translation unit. It fits the standard drivers/net/can subdirectory Kbuild pattern.

Risks: because there are no composite objects or extra flags, any future source split must update this file. A mismatched Kconfig symbol would silently omit the driver from builds.

Test signals: `make M=drivers/net/can/ifi_canfd` or an equivalent tree build should compile `ifi_canfd.o` when `CONFIG_CAN_IFI_CANFD` is enabled, and module builds should emit an `ifi_canfd` module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/ifi_canfd.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/ifi_canfd.c

Purpose: this is the SocketCAN platform driver for the IFI CANFD controller IP. It drives a register-based CAN/CAN FD core with RX/TX FIFOs, hardware acceptance filters, bus-state interrupts, optional bus error reporting, and a single echo slot.

Important APIs, types, and functions: register offsets and bit definitions cover status/control, RX/TX FIFO commands, interrupt mask/status, nominal/data timing, transmitter delay compensation, error counters, version/IP ID, FIFO payload registers, and acceptance filters. `struct ifi_canfd_priv` stores `can_priv`, NAPI, netdev, and base MMIO. Main paths include `ifi_canfd_plat_probe()`, `ifi_canfd_open()`, `ifi_canfd_start()`, `ifi_canfd_isr()`, `ifi_canfd_poll()`, `ifi_canfd_read_fifo()`, `ifi_canfd_start_xmit()`, `ifi_canfd_stop()`, `ifi_canfd_set_mode()`, and error helpers for lost messages, LEC errors, and state changes.

Control flow: probe maps registers, gets the platform IRQ, verifies the IP ID and minimum revision, allocates one-echo CAN device, registers NAPI and netdev ops, reads the CAN clock from hardware, defaults `CAN_CTRLMODE_FD`, advertises loopback/listen-only/FD/non-ISO/bus-error modes, and registers the CAN device. Open calls `open_candev()`, requests the shared IRQ, starts the controller, enables NAPI, and starts the queue. Start hard-resets the IP, selects 7/9/8/8 timing layout, writes nominal/data timing and TDC, installs broad filters for standard, extended, and CAN FD frames, resets FIFOs, clears interrupts, builds `STCMD` mode bits, enables IRQs, resets/enables the detailed error counter, and enables the controller. The ISR clears pending interrupts, disables IRQs and schedules NAPI for RX/error work, completes TX echo on remove interrupt, and wakes the queue on TX FIFO availability. NAPI handles state changes, RX overflow, detailed bus errors when enabled, and normal RX FIFO draining before reenabling IRQs. TX checks FIFO-full, stops the queue, packs ID/DLC/FD flags/data into TX FIFO registers, stores echo skb index zero, and triggers `ADD_MSG`.

State and persistence: runtime state is minimal: CAN core state, NAPI state, base MMIO, and the echo skb managed by the CAN core. Hardware holds filters, timing, FIFO contents, interrupt masks, and error counters. Close stops queue and NAPI, hard-resets the IP, masks/clears interrupts, frees IRQ, and closes the CAN device.

Dependencies and integration points: it uses platform devices, OF compatible `ifi,canfd-1.0`, SocketCAN helpers, NAPI, shared IRQs, MMIO accessors, and ethtool timestamp info. It reads clock and IP version from device registers instead of external clock APIs.

Risks: TX uses one echo slot and stops the queue until hardware reports FIFO removal or empty status; missed TX interrupts can stall transmission. RX/TX extended-ID layout requires bit swapping between standard and extended portions. Error handling clears and reenables a hardware error counter with a magic unlock sequence. `ifi_canfd_read_fifo()` reads payload as 32-bit words into frame data, so alignment and endian assumptions match the hardware register format. Probe rejects older revisions, which is safe but can surprise boards with older synthesized IP.

Test signals: verify IP ID/revision checks, classic CAN and CAN FD traffic, ISO and non-ISO FD mode bits, bitrate/data-bitrate programming, loopback/listen-only modes, extended ID bit swapping, RX overflow error frames, detailed bus error frames with `berr-reporting`, bus-off disables IRQs and calls `can_bus_off()`, TX echo completion, and clean close/reopen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/ifi_canfd/ifi_canfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/janz-ican3.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/janz-ican3.c

Purpose: this is the SocketCAN driver for the Janz MODULbus VMOD-ICAN3 CAN interface. It communicates with firmware through dual-ported memory, negotiates old, new, and fast host interfaces, converts SJA1000-style firmware events into Linux CAN errors, and exposes termination and firmware info through sysfs.

Important APIs, types, and functions: `struct ican3_dev` is the central state object, embedding `can_priv` and holding the netdev, NAPI, module number, MODULbus control/DPM mappings, completions for termination and bus-error inquiries, firmware type/info, host-interface state, echo skb queue, DPM page lock, descriptor ring indices, and free-page allocator. Message/descriptor types are `struct ican3_msg`, `struct ican3_new_desc`, and `struct ican3_fast_desc`. Key functions include `ican3_probe()`, `ican3_startup_module()`, `ican3_reset_module()`, `ican3_init_new_host_interface()`, `ican3_init_fast_host_interface()`, `ican3_send_msg()`, `ican3_recv_msg()`, `ican3_napi()`, `ican3_recv_skb()`, `ican3_xmit()`, `ican3_handle_cevtind()`, `ican3_set_bus_state()`, `ican3_get_berr_counter()`, and the sysfs termination handlers.

Control flow: probe requires Janz platform data, allocates a CAN device, initializes NAPI, echo queue, spinlock, completions, sysfs groups, CAN timing/mode callbacks, maps DPM and control resources, disables interrupts, requests the shared IRQ, enables NAPI, starts firmware, and registers the CAN device. Startup resets the module, detects firmware from the DPM firmware stamp, enables interrupts, sends connect, initializes and switches to the new host interface, enables termination, enables bus-error reporting, initializes fast descriptor rings, switches firmware to fast queues, and opens acceptance filters. Open calls `open_candev()`, sends firmware bus-on with SJA1000 bit timing, marks CAN active, and starts the queue. IRQ handling clears the microcontroller interrupt, disables module interrupts, and schedules NAPI. NAPI drains firmware control messages, handles CAN/error/inquiry responses, drains fast RX descriptors, wakes TX if descriptors and echo space are available, then reenables interrupts. TX verifies descriptor and echo space under the DPM page lock, converts a CAN frame to ICAN3 fast format, stores an echo skb in a private queue, toggles descriptor valid bits in the firmware-required order, interrupts the microcontroller, advances the TX descriptor index, and stops the queue when full.

State and persistence: persistent state lives in firmware-managed DPM pages and `struct ican3_dev` indices. The page window is global to the module, so all DPM access is serialized by `mod->lock`. Firmware type determines message formats for bus-on/off and bus-error quota. Echo skbs are kept in a private queue because there is no direct TX-done interrupt; matching a received hardware-loopback frame completes TX stats and echo delivery. Termination state and bus error counters are asynchronous inquiry results stored after completions.

Dependencies and integration points: it depends on the Janz MFD platform layer (`linux/mfd/janz.h`), platform resources, shared IRQs, SocketCAN, NAPI, sysfs netdev attribute groups, and SJA1000-compatible timing/error semantics. It supports ICANOS and CAL/CANopen firmware variants with different control messages.

Risks: dual-ported memory page selection is fragile; any access without the spinlock can read or write the wrong page. Firmware protocol transitions must happen in order, and failures during startup leave the module unregistered. TX completion is inferred from loopback echo matching, so bus errors require dropping echo skbs and re-enabling bus-error reporting. Completions for inquiry responses can time out. The remove path uses `unregister_netdev()` rather than `unregister_candev()`, so teardown correctness depends on netdev/CAN unregister compatibility in this tree. Firmware-specific message formats and the documented inquiry bug are easy regression points.

Test signals: validate probe/startup on both firmware types, old-to-new-to-fast interface negotiation, bus-on/off, standard and extended frames, one-shot mode, queue stop/wake when descriptor rings fill/drain, echo matching for self-sent frames, bus error reporting and echo drop on TX errors, bus-off handling, termination show/store, bus error counter inquiry timeout behavior, firmware info sysfs output, and clean remove with interrupts disabled and DPM unmapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/janz-ican3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/Makefile

Purpose: this Makefile builds the Kvaser PCIe FD CAN driver as a composite object when `CONFIG_CAN_KVASER_PCIEFD` is enabled.

Important APIs, types, and functions: `obj-$(CONFIG_CAN_KVASER_PCIEFD) += kvaser_pciefd.o` declares the final object/module. `kvaser_pciefd-y = kvaser_pciefd_core.o kvaser_pciefd_devlink.o` combines the core PCI/CAN implementation with devlink support.

Control flow: Kbuild conditionally links the composite object from its two parts. There is no runtime behavior in the Makefile.

State and persistence: build configuration controls whether the driver is omitted, built-in, or built as a module. The `kvaser_pciefd-y` list is persistent build metadata for the composite object.

Dependencies and integration points: the file depends on the parent Kconfig symbol and the existence of `kvaser_pciefd_core.c`, `kvaser_pciefd_devlink.c`, and shared declarations in `kvaser_pciefd.h`.

Risks: adding new source files for PCI IDs, firmware handling, or devlink features requires updating the composite list. If `CONFIG_CAN_KVASER_PCIEFD` is enabled without one of the component objects, the build fails at Kbuild time.

Test signals: a kernel or module build with `CONFIG_CAN_KVASER_PCIEFD=m` should compile both component objects and link `kvaser_pciefd.ko`; built-in mode should include both objects in vmlinux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd.h -->
## sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd.h

Purpose: this header contains common declarations for the Kvaser PCIe FD CAN driver, shared by the core PCI/CAN code and devlink support. It defines board/channel limits, DMA sizing, register-offset abstractions, IRQ masks, per-channel state, device-wide state, firmware version representation, and devlink registration APIs.

Important APIs, types, and functions: constants include `KVASER_PCIEFD_MAX_CAN_CHANNELS`, `KVASER_PCIEFD_DMA_COUNT`, `KVASER_PCIEFD_DMA_SIZE`, and `KVASER_PCIEFD_CAN_TX_MAX_COUNT`. `struct kvaser_pciefd_address_offset` describes device-family register offsets. `struct kvaser_pciefd_irq_mask` describes RX/TX/all interrupt masks. `struct kvaser_pciefd_dev_ops` supplies family-specific DMA map writes. `struct kvaser_pciefd_driver_data` groups offsets, masks, and ops. `struct kvaser_pciefd_can` embeds `can_priv` and `devlink_port`, plus per-channel registers, error counters, command/ack indices, TX completion counters, lock, BEC polling timer, and start/flush completions. `struct kvaser_pciefd` stores the PCI device, base MMIO, channel pointers, driver data, DMA buffers, channel count, clock frequencies, firmware version, and tick conversion. The header exports `kvaser_pciefd_devlink_ops`, `kvaser_pciefd_devlink_port_register()`, and `kvaser_pciefd_devlink_port_unregister()`.

Control flow: the header itself has no executable flow. It establishes the state and callback contract used when the PCI core allocates device/channel objects, maps DMA buffers, handles interrupts and TX acknowledgements, polls bus error counters, and registers devlink ports.

State and persistence: per-channel state includes CAN configuration, devlink port identity, MMIO base, cached bus error counters, command sequence, TX and ACK ring positions, completed TX accounting, sensitive-register spinlock, polling timer, and completions. Device-wide state includes PCI/MMIO resources, channel array, DMA memory pointers, clocks, firmware version, and static driver data selected by PCI IDs or equivalent match logic in the core source.

Dependencies and integration points: it includes Linux CAN device APIs, PCI, completions, spinlocks, timers, basic types, and devlink. The devlink declarations link the core driver to `kvaser_pciefd_devlink.o`; the ops and offset structs allow core logic to support multiple hardware layouts without open-coding offsets everywhere.

Risks: the fixed maximum channel and DMA constants are shared assumptions with hardware and the core implementation. `tx_idx`, `ack_idx`, and `KVASER_PCIEFD_CAN_TX_MAX_COUNT` must match the controller's TX FIFO/ack behavior. Sensitive MODE-like registers require `lock` discipline. Devlink port lifetime must match CAN channel registration/removal to avoid stale devlink state.

Test signals: compile both core and devlink objects against this header, probe hardware variants with different offset/mask tables, validate all channels up to the max, exercise TX ring wrap and ACK handling, confirm BEC polling timer updates, verify devlink port registration/unregistration per CAN channel, and test DMA map programming through `kvaser_pciefd_dev_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd.h -->
