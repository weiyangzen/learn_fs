# Research Report: subset-b-004340

Work item `subset-b-004340` covers AMD Ethernet driver sources under `sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/`. Each file section below is delimited for grouped-report reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pcnet32.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pcnet32.c

## Purpose
`pcnet32.c` is a Linux network driver for AMD PCnet32/PCnetPCI Ethernet controllers, including PCI chips such as 79C970, 79C970A, 79C971, 79C972, 79C973, 79C975, 79C976, and the older VLB path. It registers a `pci_driver`, optionally probes legacy VLB I/O ports, allocates an Ethernet `net_device`, drives the controller through CSR/BCR register accesses, and exposes normal netdev, NAPI, MII, module-parameter, suspend/resume, and ethtool control surfaces.

## Important APIs, Types, And Functions
Core hardware formats are `struct pcnet32_rx_head`, `struct pcnet32_tx_head`, and `struct pcnet32_init_block`, all matching the device descriptor/init-block ABI and using little-endian fields. `struct pcnet32_private` persists the coherent init block, coherent TX/RX descriptor rings, SKB arrays, DMA address arrays, ring cursors, MII state, NAPI object, media flags, watchdog timer, register-access vtable, and chip identity.

`struct pcnet32_access` abstracts word I/O and dword I/O variants through CSR/BCR/RAP/reset callbacks. Probe uses `pcnet32_wio_*` first and then `pcnet32_dwio_*`. Netdev hooks are `pcnet32_open`, `pcnet32_close`, `pcnet32_start_xmit`, `pcnet32_tx_timeout`, `pcnet32_get_stats`, `pcnet32_set_multicast_list`, and `pcnet32_ioctl`. Packet receive/transmit completion is split across `pcnet32_rx_entry`, `pcnet32_rx`, `pcnet32_tx`, and `pcnet32_poll`. Device creation is in `pcnet32_probe_pci` and `pcnet32_probe1`; removal is `pcnet32_remove_one`. Ettool support includes link settings, NWay reset, register dump, ring resizing, self-test/loopback, message level, link LED identification, and string/set counts.

## Control Flow
Module init initializes the debug mask, applies `tx_start_pt`, registers the PCI driver, optionally probes VLB ports, and succeeds if either PCI registration or at least one device probe succeeded. PCI probe enables the device, sets bus mastering and a 32-bit DMA mask, requests the I/O region, and calls `pcnet32_probe1`. Probe resets the chip, selects the register access method, reads CSR88/CSR89 chip version, configures chip-specific features such as MII, full-duplex, SRAM, HomePNA, and NOUFLO, allocates `net_device` and coherent state, copies the MAC from CSRs or PROM, sets up ring metadata, writes the 32-bit init-block address to CSR1/CSR2, scans PHYs, installs NAPI and ethtool ops, registers the netdev, and enables LED writes.

Open requests IRQ, resets into 32-bit mode, programs media/autoneg/full-duplex/GPSI settings, configures PHY isolation for multi-PHY devices, loads multicast filtering, initializes RX/TX rings, enables NAPI, writes CSR4 auto-padding, initializes the chip, starts the queue, starts the media watchdog for newer chips, and enables normal CSR0 interrupt/start bits. TX maps the SKB for DMA, fills a ring entry, publishes ownership last with a write barrier, advances `cur_tx`, writes `CSR0_TXPOLL`, and stops the queue if the next descriptor is still occupied. Interrupts acknowledge CSR0 sources, log bus/error conditions, mask interrupts in CSR3, and schedule NAPI. NAPI drains RX up to budget, cleans TX completions, restarts on FIFO underflow, unmasks interrupts on completion, and updates stats.

## State And Persistence
All runtime state is in memory: descriptor rings and init block are coherent DMA allocations; SKBs and DMA mappings are kept in parallel arrays; ring cursors are monotonically incremented and masked by ring size; link state is maintained through MII registers, `netif_carrier_*`, and a watchdog timer. Module parameters persist only for module lifetime: `debug`, `max_interrupt_work`, `rx_copybreak`, `tx_start_pt`, `pcnet32vlb`, `options[]`, `full_duplex[]`, and `homepna[]`. No filesystem persistence is used.

## Dependencies And Integration Points
The driver integrates with the PCI core, Linux netdev core, NAPI, DMA API, MII helpers, ethtool, generic MII ioctl handling, PM sleep callbacks, IRQ registration, I/O port allocation, and legacy probe IRQ helpers for VLB. It relies on low-level port I/O (`inw/outw/inl/outl/inb`) rather than MMIO. Kernel networking consumes packets through `netif_receive_skb`, and upper layers see normal Ethernet stats and link reporting.

## Risks
The hardware contract is order-sensitive: descriptor ownership must be written after base/length fields and after DMA mapping; the code uses barriers to enforce this. Error handling around partial ring allocation depends on later `pcnet32_free_ring` cleanup and can leave some allocation paths only indirectly cleaned. The legacy VLB path uses `lp->pci_dev` when allocating coherent memory even when `pdev` can be `NULL`, so this code is tightly tied to historical platform behavior. Ring resizing, suspend-based ethtool register reads, multicast reinitialization, and FIFO-underflow restart all stop or suspend the chip and must preserve DMA mappings and queue state. Hardware-specific quirks, such as BCR30 hangs on 79C976 and CSR address/PROM mismatches, are encoded directly.

## Test Signals
Useful validation signals are PCI probe/register logs, `ethtool -i`, `ethtool -S`/stats, `ethtool -d` register dumps, link up/down messages from the watchdog, MII ioctl/ethtool link-setting changes, TX timeout recovery, multicast/promiscuous mode toggles, suspend/resume with an active interface, and traffic tests that exercise both copy-small-RX and receive-in-place paths across ring wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pcnet32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/Makefile

## Purpose
This Makefile defines the build composition for the AMD/Pensando core driver. It builds the `pds_core.o` module/object when `CONFIG_PDS_CORE` is enabled and aggregates all implementation units that make up the core PCI, devlink, admin queue, auxiliary bus, debugfs, firmware, and hardware setup functionality.

## Important APIs, Types, And Functions
There are no C APIs in this file. The important build variable is `obj-$(CONFIG_PDS_CORE) := pds_core.o`, which binds Kconfig selection to the object. `pds_core-y` lists `main.o`, `devlink.o`, `auxbus.o`, `dev.o`, `adminq.o`, `core.o`, `debugfs.o`, and `fw.o` as the compiled units linked into `pds_core.o`.

## Control Flow
Kbuild evaluates the conditional object assignment. If `CONFIG_PDS_CORE=y` it links the objects into the built-in kernel image; if `CONFIG_PDS_CORE=m` it links them into a loadable module; if unset it builds none of them. Object ordering places `main.o` first, but runtime entry still comes from `module_init` in `main.c`.

## State And Persistence
The file has no runtime state. Its persistent effect is the static build contract: adding or removing a source file from the driver requires updating `pds_core-y`, and changing the Kconfig symbol changes whether any of these files are compiled.

## Dependencies And Integration Points
It integrates with kernel Kbuild and the `CONFIG_PDS_CORE` Kconfig symbol. The listed object files depend on common Pensando/AMD UAPI and internal headers under `include/linux/pds/` plus core kernel subsystems such as PCI, devlink, auxiliary bus, debugfs, workqueues, timers, and firmware.

## Risks
If a new implementation file is introduced but omitted from `pds_core-y`, unresolved symbols or missing functionality will appear only at build/link time. Conversely, stale object entries break builds when a source is renamed. Because the driver exports symbols to auxiliary clients, build composition must stay in sync with exported helper implementations.

## Test Signals
Primary checks are `make M=drivers/net/ethernet/amd/pds_core`, full kernel builds for built-in and modular `CONFIG_PDS_CORE`, and link/load tests that confirm `pds_core` contains all exported symbols used by client drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/adminq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/adminq.c

## Purpose
`adminq.c` implements the AMD/Pensando core AdminQ and NotifyQ completion path. It posts administrative commands to firmware, waits for completions, processes asynchronous notifications, returns interrupt credits, and bridges queue interrupts to a workqueue context. This is the central command transport used by firmware setup, devlink operations, auxiliary clients, and feature control.

## Important APIs, Types, And Functions
`pdsc_process_notifyq` consumes `union pds_core_notifyq_comp` entries and dispatches link-change and reset events through `pdsc_notify`. `pdsc_process_adminq` drains NotifyQ and AdminQ completions, copies firmware completion data into each waiting command's destination, completes the per-descriptor `struct completion`, flips CQ color at ring wrap, returns interrupt credits, and drops the AdminQ reference. `pdsc_adminq_isr` queues `pdsc_work_thread` to process completions outside hard IRQ context. `pdsc_adminq_post` is exported and synchronously posts a `union pds_core_adminq_cmd` with a caller-provided completion buffer and optional fast-poll behavior.

## Control Flow
Posting starts by taking an AdminQ reference with `pdsc_adminq_inc_if_up`, which rejects posts while the driver is stopping or firmware is marked dead. `__pdsc_adminq_post` takes `adminq_lock`, checks ring space, verifies firmware is running, copies the command into the descriptor at `head_idx`, reinitializes its completion, advances `head_idx`, and rings the kernel doorbell page with the queue id plus new index. The public `pdsc_adminq_post` waits in short slices for completion, checking firmware health between waits. It exponentially backs off polling unless `fast_poll` is requested, converts completion status through `pdsc_err_to_errno`, and queues health work on timeout or lost firmware.

Interrupt flow starts in `pdsc_adminq_isr`, which validates AdminQ availability, queues `adminqcq.work`, and exits. The worker calls `pdsc_process_adminq`; this first processes NotifyQ events by comparing event IDs against `last_eid`, then drains AdminQ completions while CQ color matches. For each completion it copies the completion into `q_info->dest` and completes the waiting command. Credits are returned for both NotifyQ and AdminQ work.

## State And Persistence
State is held in `pdsc->adminqcq`, `pdsc->notifyqcq`, `pdsc->last_eid`, queue head/tail indices, completion objects, CQ done color, `accum_work`, `adminq_refcnt`, and driver state flags. No persistent storage is used. Reference counting is a key lifetime guard: teardown sets firmware-dead state and waits until the AdminQ refcount falls to one before freeing queues.

## Dependencies And Integration Points
The file depends on queue structures from `core.h`, firmware ABI types from `pds_adminq.h`/`pds_core_if.h`, dynamic debug hex dumps, interrupt credit helpers from `pds_intr.h`, workqueues, completions, refcounts, and the blocking notifier wrapper in `core.c`. It is used by `auxbus.c`, `devlink.c`, `fw.c`, and core setup paths.

## Risks
Ring full detection and head/tail arithmetic must leave one descriptor empty; off-by-one errors can corrupt in-flight commands. Completion waiting deliberately completes timed-out descriptors to prevent later waits from hanging, but late firmware writes can still race with command-lifetime expectations. NotifyQ processing assumes event IDs increase and stops when the next event ID is not greater than `last_eid`. Firmware health loss while commands are outstanding must route to health recovery without freeing queues under active users.

## Test Signals
Tests should exercise successful AdminQ commands, ring-full returns, timeout and firmware-down paths, NotifyQ link/reset event propagation, interrupt-to-workqueue completion, `PDS_AQ_FLAG_FASTPOLL` behavior, and teardown while commands are active. Dynamic debug command/completion dumps and `debugfs` queue counters are useful observability signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/adminq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/auxbus.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/auxbus.c

## Purpose
`auxbus.c` exposes AMD/Pensando core services to auxiliary client drivers. It registers clients with firmware, unregisters them, wraps client AdminQ commands in core AdminQ requests, and creates/deletes Linux `auxiliary_device` instances for supported virtual interface types such as firmware-control and vDPA.

## Important APIs, Types, And Functions
Exported APIs are `pds_client_register`, `pds_client_unregister`, and `pds_client_adminq_cmd`, which auxiliary clients can call after binding. `pdsc_auxbus_dev_add` and `pdsc_auxbus_dev_del` are internal core helpers used by PF/VF probe, remove, SR-IOV, devlink enable toggles, and reset handling. `pdsc_auxbus_dev_register` allocates `struct pds_auxiliary_dev`, fills `vf_pdev` and `client_id`, initializes `auxiliary_device`, and adds it. `pdsc_auxbus_dev_release` frees the wrapper when the aux device lifetime ends.

## Control Flow
Client registration posts `PDS_AQ_CMD_CLIENT_REG` with a device name and expects a nonzero firmware `client_id`. Unregistration posts `PDS_AQ_CMD_CLIENT_UNREG`. Client command forwarding resolves the PF from the VF PCI device through `pci_physfn`, wraps the supplied request into `PDS_AQ_CMD_CLIENT_CMD`, copies a bounded payload into `client_cmd`, and posts it through `pdsc_adminq_post`, optionally fast-polling.

Aux-device creation starts in `pdsc_auxbus_dev_add`. It validates the client function pointer and VIF type, takes the PF `config_lock`, rejects add when the client function is firmware-dead or stopping, checks firmware-reported VIF support plus runtime enablement, registers the client with firmware, then creates the aux device. If auxiliary-device add fails, it unregisters the client ID. Deletion takes the same lock, unregisters the client, deletes/uninitializes the auxiliary device, and clears the caller's pointer.

## State And Persistence
The persistent runtime state is `struct pds_auxiliary_dev` and the stored `client_id` returned by firmware. PF `vfs[]` entries and `pdsc->padev` hold pointers to active aux devices. VIF support/enablement comes from `pdsc->viftype_status` and `pdsc->dev_ident.vif_types`. There is no disk persistence.

## Dependencies And Integration Points
This file integrates with Linux PCI PF/VF helpers, the auxiliary bus, `pds_auxbus.h`, core AdminQ posting, PF `config_lock`, firmware VIF identity, and exported GPL symbols consumed by client drivers. It is called from `main.c` for PF/VF lifecycle and from `devlink.c` when runtime enable parameters change.

## Risks
Client registration is intentionally done before `auxiliary_device_add` so a probing aux client can issue AdminQ commands, but this makes cleanup ordering important on add failure. `pds_client_adminq_cmd` assumes the PF driver data is valid and available through the VF's physical function. Feature disable loops in devlink can leave some VFs updated before a later add error is returned. Reset/remove paths must delete aux devices before tearing down AdminQ so clients can clean up through firmware.

## Test Signals
Validate aux device creation and deletion on PF probe/remove, VF probe/remove, SR-IOV enable/disable, devlink `enable_vnet` toggles, firmware not supporting a VIF type, firmware returning null client ID, and client AdminQ command forwarding with and without fast-poll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/auxbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.c

## Purpose
`core.c` implements core AMD/Pensando device services after PCI BARs are mapped: notification registration, interrupt allocation, queue/completion-queue allocation, device core initialization, VIF-type discovery, setup/teardown, interrupt start/stop, firmware-down/up recovery, PCI reset work, and periodic health handling.

## Important APIs, Types, And Functions
Notifier APIs are `pdsc_register_notify`, `pdsc_unregister_notify`, and `pdsc_notify`. Interrupt APIs are `pdsc_intr_alloc` and `pdsc_intr_free`. Queue APIs are `pdsc_qcq_alloc` and `pdsc_qcq_free`, with helpers `pdsc_q_map`, `pdsc_cq_map`, and QCQ interrupt allocation/free. Device lifecycle APIs are `pdsc_setup`, `pdsc_teardown`, `pdsc_start`, `pdsc_stop`, `pdsc_fw_down`, `pdsc_fw_up`, `pdsc_pci_reset_thread`, and `pdsc_health_thread`.

## Control Flow
`pdsc_setup` calls `pdsc_dev_init` to reset/identify firmware and allocate MSI-X vectors, then `pdsc_core_init` to allocate AdminQ and NotifyQ QCQs, submit `PDS_CORE_CMD_INIT`, read hardware queue indices/types, and map the kernel doorbell page. On initial setup it also allocates VIF-type status from defaults and firmware identity, and publishes debugfs VIF information. Successful setup sets `adminq_refcnt` to one and clears firmware-dead state.

QCQ allocation creates per-descriptor software info arrays with completions, allocates coherent queue and completion memory aligned to `PDS_PAGE_SIZE`, optionally places notify queue and completion queue in one contiguous coherent allocation, binds interrupts for interrupt-backed queues, maps descriptor pointers, and creates debugfs nodes. Free removes debugfs, frees IRQ, coherent memory, and software arrays.

Firmware health recovery is state-driven. `pdsc_health_thread` holds `config_lock`, skips transition states, calls `pdsc_is_fw_good`, and if running state changed invokes `pdsc_fw_down` or `pdsc_fw_up`. Firmware-down sets `PDSC_S_FW_DEAD`, waits for AdminQ users to drain, reports devlink health, notifies clients of reset state 0, masks interrupts, and tears down core queues without removing VIF metadata. Firmware-up rebuilds setup without initial-only allocation, restarts interrupts, increments recovery count, marks devlink reporter healthy, and notifies clients of reset state 1.

## State And Persistence
Runtime state lives in `struct pdsc`: state bits, firmware status/generation/heartbeat, workqueue work items, health reporter pointer, interrupt table, AdminQ/NotifyQ QCQs, doorbell mapping, VIF-type status, and last notify event ID. The blocking notifier chain is static module state. No persistent storage is written; recovery reconstructs queues and MMIO mappings from firmware identity and PCI BAR state.

## Dependencies And Integration Points
The file depends on PCI MSI-X APIs, DMA coherent allocation, vmalloc/vcalloc, devlink health reporter updates, workqueues, timers indirectly through `main.c`, debugfs helpers, AdminQ ISR from `adminq.c`, device command helpers from `dev.c`, and firmware ABI definitions from `linux/pds/*`. Auxiliary clients observe reset/link events through the notifier chain.

## Risks
Queue setup is sensitive to alignment, descriptor sizing, ring power-of-two lengths, CQ color handling, and firmware-returned queue IDs. `pdsc_adminq_wait_and_dec_once_unused` busy-waits until AdminQ users drain; a leaked reference can stall recovery. `pdsc_fw_down` returns early for VFs after setting firmware-dead state, so VF recovery semantics depend on PF reset handling. PCI health work deliberately queues reset work to avoid reset/health deadlock; changes in locking order around `config_lock` and PCI reset callbacks can reintroduce deadlocks.

## Test Signals
Exercise PF initial setup, MSI-X allocation failures, AdminQ/NotifyQ QCQ allocation failures, firmware-down/up recovery, devlink health reports, notifier events to clients, PCI bad-status reset work, teardown during active AdminQ commands, and debugfs queue visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.h

## Purpose
`core.h` is the private header for the AMD/Pensando core driver. It defines driver constants, central runtime structures, queue and completion abstractions, interrupt tracking, VIF-type bookkeeping, state flags, doorbell encoding helpers, and prototypes shared across the driver's implementation files.

## Important APIs, Types, And Functions
Important structures include `pdsc_dev_bar` for PCI BAR metadata, `pdsc_vf` for per-VF auxiliary-device state, `pdsc_devinfo` for firmware/device strings, `pdsc_queue` for submission queues, `pdsc_intr_info` for MSI-X vectors, `pdsc_q_info`/`pdsc_cq_info`/`pdsc_buf_info` for descriptor software metadata, `pdsc_cq` for completion queues, `pdsc_qcq` for queue/completion/interrupt bundles, `pdsc_viftype` for supported runtime service types, and `pdsc` as the device-private root.

`enum pdsc_state_flags` defines `PDSC_S_FW_DEAD`, `PDSC_S_INITING_DRIVER`, and `PDSC_S_STOPPING_DRIVER`. `enum pds_core_dbell_bits` and `pds_core_dbell_ring` define how queue id, ring id, and descriptor index are encoded into 64-bit doorbell writes. Prototypes expose devlink, debugfs, device command, interrupt, queue, setup, notification, auxiliary bus, AdminQ, firmware, and reset functions across compilation units.

## Control Flow
The header itself has no runtime control flow, but it establishes the cross-file call graph. `main.c` owns PCI/module lifecycle and uses setup/start/stop, devlink, debugfs, auxbus, and reset prototypes. `core.c` implements setup, queues, interrupts, health, and notification. `dev.c` implements devcmd and identity. `adminq.c` implements AdminQ transport. `auxbus.c`, `devlink.c`, `debugfs.c`, and `fw.c` use the shared `pdsc` state and helper declarations.

## State And Persistence
`struct pdsc` is the persistent in-kernel state for each PCI function. It stores PCI/device pointers, debugfs dentries, BAR mappings, PF/VF relationship data, firmware state, timer/workqueue objects, devlink health reporter, firmware recovery count, identity data, interrupt metadata, locks, MMIO register pointers, AdminQ/NotifyQ queues, and reset work. All state is runtime-only.

## Dependencies And Integration Points
The header includes debugfs and devlink headers plus Pensando/AMD common, core interface, AdminQ, and interrupt ABI headers from `include/linux/pds/`. It is the internal integration point between Linux subsystems and the device firmware ABI. Exported symbols declared here are used by auxiliary client modules as well as internal objects.

## Risks
Because this header defines shared structure layout, changes can affect all implementation files and exported client assumptions. Locking fields (`devcmd_lock`, `config_lock`, `adminq_lock`, `adminq_refcnt`) encode concurrency expectations that are not type-enforced. Doorbell bit macros must match firmware/hardware ABI exactly. The `pdsc` structure mixes PF-only and VF-only fields, so lifecycle code must guard fields by `pdev->is_virtfn`.

## Test Signals
Build coverage is the primary signal for declaration consistency. Runtime signals include successful PF/VF probe, devlink operations, auxiliary-client binding, AdminQ command completion, firmware recovery, debugfs node creation, and sparse/lockdep checks around MMIO and locking annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/debugfs.c

## Purpose
`debugfs.c` provides read-only debugfs observability for the AMD/Pensando core driver. It creates the module-level debugfs directory, per-device directories, identity and VIF-type files, queue/completion queue directories, and interrupt-control register dumps for AdminQ/NotifyQ-style QCQs.

## Important APIs, Types, And Functions
Public helpers are `pdsc_debugfs_create`, `pdsc_debugfs_destroy`, `pdsc_debugfs_add_dev`, `pdsc_debugfs_del_dev`, `pdsc_debugfs_add_ident`, `pdsc_debugfs_add_viftype`, `pdsc_debugfs_add_qcq`, and `pdsc_debugfs_del_qcq`. `identity_show` emits firmware heartbeat, identity counts, interrupt coalescing factors, and VIF-type words. `viftype_show` emits each named VIF type's support and enable state. `intr_ctrl_regs` names the interrupt-control register offsets exposed through `debugfs_create_regset32`.

## Control Flow
Module init calls `pdsc_debugfs_create`; module exit calls recursive destroy. Probe calls `pdsc_debugfs_add_dev` before deeper device init, creating a directory named by PCI device and a `state` file. Device identity discovery calls `pdsc_debugfs_add_ident`, which avoids duplicate creation during reset flows by checking for an existing `identity` file. Initial setup calls `pdsc_debugfs_add_viftype`. QCQ allocation calls `pdsc_debugfs_add_qcq`, creating top-level QCQ metadata, `q/`, `cq/`, and optional `intr/` subdirectories. Queue free and device remove remove the corresponding subtrees.

## State And Persistence
The only module-level state is `pdsc_dir`. Per-device and per-QCQ dentries are stored in `pdsc->dentry` and `qcq->dentry`. The files expose live kernel memory and MMIO register state read-only; there is no persistence beyond runtime debugfs entries.

## Dependencies And Integration Points
This file integrates with Linux debugfs, seq_file show helpers, PCI names, MMIO read helpers, devm allocation for register-set metadata, and shared driver state from `core.h`. It is called from module lifecycle, probe/remove, identity setup, VIF setup, and QCQ allocation/free.

## Risks
Debugfs files expose live data without taking driver locks, so output can be transient during reset or teardown. `pdsc_debugfs_add_ident` uses `debugfs_lookup` to avoid duplicates but does not explicitly drop the looked-up dentry, which is a pattern worth reviewing against current debugfs lookup semantics. `pdsc_debugfs_add_qcq` returns early on subdirectory allocation errors and can leave partial trees, though recursive removal later handles normal cleanup. Register-set memory is devm-managed while debugfs lifetime is tied to queue/device removal; teardown ordering must keep the device alive until debugfs entries are removed.

## Test Signals
Mount debugfs and verify per-device `state`, `identity`, `viftypes`, queue, CQ, and interrupt files after probe. Exercise firmware reset/recovery to ensure identity is not duplicated and stale QCQ directories disappear/reappear. Read files during traffic/AdminQ activity to verify counters and ring indices change without read faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/dev.c

## Purpose
`dev.c` implements low-level device-command interaction with AMD/Pensando firmware. It converts firmware status codes to Linux errors, checks firmware health, rings the device command doorbell, waits for command completion, resets/identifies the device, caches device identity strings and capabilities, and allocates/free MSI-X interrupt vectors based on firmware identity.

## Important APIs, Types, And Functions
Exported/internal APIs include `pdsc_err_to_errno`, `pdsc_is_fw_running`, `pdsc_is_fw_good`, `pdsc_devcmd_locked`, `pdsc_devcmd`, `pdsc_devcmd_init`, `pdsc_devcmd_reset`, `pdsc_dev_init`, and `pdsc_dev_uninit`. Helpers include `pdsc_devcmd_status`, `pdsc_devcmd_done`, `pdsc_devcmd_dbell`, `pdsc_devcmd_clean`, `pdsc_devcmd_str`, `pdsc_devcmd_wait`, `pdsc_devcmd_identify_locked`, `pdsc_init_devinfo`, and `pdsc_identify`.

## Control Flow
`pdsc_dev_init` begins by reading device info registers into `pdsc->dev_info` and firmware generation, sets the default device-command timeout, sends reset if firmware is running, identifies the device, publishes debugfs identity, allocates software interrupt metadata, and requests an exact number of MSI-X vectors capped by online CPUs and firmware `nintrs`.

Device commands are serialized by `devcmd_lock` unless a caller already holds it and uses `pdsc_devcmd_locked`. The locked function copies the command into MMIO command registers, clears `done`, rings the command doorbell, and calls `pdsc_devcmd_wait`. Waiting loops until firmware stops running, the done bit appears, or the timeout expires, sleeping briefly between polls. On timeout it cleans the command register area; on `-ENXIO` or timeout it queues health work when available; otherwise it copies the completion from MMIO.

Identify writes a Linux driver identity block into `cmd_regs->data`, runs `PDS_CORE_CMD_IDENTIFY`, copies firmware identity back from the same data window, and logs the firmware version if printable. Uninit frees all allocated interrupts through `pdsc_intr_free` and releases PCI IRQ vectors.

## State And Persistence
The file maintains runtime caches in `pdsc`: `fw_status`, `last_fw_time`, `last_hb`, `fw_generation`, `dev_info`, `dev_ident`, `devcmd_timeout`, `intr_info`, and `nintrs`. Device command data and completion are exchanged through MMIO BAR register windows. There is no filesystem persistence.

## Dependencies And Integration Points
It depends on PCI IRQ vector APIs, MMIO accessors, `utsname()` for driver identity, firmware ABI structures from `pds_core_if.h`, health work from `core.c`, debugfs identity publication, and interrupt free helpers. Higher layers in `core.c`, `devlink.c`, and `fw.c` use the device-command functions.

## Risks
The command data window is shared between identify, firmware update chunks, firmware list queries, and core init, so callers must hold `devcmd_lock` when touching `cmd_regs->data`. Firmware health checks update cached status as a side effect. Timeouts clean only command MMIO state and rely on health recovery for broader repair. Interrupt allocation requires exactly `nintrs` MSI-X vectors; partial availability is treated as failure. Error-code translation collapses several firmware statuses to generic Linux errors, which may hide detail from callers.

## Test Signals
Validation should cover identify success/failure, firmware stopped before command, timeout, bad PCI status, reset when firmware is already down, exact MSI-X allocation failure, printable and invalid firmware strings, debugfs identity creation, and health work queued after command transport failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/devlink.c

## Purpose
`devlink.c` implements devlink operations and parameters for the AMD/Pensando core driver. It exposes runtime enablement for supported VIF/client types, firmware flash update, firmware/device version reporting, serial number reporting, and devlink health diagnosis for firmware state.

## Important APIs, Types, And Functions
`pdsc_dl_enable_get`, `pdsc_dl_enable_set`, and `pdsc_dl_enable_validate` back the generic `enable_vnet` devlink parameter. `pdsc_dl_flash_update` delegates devlink firmware flashing to `pdsc_firmware_update`. `pdsc_dl_info_get` reports stored firmware slot versions, running firmware version, ASIC id/revision, and serial number. `pdsc_fw_reporter_diagnose` emits firmware health state, generation, and recovery count. `pdsc_dl_find_viftype_by_id` maps a devlink parameter id to a `pdsc_viftype` entry.

## Control Flow
Devlink parameter get finds a matching VIF type in `pdsc->viftype_status` and returns its enabled state. Set validates support, short-circuits if unchanged, stores the new enablement, then iterates existing VFs to add or delete vDPA auxiliary devices. Validate rejects unsupported or absent VIF types. Firmware flash update is a thin call into `fw.c`.

Info get sends `PDS_CORE_FW_GET_LIST` through the devcmd path while holding `devcmd_lock`, copies the firmware list out of the command data window, reports known slot names (`fw.goldfw`, `fw.mainfwa`, `fw.mainfwb`) or generated slot names, then reports running firmware, ASIC id/rev, and serial. The health reporter takes `config_lock`, classifies state as dead, unhealthy, or healthy using `PDSC_S_FW_DEAD` and `pdsc_is_fw_good`, then appends numeric state, generation, and recovery counters.

## State And Persistence
Runtime state is in `pdsc->viftype_status`, `pdsc->num_vfs`, `pdsc->vfs[]`, `pdsc->dev_info`, firmware command data, `fw_status`, `fw_generation`, and `fw_recoveries`. Devlink parameters are runtime-mode only; this file does not persist settings across reloads.

## Dependencies And Integration Points
It integrates with devlink core, devlink params, devlink info API, devlink health reporters, auxiliary-device creation/deletion from `auxbus.c`, firmware update from `fw.c`, and device command locking from `dev.c`. The actual devlink ops and params are registered by `main.c`.

## Risks
`pdsc_dl_enable_set` updates the enabled flag before iterating VFs; if adding an aux device fails partway through, earlier VFs may have changed while the function returns an error. The function does not explicitly take `config_lock`; auxbus helpers take it per add/delete, so multi-VF transitions are not atomic. Firmware info reads share the devcmd data window and must keep locking discipline. Health diagnosis reads firmware status while holding `config_lock`, which must remain compatible with reset and recovery paths.

## Test Signals
Use `devlink dev info`, `devlink dev param show/set enable_vnet`, `devlink health show/diagnose`, and `devlink dev flash` on supported hardware. Validate unsupported VIF behavior, VF aux-device creation/deletion after toggles, firmware slot list sizes beyond named slots, and health reporter state during forced firmware down/up recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/fw.c

## Purpose
`fw.c` implements devlink-triggered firmware update for AMD/Pensando core devices. It downloads the firmware image to the device in command-data-sized segments, starts an asynchronous install, waits for install completion, activates/selects the installed slot, waits for activation completion, and reports progress through devlink flash notifications.

## Important APIs, Types, And Functions
The public function is `pdsc_firmware_update`. Helpers are `pdsc_devcmd_fw_download_locked`, `pdsc_devcmd_fw_install`, `pdsc_devcmd_fw_activate`, and `pdsc_fw_status_long_wait`. Constants define a long install timeout of 25 minutes, a select timeout of 30 seconds, and progress notification interval fraction of 32.

## Control Flow
The update starts by checking `cmd_regs`, notifying "Preparing to flash", and setting chunk size to the firmware command data window size. It loops over the firmware image; each iteration notifies download progress at coarse intervals, locks `devcmd_lock`, copies a chunk into `cmd_regs->data`, sends `PDS_CORE_CMD_FW_DOWNLOAD` with the data-window offset, image offset, and length, unlocks, and advances. After all chunks download, it notifies completion of download and a long install timeout, sends `PDS_CORE_FW_INSTALL_ASYNC`, and treats the completion slot as the target firmware slot.

Install and activation are asynchronous. `pdsc_fw_status_long_wait` repeatedly sends a firmware-control status command, sleeping 20 ms between polls, while the command returns `-EAGAIN` or `-ETIMEDOUT` and the operation timeout has not expired. After install succeeds, the code notifies selecting timeout, starts `PDS_CORE_FW_ACTIVATE_ASYNC` for the returned slot, waits for activation status, and finally sends "Flash done" or "Flash failed".

## State And Persistence
The function uses transient stack state for offsets, slot, and progress intervals. Firmware bytes are temporarily copied into the MMIO command data window. Persistent device-side effects are the installed/activated firmware image in hardware-managed storage; the driver itself writes no files.

## Dependencies And Integration Points
It is called from devlink flash update in `devlink.c`, relies on the Linux firmware loader's `struct firmware`, uses devlink flash status/timeout notifications, uses netlink extack error messages, and serializes MMIO command data access with `devcmd_lock` and `pdsc_devcmd*` helpers.

## Risks
Firmware update is long-running and command-timeout behavior is deliberately tolerated while polling async status; distinguishing real transport failure from in-progress status is critical. Progress interval calculation uses `fw->size / 32`; for very small firmware images this can be zero, making progress notification occur every loop iteration but still advancing by chunk size. Update cannot proceed if command registers are unavailable. A failure after install but before activation may leave device firmware staged but not selected, depending on firmware semantics.

## Test Signals
Use `devlink dev flash` with valid firmware, invalid firmware, truncated firmware, and forced device-command failures. Observe devlink status notifications for preparing/downloading/installing/selecting/done/failed, extack messages for segment download/install/select failures, and firmware slot/version changes through `devlink dev info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/main.c

## Purpose
`main.c` owns the AMD/Pensando core driver's module, PCI, devlink, PF/VF, SR-IOV, reset, AER, BAR-mapping, workqueue, timer, and high-level lifecycle logic. It distinguishes PF from VF behavior, initializes PF firmware/core services, creates auxiliary devices for clients, and registers the `pci_driver`.

## Important APIs, Types, And Functions
Important functions include `pdsc_probe`, `pdsc_remove`, `pdsc_init_pf`, `pdsc_init_vf`, `pdsc_sriov_configure`, `pdsc_map_bars`, `pdsc_unmap_bars`, `pdsc_map_dbpage`, `pdsc_wdtimer_cb`, `pdsc_reset_prepare`, `pdsc_reset_done`, `pdsc_pci_error_detected`, `pdsc_pci_error_resume`, `pdsc_get_pf_struct`, module init/exit, and helper health timer stop/restart functions. Static objects include the PCI ID table, PF/VF devlink ops, devlink params, firmware health reporter ops, IDA for unique ids, and PCI error handlers.

## Control Flow
Module init verifies `KBUILD_MODNAME` matches `PDS_CORE_DRV_NAME`, creates debugfs root, and registers the PCI driver. Probe allocates a devlink instance with PF or VF ops, stores `pdsc`, marks initialization, sets PCI drvdata, creates debugfs device state, allocates a unique id, sets a coherent DMA mask, enables the PCI device, and dispatches to PF or VF init.

PF init requests PCI regions, maps BAR0 register windows and BAR1 doorbells, creates a single-threaded workqueue, initializes health and reset work, sets the watchdog timer, initializes locks, marks firmware dead, runs `pdsc_setup`, starts interrupts, creates the FWCTL aux device, registers devlink params and firmware health reporter, registers devlink, and starts the watchdog timer. VF init obtains PF driver data, records VF id, registers VF devlink, stores the VF pointer in PF `vfs[]`, and creates a vDPA aux device if enabled/supported.

Remove unregisters devlink first to block new users. PF remove destroys health reporter and params, disables SR-IOV and aux devices before AdminQ teardown, stops the watchdog/workqueue, marks stopping, masks interrupts, tears down core/device state, unmaps BARs, releases PCI regions, disables PCI, frees IDA/debugfs/devlink. VF remove unregisters its aux device from the PF and clears the PF VF pointer.

Reset prepare stops health checks, marks firmware down, deletes aux devices, unmaps BARs, releases regions, and disables PCI. Reset done re-enables PCI, remaps PF BARs, runs firmware-up recovery, restarts health checks, and recreates aux devices. AER frozen-channel handling requests reset; resume triggers locked function reset if firmware remains dead.

## State And Persistence
Per-device runtime state is `struct pdsc` allocated as devlink private data. Persistent kernel-lifetime state includes the PCI driver registration, debugfs root, and `pdsc_ida`. PF runtime state includes BAR mappings, workqueue, watchdog timer, locks, aux-device pointers, devlink reporter/params, and SR-IOV VF array. No disk persistence is used.

## Dependencies And Integration Points
The file integrates with PCI core, SR-IOV, AER/FLR reset callbacks, devlink allocation/registration/params/health, debugfs, DMA mask setup, workqueues, timers, auxiliary bus, firmware/core setup from `core.c`/`dev.c`, and Kbuild/module macros. `pdsc_get_pf_struct` is exported for VF/client paths.

## Risks
Lifecycle ordering is the main risk. Aux devices must be removed before AdminQ teardown so clients can cleanly issue firmware commands. Devlink must unregister before stopping internals to avoid new callbacks during teardown. BAR mapping currently maps only the first memory BAR fully and records later BAR metadata; doorbell mapping relies on the recorded BAR index. Reset paths differ for PF and VF and must avoid workqueue/timer use after destruction. SR-IOV configuration allocates `vfs` before enabling VFs and must free it on all disable/error paths.

## Test Signals
Validate PF and VF probe/remove, module load/unload, SR-IOV enable/disable, devlink registration, FWCTL/vDPA aux-device creation, FLR and AER reset flows, firmware health watchdog recovery, BAR signature failure handling, DMA mask failure, and remove while VFs and aux clients are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sun3lance.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sun3lance.c

## Purpose
`sun3lance.c` is a legacy Ethernet driver for the on-board AMD LANCE controller on Sun3/Sun3x systems. It uses fixed or platform-specific register addresses, DVMA memory for the init block and descriptor rings, and the classic netdev interface to support early Sun hardware use cases such as RARP/BOOTP and NFS root.

## Important APIs, Types, And Functions
Hardware formats are `struct lance_rx_head`, `struct lance_tx_head`, `struct lance_init_block`, and `struct lance_memory`. Driver private state is `struct lance_private`, containing I/O register pointers, DVMA shared memory, RX/TX cursors, a bit-lock, and queue-full flag. The netdev operations are `lance_open`, `lance_close`, `lance_start_xmit`, and `set_multicast_list`; receive and interrupt handling is in `lance_rx` and `lance_interrupt`. Probe/module functions are `sun3lance_probe`, `lance_probe`, `sun3lance_init`, and `sun3lance_cleanup`.

## Control Flow
Module init calls `sun3lance_probe`, which rejects non-Sun3/Sun3x machines, checks IDPROM machine type for known on-board LANCE systems, allocates an Ethernet device, calls `lance_probe`, and registers the netdev. `lance_probe` maps the LANCE register area, probes CSR behavior, allocates aligned DVMA shared memory, requests the fixed IRQ, copies the PROM MAC address into the netdev and byte-swapped init block, initializes descriptor base pointers, sets netdev ops, and marks the link present.

Open stops the chip, initializes TX/RX rings, writes CSR1/CSR2 to point at the init block and CSR3 endian/bus mode, starts initialization, busy-waits for IDON, then starts RX/TX with interrupts enabled and starts the netdev queue. TX stops the queue, takes a bit-lock, pads short packets to Ethernet minimum, copies SKB data into the DVMA TX buffer, publishes ownership bits last, advances `new_tx`, writes transmit-demand/start bits, frees the SKB, clears the lock, and restarts the queue if the next descriptor is host-owned.

Interrupt handling flushes CPU cache, reads/acks CSR0, clears errors, reaps TX descriptors and updates stats, wakes the queue when space returns, runs `lance_rx` for RX interrupts, logs babble/miss/memory errors, and restarts the chip on memory error. RX loops while descriptors are host-owned, validates complete packets, allocates SKBs, copies from DVMA RX buffers, passes packets via `netif_rx`, updates stats, then returns descriptors to chip ownership.

## State And Persistence
State is in DVMA shared memory and `lance_private` ring cursors. The driver uses fixed `LANCE_OBIO` and `LANCE_IRQ` for Sun3 and `SUN3X_LANCE` for Sun3x. Module parameter `lance_debug` controls logging. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on m68k/Sun3 architecture headers, IDPROM machine data, DVMA allocation/address translation, cache flushing, low-level I/O register access, Linux netdev/SKB APIs, fixed IRQ registration, and module init/exit. It does not use PCI, NAPI, DMA API, ethtool, or phylib.

## Risks
The driver is hardware- and architecture-specific and relies on empirical fixed addresses/IRQs. It uses old-style bit locking and direct interrupt disabling rather than modern spinlock patterns. Cleanup unregisters and frees the netdev but does not visibly free the DVMA allocation or IRQ in module exit after probe success, which is a legacy lifetime concern. Multicast support is marked untested and mostly uses broad filtering. Cache coherency depends on `flush_cache_all` in interrupt handling.

## Test Signals
Real validation requires Sun3/Sun3x hardware or emulator support. Signals include successful probe at expected address/IRQ, BOOTP/NFS-root traffic, TX/RX packet counters, TX timeout recovery, CSR memory-error restart, multicast/promiscuous toggles, module parameter debug logs, and module unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sun3lance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sunlance.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sunlance.c

## Purpose
`sunlance.c` is the Linux SPARC/SBus LANCE Ethernet driver. It supports LANCE devices behind plain SBus, `ledma`, or `lebuffer`, with either coherent DVMA memory or PIO buffer access. It registers as a platform driver for Open Firmware nodes named `le` and provides netdev and basic ethtool integration for classic Sun systems.

## Important APIs, Types, And Functions
Hardware formats are `struct lance_rx_desc`, `struct lance_tx_desc`, and `struct lance_init_block`. `struct lance_private` stores LANCE registers, DMA registers, coherent or PIO init-block storage, ring cursors, platform-device links, cable-selection state, burst-size settings, busmaster CSR value, function pointers for DVMA/PIO ring/RX/TX implementations, multicast timer, and DMA address. Major functions include `load_csrs`, `lance_init_ring_dvma`, `lance_init_ring_pio`, `init_restart_ledma`, `init_restart_lance`, `lance_rx_dvma`, `lance_tx_dvma`, `lance_rx_pio`, `lance_tx_pio`, `lance_open`, `lance_close`, `lance_reset`, `lance_start_xmit`, `lance_set_multicast`, `sparc_lance_probe_one`, `sunlance_sbus_probe`, and `sunlance_sbus_remove`.

## Control Flow
The platform probe determines whether the parent is `ledma`, `lebuffer`, or neither, then calls `sparc_lance_probe_one`. Probe allocates a netdev, maps LANCE registers, optionally maps LEDMA registers, either maps PIO `lebuffer` memory or allocates coherent init-block memory, selects the DVMA or PIO function set, derives busmaster and burst settings from device tree properties, resolves cable selection/auto-carrier detection, resets LEDMA, sets netdev ops/ethtool ops/IRQ, initializes a multicast retry timer, registers the netdev, and stores driver data.

Open stops LANCE, requests IRQ, programs LEDMA high address bits for DVMA, clears mode and multicast filters, initializes rings, loads CSR1/2/3, starts the netdev queue, initializes/restarts the chip, and optionally sends a fake packet to detect carrier loss during auto-select. Interrupts ack CSR0 sources, clear errors, call selected RX/TX handlers, count babble/miss errors, and on memory error stop, reset DMA FIFO, reinitialize rings, reload CSRs, restart, and wake the queue.

TX copies packet data into the selected TX buffer path, pads to `ETH_ZLEN`, sets ownership, advances the ring, stops the queue when full, kicks transmit demand, and frees the SKB. TX completion handlers update collision/error stats, toggle TPE/AUI on carrier loss when auto-select is enabled, restart on buffer/underflow errors, and wake the queue. RX handlers copy completed packets into SKBs and return descriptors to chip ownership. Multicast updates stop and restart the chip; if TX is active they defer through a timer.

## State And Persistence
Runtime state includes coherent/Pio init block, descriptor rings and packet buffers, ring indices, cable selection (`tpe`, `auto_select`), LEDMA burst settings, multicast timer, mapped resources, and netdev stats. There is no disk persistence. Device-tree properties and IDPROM MAC address seed initial runtime state.

## Dependencies And Integration Points
The file depends on SPARC/SBus platform devices, Open Firmware properties, SBUS read/write helpers, LEDMA register definitions, auxio link-test control, IDPROM, DMA coherent allocation, netdev/SKB APIs, ethtool driver info, timers, IRQs, and platform-driver registration.

## Risks
Two access paths, DVMA and PIO, must remain behaviorally equivalent. Hardware cache/DMA quirks are handled with register readbacks, FIFO invalidation, and LEDMA burst configuration; regressions are hard to detect without old hardware. Multicast changes defer when TX is busy because callbacks can come from interrupt context. Auto carrier selection intentionally toggles media on carrier loss and can be disruptive if the platform properties are wrong. Resource cleanup must match whether registers, LEDMA, PIO buffer, or coherent memory were allocated.

## Test Signals
Validation requires SPARC/SBus hardware or suitable emulation. Test probe on plain, LEDMA, and lebuffer configurations; RX/TX traffic; queue full/wake; carrier-loss auto-selection; multicast/promiscuous changes during active TX; TX underflow restart; memory-error restart; platform remove cleanup; and `ethtool -i`/link reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sunlance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/Makefile

## Purpose
This Makefile defines the Kbuild composition for the AMD XGBE Ethernet driver. It builds `amd-xgbe.o` when `CONFIG_AMD_XGBE` is enabled and conditionally includes PCI, DCB, and debugfs support objects based on their Kconfig symbols.

## Important APIs, Types, And Functions
There are no runtime APIs in this Makefile. Build variables are `obj-$(CONFIG_AMD_XGBE) += amd-xgbe.o`, `amd-xgbe-objs := ...` for the core object list, and conditional object additions `amd-xgbe-$(CONFIG_PCI)`, `amd-xgbe-$(CONFIG_AMD_XGBE_DCB)`, and `amd-xgbe-$(CONFIG_DEBUG_FS)`.

## Control Flow
Kbuild links the fixed object list into `amd-xgbe.o`: main driver, netdev operations, hardware operations, descriptors, ethtool, MDIO, hardware timestamping, PTP/PPS, I2C, two PHY variants, platform support, and self-test. If PCI support is enabled, `xgbe-pci.o` is included. If AMD XGBE DCB support is enabled, `xgbe-dcb.o` is included. If debugfs is enabled, `xgbe-debugfs.o` is included.

## State And Persistence
The file has no runtime state. Its persistent role is the source-to-object build contract for XGBE. Configuration symbols determine which feature code is compiled into the driver.

## Dependencies And Integration Points
It integrates with Kbuild and Kconfig symbols `CONFIG_AMD_XGBE`, `CONFIG_PCI`, `CONFIG_AMD_XGBE_DCB`, and `CONFIG_DEBUG_FS`. Runtime integration for the listed objects includes netdev, MDIO, PTP, I2C, platform, PCI, DCB, debugfs, and self-test subsystems, but those are implemented in the referenced source files rather than in this Makefile.

## Risks
Incorrect object membership can cause missing symbols, disabled features, or dead code in certain configurations. Conditional objects must stay aligned with preprocessor/Kconfig guards in the source. Since self-test is always in the base object list, build breakage in self-test affects all XGBE builds.

## Test Signals
Run build matrix checks with `CONFIG_AMD_XGBE` built-in and modular, with PCI on/off where supported, `CONFIG_AMD_XGBE_DCB` on/off, and `CONFIG_DEBUG_FS` on/off. Link checks should confirm optional symbols appear only under the right configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/Makefile -->
