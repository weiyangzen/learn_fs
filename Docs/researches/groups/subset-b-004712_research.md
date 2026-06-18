# subset-b-004712 WAN Driver Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/farsync.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/farsync.c

Purpose: PCI HDLC WAN driver for FarSite FarSync T-series adapters, supporting X.21, V.35, V.24, and TE1 cards through the Linux generic HDLC layer plus a FarSync raw mode. It owns PCI probe/remove, card reset/download handoff, firmware shared-memory validation, port registration, descriptor rings, transmit queueing, receive processing, DMA on TXU-family boards, carrier tracking, private ioctls, and generic WAN interface ioctls.

Important APIs, types, and functions: internal hardware contract is modeled by `struct fst_shared`, `struct rxdesc`, `struct txdesc`, `struct cirbuff`, `struct port_cfg`, `struct su_config`, and `struct su_status`. Runtime state is split between `struct fst_card_info` and `struct fst_port_info`. PCI integration uses `fst_pci_dev_id`, `fst_driver`, `fst_add_one()`, and `fst_remove_one()`. Netdev and HDLC entry points are `fst_open()`, `fst_close()`, `fst_start_xmit()`, `fst_attach()`, `fst_ioctl()`, `fst_siocdevprivate()`, and `fst_tx_timeout()`. Interrupt and deferred paths are `fst_intr()`, `fst_process_int_work_q()`, `fst_process_tx_work_q()`, `do_bottom_half_rx()`, `do_bottom_half_tx()`, `fst_intr_rx()`, and DMA completion helpers.

Control flow: probe enables PCI regions, maps card memory/control windows, requests IRQ, resets the onboard processor, sets up DMA if applicable, allocates HDLC netdevs, registers ports, and stores the card in the global card array. Firmware is not started automatically; userspace can reset, write firmware blocks, release the CPU, and call `FSTGETCONF`, which validates `SMC_VERSION`, `END_SIG`, task status, and then enables interrupts. TX packets enter a per-port circular software queue from `fst_start_xmit()`, then a tasklet copies or DMA-transfers them to card buffers and gives descriptors to firmware. RX interrupts schedule bottom-half processing; received descriptors are validated, copied or DMAed into SKBs, classified as raw FarSync or HDLC, and delivered with `netif_rx()`.

State and persistence: all persistent runtime state is in kernel memory and card shared memory; there is no disk persistence. Card state advances through `FST_UNINIT`, `FST_RESET`, `FST_DOWNLOAD`, `FST_STARTING`, `FST_RUNNING`, and error states. Port state tracks descriptor positions, queued SKBs, mode, running flag, carrier status, and flow-control state. Firmware-visible configuration persists in mapped card memory until reset or unload.

Dependencies and integration points: depends on PCI, I/O memory, generic HDLC, netdevice APIs, tasklets, DMA coherent buffers, uaccess, and FarSync firmware layout from `farsync.h`. It exposes private `SIOCDEVPRIVATE` ioctls and generic HDLC WAN ioctls. It integrates with link status through modem signals or TE1 alarms and with module parameters controlling queue watermarks, max RX work, and excluded cards.

Risks: hardware/firmware ABI is fragile because packed shared memory offsets and magic versions must match firmware. `fst_issue_cmd()` waits under repeated sleeps for firmware mailbox clearance, so firmware stalls can delay operations. TX/RX DMA state is one-per-card, not per-port, which constrains concurrency. Error recovery assumes one frame per 8 KiB buffer. Raw private ioctls write arbitrary card memory after range checks and require `CAP_NET_ADMIN`; firmware loading mistakes can leave the card unusable until reset. Probe/remove paths have many resource stages and need hardware testing.

Test signals: compile coverage with FarSync enabled, PCI probe/remove on each supported device ID, firmware download and `FSTGETCONF` transition to `FST_RUNNING`, HDLC attach/open/close, raw mode RX protocol tagging, TX queue watermarks, DMA and non-DMA transfer paths, carrier transitions for modem and TE1 alarms, oversized packet drops, RX CRC/frame/overflow counters, and card removal after active ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/farsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/farsync.h -->
# sources/distributed-fs/ceph-client/drivers/net/wan/farsync.h

Purpose: userspace-visible ABI header for the FarSync driver. It defines device names, the public version, private ioctl numbers, firmware download structure, configuration/status structure, valid-bit masks, card/line/protocol/state constants, TE1 configuration values, modem-signal bits, and optional debug flags.

Important APIs, types, and functions: primary exported data contracts are `struct fstioc_write` for firmware/card-memory writes and `struct fstioc_info` for `FSTGETCONF`/`FSTSETCONF`. Important constants include `FSTWRITE`, `FSTCPURESET`, `FSTCPURELEASE`, `FSTGETCONF`, `FSTSETCONF`, `FSTVAL_*`, `FST_TYPE_*`, `FST_*` state values, `V24`/`X21`/`V35`/`T1`/`E1`/`J1`, `FST_RAW`, `FST_GEN_HDLC`, modem input/output masks, and TE1 clocking/framing/coding/loop/buffer options.

Control flow: this header has no executable flow, but it determines how userspace drives `farsync.c`: reset the onboard CPU, write firmware blocks, release the CPU, poll/get config to complete startup, and set selected runtime options through valid-bit gated fields. `valid` is central: get operations report which fields are meaningful, while set operations request selective updates.

State and persistence: structures mirror live driver/card state rather than persistent storage. The constants are ABI-sensitive because several values overlap with firmware shared-memory configuration fields; changing them would break userspace tools or firmware expectations.

Dependencies and integration points: requires socket ioctl numbering from the kernel UAPI context and is consumed by `farsync.c` plus external FarSync configuration utilities. TE1 values map onto firmware `suConfig`/`suStatus` fields, and generic HDLC protocol selection maps to Linux WAN ioctl behavior.

Risks: the flexible array in `struct fstioc_write` must be used with careful userspace sizing. `struct fstioc_info` is large and version-sensitive; field additions must preserve compatibility. The `valid` mask excludes debug from `FSTVAL_ALL`, so callers must explicitly request or interpret debug behavior.

Test signals: ABI tests should verify ioctl numbers, structure sizes/offsets for target architectures, `FSTGETCONF` zeroed-input behavior, valid mask semantics, TE1 value mapping, and compatibility with existing FarSync firmware loading tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/farsync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wan/framer/Kconfig

Purpose: Kconfig menu for the WAN framer subsystem. It introduces `FRAMER` as the user-visible subsystem switch, `GENERIC_FRAMER` as the internal core selector, and `FRAMER_PEF2256` as the Lantiq PEF2256/FALC56 framer driver option.

Important APIs, types, and functions: no code APIs are declared, but the config symbols gate compilation of `framer-core.o` and the PEF2256 module. `FRAMER_PEF2256` depends on device tree and I/O memory support, and selects `GENERIC_FRAMER`, `MFD_CORE`, and `REGMAP_MMIO`.

Control flow: build selection starts with `menuconfig FRAMER`; if enabled, users can select the PEF2256 driver. Selecting PEF2256 automatically enables the generic framer core and required infrastructure.

State and persistence: only build-time state. It does not create runtime configuration or persisted settings.

Dependencies and integration points: integrates with the kernel build system, OF/platform device matching, MFD child devices, and MMIO regmap. The help text describes the framer abstraction used by HDLC/TDM consumers such as the QMC HDLC driver.

Risks: if future framer consumers select only `GENERIC_FRAMER` without `FRAMER`, menu visibility and dependency intent should remain coherent. PEF2256 currently depends on OF, so non-DT platforms cannot build/use it through this option.

Test signals: Kconfig tests should cover `FRAMER=n`, `FRAMER=y/m` with `FRAMER_PEF2256=n`, and `FRAMER_PEF2256=y/m`, verifying selected symbols and linked objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wan/framer/Makefile

Purpose: build rules for the framer subsystem directory.

Important APIs, types, and functions: maps `CONFIG_GENERIC_FRAMER` to `framer-core.o` and `CONFIG_FRAMER_PEF2256` to the `pef2256/` subdirectory.

Control flow: during kbuild, object inclusion follows the selected Kconfig symbols. The PEF2256 directory is entered only when its driver is enabled.

State and persistence: build-only file with no runtime state.

Dependencies and integration points: depends on symbols defined in the adjacent Kconfig. It is the bridge from subsystem selection to the core framework and provider driver.

Risks: if additional framer drivers are added, they must be placed under the correct symbol and should select or depend on `GENERIC_FRAMER` consistently. Misalignment with Kconfig would produce missing symbols or unused objects.

Test signals: build matrix with generic core only and with PEF2256 enabled as built-in/module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/framer-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/framer/framer-core.c

Purpose: generic framer framework for E1/T1 line-interface components. It lets provider drivers create `struct framer` class devices and lets consumer drivers obtain, configure, power, monitor, and release those framers through OF phandles or parent lookup.

Important APIs, types, and functions: exported consumer APIs include `framer_init()`, `framer_exit()`, `framer_power_on()`, `framer_power_off()`, `framer_get_status()`, `framer_set_config()`, `framer_get_config()`, notifier registration helpers, `framer_get()`, `framer_put()`, and devm variants. Provider APIs include `framer_create()`, `framer_destroy()`, `devm_framer_create()`, `framer_provider_simple_of_xlate()`, `__framer_provider_of_register()`, and devm unregister helpers. Internal state uses the framer class, provider list, IDA IDs, mutex-protected init/power counts, work items, notifier chains, runtime PM, and optional regulator.

Control flow: providers create a framer device, optionally register an OF provider, and supply operations. Consumers resolve a framer, get device/module references, create a stateless device link, call init, optionally configure, power on/off, register notifiers, and release resources. If provider ops request `FRAMER_FLAG_POLL_STATUS`, `framer_init()` captures initial status and schedules periodic polling; changes trigger blocking notifier events. Direct status notifications from atomic context are deferred through workqueue.

State and persistence: state is in memory: init/power reference counts, previous status, notifier list, work items, class device lifetime, provider list, and regulator/runtime PM state. No disk persistence exists. Lifetime is reference-counted with device model and devres.

Dependencies and integration points: depends on Linux device model, class devices, OF phandle parsing, module references, device links, runtime PM, regulators, workqueues, IDA, mutexes, and blocking notifiers. PEF2256 is a provider; QMC HDLC is a consumer.

Risks: `framer_exit()` decrements `init_count` without visible underflow guard, so consumer call ordering matters. `framer_power_off()` similarly assumes balanced power calls. Provider lookup returns `-EPROBE_DEFER` for missing providers, which is correct for probe ordering but can hide permanent DT errors until later. Polling work reschedules unconditionally until cancelled, making balanced `framer_exit()`/destroy important.

Test signals: provider create/destroy, OF phandle and parent lookup, optional `devm_framer_optional_get()`, balanced and unbalanced init/power call behavior, notifier delivery from polling and explicit status change, runtime PM disabled/enabled paths, optional regulator enable/disable, provider unregister while consumers are absent, and module refcount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/framer-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/Makefile

Purpose: kbuild rules for the Lantiq PEF2256 framer provider.

Important APIs, types, and functions: maps `CONFIG_FRAMER_PEF2256` to the module object `framer-pef2256.o`, built from `pef2256.o`.

Control flow: when the PEF2256 config is selected, this directory builds a single module/built-in object that registers the platform driver.

State and persistence: build-only file.

Dependencies and integration points: aligns the module name advertised by Kconfig with the object composition. The resulting driver depends on the generic framer framework, MFD, regmap MMIO, clocks, GPIO, and OF matching.

Risks: future split files must be added to `framer-pef2256-objs`; otherwise symbols will be missing. Module naming should remain consistent with Kconfig help and userspace expectations.

Test signals: verify module builds as `framer-pef2256` for `m` and links into vmlinux for `y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/pef2256-regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/pef2256-regs.h

Purpose: register and bitfield definition header for the Lantiq PEF2256/FALC56 framer.

Important APIs, types, and functions: defines offsets for command, interrupt mask/status, framer mode, transmit/receive control, line interface mode, system interface control, clock mode, global config, port config, global counter mode, version/status, receive status, global interrupt status, and wafer ID registers. Bit helpers use `BIT()`, `GENMASK()`, `FIELD_PREP_CONST()`, and `FIELD_PREP()` for coding modes, frame formats, clock rates, buffer depths, LOS thresholds, carrier status, interrupt bits, and version decoding.

Control flow: no executable flow. `pef2256.c` consumes these constants to identify chip version, program E1 line/system/signaling/errors, mask/unmask interrupts, read carrier status, and decode interrupt sources.

State and persistence: register definitions only. Hardware state is represented by the chip registers programmed through these offsets.

Dependencies and integration points: depends on Linux bitfield helpers. It is tightly coupled to the PEF2256 datasheet and to the register programming sequences in `pef2256.c`.

Risks: wrong bit masks or version-specific constants can silently misprogram clocks, line thresholds, coding, or interrupt handling. Some fields are split across registers, such as SSD in `FMR1` and `SIC1`; users must update both sides consistently.

Test signals: static compile of all macros, hardware register trace comparison against datasheet-recommended E1 setup, version detection for 1.2/2.1/2.2, LOS/AIS interrupt mask behavior, and tests for all supported mclk/sysclk/data-rate combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/pef2256-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/pef2256.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/pef2256.c

Purpose: platform driver for the Lantiq PEF2256/FALC56 framer. It exposes the chip through the generic framer framework, configures E1 line/system/signaling/error behavior, handles LOS/AIS carrier interrupts, creates MFD children, and exposes a read-only version sysfs attribute.

Important APIs, types, and functions: core state is `struct pef2256`, including regmap, clocks, reset GPIO, version, rates, subordinate/master clocking, frame type, channel phase, carrier atomic, and framer pointer. Register helpers wrap regmap byte operations. Setup functions include `pef2256_setup_gcm()`, `pef2256_setup_e1_line()`, `pef2256_setup_e1_los()`, `pef2256_setup_e1_system()`, `pef2256_setup_e1_signaling()`, `pef2256_setup_e1_errors()`, and `pef2256_setup_e1()`. Framer ops are `pef2256_framer_get_status()`, `pef2256_framer_set_config()`, and `pef2256_framer_get_config()`. Probe/remove are `pef2256_probe()` and `pef2256_remove()`.

Control flow: probe maps MMIO, initializes regmap, enables `mclk`, `sclkr`, and `sclkx`, validates equal system clock rates, toggles reset GPIO, identifies chip version, parses DT data rate/edge/channel phase, creates the framer, masks and clears interrupts, requests IRQ, adds pinctrl and codec child devices, applies E1 setup, registers the OF framer provider, and creates sysfs `version`. Configuration through framer ops validates E1-only support, maps internal/external clocking to master/subordinate mode, and re-runs E1 setup. IRQ handling reads GIS, dispatches ISR handlers, and updates carrier when LOS/AIS status changes.

State and persistence: runtime state is in `struct pef2256`, chip registers, clock framework state, optional reset GPIO, MFD children, sysfs attribute, and framer class/provider registration. Carrier status is cached atomically. There is no disk persistence.

Dependencies and integration points: depends on platform/OF, regmap MMIO, clocks, GPIO, MFD core, generic framer provider APIs, notifier delivery via `framer_notify_status_change()`, and the register definitions header. Consumers such as QMC HDLC can obtain the framer by phandle and receive carrier/config services.

Risks: only E1 is supported despite framer abstractions having T1 notions, so consumers requesting T1 receive `-EOPNOTSUPP`. Clock/data-rate validation is strict and DT-sensitive. Register sequences differ for chip versions, especially GCM and LIM fields. `device_create_file()` return value is not checked. Interrupt masking and carrier cache need real hardware validation because status bits are read-clear in several places.

Test signals: probe with all supported chip versions and clock rates, invalid clock/rate/channel-phase DT failures, reset GPIO timing, sysfs version presence/removal, framer get/set/get config, LOS/AIS carrier notification, MFD child creation, remove interrupt masking, and interop with QMC HDLC carrier changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/framer/pef2256/pef2256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/fsl_qmc_hdlc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/fsl_qmc_hdlc.c

Purpose: Freescale/NXP QMC HDLC netdevice driver. It binds a QMC channel to the Linux generic HDLC stack, optionally controls an external framer, maps TE1 timeslots, queues DMA-backed RX/TX descriptors, and reports carrier based on framer status.

Important APIs, types, and functions: state is held in `struct qmc_hdlc` and descriptor metadata in `struct qmc_hdlc_desc`. Framer helpers are `qmc_hdlc_framer_init()`, `qmc_hdlc_framer_start()`, `qmc_hdlc_framer_stop()`, `qmc_hdlc_framer_set_iface()`, `qmc_hdlc_framer_get_iface()`, and the notifier callback. Data path helpers include `qmc_hdlc_recv_queue()`, `qmc_hcld_recv_complete()`, `qmc_hdlc_xmit_queue()`, `qmc_hdlc_xmit_complete()`, and `qmc_hdlc_xmit()`. Interface and timeslot management uses `qmc_hdlc_xlate_slot_map()`, `qmc_hdlc_xlate_ts_info()`, `qmc_hdlc_set_iface()`, and `qmc_hdlc_ioctl()`.

Control flow: probe obtains a child QMC channel, verifies it is in HDLC mode, reads current timeslot masks into `slot_map`, optionally gets and initializes a framer, allocates/registers an HDLC netdev, and installs HDLC attach/xmit ops. Open powers on the framer, registers carrier notifier, opens HDLC, configures QMC HDLC parameters, queues RX descriptors, starts the channel, and starts the netdev queue. RX completion unmaps DMA, handles QMC error flags, strips CRC, submits the SKB, and requeues the descriptor. TX maps the SKB, submits it to QMC, advances the ring, and wakes the queue on completion.

State and persistence: state is in memory and QMC/framer hardware. TX descriptors hold SKBs until completion. RX descriptors are continuously recycled. `slot_map` caches the user-visible compact timeslot map. `is_crc32` is selected by HDLC attach parity. There is no persistent storage.

Dependencies and integration points: depends on `soc/fsl/qe/qmc.h`, DMA mapping, generic HDLC, TE1 WAN ioctls, generic framer APIs, notifier chains, mutex/spinlock helpers, and platform/OF matching for `fsl,qmc-hdlc`.

Risks: RX requeue failure after completion leaves fewer active descriptors and only increments errors. Timeslot translation assumes TX/RX availability masks match and that compact slot maps fit 32 bits. Framer set-interface can fail after QMC timeslots were already changed, leaving partial configuration. TX queue capacity depends on callbacks freeing descriptors; missing completions stop progress.

Test signals: probe with and without optional framer, QMC mode mismatch, timeslot translation round trips, E1/T1 ioctl get/set while down, open/close cleanup after partial RX queueing, CRC16 and CRC32 attach modes, RX error counters for overflow/unaligned/CRC/abort flags, TX descriptor exhaustion/wakeup, carrier notifier behavior, and DMA mapping failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/fsl_qmc_hdlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.c

Purpose: Freescale QUICC Engine UCC Fast HDLC driver. It programs UCC Fast, optional TDM/SI routing, MURAM parameter RAM, DMA buffer descriptor rings, NAPI processing, generic HDLC netdev operations, and suspend/resume state restoration.

Important APIs, types, and functions: major functions are `uhdlc_init()`, `ucc_hdlc_tx()`, `hdlc_tx_done()`, `hdlc_rx_done()`, `ucc_hdlc_poll()`, `ucc_hdlc_irq_handler()`, `uhdlc_ioctl()`, `uhdlc_open()`, `uhdlc_close()`, `ucc_hdlc_attach()`, `uhdlc_suspend()`, `uhdlc_resume()`, `uhdlc_memclean()`, `hdlc_map_iomem()`, `ucc_hdlc_probe()`, and `ucc_hdlc_remove()`. It uses `utdm_primary_info` defaults and `struct ucc_hdlc_private` from the header.

Control flow: probe parses DT UCC index, clocks, register resources, optional TDM/loopback/HDLC bus flags, maps SI/SIRAM when needed, initializes hardware and descriptor rings through `uhdlc_init()`, allocates an HDLC netdev, attaches NAPI, and registers it. Open requests IRQ, issues QE init commands, enables UCC RX/TX and optional TDM port, enables NAPI, starts queue, then calls `hdlc_open()`. IRQ masks events and schedules NAPI. Poll processes TX completions and RX frames, then reenables interrupts. Close disables NAPI, gracefully stops TX/RX, disables TDM/UCC, frees IRQ, stops queue, and closes HDLC.

State and persistence: state is in allocated private memory, coherent DMA BD rings/buffers, MURAM parameter RAM, UCC registers, optional TDM mappings, SKB pointer arrays, NAPI state, and PM backup fields. No disk persistence exists. Suspend stores GUMR/GUEMR, parameter RAM, and clock mux registers; resume restores them and rebuilds descriptors.

Dependencies and integration points: depends on QUICC Engine APIs (`qe_issue_cmd`, `qe_muram_alloc`, `ucc_fast_init`, `ucc_tdm_init`), OF platform parsing, DMA coherent allocation, generic HDLC, NAPI, netdevice queue accounting, and optional PM.

Risks: cleanup is complex; `ucc_hdlc_remove()` does not unregister/free the netdev in the visible code before freeing private state, which is a notable lifecycle risk if not handled elsewhere. `uhdlc_init()` allocates `riptr`/`tiptr` local MURAM offsets but only stores them in parameter RAM for later cleanup. RX allocation failure in `hdlc_rx_done()` returns before recycling the current BD. Probe has multiple mappings and allocations with different cleanup labels. PM resume rebuilds rings and can lose in-flight packets.

Test signals: DT probe for valid/invalid UCC numbers and clocks, TDM and non-TDM modes, loopback and HDLC bus modes, open/close cycles, NAPI RX/TX under load, raw/PPP/Ethernet packet paths, parity/encoding attach validation, RX BD error counters, TX underrun/carrier restart, suspend/resume while interface is running, and remove/unbind leak tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.h

Purpose: private definitions for the Freescale QUICC Engine UCC HDLC driver. It captures the hardware parameter RAM layout, driver-private runtime state, ring sizes, buffer sizing, CRC defaults, address/header constants, and event masks.

Important APIs, types, and functions: `struct ucc_hdlc_param` mirrors UCC HDLC parameter RAM fields in big-endian hardware order. `struct ucc_hdlc_private` carries UCC/TDM handles, netdev, NAPI, register pointers, DMA buffers, BD rings, SKB arrays, ring indices, configuration flags, locks, and PM backup state. Macros include `UCCE_HDLC_RX_EVENTS`, `UCCE_HDLC_TX_EVENTS`, `TX_BD_RING_LEN`, `RX_BD_RING_LEN`, `MAX_RX_BUF_LENGTH`, `MAX_FRAME_LENGTH`, `HDLC_HEAD_LEN`, `HDLC_CRC_SIZE`, `CRC_16BIT_MASK`, and default HDLC/PPP address/header constants.

Control flow: no executable flow. The C file uses these definitions to allocate rings, program parameter RAM, classify interrupt events, prepend/strip headers, compute ring wrap masks, and restore PM state.

State and persistence: defines in-memory and MURAM state structures only. Hardware register/parameter contents persist only while the device is powered or until reinitialized.

Dependencies and integration points: includes QUICC Engine headers for `ucc_fast`, `ucc_tdm`, `qe_bd`, and register definitions. The netdev/HDLC-facing state is intentionally private to `fsl_ucc_hdlc.c`.

Risks: ring modulo macros assume power-of-two ring sizes. `struct ucc_hdlc_param` layout must exactly match hardware. Fixed buffer sizes constrain max frame behavior. PM backup fields are compiled only with `CONFIG_PM`, so non-PM code must not touch them.

Test signals: structure offset/size review against QE documentation, ring wrap tests, max-frame tests, CRC/header behavior for raw and PPP modes, and PM builds with and without `CONFIG_PM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/fsl_ucc_hdlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64570.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hd64570.c

Purpose: reusable Hitachi HD64570 SCA support code for board-specific synchronous HDLC WAN drivers. It manages SCA descriptor rings in shared/windowed RAM, MSCI/DMA setup, interrupt service, carrier detection, generic HDLC attach/open/close/xmit helpers, and optional RAM/ring debugging.

Important APIs, types, and functions: expects board-provided `card_t`, `port_t`, `sca_in/out`, window helpers, and port lookup macros. Core helpers include `sca_intr_status()`, `sca_init_port()`, `sca_msci_intr()`, `sca_rx_intr()`, `sca_tx_intr()`, `sca_intr()`, `sca_set_port()`, `sca_open()`, `sca_close()`, `sca_attach()`, `sca_xmit()`, optional `sca_detect_ram()`, and `sca_init()`. Descriptor and register constants come from `hd64570.h`.

Control flow: board code initializes card-wide wait states/DMA, initializes each port's descriptor rings and DMA registers, configures MSCI mode/CRC/encoding/clocking on open, enables interrupts and DMA, and then uses `sca_intr()` to dispatch MSCI, RX DMA, and TX DMA events. RX drains descriptors until hardware current descriptor catches up, copies from possibly window-crossing RAM into SKBs, and passes frames to HDLC. TX copies SKB data into card RAM, marks descriptor EOM, advances EDAL, enables DMA, and stops queue if the future descriptor is occupied.

State and persistence: per-port indices `rxin`, `txin`, `txlast`, `rxpart`, encoding/parity/settings, and descriptor status bytes represent live state. Packet descriptors and buffers live in card RAM. No persistence beyond device runtime.

Dependencies and integration points: integrates with generic HDLC, netdevice carrier and stats, SCA hardware access macros supplied by board drivers, and optional debug macros. It supports two logical channels and windowed memory paging.

Risks: relies on board-specific macros and compile-time options such as `PAGE0_ALWAYS_MAPPED` and `NEED_SCA_MSCI_INTR`, so behavior varies by includer. RX alloc failure drops without descriptor recycling in `sca_rx()` but caller advances descriptor state. Window switching must restore descriptor page correctly. `BUG_ON()` in TX can crash if queue discipline assumptions fail.

Test signals: board-level probe/open/close, two-channel interrupt dispatch, RX frames crossing memory windows, RX error flags and partial frames, TX queue stop/wake, carrier changes on DCD, baud-rate calculation, all supported encodings/parities, and RAM detection when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64570.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64570.h -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hd64570.h

Purpose: register map and descriptor definitions for Hitachi HD64570 SCA chips.

Important APIs, types, and functions: defines global control/wait/interrupt registers, MSCI per-channel offsets, timer offsets, DMA channel offsets, register-address helper macros such as `DSR_RX()`/`DIR_TX()`/`DCR_RX()`, packed `pkt_desc`, descriptor status bits, DMA interrupt/status bits, DMA master enable, MSCI commands, mode/CRC/encoding constants, modem status bits, interrupt enables, and clock-source values.

Control flow: no executable flow. `hd64570.c` uses these constants to program HDLC mode, DMA chain mode, descriptor rings, interrupt masks, carrier status, and baud-rate generator settings.

State and persistence: definitions only. Hardware state resides in SCA registers and descriptor memory programmed by callers.

Dependencies and integration points: consumed by HD64570 board-support code. It assumes mode 0/1 address layout and notes address XOR requirements for modes 2/3.

Risks: packed descriptor layout must match hardware byte ordering and alignment. Register offsets are mode-specific; using them with the wrong bus mode would break access. Several constants are shared conceptually with HD64572 but are not identical.

Test signals: compile users of the header, compare offsets with HD64570 manual, descriptor layout checks, mode/encoding/parity register programming tests, and interrupt mask/status validation on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64570.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64572.c -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hd64572.c

Purpose: reusable HD64572 SCA-II support code for synchronous HDLC WAN cards. It is similar in role to `hd64570.c` but targets the SCA-II register map, direct mapped RAM, 32-bit descriptor pointers, and NAPI-based interrupt processing.

Important APIs, types, and functions: uses board-defined `card_t`, `port_t`, `get_port()`, and netdev embedding conventions. Main helpers are `sca_init_port()`, `sca_msci_intr()`, `sca_rx_done()`, `sca_tx_done()`, `sca_poll()`, `sca_intr()`, `sca_set_port()`, `sca_open()`, `sca_close()`, `sca_attach()`, `sca_xmit()`, `sca_detect_ram()`, and `sca_init()`. It defines MMIO access wrappers and `NAPI_WEIGHT`.

Control flow: port init builds RX/TX descriptor rings in card RAM, resets DMA channels, sets current/error descriptor pointers, enables RX DMA, configures TX DMA, initializes carrier, and registers NAPI. IRQ checks ISR0 for each port, disables that port's interrupts, and schedules NAPI. Poll handles MSCI DCD change, TX completion, and RX completion, then reenables interrupts when under budget. Open programs MSCI HDLC mode, CRC, encoding, idle/underrun behavior, DMA thresholds, clocks, enables RX/TX, enables NAPI, carrier, and queue. TX copies the SKB into RAM, marks descriptor EOM, advances EDAL, enables DMA, and frees the SKB.

State and persistence: runtime state is per-port descriptor indices, NAPI state, carrier state, clock settings, encoding/parity, RX partial-frame flag, card RAM descriptors/buffers, and SCA-II registers. No storage persistence exists.

Dependencies and integration points: depends on generic HDLC, netdevice/NAPI APIs, MMIO accessors, and board-specific definitions. Register and status definitions come from `hd64572.h`.

Risks: the RX init writes EDAL using `card->tx_ring_buffers - 1` for the RX path, which is suspicious if RX/TX ring sizes differ. TX uses `BUG_ON()` for descriptor availability. RX allocation failure drops the frame without incrementing `received`, and descriptor advancement still occurs. Interrupt masks are hard-coded bit patterns and require hardware validation. Direct RAM copies assume `HDLC_MAX_MRU`-sized buffers and valid card memory sizing.

Test signals: NAPI scheduling under RX/TX load, DCD carrier changes, RX error and partial-frame handling, TX underrun counters, ring sizes where RX and TX differ, queue stop/wake behavior, baud-rate calculation, CRC32 and CRC16 modes, RAM detection, and interrupt mask reenable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64572.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64572.h -->
# sources/distributed-fs/ceph-client/drivers/net/wan/hd64572.h

Purpose: register map, descriptor structures, and programming constants for Hitachi/Renesas HD64572 SCA-II chips.

Important APIs, types, and functions: defines wait/interrupt registers, channelized register macros (`M_REG`, `DRX_REG`, `DTX_REG`, timer/status macros), MSCI registers, timer registers, DMA global and channel registers, `pcsca_bd_t`, `pkt_desc`, descriptor status bits, status counters, interrupt constants, mode/CRC/encoding/loopback values, control bits, clock-source values, command codes, status bits, interrupt enables, frame interrupt bits, DMA status/interrupt/mode/command bits, and DMA priority bits.

Control flow: no executable flow. `hd64572.c` uses the constants for descriptor-ring setup, DMA control, MSCI HDLC configuration, interrupt handling, NAPI polling, carrier detection, and clock programming.

State and persistence: definitions only. The represented state lives in SCA-II registers and card RAM descriptors.

Dependencies and integration points: consumed by SCA-II board-support code. It reflects CPU modes 0 and 2 and carries legacy Cyclades/PC300 history in comments.

Risks: there is a duplicate `DARBH` definition for RX and TX comments, which is harmless preprocessor-wise but confusing. The header mixes older `pcsca_bd_t` and generic `pkt_desc` descriptor formats. Hard-coded bit constants must match the selected CPU/bus mode. Some names overlap with HD64570 but semantics and offsets differ.

Test signals: compile all includers, compare offsets against the HD64572 manual, descriptor layout/alignment checks, interrupt bitmask validation for both channels, CRC/encoding command programming, and DMA status/interrupt tests on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wan/hd64572.h -->
