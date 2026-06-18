# subset-b-004613 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_minidump.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_minidump.c

### Purpose
`qlcnic_minidump.c` implements QLogic qlcnic firmware minidump capture. It loads a firmware-provided dump template, interprets template entries, reads selected adapter registers/memory/flash/cache regions, and stores the captured dump in `adapter->ahw->fw_dump` for later collection.

### Important APIs, Types, And Functions
The file defines packed template entry payloads such as `__crb`, `__ctrl`, `__cache`, `__mem`, `__mux`, `__queue`, `__pollrd`, `__mux2`, and `__pollrdmwr`, plus opcode-to-handler tables for 82xx and 83xx hardware. Public entry points include `qlcnic_fw_cmd_get_minidump_temp()`, `qlcnic_dump_fw()`, and `qlcnic_83xx_get_minidump_template()`. Template header helpers cache version, capability masks, saved-state accessors, and system-info fields for both 82xx and 83xx layouts.

### Control Flow
Template acquisition first asks firmware for size/version, falls back to flash for 83xx, DMA-reads the template when possible, verifies checksum, caches header fields, optionally allocates a PEX DMA buffer, and enables dump state. Capture checks that a template exists, dump capture is enabled, and the previous dump was cleared. It computes required dump size from enabled capability masks, allocates `fw_dump->data`, writes driver/firmware version into the template header, then walks template entries. Each enabled entry dispatches to its opcode handler and is skipped if the handler size does not match the template's `cap_size`. Completion marks `fw_dump->clr` and emits a `FW_DUMP=<netdev>` uevent.

### State, Persistence, And Dependencies
Persistent driver state is in `struct qlcnic_fw_dump`: template header, template size/version, capability mask, data buffer, clear flag, and optional DMA buffer/physical address. Hardware state is accessed through qlcnic indirect register helpers, shared flash locks, 83xx flash readers, mailbox commands, memory test-agent registers, and PEX DMA engines. The dump itself is in kernel memory until cleared by higher-level driver paths.

### Integration Points
The file plugs into qlcnic hardware ops through template-header helper callbacks and into diagnostic/ethtool dump flows through `qlcnic_dump_fw()`. 83xx firmware-update paths can refresh templates when firmware version increases and can request extended iSCSI dump capability on QLE8830 devices.

### Risks
The code executes template-directed register writes and polling, so malformed templates can hang capture, skip data, or touch unintended device windows. Memory reads require alignment and size multiples for the test-agent path. PEX DMA has fallback behavior, but DMA descriptor setup and saved-state DMA-engine index must be valid. `qlcnic_read_memory_test_agent()` appears to increment the local `ret` pointer rather than a byte counter in the loop, which is suspicious even though the function returns `mem->size`. Flash access and dump buffers must be serialized by existing locks and clear-state checks.

### Test Signals
Useful signals include successful template load from firmware and flash, checksum-failure rejection, capture with each supported opcode, disabled capture rejection, previous-dump-not-cleared rejection, PEX DMA unavailable fallback to test-agent reads, uevent generation, and validation that captured section sizes match template `cap_size`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_minidump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov.h

### Purpose
`qlcnic_sriov.h` is the shared SR-IOV contract for qlcnic 83xx-style PF/VF operation. It defines the back-channel mailbox wire format, VF/vport state containers, VLAN/resource accounting, and the function prototypes used by PF, VF, and common SR-IOV code.

### Important APIs, Types, And Functions
Important types are `qlcnic_bc_hdr`, `qlcnic_bc_payload`, `qlcnic_bc_trans`, `qlcnic_trans_list`, `qlcnic_vf_info`, `qlcnic_vport`, `qlcnic_resources`, `qlcnic_back_channel`, and `qlcnic_sriov`. The header exposes common routines such as `qlcnic_sriov_init()`, `qlcnic_sriov_cleanup()`, `qlcnic_sriov_vf_init()`, `qlcnic_sriov_handle_bc_event()`, VLAN helpers, and PF-only netdev VF operations behind `CONFIG_QLCNIC_SRIOV`.

### Control Flow
The header does not implement control flow, but its state enums define it. `qlcnic_trans_state` models mailbox transaction progress from initialization through channel-free wait, response wait, abort, and end. `qlcnic_vf_state` bits track send/receive/channel ownership, VF channel availability, FLR, and soft-FLR. `qlcnic_vlan_mode` distinguishes no VLAN, PF-provided PVID, and guest-VLAN mode.

### State, Persistence, And Dependencies
All state is in kernel memory beneath `adapter->ahw->sriov`. Per-VF state includes context IDs, completions, work items, send locks, receive active/pending lists, VLAN arrays, and vport policy. The header depends on Linux PCI/types, qlcnic core structures, kernel lists, spinlocks, mutexes, workqueues, and completions.

### Integration Points
This header is included by `qlcnic_sriov_common.c`, `qlcnic_sriov_pf.c`, and other qlcnic code that needs to configure PF opmode, VF opmode, or mailbox interface IDs. Inline stubs keep non-SRIOV builds compiling while dropping PF-only behavior.

### Risks
The bitfield layout of `qlcnic_bc_hdr` is endian-specific and must match firmware/PF/VF expectations. Many fields are shared across interrupt, workqueue, and netdev control paths, so locking discipline around transaction lists, VLAN arrays, and send state is critical. Compile-time stubs can hide SR-IOV behavior changes in non-SRIOV builds.

### Test Signals
Compile both `CONFIG_QLCNIC_SRIOV=y` and disabled builds. Exercise channel init/term, multi-fragment mailbox transactions, FLR state transitions, VF VLAN add/delete, PF netdev VF operations, and endian-sensitive mailbox header encoding where feasible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_common.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_common.c

### Purpose
`qlcnic_sriov_common.c` provides the common PF/VF SR-IOV infrastructure, with most VF-side behavior. It initializes SR-IOV state, implements the back-channel mailbox transaction engine, installs VF hardware/nic ops, handles VF firmware reset polling, and manages VF guest VLAN tracking.

### Important APIs, Types, And Functions
Public functions include `qlcnic_sriov_init()`, `qlcnic_sriov_cleanup()`, `qlcnic_sriov_vf_init()`, `qlcnic_sriov_vf_set_ops()`, `qlcnic_sriov_vf_register_map()`, `qlcnic_sriov_handle_bc_event()`, `qlcnic_sriov_cfg_bc_intr()`, `qlcnic_sriov_vf_set_multi()`, and VLAN allocation/add/delete helpers. Core internals include `qlcnic_sriov_prepare_bc_hdr()`, `__qlcnic_sriov_send_bc_msg()`, `qlcnic_sriov_process_bc_cmd()`, `__qlcnic_sriov_issue_cmd()`, and the VF IDC state handlers.

### Control Flow
Initialization allocates `qlcnic_sriov`, per-VF records, transaction and async workqueues, list heads, completions, locks, and PF-side default vports where needed. VF bringup waits for device-ready, configures rings and interrupts, creates the back channel, initializes vport/NIC info, fetches ACL/VLAN policy, sets up the netdev, and schedules IDC polling. Mailbox commands are wrapped as back-channel transactions with sequence IDs and fragments; events complete channel-free waits, deliver requests/responses, or schedule FLR handling. VF IDC polling detaches, reinitializes, or fails the VF according to firmware state.

### State, Persistence, And Dependencies
State is in `adapter->ahw->sriov`, per-VF transaction lists, completions, workqueues, async command lists, VLAN arrays, and adapter reset flags. Dependencies include qlcnic 83xx mailbox/register APIs, PCI SR-IOV function mapping, netdev multicast/unicast lists, qlcnic MAC filter helpers, delayed work, and firmware IDC registers.

### Integration Points
VF hardware ops replace normal mailbox command submission with `qlcnic_sriov_issue_cmd()`. PF builds call into `qlcnic_sriov_pf_process_bc_cmd()` for received VF commands. Netdev multicast programming and guest VLAN configuration are integrated with qlcnic MAC filter lists and promiscuous mode programming.

### Risks
The transaction engine is concurrency-sensitive: channel ownership, `send_cmd`, response completions, pending/active lists, async no-wait commands, and FLR cleanup all interact. Timeouts set `need_fw_reset` and clear mailbox readiness, so retry behavior affects VF recovery. VLAN list validation must prevent disallowed or duplicate guest VLAN programming. Cleanup order must flush workqueues before freeing transactions and per-VF memory.

### Test Signals
Test channel init/term, mailbox response timeout, multi-fragment command/response, async no-wait commands, PF reset during VF mailbox traffic, IDC ready/init/quiescent/failed transitions, VF multicast programming with and without guest VLANs, guest VLAN validation, shutdown/resume, and workqueue cleanup under active transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_pf.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_pf.c

### Purpose
`qlcnic_sriov_pf.c` implements PF-side SR-IOV control. It enables/disables PCI VFs, allocates and configures PF/VF vports, partitions firmware resources, proxies validated VF mailbox commands, handles VF FLR cleanup, and exposes netdev VF administration for MAC, VLAN, spoof-check, and rate limits.

### Important APIs, Types, And Functions
Important entry points are `qlcnic_pci_sriov_configure()`, `qlcnic_sriov_pf_cleanup()`, `qlcnic_sriov_pf_disable()`, `qlcnic_sriov_pf_process_bc_cmd()`, `qlcnic_sriov_pf_handle_flr()`, `qlcnic_sriov_pf_reset()`, `qlcnic_sriov_pf_reinit()`, `qlcnic_sriov_set_vf_mac()`, `qlcnic_sriov_set_vf_vlan()`, `qlcnic_sriov_set_vf_tx_rate()`, `qlcnic_sriov_get_vf_config()`, and `qlcnic_sriov_set_vf_spoofchk()`. Internal handler tables whitelist back-channel commands and firmware mailbox commands.

### Control Flow
Enable checks MSI-X, brings the interface down under RTNL, sets SR-IOV PF opmode, initializes SR-IOV state, creates the FLR workqueue, enables VLAN filtering/eswitch/vport/back-channel events, allocates VLAN arrays, restores the interface, and calls `pci_enable_sriov()`. Disable refuses assigned VFs, disables PCI SR-IOV, brings the interface down, frees VLANs, tears down PF SR-IOV state, reconfigures normal opmode, and restores the interface. VF channel init creates a VF vport, assigns default resources/ACL, and marks the VF channel active; channel term clears VLAN state and destroys the vport.

### State, Persistence, And Dependencies
PF state lives in `qlcnic_sriov`, `qlcnic_vport`, per-VF context IDs, VLAN arrays, and PF opmode flags. Dependencies include PCI SR-IOV APIs, qlcnic mailbox commands for vport/NIC/eswitch/MAC-VLAN/context programming, RTNL/netdev lifecycle functions, FLR workqueues, and the common back-channel transaction engine.

### Integration Points
The file is the policy gate for VF requests sent through `qlcnic_sriov_common.c`. It validates VF context IDs, vport handles, interrupt configuration, MTU, RSS, LRO, interrupt coalescing, MAC/VLAN operations, guest VLAN commands, and allowed passthrough commands before issuing firmware mailbox commands as the PF.

### Risks
Resource partitioning arithmetic must leave enough queues and filters for PF and VFs. VF mailbox validation is the security boundary; missing checks could let a VF operate on another function's vport or context. FLR and soft-FLR paths cancel work and delete contexts while mailbox traffic may be in flight. Netdev VF attribute changes are rejected while the VF driver is loaded, so state consistency depends on `QLC_BC_VF_STATE`.

### Test Signals
Exercise enable/disable success and rollback, assigned-VF disable rejection, VF channel init/term, all whitelisted mailbox handlers with invalid context/vport inputs, hardware and soft FLR, PF reset/reinit, VF MAC duplicate checks, VLAN modes including guest/PVID/no VLAN, spoof-check, rate validation, and `ip link show` VF config reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sysfs.c

### Purpose
`qlcnic_sysfs.c` exposes qlcnic diagnostic and management controls through sysfs and optional hwmon. It supports bridged mode, diagnostic mode, LED beaconing, CRB/memory access, NPAR/eswitch/port-mirroring configuration, port/eswitch statistics, PCI function reporting, 83xx flash access, and ASIC temperature reporting.

### Important APIs, Types, And Functions
Public functions include `qlcnic_create_sysfs_entries()`, `qlcnic_remove_sysfs_entries()`, `qlcnic_82xx_add_sysfs()`, `qlcnic_82xx_remove_sysfs()`, `qlcnic_83xx_add_sysfs()`, `qlcnic_83xx_remove_sysfs()`, `qlcnic_register_hwmon_dev()`, and `qlcnic_unregister_hwmon_dev()`. Key handlers cover `bridged_mode`, `diag_mode`, `beacon`, binary `crb`, `mem`, `npar_config`, `pci_config`, `port_stats`, `esw_stats`, `esw_config`, `pm_config`, and 83xx `flash`.

### Control Flow
Attribute creation is capability/opmode dependent. Basic bridged-mode sysfs is created when firmware advertises bridge support. Diagnostic entries always expose port stats, skip privileged controls for non-privileged functions, skip most controls in maintenance mode, and add eswitch/NPAR/PM/stat entries only when supported and running as management function. Read/write handlers validate sizes, offsets, function IDs, VLAN/bandwidth values, opmodes, and diagnostic-mode state before calling firmware helpers. Flash writes use command tokens to set erase/bulk/write mode and then perform locked flash operations.

### State, Persistence, And Dependencies
State changes include adapter flags (`QLCNIC_DIAG_ENABLED`, bridge, LED), NPAR cached fields, eswitch settings, VLAN/PVID state, flash contents, and hwmon device registration. Dependencies are Linux sysfs/bin_attribute APIs, RTNL for netdev feature changes, qlcnic firmware mailbox helpers, 82xx/83xx register accessors, flash locks, and optional `CONFIG_QLCNIC_HWMON`.

### Integration Points
These sysfs files are used by diagnostics and management tools outside normal netdev/ethtool paths. Beacon operations integrate with diagnostic resource allocation when the device is down. Hwmon exposes temperature under the standard sensor interface while skipping VF devices.

### Risks
CRB/memory and flash interfaces are powerful and gated mainly by diagnostic mode, opmode, offset/size checks, and flash locks. The static `flash_mode` in the write handler is shared across devices and calls, which is a notable state-coupling risk. Binary structures are endian-swapped in-place, so callers must match kernel structure layouts. Partial sysfs creation failures only log warnings, so remove paths must tolerate missing files.

### Test Signals
Test sysfs creation/removal for 82xx, 83xx, management, non-privileged, VF, maintenance, and eswitch modes. Validate invalid CRB/mem offsets, beacon while resetting/down/up, NPAR bandwidth bounds, eswitch VLAN/default validation, PM same-port validation, flash read/write/erase error paths, stats clear/read behavior, and hwmon registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Kconfig

### Purpose
`qualcomm/Kconfig` declares the Qualcomm Ethernet driver menu and build-time configuration symbols for QCA7000, Qualcomm EMAC, Qualcomm PPE, and rmnet.

### Important APIs, Types, And Functions
The key symbols are `NET_VENDOR_QUALCOMM`, `QCA7000`, `QCA7000_SPI`, `QCA7000_UART`, `QCOM_EMAC`, and `QCOM_PPE`. It also sources `drivers/net/ethernet/qualcomm/rmnet/Kconfig`.

### Control Flow
Kconfig visibility is gated by `NET_VENDOR_QUALCOMM`. SPI and UART QCA7000 protocol drivers select the common `QCA7000` support symbol and depend on their bus frameworks plus OF. `QCOM_EMAC` depends on DMA and MMIO support and selects `CRC32` and `PHYLIB`. `QCOM_PPE` depends on clocks, MMIO, OF, and either Qualcomm architecture or compile-test.

### State, Persistence, And Dependencies
There is no runtime state. The file persists build selections into kernel configuration and controls which objects the Makefiles can compile. Dependencies express required kernel subsystems for bus access, PHY handling, CRC support, regmap MMIO, and platform availability.

### Integration Points
The symbols are consumed by the Qualcomm Ethernet Makefiles. `QCOM_EMAC` builds the EMAC driver under `emac/`; `QCOM_PPE` builds `ppe/`; QCA7000 symbols build SPI/UART modules.

### Risks
Incorrect dependencies can expose drivers on unsupported builds or hide compile-test coverage. `NET_VENDOR_QUALCOMM` only controls menu visibility, so per-driver dependencies remain the real guardrails.

### Test Signals
Run Kconfig/compile coverage for built-in and module combinations, `COMPILE_TEST`, missing PHYLIB/SPI/SERIAL_DEV_BUS dependencies, and menu visibility when `NET_VENDOR_QUALCOMM=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Makefile

### Purpose
`qualcomm/Makefile` maps Qualcomm Ethernet Kconfig symbols to kernel objects and subdirectories.

### Important APIs, Types, And Functions
It builds `qca_7k_common.o` for `CONFIG_QCA7000`, composes `qcaspi` from `qca_7k.o`, `qca_debug.o`, and `qca_spi.o`, composes `qcauart` from `qca_uart.o`, always descends into `emac/`, and conditionally descends into `ppe/` and `rmnet/`.

### Control Flow
The build system evaluates `obj-$(CONFIG_...)` lines to include objects or modules. `obj-y += emac/` means the subdirectory is always visited, while its own Makefile controls whether `qcom-emac.o` is built.

### State, Persistence, And Dependencies
There is no runtime state. Build state is the selected object list derived from Kconfig. The file depends on matching symbol definitions in `Kconfig` and object names in the Qualcomm source tree.

### Integration Points
This is the parent build glue between `drivers/net/ethernet/` and Qualcomm driver families. It delegates EMAC object composition to `emac/Makefile`.

### Risks
Unconditional descent into `emac/` is safe only because the child Makefile is symbol-gated. Object-list drift from renamed source files causes build failures. Module names are determined by target object names, so changes affect userspace module loading.

### Test Signals
Build with QCA7000 SPI, QCA7000 UART, QCOM_EMAC, QCOM_PPE, and RMNET as built-in/module/off combinations and verify expected modules and no orphan object references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/Makefile

### Purpose
`qualcomm/emac/Makefile` defines the Qualcomm EMAC driver object composition.

### Important APIs, Types, And Functions
When `CONFIG_QCOM_EMAC` is enabled, it builds `qcom-emac.o` from `emac.o`, `emac-mac.o`, `emac-phy.o`, `emac-sgmii.o`, `emac-ethtool.o`, and three SGMII variant files: `emac-sgmii-fsm9900.o`, `emac-sgmii-qdf2432.o`, and `emac-sgmii-qdf2400.o`.

### Control Flow
Kbuild links the listed component objects into the single driver object. If `QCOM_EMAC=m`, the same composition becomes the module payload; if built-in, it is linked into the kernel image.

### State, Persistence, And Dependencies
There is no runtime state. The file depends on `CONFIG_QCOM_EMAC` from the parent Kconfig and on every listed `.c` file providing compatible symbols.

### Integration Points
This Makefile ties the platform probe/core file to MAC, PHY, SGMII, and ethtool support so the driver is built as one coherent unit.

### Risks
Missing a support object can create link-time failures or silently remove callbacks if symbols are weak elsewhere. Adding SoC-specific SGMII files requires updating this list.

### Test Signals
Compile `CONFIG_QCOM_EMAC=y` and `m`, verify `qcom-emac` contains MAC/PHY/SGMII/ethtool symbols, and run allmodconfig/allyesconfig build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-ethtool.c

### Purpose
`emac-ethtool.c` implements ethtool operations for the Qualcomm EMAC driver, exposing statistics, ring sizing, pause configuration, register snapshots, PHY autonegotiation restart, debug message level, and a private single-pause-mode flag.

### Important APIs, Types, And Functions
The file defines `emac_ethtool_stat_strings`, `EMAC_STATS_LEN`, private flag `single-pause-mode`, and `emac_ethtool_ops`. Handlers include `emac_get_ethtool_stats()`, `emac_get_ringparam()`, `emac_set_ringparam()`, `emac_get_pauseparam()`, `emac_set_pauseparam()`, `emac_get_regs()`, `emac_nway_reset()`, `emac_set_priv_flags()`, and `emac_set_ethtool_ops()`.

### Control Flow
Statistics are read under `adpt->stats.lock` after `emac_update_hw_stats()`. Ring and pause setters update adapter fields and reinitialize the device with `emac_reinit_locked()` if the netdev is running. Register dumps read a small curated set of runtime registers. Private flags toggle `adpt->single_pause_mode`, again reinitializing if active.

### State, Persistence, And Dependencies
State is stored in `emac_adapter`: `msg_enable`, descriptor counts, flow-control booleans, `automatic`, `single_pause_mode`, and statistics. Dependencies include Linux ethtool, PHY library link-setting helpers, EMAC register definitions, and the driver's reinit/stat helpers.

### Integration Points
`emac_set_ethtool_ops()` attaches these callbacks to `net_device`. PHY link settings are delegated to standard PHY ethtool helpers, while EMAC-specific state changes feed back into MAC start/config paths.

### Risks
Changing ring sizes while running depends on correct stop/realloc/start behavior in `emac_reinit_locked()`. `memcpy(data, &adpt->stats, EMAC_STATS_LEN * sizeof(u64))` assumes `struct emac_stats` starts with exactly the exported u64 counters before the spinlock. Register dump versioning must change if `emac_regs[]` changes.

### Test Signals
Use `ethtool -S`, `-g/-G`, `-a/-A`, `-d`, `--show-priv-flags`, `--set-priv-flags`, and `-r` on stopped and running interfaces. Validate descriptor clamping, mini/jumbo ring rejection, pause reconfiguration, stat ordering, and register dump length/version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.c

### Purpose
`emac-mac.c` implements Qualcomm EMAC MAC and DMA operation: multicast filtering, register programming, descriptor ring allocation, device start/stop, PHY link adjustment, receive completion, transmit completion, and packet transmit descriptor construction.

### Important APIs, Types, And Functions
Public functions include `emac_mac_up()`, `emac_mac_down()`, `emac_mac_reset()`, `emac_mac_stop()`, `emac_mac_mode_config()`, `emac_mac_rx_process()`, `emac_mac_tx_process()`, `emac_mac_rx_tx_ring_init_all()`, `emac_mac_rx_tx_rings_alloc_all()`, `emac_mac_rx_tx_rings_free_all()`, `emac_mac_tx_buf_send()`, and multicast hash helpers. Internal helpers configure MAC/DMA/RX/TX registers, allocate/free TX/RX rings, refill RFDs, parse RRDs, prepare TSO/checksum offloads, and fill TPD descriptors.

### Control Flow
Bringup resets ring indices, programs MAC/DMA/ring registers, refills RX buffers, connects the PHY in SGMII mode, enables interrupts, starts PHY polling, enables NAPI, and starts the netdev queue. Link changes start or stop MAC datapath and notify SGMII. RX processing consumes hardware RRDs up to budget, maps RFD buffers to SKBs, drops error packets, sets checksum/VLAN metadata, submits SKBs to GRO, updates process indices, and refills buffers. TX maps head/frags into TPDs, programs checksum/TSO/VLAN fields, marks the last descriptor after a write barrier, advances the hardware producer index, and later unmaps/frees completed buffers.

### State, Persistence, And Dependencies
State is in `emac_adapter`, one RX queue, one TX queue, descriptor ring memory from a coherent DMA allocation, per-descriptor SKB/DMA bookkeeping, netdev queue state, NAPI state, PHY state, and hardware mailbox/descriptor registers. Dependencies include Linux DMA mapping, SKB/GSO/checksum helpers, PHYLIB, CRC32 multicast hashing, SGMII helpers, and EMAC register definitions from `emac.h`.

### Integration Points
The core platform driver calls these routines from netdev open/stop/start_xmit, interrupt/NAPI paths, multicast mode updates, and reinit flows. Etthtool ring/pause/private-flag changes feed into this file via adapter fields and reinitialization.

### Risks
Descriptor accounting is the main risk: mapping failures must unwind produced descriptors correctly, TX queue stop/wake thresholds must leave room for worst-case SKBs, and RX refill must preserve one blank buffer slot. The driver logs but does not support multi-RFD receive packets. Hardware checksum quirks require ignoring L4F in the drop mask. Start/stop ordering must avoid PHY adjust-link races, which is why interrupts are disabled before `phy_disconnect()`.

### Test Signals
Exercise open/close, link up/down, MTU changes including jumbo, VLAN RX/TX, RX checksum on/off, TCPv4/v6 TSO, fragmented SKBs, DMA mapping failure injection, low RX buffer refill, TX queue stop/wake, multicast/promiscuous/allmulti modes, NAPI budget limits, and repeated ethtool-triggered reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.h

### Purpose
`emac-mac.h` defines Qualcomm EMAC MAC-layer descriptor formats, ring/queue data structures, descriptor bitfield helpers, DMA ordering enums, wrapper register offsets, and public MAC function prototypes.

### Important APIs, Types, And Functions
Key types are `emac_rrd`, `emac_tpd`, `emac_ring_header`, `emac_buffer`, `emac_rfd_ring`, `emac_rrd_ring`, `emac_rx_queue`, `emac_tpd_ring`, and `emac_tx_queue`. Macros such as `BITS_GET`, `BITS_SET`, `RRD_*`, and `TPD_*` encode/decode hardware descriptor fields. Prototypes expose MAC up/down/reset/stop, mode config, RX/TX process, transmit send, ring init/alloc/free, and multicast hash programming.

### Control Flow
The header has no executable control flow, but it defines the data model consumed by `emac-mac.c`: RFDs provide empty RX buffers, RRDs return completed RX packets, and TPDs describe TX buffers and offloads. Producer/consumer indices in queue structures map to hardware mailbox registers selected during ring initialization.

### State, Persistence, And Dependencies
Queue state persists in memory while the netdev is open and mirrors hardware descriptor state. DMA addresses are stored both in descriptors and software `emac_buffer` entries so completions can unmap and free SKBs. The header depends on Linux endian/bit macros through included kernel context and forward-declares `struct emac_adapter`.

### Integration Points
This header is shared by the EMAC core, MAC implementation, ethtool statistics/configuration, and other driver files through `emac.h`. It is the contract between software queues and the EMAC DMA engine.

### Risks
Bitfield macros must preserve little-endian descriptor layout. Descriptor sizes and index masks must match hardware register programming in `emac-mac.c`. Any change to ring structures affects allocation, NAPI processing, and TX completion assumptions.

### Test Signals
Compile with sparse/endian checks, validate descriptor encoding against hardware documentation or known packets, test wraparound of producer/consumer indices, and exercise RX/TX paths with checksum, TSO, VLAN, and DMA address high-bit cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.c

### Purpose
`emac-phy.c` implements the EMAC MDIO bus adapter and external PHY discovery for Qualcomm EMAC.

### Important APIs, Types, And Functions
The main public API is `emac_phy_config()`. Internal MDIO callbacks are `emac_mdio_read()` and `emac_mdio_write()`, which program `EMAC_PHY_STS` and `EMAC_MDIO_CTRL`, then poll for `MDIO_START`/`MDIO_BUSY` completion.

### Control Flow
`emac_phy_config()` allocates a managed `mii_bus`, fills bus identity/callbacks/parent/private adapter, and registers the bus differently for ACPI and device tree. ACPI registration uses `mdiobus_register()`, reads optional `phy-channel`, and falls back to `phy_find_first()`. Device tree registration uses `of_mdiobus_register()`, reads the `phy-handle` phandle, and resolves it with `of_phy_find_device()`. Failure to find a PHY unregisters the bus and returns `-ENODEV`.

### State, Persistence, And Dependencies
The adapter stores `adpt->mii_bus` and `adpt->phydev`. MDIO transactions use MMIO registers and the adapter base pointer. ACPI paths manually take a reference to match OF helper reference behavior. Dependencies include PHYLIB, OF MDIO, ACPI property helpers, and `readl_poll_timeout()`.

### Integration Points
The platform probe path calls `emac_phy_config()` before MAC bringup. `emac_mac_up()` later connects the discovered `phydev` with `phy_connect_direct()` in SGMII mode and uses PHY callbacks for link changes.

### Risks
MDIO polling timeout units and clock selection must match hardware. ACPI fallback to first PHY can hide bad firmware descriptions. Reference handling must stay balanced with the driver's unload path. Bus unregister on PHY lookup failure is manual despite devm allocation.

### Test Signals
Test ACPI with explicit and missing `phy-channel`, DT with valid/missing `phy-handle`, MDIO read/write timeout injection, no-PHY bus registration, repeated probe/remove, and link negotiation through the discovered PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.h

### Purpose
`emac-phy.h` declares the Qualcomm EMAC PHY configuration entry point.

### Important APIs, Types, And Functions
It forward-declares `struct emac_adapter` and declares `int emac_phy_config(struct platform_device *pdev, struct emac_adapter *adpt);`.

### Control Flow
The header has no executable control flow. It allows the core EMAC driver to call PHY/MDIO setup without exposing MDIO register details.

### State, Persistence, And Dependencies
No state is stored here. The declaration depends on `struct platform_device` being visible through surrounding includes, and `emac_adapter` is intentionally forward-declared to avoid pulling in the full adapter definition.

### Integration Points
`emac.h` includes this header, making `emac_phy_config()` available to the platform driver and tying the PHY implementation into the single `qcom-emac` object.

### Risks
Because this header omits a direct platform-device include, include order matters. Any signature change must be reflected in `emac-phy.c` and all callers.

### Test Signals
Build coverage is the main signal: compile EMAC with normal configs, include-order changes, and static analysis to ensure the prototype matches the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.h -->
