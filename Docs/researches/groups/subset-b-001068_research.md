# subset-b-001068 Research

Grouped research for the listed Linux kernel Bluetooth and bus-driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_nokia.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_nokia.c

## Purpose
Implements the Nokia H4+ Bluetooth UART protocol as a `serdev` HCI UART device. It handles Nokia-specific packet types, GPIO wake/reset lines, runtime PM, controller negotiation, alive probing, firmware download, baud-rate switching, and registration of the resulting HCI device.

## Important APIs, Types, And Functions
The central state object is `struct nokia_bt_dev`, which embeds `struct hci_uart`, stores `serdev`, reset/wakeup GPIOs, system clock rate, RX/TX queues, negotiation completion, manufacturer/version IDs, and runtime TX/RX wake state. Protocol parsing uses `struct h4_recv_pkt` entries for normal H4 ACL/SCO/event frames plus Nokia negotiation, alive, and radio packet types. `nokia_proto` supplies the HCI UART callbacks: `open`, `close`, `recv`, `enqueue`, `dequeue`, `flush`, and `setup`. Probe is handled by `nokia_bluetooth_serdev_probe()`, which acquires GPIOs and `sysclk`, requests the host-wakeup IRQ, initializes the TX queue, sets word alignment, and calls `hci_uart_register_device()`.

## Control Flow
`nokia_setup()` disables flow control, takes a runtime PM reference, resets the controller, sends a negotiation packet, verifies liveness, downloads firmware, switches to the maximum baud rate, and installs Broadcom BDADDR handling for BCM2048 devices. Negotiation and alive packets are sent through `nokia_enqueue()` and waited on through `init_completion`; receive callbacks complete the same completion after validating payloads. Firmware is requested from `nokia/bcmfw.bin` or `nokia/ti1273.bin`, then HCI command records are replayed synchronously with `__hci_cmd_sync()`. Normal receive data is reassembled by `h4_recv_buf()`, and Nokia radio packets are converted into HCI events before being handed to `hci_recv_frame()`.

## State And Persistence
Persistent runtime state lives only in kernel memory: TX queue, partial RX skb, manufacturer/version IDs, BDADDR, init status, and wake flags. Hardware state is changed through GPIOs, UART baud/flow control, runtime PM references, and firmware commands. There is no disk persistence beyond firmware files loaded through the firmware API.

## Dependencies And Integration Points
The driver depends on `serdev`, GPIO descriptors named `reset`, `host-wakeup`, and `bluetooth-wakeup`, a `sysclk`, runtime PM, `hci_uart.h`, and `btbcm` for BCM2048 address programming. It binds to `nokia,h4p-bluetooth` device-tree nodes and integrates with the Bluetooth core through the HCI UART protocol table.

## Risks And Test Signals
Risks are mostly ordering and hardware-timing sensitive: missing CTS, wrong GPIO polarity, unsupported manufacturer IDs, incomplete firmware records, bad packet alignment, and runtime PM reference imbalance during wake transitions. Useful signals are successful `hci_register_dev`, negotiation/alive debug logs, firmware command completion, clean suspend/resume with host wake IRQ activity, and traffic tests at the final baud rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_nokia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_qca.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_qca.c

## Purpose
Implements Qualcomm Bluetooth HCI UART support, including H4 framing plus Qualcomm HCI In-Band Sleep, SoC-specific power sequencing, firmware/NVM setup, baud-rate negotiation, subsystem-restart memory dumps, debugfs counters, serdev probing, and suspend/resume behavior.

## Important APIs, Types, And Functions
`struct qca_data` is the protocol runtime state: RX skb, TX queues, IBS wait queue, memdump queue, IBS spinlock/state, clock votes, timers, ordered workqueue, completions, flags, memdump state, firmware/controller IDs, and debug counters. `struct qca_serdev` stores serdev-side power/control resources such as `bt_en`, `sw_ctrl`, `susclk`, SoC type, regulator/power-sequencer data, UART speeds, broken-BDADDR marker, HFP offload support, and optional firmware names. The exported protocol is `qca_proto`, and the serdev driver is `qca_serdev_driver`. Major helpers include `qca_open()`, `qca_close()`, `qca_enqueue()`, `qca_recv()`, `qca_set_speed()`, `qca_setup()`, `qca_power_on()`, `qca_power_off()`, `qca_hw_error()`, and `qca_controller_memdump()`.

## Control Flow
Open allocates `qca_data`, requires UART flow control, creates queues/timers/work, and initializes IBS states as asleep. Transmit prepends the HCI packet type; if IBS is disabled or suspend is active it queues directly, otherwise it either sends while awake, queues while waking, or starts a WAKE_IND handshake. Device WAKE/SLEEP/ACK bytes are parsed as synthetic H4 receive packet types and drive `device_want_to_wakeup()`, `device_want_to_sleep()`, and `device_woke_up()`. Setup disables IBS during initialization, powers the controller, reads SoC version, sets init/operating speeds, downloads firmware/NVM through `qca_uart_setup()`, enables quirks and debugfs, registers coredump callbacks, and retries power-on up to `MAX_INIT_RETRIES`.

## State And Persistence
State is volatile kernel state plus hardware regulator/GPIO/clock/UART state. The driver tracks many flags: `QCA_IBS_DISABLED`, vendor-event dropping, suspend, memdump collection, hardware error, SSR, BT off, ROM firmware, and debugfs creation. Memory dumps are streamed into the HCI devcoredump facility; firmware names are read from firmware-name properties but not persisted.

## Dependencies And Integration Points
The file depends on `btqca` vendor helpers, `hci_uart`, serdev, optional ACPI/OF matches, regulators, clocks, GPIOs, power sequencing, debugfs, devcoredump, and Bluetooth core quirks. It supports many compatible strings, including QCA2066, QCA6390, WCN3950/3988/399x/6750/6855/7850, and ACPI IDs. It also wires HFP non-HCI data path support for capable SoCs.

## Risks And Test Signals
Risk concentrates in concurrent state machines: IBS timers and workqueue, suspend waiting on RX sleep, SSR/memdump flag clearing, vendor-event dropping during baud changes, power-sequencer versus legacy regulator control, and non-persistent setup shutdown paths. Test signals include successful firmware setup, debugfs IBS counters changing as expected, suspend/resume without wake storms, coredump creation on forced crash, BT on/off cycles, max-speed property coverage, and probe on both OF and ACPI-described devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_qca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_serdev.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_serdev.c

## Purpose
Provides the shared `serdev` transport glue for Bluetooth HCI UART protocol drivers. It connects serdev RX/TX callbacks to `struct hci_uart_proto`, creates/registers `struct hci_dev`, and manages open/close, flushing, setup, and asynchronous writes.

## Important APIs, Types, And Functions
The main exported APIs are `hci_uart_register_device_priv()` and `hci_uart_unregister_device()`. The serdev callbacks are `hci_uart_receive_buf()` and `hci_uart_write_wakeup()`. HCI device callbacks include `hci_uart_open()`, `hci_uart_close()`, `hci_uart_flush()`, `hci_uart_send_frame()`, and `hci_uart_setup()`. TX uses `hci_uart_write_work()`, `hu->tx_skb`, and the protocol `dequeue()` callback to drain frames through `serdev_device_write_buf()`.

## Control Flow
Registration installs serdev client ops, initializes the protocol lock, opens the serdev port, calls the protocol `open()`, marks the protocol ready, allocates an HCI device, sets bus/callbacks/quirks, and registers it unless `HCI_UART_INIT_PENDING` defers registration. Sending from Bluetooth core calls the protocol `enqueue()` and schedules TX wakeup. The write worker loops until no wakeup was raced in, writes as much of each skb as serdev accepts, stores a partially written skb if needed, updates TX counters, and frees completed frames. Receive callbacks ignore data until the protocol is ready, then call protocol `recv()` and update RX byte counters.

## State And Persistence
State lives in the caller-owned `struct hci_uart`: flags, HCI device, protocol pointer, protocol private data, pending TX skb, TX state bits, init/oper speeds, alignment, and work items. There is no persistence; all state is created on probe/registration and destroyed on unregister.

## Dependencies And Integration Points
This file is the bridge between `drivers/bluetooth` protocol implementations and the serdev subsystem. It depends on Bluetooth core HCI registration and quirks, `struct hci_uart_proto` from `hci_uart.h`, and serdev write/flush/open/close semantics. It also supports optional raw/external-config/no-suspend-notifier HCI quirks through flags populated by protocol drivers.

## Risks And Test Signals
Risks include partial-write handling, TX wakeup races, registering devices before vendor setup is ready, closing serdev too early for non-persistent setup devices, and protocol callbacks that assume stronger locking than provided. Test signals are reliable HCI device registration/unregistration, stable TX/RX counters, no leaked `tx_skb`, working suspend notifier quirks, and successful vendor protocol setup through serdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_serdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_uart.h -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_uart.h

## Purpose
Defines the common HCI UART line-discipline and serdev protocol interface used by Bluetooth UART transports. It centralizes protocol IDs, ioctl numbers, flags, core structures, and H4 receive packet descriptors.

## Important APIs, Types, And Functions
`struct hci_uart_proto` is the protocol vtable for open/close/flush/setup/set_baudrate/recv/enqueue/dequeue. `struct hci_uart` stores tty/serdev handles, HCI device pointer, protocol flags, work items, protocol pointer, lock, private data, TX state, speed settings, and alignment/padding. Public functions include protocol registration (`hci_uart_register_proto()`, `hci_uart_unregister_proto()`), serdev device registration (`hci_uart_register_device_priv()`, `hci_uart_register_device()`, `hci_uart_unregister_device()`), TX helpers, init readiness, baud/flow-control helpers, and speed setters. `struct h4_recv_pkt` and the `H4_RECV_*` macros describe packet type, header length, length offset/size, maximum length, and receive callback.

## Control Flow
This header does not execute control flow, but it defines the contract used by both tty line discipline and serdev implementations. Protocol modules fill `struct hci_uart_proto`; core HCI UART code registers protocols by ID and calls protocol callbacks during open, setup, RX parsing, enqueue/dequeue, and close. H4-derived drivers pass arrays of `struct h4_recv_pkt` to `h4_recv_buf()` for reassembly.

## State And Persistence
It declares in-memory state only. Flag bits distinguish protocol set/registered/ready/init states and HCI device quirks such as raw, reset-on-init, init-pending, external-config, and vendor-detect.

## Dependencies And Integration Points
The header is consumed by all HCI UART protocol files. It depends on Bluetooth core types such as `struct hci_dev`, `struct sk_buff`, and HCI packet constants, plus tty/serdev abstractions. Conditional declarations mirror Kconfig options for H4, BCSP, LL, ATH3K, 3WIRE, Intel, BCM, QCA, AG6XX, MRVL, and AML protocol modules.

## Risks And Test Signals
Interface risk comes from changing IDs, flag meanings, or callback semantics because many protocol modules depend on them. Test signals are build coverage across enabled/disabled protocol configs, H4 parser tests using ACL/SCO/event/ISO frames, and runtime smoke tests for both tty and serdev Bluetooth UART devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_vhci.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_vhci.c

## Purpose
Implements the Bluetooth virtual HCI misc device `/dev/vhci`. User space can create virtual HCI controllers, inject HCI frames into the Bluetooth core, read frames emitted by the core, and use debugfs controls for suspend, wakeup, Microsoft/AOSP extension testing, and devcoredump testing.

## Important APIs, Types, And Functions
`struct vhci_data` holds the HCI device, read waitqueue, outgoing read queue, open mutex, open timeout work, suspend work, suspend/wakeup/debug capability state, and initialization counter. HCI callbacks are `vhci_open_dev()`, `vhci_close_dev()`, `vhci_flush()`, `vhci_send_frame()`, `vhci_wakeup()`, and `vhci_setup()`. Character-device operations are `vhci_open()`, `vhci_read()`, `vhci_write()`, `vhci_poll()`, and `vhci_release()`. Debugfs operations expose `force_suspend`, `force_wakeup`, `msft_opcode`, `aosp_capable`, and `force_devcoredump`.

## Control Flow
Opening `/dev/vhci` allocates `vhci_data`, initializes queues/work, and schedules a one-second default device creation timeout. User writes with packet type `HCI_VENDOR_PKT` cancel the timeout and create a controller with opcode bits selecting external config and raw mode; normal HCI event/ACL/SCO/ISO writes inject frames into `hci_recv_frame()`. HCI frames sent by the Bluetooth core are prefixed with packet type, queued to `readq`, and woken for user-space reads after initialization. Release unregisters and frees the HCI device, removes debugfs files, drains queues, and frees private state.

## State And Persistence
All state is per open file descriptor and per virtual HCI device. Debugfs toggles are runtime-only. The module parameter `amp` exists but is not used in the shown code path. There is no persistent storage; devcoredump data goes through the kernel devcoredump facility.

## Dependencies And Integration Points
The file integrates with the miscdevice subsystem, Bluetooth core HCI registration, debugfs, waitqueues, workqueues, poll/read/write file operations, optional `CONFIG_BT_MSFTEXT`, optional `CONFIG_BT_AOSPEXT`, and optional `CONFIG_DEV_COREDUMP`. It is a key test hook for user-space Bluetooth stacks and kernel HCI behavior.

## Risks And Test Signals
Risks include userspace ABI regressions, failure to handle malformed packet lengths/types, races between auto-creation and explicit creation, debugfs lifetime issues, and queue wakeup mistakes that hang readers. Test signals are `/dev/vhci` open/read/write/poll behavior, virtual controller registration, injected frame delivery, debugfs suspend/resume effects, and forced devcoredump done/abort/timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/hci_vhci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/virtio_bt.c -->
# sources/distributed-fs/ceph-client/drivers/bluetooth/virtio_bt.c

## Purpose
Implements a generic virtio Bluetooth HCI driver. It maps HCI packets to two virtqueues, registers an HCI device with optional vendor-specific setup behavior, and supports virtio feature bits for vendor HCI, Microsoft extensions, AOSP extensions, and v2 config layout.

## Important APIs, Types, And Functions
`struct virtio_bluetooth` stores the virtio device, TX/RX virtqueues, RX work item, and HCI device. Core helpers are `virtbt_add_inbuf()`, `virtbt_open_vdev()`, `virtbt_close_vdev()`, `virtbt_send_frame()`, `virtbt_rx_work()`, `virtbt_tx_done()`, `virtbt_rx_done()`, `virtbt_probe()`, and `virtbt_remove()`. Vendor setup functions include Zephyr build-info/BDADDR, Intel read-version/BDADDR, Realtek ROM-version, and a generic reset shutdown callback.

## Control Flow
Probe requires `VIRTIO_F_VERSION_1`, checks that the config type is primary, allocates state, finds TX/RX virtqueues, allocates and configures an HCI device, applies optional vendor setup callbacks and quirks based on virtio config, registers the HCI device, marks the virtio device ready, and posts the initial RX buffer. Sending prepends the HCI packet type and queues the skb as an outbuf. RX completion schedules work, which gets one used RX buffer, validates length and packet type/header size, hands valid frames to `hci_recv_frame()`, replenishes the RX buffer, and kicks the RX queue.

## State And Persistence
State is volatile: virtqueue buffers, pending RX work, and HCI device metadata. Vendor features are read from virtio configuration and reflected in HCI callbacks/quirks. No state is persisted.

## Dependencies And Integration Points
The driver binds to `VIRTIO_ID_BT`, uses UAPI `virtio_bt` config/vendor constants, the virtio queue API, and Bluetooth core HCI registration. It also integrates with Zephyr, Intel, and Realtek vendor HCI command conventions when the device advertises vendor HCI support.

## Risks And Test Signals
Risks include failing to replenish RX buffers, accepting malformed virtqueue lengths, feature/config version mismatches, missing cleanup on probe error, and vendor-specific setup commands blocking registration. Test signals include virtio probe/remove cycles, frame loopback through TX/RX queues, malformed packet rejection logs, vendor feature negotiation, and HCI registration with correct bus type and quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/virtio_bt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/bus/Kconfig

## Purpose
Defines Kconfig entries for the kernel bus-driver menu. It selects architecture-specific SoC interconnect, external bus, firewall, configuration, and management-complex bus drivers and includes subordinate Kconfig files for fsl-mc and MHI.

## Important APIs, Types, And Functions
The file is declarative Kconfig. Key symbols in this subset include `ARM_CCI`, `ARM_CCI400_COMMON`, `ARM_CCI400_PORT_CTRL`, `ARM_INTEGRATOR_LM`, `BRCMSTB_GISB_ARB`, `DA8XX_MSTPRI`, and the included `FSL_MC_BUS` subtree. Other symbols cover MOXTET, HiSilicon LPC, i.MX, IXP4xx, MIPS CDMM, MVEBU, OMAP, Qualcomm, STM32, Allwinner, Tegra, TI, TS-NBUS, UniPhier, and Versatile Express.

## Control Flow
Kconfig evaluation controls build inclusion. Dependencies restrict symbols to relevant architectures or `COMPILE_TEST`, `select` enables helper subsystems such as `GENERIC_MSI_IRQ`, `REGMAP`, or `OF_DYNAMIC`, and `default` expresses platform defaults. The `source` statements include `drivers/bus/fsl-mc/Kconfig` and `drivers/bus/mhi/Kconfig`.

## State And Persistence
The state is the generated kernel configuration. It persists through `.config` and derived build artifacts, not through runtime code.

## Dependencies And Integration Points
This file connects architecture/platform configuration to `drivers/bus/Makefile`. The fsl-mc section depends on OF and supported architectures, MHI has its own included configuration, and individual entries coordinate with platform device-tree support and subsystem dependencies.

## Risks And Test Signals
Risks include incorrect dependency constraints, missing `select`s, silent build exclusion on valid platforms, and overly broad defaults that build unusable drivers. Test signals are `allyesconfig`, `allmodconfig`, architecture defconfigs, `COMPILE_TEST` builds, and confirming Makefile objects appear only under the intended symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/bus/Makefile

## Purpose
Maps bus-driver Kconfig symbols to built objects and subdirectories. It is the build-system companion to `drivers/bus/Kconfig`.

## Important APIs, Types, And Functions
The file uses kernel kbuild `obj-$(CONFIG_...)` assignments. In this subset, it builds `arm-cci.o`, `arm-integrator-lm.o`, `brcmstb_gisb.o`, `da8xx-mstpri.o`, and descends into `fsl-mc/` when `CONFIG_FSL_MC_BUS` is enabled. It always descends into `mhi/` with `obj-y += mhi/`, leaving that subtree to its own Kconfig and Makefile decisions.

## Control Flow
Kbuild expands each `obj-*` variable based on the resolved kernel configuration. Built-in, module, or omitted status follows the selected symbol type. Directory recursion gives sub-Makefiles control of composite objects such as the fsl-mc bus driver.

## State And Persistence
There is no runtime state. The output is persisted as build artifacts in the kernel build tree.

## Dependencies And Integration Points
This file must remain synchronized with `drivers/bus/Kconfig` and with source filenames. It integrates with kbuild, architecture defconfig choices, and subdirectory Makefiles for fsl-mc and MHI.

## Risks And Test Signals
Risks include stale object names, missing objects for new symbols, recursive directory inclusion under the wrong condition, or module/built-in mismatches. Test signals are clean kernel builds across relevant configs and checking that selected symbols produce expected `.o` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/arm-cci.c -->
# sources/distributed-fs/ceph-client/drivers/bus/arm-cci.c

## Purpose
Provides ARM Cache Coherent Interconnect support, especially CCI-400 port control for low-level power management and platform population for CCI PMU child devices.

## Important APIs, Types, And Functions
Global initialization stores `cci_ctrl_base` and `cci_ctrl_phys`. Under `CONFIG_ARM_CCI400_PORT_CTRL`, `struct cci_ace_port` describes ACE/ACE-Lite ports, `struct cpu_port` caches logical CPU to CCI port mapping, and exported APIs include `cci_ace_get_port()`, `cci_disable_port_by_cpu()`, `__cci_control_port_by_device()`, `__cci_control_port_by_index()`, and `cci_probed()`. `cci_enable_port_for_self()` is naked ARM assembly for MMU-off cluster bring-up.

## Control Flow
`early_initcall(cci_init)` probes the first matching CCI node, maps the control block, parses child `arm,cci-400-ctrl-if` nodes, maps port registers, classifies ACE versus ACE-Lite ports, caches CPU MPIDR-to-port associations, and flushes cache lines so low-level noncoherent code can use the data. `core_initcall(cci_platform_init)` registers a platform driver whose probe only populates child devices once `cci_probed()` succeeds. Port control writes snoop/DVM enable bits and busy-waits on the CCI status register.

## State And Persistence
Runtime state is static and read-mostly after initialization: control MMIO address, port descriptors, port count, and CPU port cache. Hardware state is the port enable/disable state in CCI registers. There is no persistent software state.

## Dependencies And Integration Points
The driver depends on device tree matching for CCI-400/500/550, OF address parsing, platform population, ARM cache flush helpers, SMP MPIDR mapping, and optional PMU auxdata. It is called by low-level CPU/cluster power-management paths where normal locking may not be available.

## Risks And Test Signals
Risks are severe because port control runs in fragile power states: wrong MPIDR mapping, bad device-tree `interface-type`, missing cache maintenance, polling forever, or using general port control on CPU ACE ports. Test signals include early boot probe logs, CPU hotplug/idle cluster transitions, CCI PMU child device creation, and stress testing suspend/resume on CCI-400 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/arm-cci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/arm-integrator-lm.c -->
# sources/distributed-fs/ceph-client/drivers/bus/arm-integrator-lm.c

## Purpose
Implements the ARM Integrator AP Logical Module bus driver. It discovers installed logic modules through the Integrator system controller and populates matching device-tree child nodes for occupied slots.

## Important APIs, Types, And Functions
`integrator_ap_lm_probe()` is the platform probe entry point. It finds the `arm,integrator-ap-syscon` regmap, reads `INTEGRATOR_SC_DEC_OFFSET`, and loops over four slot bits. `integrator_lm_populate()` computes the expansion slot base address and calls `of_platform_default_populate()` for child nodes whose first resource starts at that slot base.

## Control Flow
Probe obtains the syscon regmap, reads the decode register, then for each detected module bit calls `integrator_lm_populate()`. Population scans available children below the LM bus node, resolves child address resources, compares against `0xc0000000 + slot * 0x10000000`, and populates only the matching module subtree.

## State And Persistence
The driver keeps no long-lived private state. It reads hardware presence bits and creates platform child devices, which then persist in the Linux device model until driver removal or reboot.

## Dependencies And Integration Points
It depends on OF, syscon/regmap, platform bus population, and the `arm,integrator-ap-lm` compatible. It integrates with child device-tree descriptions for actual devices hosted on the logical modules.

## Risks And Test Signals
Risks include stale/missing syscon nodes, wrong address resources in child nodes, slot-bit interpretation errors, and duplicate/missing child population. Test signals are module detection logs, created platform devices under the LM bus, and child driver probes for each installed module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/arm-integrator-lm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/brcmstb_gisb.c -->
# sources/distributed-fs/ceph-client/drivers/bus/brcmstb_gisb.c

## Purpose
Implements the Broadcom STB GISB arbiter driver. It decodes internal bus timeout, target-abort, breakpoint, die, and panic errors into useful address/master diagnostics and exposes the arbiter timeout through sysfs.

## Important APIs, Types, And Functions
`struct brcmstb_gisb_arb_device` stores MMIO base, SoC-specific register offset table, endian mode, mutex, global list node, valid master mask, master names, and suspend-saved timeout. Helpers `gisb_read()`, `gisb_write()`, `gisb_read_address()`, and `gisb_read_bp_address()` abstract SoC register layouts. Error decode paths include `brcmstb_gisb_arb_decode_addr()`, IRQ handlers for timeout/target abort/breakpoint, MIPS bus error handling, and panic/die notifier callbacks. Sysfs is `gisb_arb_timeout`.

## Control Flow
Probe maps the MMIO resource, chooses an offset table from the OF compatible, requests required timeout and target-abort IRQs plus optional breakpoint IRQ, parses master masks/names, adds the device to a global list, installs the MIPS bus error handler when applicable, and registers panic/die notifiers for the first device. IRQ and notifier paths read captured status/address/master registers, print a critical diagnostic, then clear the capture register. Suspend stores the timeout register; noirq resume restores it before interrupt handling can observe stale values.

## State And Persistence
Runtime state includes the global list of arbiters, per-device master naming, and saved timeout. Hardware state includes timeout and captured error registers. Sysfs writes change the live hardware timeout and are not persistently stored by the driver.

## Dependencies And Integration Points
The driver depends on platform/OF probing, Broadcom compatible strings, interrupt delivery, optional MIPS trap integration, panic/die notifier chains, sysfs attribute groups, and PM sleep callbacks.

## Risks And Test Signals
Risks include incorrect offset tables for a compatible, endian mismatches, optional register absence, not clearing the right capture register, notifier ordering during panic, and invalid timeout values. Test signals are sysfs timeout read/write, injected GISB timeout/TEA/breakpoint diagnostics with decoded master names, suspend/resume retaining timeout, and MIPS bus error fixup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/brcmstb_gisb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/da8xx-mstpri.c -->
# sources/distributed-fs/ceph-client/drivers/bus/da8xx-mstpri.c

## Purpose
Programs TI DA8xx master peripheral priority registers for boards that need fixed bus-priority tuning. The current table targets DA850 LCDK to avoid LCD controller FIFO underflow by adjusting LCDC and EDMA priorities.

## Important APIs, Types, And Functions
`struct da8xx_mstpri_descr` maps each master to register offset, shift, and mask. `struct da8xx_mstpri_priority` stores the desired priority value, and `struct da8xx_mstpri_board_priorities` ties a board compatible string to a priority list. `da8xx_mstpri_get_board_prio()` selects the board table using `of_machine_is_compatible()`, and `da8xx_mstpri_probe()` maps registers and applies each masked update.

## Control Flow
Probe maps the MSTPRI resource, locates a board-specific priority list, then for each requested change validates the register offset against resource size, reads the register, clears the target field, inserts the new priority value, and writes the register back.

## State And Persistence
The driver keeps no private runtime state. Its only lasting effect is programming SoC priority registers during probe; values persist until hardware reset or later firmware/kernel writes.

## Dependencies And Integration Points
It depends on platform/OF probing, DA8xx memory-mapped priority registers, and machine compatible strings such as `ti,da850-lcdk`. It indirectly integrates with display and DMA drivers by shaping bus arbitration.

## Risks And Test Signals
Risks include hard-coded policy becoming stale, missing board table entries, incorrect bitfield definitions, and changing arbitration in ways that harm other peripherals. Test signals include clean probe on supported boards, no out-of-range warnings, stable LCD output under DMA load, and absence of tilcdc FIFO-underflow warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/da8xx-mstpri.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Kconfig

## Purpose
Defines Kconfig options for the Freescale/NXP DPAA2 Management Complex bus and its optional userspace support.

## Important APIs, Types, And Functions
`FSL_MC_BUS` enables the core QorIQ DPAA2 fsl-mc bus driver. It depends on OF and supported architectures or `COMPILE_TEST`, and selects `GENERIC_MSI_IRQ`. `FSL_MC_UAPI_SUPPORT` enables userspace interrogation/configuration support and depends on `FSL_MC_BUS`.

## Control Flow
Kconfig resolution controls whether the fsl-mc composite object and optional UAPI object are built. The main bus option gates discovery and binding of DPAA2 objects represented as Linux devices; UAPI support is layered on top.

## State And Persistence
The file contributes configuration state through `.config`; it has no runtime state.

## Dependencies And Integration Points
It is included by `drivers/bus/Kconfig` and consumed by `drivers/bus/fsl-mc/Makefile`. It connects DPAA2 object discovery to OF-described platforms and MSI interrupt infrastructure.

## Risks And Test Signals
Risks include excluding valid architectures, missing interrupt infrastructure selection, or enabling UAPI without the bus. Test signals are config dependency checks, compile-test builds, and boot-time fsl-mc bus discovery on Layerscape/DPAA2 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Makefile

## Purpose
Builds the Freescale/NXP Management Complex bus driver as a composite kbuild object and optionally builds the userspace support module.

## Important APIs, Types, And Functions
`mc-bus-driver-objs` combines `fsl-mc-bus.o`, `mc-sys.o`, `mc-io.o`, `dpbp.o`, `dpcon.o`, `dprc.o`, `dprc-driver.o`, `fsl-mc-allocator.o`, `fsl-mc-msi.o`, `dpmcp.o`, and `obj-api.o`. `obj-$(CONFIG_FSL_MC_BUS)` builds the composite object, and `obj-$(CONFIG_FSL_MC_UAPI_SUPPORT)` adds `fsl-mc-uapi.o`.

## Control Flow
Kbuild links the listed objects into `mc-bus-driver.o` when `FSL_MC_BUS` is selected. The order matters because the composite driver contains command APIs, bus registration, MSI support, resource allocation, and object drivers that are initialized together.

## State And Persistence
There is no runtime state in the Makefile; it produces build artifacts.

## Dependencies And Integration Points
It depends on `drivers/bus/fsl-mc/Kconfig` symbols and on the listed source files remaining present. It integrates core fsl-mc command APIs with Linux bus/driver registration and optional UAPI support.

## Risks And Test Signals
Risks include omitting a required object from the composite, stale filenames, or building UAPI support without core bus support. Test signals are successful link of `mc-bus-driver.o`, symbol availability for exported DPAA2 APIs, and module/built-in smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpbp.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpbp.c

## Purpose
Implements the DPAA2 Data Path Buffer Pool command API wrapper. It opens, closes, enables, disables, resets, and queries DPBP objects through the Management Complex portal.

## Important APIs, Types, And Functions
Exported functions are `dpbp_open()`, `dpbp_close()`, `dpbp_enable()`, `dpbp_disable()`, `dpbp_reset()`, and `dpbp_get_attributes()`. They use `struct fsl_mc_command`, command-specific parameter layouts from `fsl-mc-private.h`, and public `struct dpbp_attr`.

## Control Flow
Each function builds an MC command header with `mc_encode_cmd_header()`, fills little-endian command parameters when needed, calls `mc_send_command()`, and decodes response fields. `dpbp_open()` returns a token for later commands; `dpbp_get_attributes()` decodes BPID and object ID.

## State And Persistence
The file stores no local state. Object state lives in MC firmware and is addressed through tokens returned by open calls.

## Dependencies And Integration Points
It depends on `linux/fsl/mc.h`, private command IDs/structs, endian conversion helpers, and MC portal I/O. Other DPAA2 drivers use these exports to control buffer pool objects discovered by the fsl-mc bus.

## Risks And Test Signals
Risks include command ID/layout drift against MC firmware, endian mistakes, token misuse, and failing to close sessions. Test signals are successful open/close cycles, buffer pool enable/reset behavior, and correct BPID/id attributes reported by MC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpbp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpcon.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpcon.c

## Purpose
Implements DPAA2 Data Path Concentrator command wrappers. It provides session management, enable/disable/reset, attribute retrieval, and notification destination configuration for DPCON objects.

## Important APIs, Types, And Functions
Exported functions are `dpcon_open()`, `dpcon_close()`, `dpcon_enable()`, `dpcon_disable()`, `dpcon_reset()`, `dpcon_get_attributes()`, and `dpcon_set_notification()`. Attributes include object ID, QBMan channel ID, and priority count. Notification config sets DPIO ID, priority, and user context.

## Control Flow
The wrappers create `struct fsl_mc_command` instances, encode headers with the DPCON command ID and token, fill request parameters with CPU-to-little-endian conversions, call `mc_send_command()`, and decode response parameters for getters.

## State And Persistence
No local state is stored. DPCON configuration and notification routing live in the MC-managed object state after successful commands.

## Dependencies And Integration Points
The file depends on MC portal I/O and command layouts in `fsl-mc-private.h`. DPCON allocation is coordinated by `fsl-mc-allocator.c`, and functional DPAA2 drivers use configured DPCON objects for notifications.

## Risks And Test Signals
Risks include wrong notification routing, stale command layouts, invalid tokens, and priority/channel interpretation errors. Test signals are successful MC command return codes, expected QBMan channel attributes, and interrupts/notifications arriving at the configured DPIO/user context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpmcp.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpmcp.c

## Purpose
Implements minimal DPAA2 Data Path Management Command Portal command wrappers for opening and closing DPMCP objects.

## Important APIs, Types, And Functions
The file defines `dpmcp_open()` and `dpmcp_close()`. They use `struct fsl_mc_command`, `DPMCP_CMDID_OPEN`, `DPMCP_CMDID_CLOSE`, `struct dpmcp_cmd_open`, and MC token helpers.

## Control Flow
`dpmcp_open()` encodes an open command with object ID, sends it through the supplied MC portal, and reads the returned token from the response header. `dpmcp_close()` sends a close command for an existing token.

## State And Persistence
No local state is kept. The only session state is the MC token held by the caller and tracked by MC firmware.

## Dependencies And Integration Points
It depends on `linux/fsl/mc.h` and private fsl-mc command definitions. DPMCP objects are also treated as allocatable resources by the fsl-mc allocator, although generic object allocation forbids requesting DPMCP through `fsl_mc_object_allocate()`.

## Risks And Test Signals
Risks are narrow: command ID/layout mismatch, invalid object IDs, leaked tokens, or closing the wrong session. Test signals are successful portal open/close during fsl-mc bus operation and no MC firmware errors for DPMCP resource handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dpmcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc-driver.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc-driver.c

## Purpose
Implements the Linux driver for DPAA2 Data Path Resource Container objects. It opens DPRCs, scans Management Complex objects into Linux devices, reconciles add/remove/plug state, sets up MSI-backed DPRC interrupts, and tears everything down on removal.

## Important APIs, Types, And Functions
Key exported functions include `dprc_remove_devices()`, `fsl_mc_device_lookup()`, `dprc_scan_objects()`, `dprc_scan_container()`, `disable_dprc_irq()`, `get_dprc_irq_state()`, `enable_dprc_irq()`, `dprc_setup()`, and `dprc_cleanup()`. Static helpers include `fsl_mc_device_match()`, allocatable-object detection, child add/remove callbacks, `check_plugged_state_change()`, `dprc_irq0_handler_thread()`, `register_dprc_irq_handler()`, and `dprc_setup_irq()`.

## Control Flow
Probe calls `dprc_setup()`, scans the container, then sets up IRQs. Setup creates a child MC portal when needed or creates the root UAPI device file, finds and assigns the MSI domain, opens the DPRC, reads attributes, and validates API version. Scanning initializes resource pools, locks the bus scan mutex, queries object count/descriptors, applies a dpseci coherency quirk, optionally populates the IRQ pool, removes Linux child devices no longer present in MC, then adds newly discovered devices with allocatable resources first. The threaded IRQ handler reads/clears DPRC interrupt status and rescans on object/container add/remove/create/destroy events.

## State And Persistence
State lives in the fsl-mc bus/device model: MC handle, MC portal, DPRC attributes, MSI domain, IRQ pool, scan mutex, IRQ enabled flag, and Linux child devices. Firmware owns the authoritative object inventory; the driver continually reconciles Linux state to it.

## Dependencies And Integration Points
It depends on `dprc.c` command wrappers, `fsl-mc-bus` device creation/removal, fsl-mc MSI allocation, UAPI file support for root DPRCs, resource pools from `fsl-mc-allocator.c`, and Linux driver-core attach/release behavior.

## Risks And Test Signals
Risks include races while objects are added/removed during scanning, child devices bound before allocatable pools exist, IRQ pool sizing mistakes, MSI-domain absence, teardown failure when `mc_io` is lost, and incomplete rollback on probe errors. Test signals include dynamic MC object hotplug, DPRC IRQ-triggered rescans, root and child DPRC probe/remove, interrupt pool allocation/free, and no stale Linux devices after MC object removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc.c

## Purpose
Provides the DPAA2 Data Path Resource Container command API wrappers used to communicate with Management Complex firmware. It covers opening/closing containers, resetting child containers, IRQ configuration, object enumeration, region lookup, API versioning, container ID lookup, and endpoint connection queries.

## Important APIs, Types, And Functions
Exported APIs include `dprc_open()`, `dprc_close()`, `dprc_reset_container()`, IRQ functions (`dprc_set_irq()`, `dprc_set_irq_enable()`, `dprc_set_irq_mask()`, `dprc_get_irq_status()`, `dprc_clear_irq_status()`), inventory functions (`dprc_get_attributes()`, `dprc_get_obj_count()`, `dprc_get_obj()`, `dprc_get_obj_region()`), `dprc_get_api_version()`, `dprc_get_container_id()`, and `dprc_get_connection()`. The file caches DPRC API major/minor versions in static variables to select command variants.

## Control Flow
Each API constructs an MC command, fills command-specific parameters, sends it with `mc_send_command()`, and decodes response fields. Version-aware calls choose newer command IDs for reset options and object regions: reset uses V2 for API >= 6.5, and region lookup uses V2/V3 for API >= 6.3/6.6 so base address and 64K portal sizing are represented correctly.

## State And Persistence
The only local state is cached DPRC API version. MC firmware owns all container, interrupt, object, region, and connection state. Callers hold tokens returned from open operations.

## Dependencies And Integration Points
This is the command-marshaling layer beneath `dprc-driver.c` and other fsl-mc components. It depends on private command IDs/parameter structures, endian helpers, MC portal I/O, and public fsl-mc descriptors.

## Risks And Test Signals
Risks include firmware API drift, stale global version cache across heterogeneous portals, endian/layout mismatches, returning `-ENOTCONN` for all connection query errors, and incorrect region sizing on older MC versions. Test signals are MC command conformance tests, object scan correctness, IRQ programming success, child container reset behavior for different API versions, and endpoint connection discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-allocator.c -->
# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-allocator.c

## Purpose
Implements fsl-mc resource pools for allocatable DPAA2 objects and IRQ resources. It binds to DPBP, DPMCP, and DPCON devices, inserts them into per-bus pools, allocates/free objects for functional devices, and manages MSI IRQ pools shared by devices in a DPRC.

## Important APIs, Types, And Functions
Core exports are `fsl_mc_resource_allocate()`, `fsl_mc_resource_free()`, `fsl_mc_object_allocate()`, `fsl_mc_object_free()`, `fsl_mc_populate_irq_pool()`, `fsl_mc_cleanup_irq_pool()`, `fsl_mc_allocate_irqs()`, `fsl_mc_free_irqs()`, and `fsl_mc_init_all_resource_pools()`. Static helpers validate allocatable devices, add/remove devices from pools, map object type strings to pool types, and implement `fsl_mc_allocator_probe()`/`remove()`.

## Control Flow
`fsl_mc_init_all_resource_pools()` initializes each pool on DPRC scan. The allocator driver probes DPBP/DPMCP/DPCON devices and adds them as free resources in the parent bus pool. Functional drivers call `fsl_mc_object_allocate()` to remove a free resource from the pool and create an autoremove consumer device link; freeing returns the resource to the list. IRQ pool population allocates a block of MSI interrupts, wraps each vector in `struct fsl_mc_device_irq`, and inserts those resources into the IRQ pool. Device IRQ allocation removes enough IRQ resources for a device and records back-pointers/indexes; free returns them.

## State And Persistence
State is held in each `struct fsl_mc_bus`: resource pools, free lists, max/free counts, mutexes, and `irq_resources`. Individual allocatable MC devices point at their `struct fsl_mc_resource`. IRQ resources track virtual IRQ numbers and owning MC devices. There is no persistent storage; MC object inventory remains authoritative.

## Dependencies And Integration Points
The allocator depends on fsl-mc bus type helpers, fsl-mc MSI domain functions, Linux device links, devm allocation tied to the bus/device, and pool type constants shared with private headers. It is deliberately ordered by DPRC scanning before functional devices so resource consumers can allocate DPBP/DPCON objects during probe.

## Risks And Test Signals
Risks include free/max count corruption, removing an allocated resource, DPMCP misuse, leaked device links, insufficient IRQ pool sizing, freeing IRQ pools while vectors are still allocated, and silent returns on invariant violations. Test signals include resource exhaustion paths, add/remove of allocatable devices, allocation/free under driver bind/unbind, IRQ allocation for DPRCs and child devices, and cleanup only when free counts equal max counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-allocator.c -->
