# subset-b-003925 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip.h

Purpose: HFI1 chip-facing contract header. It collects hardware dimensions, packet buffer control fields, interrupt source numbering, link-state and 8051 firmware constants, resource-lock bits, receive/transmit counter indexes, CSR access helpers, and prototypes for chip, firmware, interrupt, counter, link, QSFP, and context management code.

Important APIs/types: `read_csr()`, `write_csr()`, `read_kctxt_csr()`, `write_kctxt_csr()`, `read_uctxt_csr()`, `write_uctxt_csr()`, `get_csr_addr()`, `create_pbc()`, `acquire_chip_resource()`, `release_chip_resource()`, `set_link_state()`, `start_freeze_handling()`, `update_usrhead()`, `hfi1_read_cntrs()`, interrupt handlers, and `struct is_table` are the major exported surfaces. The `C_*` counter enums are shared indexes for device and port counter arrays and must stay aligned with counter read code.

Control flow: there is no body-level control flow beyond inline CSR address calculation and VL/index conversion. Runtime control flow is defined by call contracts: chip code reads capability CSRs, programs context CSRs with kernel or user spacing, arbitrates ASIC shared resources through scratch bits and mutexes, transitions link state through workqueue handlers, and dispatches interrupts using source ranges and `is_table` entries.

State and persistence: the header describes persistent hardware state in CSRs, 8051 data memory/config fields, ASIC scratch resource flags, PBC words, RcvArray/TID entries, and per-VL counters. Software persistence is indirect through `struct hfi1_devdata`, `struct hfi1_pportdata`, and `struct hfi1_ctxtdata` fields manipulated by the declared functions.

Dependencies and integration: includes `chip_registers.h` and relies on kernel bit macros plus HFI1 core structs from other headers. Nearly every HFI1 implementation file consumes these definitions, so it is the central integration point between register metadata, firmware loading, link management, receive handling, send DMA, debugfs, and counter export.

Risks: ABI drift in bit masks, enum order, interrupt ranges, or CSR spacing can corrupt hardware programming without compiler errors. The distinction between 0x100 kernel-context CSR spacing and 0x1000 user-context spacing is safety critical because user-mappable CSRs must not expose adjacent contexts. Resource bits in ASIC scratch are shared between HFI instances and OSes, so incorrect acquisition/release can deadlock or race external firmware/QSFP/EPROM access.

Test signals: build coverage across the whole driver, register trace review during probe, counter name/value alignment tests, interrupt source remapping tests, link bringup/down testing, resource lock contention tests on dual-HFI devices, and receive/send smoke tests that validate the PBC/RHF/TID field constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip_registers.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip_registers.h

Purpose: generated-style register map for HFI1 silicon. It names the base address blocks (`CORE`, `ASIC`, `MISC`, `DCC_CSRS`, `DC_LCB_CSRS`, `DC_8051_CSRS`, `RXE`, `TXE`, `CCE`, PCIe) and defines offsets, reset values, masks, shifts, and status bits for link, firmware, receive, send, DMA, interrupt, GPIO, QSFP, EEPROM, thermal, PCIe, and error reporting registers.

Important APIs/types: this header exports macros only. Important families include `DCC_CFG_*` link/port configuration, `DC_DC8051_*` firmware command/status/RAM access, `DC_LCB_*` link-control-block status and error bits, `ASIC_*` SBUS/GPIO/QSFP/EEPROM/thermal registers, `CCE_*` interrupt/MSI-X/error registers, `RCV_*` context/TID/header/eager/QP-map registers, and `SEND_*` PIO, SDMA, egress, credit, SC/VL, and error registers.

Control flow: no executable control flow is present. Driver code composes these offsets with `read_csr()`, `write_csr()`, `read_kctxt_csr()`, `write_kctxt_csr()`, `read_uctxt_csr()`, and per-engine/per-context strides defined in `chip.h`.

State and persistence: every macro corresponds to persistent device state or W1C/W1S status in MMIO, PCI config space, or firmware-facing register windows. Hardware state includes interrupt routing, receive queue heads/tails, TID tables, send contexts, SDMA descriptors, credit accounting, port link state, 8051 requests, QSFP GPIO state, EEPROM controller mode, and accumulated counters.

Dependencies and integration: consumed by `chip.h` and all low-level HFI1 implementation files. It is the single source for field masks used by chip init, firmware loading, IRQ setup, debugfs CSR windows, EPROM access, link-state changes, receive queue management, and send/SDMA programming.

Risks: macro mistakes are high blast radius: a wrong mask or offset can acknowledge the wrong interrupt, clear error state, expose user contexts, or program packet routing incorrectly. Because many values are raw constants rather than typed fields, misuse is usually detected only by hardware behavior. W1C and reset-value semantics must be preserved when callers modify bitfields.

Test signals: compile coverage is necessary but insufficient. Useful signals are probe register traces, MSI-X mapping checks, link bringup, receive/send loopback, SDMA stress, error injection with expected status bits, EPROM/QSFP diagnostics, and comparison against hardware specification or generated-register provenance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/common.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/common.h

Purpose: kernel/user shared HFI1 protocol definitions. It defines protocol versioning, capability-mask layout and mutation macros, default/reserved capability policy, receive header flag (RHF) bitfields, receive type constants, LRH/KDETH constants, MTU/padding/PKey constants, and inline RHF decoders.

Important APIs/types: `HFI1_CAP_*` macros manipulate the global `hfi1_cap_mask` for kernel and user capability domains. `HFI1_CAP_WRITABLE_MASK`, `HFI1_CAP_RESERVED_MASK`, `HFI1_CAP_MUST_HAVE_KERN`, `HFI1_CAP_MASK_DEFAULT`, and `HFI1_CAP_K2U` define policy. Inline helpers include `rhf_to_cpu()`, `rhf_err_flags()`, `rhf_rcv_type()`, `rhf_rcv_type_err()`, `rhf_pkt_len()`, `rhf_egr_index()`, `rhf_rcv_seq()`, `rhf_hdrq_offset()`, `rhf_use_egr_bfr()`, `rhf_dc_info()`, and `rhf_egr_buf_offset()`.

Control flow: no complex flow exists here. Runtime receive code reads the 64-bit RHF from the header queue, decodes packet type, length, eager-buffer index/offset, sequence, and error bits through these helpers, then dispatches to type-specific handlers in `driver.c`.

State and persistence: capability state persists in the module-global `hfi1_cap_mask`, with separate kernel/user bit ranges and a locked bit. RHF values are persistent hardware-produced queue entries until the receive head is advanced. The header also defines constants shared with user-space ABI via `rdma/hfi/hfi1_user.h`.

Dependencies and integration: includes the public HFI1 user ABI header and is consumed by receive, user-context, and TID paths. Its RHF decoders are on the performance-sensitive receive hot path, and its capability masks are used by module parameter parsing in `driver.c`.

Risks: capability policy mistakes can expose unsupported features to user processes or allow user contexts without kernel support. RHF length and offset units differ by field: packet length returns bytes, header/eager offsets are derived from dword or 64-byte block units. Any change to bit positions must match hardware and user ABI.

Test signals: cap-mask module parameter tests, user-context open tests, receive packet parsing across expected/eager/IB/bypass/error types, error flag reporting, and ABI compatibility checks against user-space libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.c

Purpose: debugfs diagnostics and privileged control surface for HFI1 devices. It creates global driver stats files plus per-device files for opcode stats, context stats, QP stats, SDMA engines, receive contexts, PIO contexts, counters, port counters, QSFP/I2C access, ASIC resource flags, 8051 memory, LCB CSR access, expansion-ROM write protection, and fault-injection integration.

Important APIs/functions: `hfi1_dbg_init()`, `hfi1_dbg_exit()`, `hfi1_dbg_ibdev_init()`, and `hfi1_dbg_ibdev_exit()` own debugfs lifetime. The file defines many seq-file iterators (`opcode_stats`, `tx_opcode_stats`, `ctx_stats`, `qp_stats`, `sdes`, `rcds`, `pios`, `sdma_cpu_list`, `driver_stats_names`, `driver_stats`) and read/write handlers for counters, port counters, `asic_flags`, `dc8051_memory`, `lcb`, `i2c1/2`, `qsfp1/2`, `qsfp_dump`, and `exprom_wp`.

Control flow: global init creates `/sys/kernel/debug/hfi1` and driver stats. Per-device init creates `hfi1_<unit>` plus a unit symlink, then registers seq files and per-port files. Reads aggregate statistics from contexts, per-CPU transmit stats, xarray device table, hardware counters, or low-level chip accessors. Writes to ASIC flags, I2C/QSFP, LCB, and expansion-ROM protection parse user input, validate offsets/sizes, acquire chip resources where required, perform hardware access, and release resources on close or release.

State and persistence: persistent state includes the root dentry, per-device debugfs dentries stored on `struct hfi1_ibdev`, hardware resource bits in `ASIC_CFG_SCRATCH`, EEPROM/QSFP/LCB/8051 hardware state, global `exprom_wp_disabled`, and `exprom_in_use` single-open protection. The debugfs files expose live counters and can modify persistent hardware state until reset or driver cleanup.

Dependencies and integration: depends on Linux debugfs/seq_file/fault-inject APIs and on HFI1 modules for QP iteration, SDMA dumps, QSFP/I2C access, chip resources, CSR access, counter readers, and fault debugfs. It is called from driver/module and per-IB-device registration paths.

Risks: debugfs write handlers are intentionally powerful and require root/write permissions, but incorrect validation can touch raw I2C devices, LCB CSRs, ASIC scratch flags, or expansion-ROM write protection. `fault_opcodes_read()` in `fault.c` can expose an empty-bitmap bug, but debugfs here invokes that subsystem. The I2C offset encoding in `ppos` rejects address 0 to catch accidental `cat`/`cp`, but still allows arbitrary device offsets for valid addresses. Resource acquisition on open and release must remain symmetric.

Test signals: debugfs tree creation/removal on probe/remove, repeated open/close of QSFP/I2C/exprom files, counter reads under traffic, context/QP seq iteration under teardown, LCB read/write alignment validation, EPROM write-protect release restoring protection, and `CONFIG_DEBUG_FS=n` build coverage through `debugfs.h` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.h

Purpose: debugfs helper interface for HFI1. It provides seq-file boilerplate macros and the public lifecycle hooks used by the driver to create or destroy global and per-device debugfs entries.

Important APIs/types: `DEBUGFS_SEQ_FILE_OPS(name)`, `DEBUGFS_SEQ_FILE_OPEN(name)`, and `DEBUGFS_FILE_OPS(name)` generate `seq_operations`, open helpers that set `seq->private = inode->i_private`, and file operations. Public functions are `hfi1_dbg_ibdev_init()`, `hfi1_dbg_ibdev_exit()`, `hfi1_dbg_init()`, and `hfi1_dbg_exit()`, with no-op inline stubs when `CONFIG_DEBUG_FS` is disabled.

Control flow: implementation files define `_name_seq_start/next/stop/show`, invoke the macros, and pass the generated file ops to `debugfs_create_file()`. The conditional declarations allow callers to invoke debugfs setup unconditionally while build configuration decides whether anything happens.

State and persistence: no state is stored in this header. It standardizes how seq files preserve the HFI1 object pointer passed as `inode->i_private`.

Dependencies and integration: used by `debugfs.c` and `fault.c`. It relies on Linux `seq_file`, `file_operations`, and `THIS_MODULE` symbols being visible through including translation units.

Risks: the macros assume each caller uses the exact `_name_seq_*` naming convention and that `inode->i_private` remains valid for the lifetime of the open file. Any generated file operation has a fixed `seq_release`, so custom private allocations require separate file ops.

Test signals: build with debugfs enabled and disabled, seq-file read smoke tests for each generated file, and device removal while debugfs files are open to catch lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.c

Purpose: character-device class and node management for HFI1. It allocates the major range, registers kernel-only and user-accessible device classes, creates device nodes for individual minors, and cleans them up.

Important APIs/functions: `dev_init()` allocates the chrdev region and registers `hfi1` and `hfi1_user` classes. `hfi1_cdev_init()` initializes a `struct cdev`, sets its parent/name, adds it to the device number, and creates a device node in the correct class. `hfi1_cdev_cleanup()` unregisters the device and deletes the cdev. `class_name()` returns `"hfi1"` for debugfs naming.

Control flow: module init calls `dev_init()`. Per-device or per-file setup calls `hfi1_cdev_init()` with a minor, file ops, access flag, and kobject parent. Failures unwind in order: device creation failure deletes the cdev, class registration failure unregisters the range. Cleanup unregisters classes and frees the chrdev range.

State and persistence: `hfi1_dev` stores the allocated major/minor base. The `class` devnode helper gives kernel/control nodes mode `0600`; `user_class` gives user nodes mode `0666`. Created `struct device *` pointers are stored by callers and nulled during cleanup.

Dependencies and integration: depends on Linux cdev, device, and fs APIs plus HFI1 constants such as `HFI1_NMINORS` and `DRIVER_NAME`. Other driver code uses this helper to expose user and control file operations.

Risks: node permissions are security relevant: passing `user_accessible=true` creates world-readable/writable nodes. Cleanup only calls `cdev_del()` when a device pointer exists, so callers must not manually clear `*devp` before cleanup. Class registration/unregistration ordering must remain symmetric.

Test signals: module load/unload, udev-visible node modes, failed device_create injection, repeated cdev setup/cleanup, and user-open tests for the intended minors only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.h

Purpose: public declarations for HFI1 character-device setup and cleanup.

Important APIs/types: declares `hfi1_cdev_init()`, `hfi1_cdev_cleanup()`, `class_name()`, `dev_init()`, and `dev_cleanup()`. The init helper accepts the minor number, node name, `file_operations`, cdev storage, output device pointer, user-accessible flag, and parent kobject.

Control flow: module and per-device code include this header to initialize the global device subsystem, create per-minor nodes, and tear them down on remove or error unwind.

State and persistence: no state is stored in the header. It describes ownership rules for caller-provided `struct cdev` and `struct device **`.

Dependencies and integration: relies on cdev/device types being visible from including files or previous includes. It is used by HFI1 init and debugfs naming code.

Risks: the API exposes permission choice as a boolean; wrong caller choice can expose privileged file operations. The cleanup contract requires the same `cdev` and device pointer created by `hfi1_cdev_init()`.

Test signals: compile coverage, cdev open path tests, device node permission checks, and error-unwind tests around partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/driver.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/driver.c

Purpose: core HFI1 receive-path, capability, MTU/LID, LED override, and reset logic. It owns module parameters (`max_mtu`, `cu`, `cap_mask`), global driver statistics, active-unit counting, receive header/eager-buffer parsing, ECN/CNP processing, slow/fast interrupt receive loops, packet type dispatch, IPoIB receive handoff, and several port state helpers.

Important APIs/functions: `hfi1_caps_set()`, `hfi1_caps_get()`, `get_pci_dev()`, `hfi1_count_active_units()`, `hfi1_rcvbuf_validate()`, `hfi1_process_ecn_slowpath()`, `handle_receive_interrupt_napi_fp()`, `handle_receive_interrupt_nodma_rtail()`, `handle_receive_interrupt_dma_rtail()`, `handle_receive_interrupt()`, `handle_receive_interrupt_napi_sp()`, `receive_interrupt_work()`, `mtu_to_enum()`, `enum_to_mtu()`, `set_mtu()`, `hfi1_set_lid()`, `hfi1_start_led_override()`, `shutdown_led_override()`, `hfi1_reset_device()`, `handle_eflags()`, `seqfile_dump_rcd()`, `normal_rhf_rcv_functions`, and `netdev_rhf_rcv_functions`.

Control flow: receive interrupt handlers initialize an `hfi1_packet` from the current receive header queue head, determine queue completion by sequence or DMA tail, optionally prescan for ECN, process packets via `rhf_rcv_function_map`, periodically update user/kernel receive heads, flush pending QP response work, and finally call `update_usrhead()` to rearm interrupts. The slow path also handles link armed-to-active transition, control-context invalid RHFs, drop mode, and switching static contexts back to fast handlers. Packet dispatch parses 9B, 16B bypass, expected, eager, error, and invalid RHF types, then calls verbs, TID RDMA, 16B, IPoIB, or error handlers.

State and persistence: persistent software state includes `hfi1_cap_mask`, `hfi1_stats`, receive context queue heads and sequence numbers, QP wait lists, per-port LID/LMC/MTU/link state, LED override timer state, and fault-injection counters through calls into `fault.c`. Hardware state is touched through receive head updates, MTU/VL config, LED CSR writes, and reset/reinitialization.

Dependencies and integration: integrates RDMA core (`rvt_qp`, QP lookup/state, verbs receive/send scheduling), HFI1 chip helpers, SDMA reset, tracepoints, IPoIB/netdev receive, congestion control (`process_becn`, CNP handlers), TID RDMA handlers, and debugfs dump functions.

Risks: this is hot-path code with deliberate omitted bounds checks on RHF type dispatch because hardware is trusted. Queue head/tail, RHF sequence, and DMA memory barrier ordering are correctness critical. `set_all_fastpath()` changes interrupt handlers while processing packets, so context references and teardown ordering matter. ECN prescan mutates BTH bits in-place. `hfi1_reset_device()` refuses reset with open contexts but still performs a broad reinitialization path that depends on cleanup and hardware availability.

Test signals: receive stress across no-DMA-tail, DMA-tail, NAPI fast, and NAPI slow modes; link armed-to-active traffic; ECN/FECN/BECN/CNP behavior; TID expected/eager receive; 9B and 16B packet parsing; IPoIB receive; fault-injection packet drops; MTU change while link is up with VL drain; LED override timer; and reset with/without open contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.c

Purpose: HFI1 EFI variable reader. It retrieves per-device firmware/platform data stored as EFI runtime variables under an HFI1-specific GUID, using PCI domain/bus/slot/function plus a caller-provided kind suffix.

Important APIs/functions: internal `read_efi_var()` reads a named EFI variable into a kmalloc buffer and returns its actual size. Public `read_hfi1_efi_var()` builds `<domain>:<bus>:<slot>.<func>-<kind>`, tries lowercase PCI address first, then uppercase, and returns the allocated data to the caller.

Control flow: `read_efi_var()` checks EFI GetVariable support, allocates a UTF-16 variable name and 4 KiB temporary buffer, converts ASCII to UTF-16 by direct widening, calls `efi.get_variable()`, maps status to `0`, `-ENOENT`, or `-EINVAL`, duplicates the exact result length, and cleans temporary allocations. `read_hfi1_efi_var()` handles the name fallback.

State and persistence: no driver state persists here. Persistent data lives in firmware EFI variable storage. On success, ownership of a newly allocated buffer and size is transferred to the caller; on failure, outputs are guaranteed NULL/zero by `read_efi_var()`.

Dependencies and integration: depends on Linux EFI runtime support, PCI address helpers, `string_upper()`, and `struct hfi1_devdata` from `hfi.h`. It is an alternate platform configuration source alongside EPROM.

Risks: all non-success/non-not-found EFI statuses collapse to `-EINVAL`, losing diagnostics such as buffer-too-small. `EFI_DATA_SIZE` is fixed at 4096 bytes; larger variables are not retried with the required size. EFI runtime calls can be unavailable or platform-sensitive, so callers must handle `-EOPNOTSUPP`, `-ENOENT`, and malformed data.

Test signals: EFI unsupported path, missing variable path, lowercase and uppercase PCI-name fallback, correct buffer size/content return, allocation failure injection, and validation by the caller that consumes the returned platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.h

Purpose: declaration header for HFI1 EFI variable access.

Important APIs/types: includes Linux EFI and HFI1 core definitions, and declares `read_hfi1_efi_var(struct hfi1_devdata *dd, const char *kind, unsigned long *size, void **return_data)`.

Control flow: callers use this function when they need per-adapter EFI-backed configuration data. The implementation allocates the returned buffer and reports the byte count.

State and persistence: no state is stored in the header. The API exposes firmware-persistent data as caller-owned kernel memory.

Dependencies and integration: integrated with platform configuration loading code and the HFI1 device data model.

Risks: caller must free returned data on success and treat failure outputs as empty. The header includes `hfi.h`, which may be heavier than a forward declaration but gives the implementation and callers a consistent `struct hfi1_devdata` view.

Test signals: compile coverage, EFI config read integration, and caller cleanup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/efivar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.c

Purpose: EPROM controller support and platform configuration extraction for discrete HFI1 devices. It initializes the SPI EPROM controller, reads arbitrary EPROM byte ranges via page reads, and locates a platform configuration file in either legacy partition format or segment/table-of-contents format.

Important APIs/functions: `eprom_init()` resets and wakes the EPROM controller and marks `dd->eprom_available`. `eprom_read_platform_config()` arbitrates EPROM access and returns allocated platform config data. Internal helpers include `read_page()`, `read_length()`, `read_partition_platform_config()`, and `read_segment_platform_config()`. Local metadata types are `struct hfi1_eprom_footer` and `struct hfi1_eprom_table_entry`.

Control flow: initialization only runs for discrete PCI device ID `PCI_DEVICE_ID_INTEL0`, acquires `CR_EPROM`, resets the controller, sets full speed, sends release-powerdown, and releases the resource. Reads acquire `CR_EPROM`, read the last page of the first 128 KiB segment, choose segment mode if `FOOTER_MAGIC` is present, otherwise read partition 1. Segment mode validates footer version, oprom size, table bounds, finds file type `HFI1_EFT_PLATFORM_CONFIG`, validates size and offset arithmetic, then copies file bytes across segments while skipping footer/table space in segment zero. Partition mode reads the 4 KiB config partition, checks `APO=` magic, and trims at trailing `egamiAPO` if found.

State and persistence: hardware-persistent state is the external EPROM contents and SPI controller state. Software persistent state is `dd->eprom_available`; returned buffers are caller-owned. The shared ASIC resource bit prevents concurrent EPROM access across HFI instances.

Dependencies and integration: uses CSR definitions from `chip_registers.h` through `hfi.h`, common definitions, chip resource arbitration, PCI device IDs, and kernel allocation/copy helpers. Platform initialization code can consume this data when EFI variables are absent or unsuitable.

Risks: the EPROM may wrap reads beyond physical size even when addresses fit the command field, so malformed offsets can return unexpected but hardware-valid data. Segment parsing must defend against footer/table overlap, oversized config files, and integer wrap. The 80 second resource timeout reflects erase/write time, so callers can block for a long time. Only discrete chips are supported.

Test signals: EPROM init on discrete and non-discrete devices, resource contention, valid partition and segment images, missing magic, bad footer version, oversize config entry, offset wrap rejection, cross-segment file extraction, and caller validation of returned config bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.h

Purpose: declaration header for HFI1 EPROM support.

Important APIs/types: forward-declares `struct hfi1_devdata` and declares `eprom_init()` plus `eprom_read_platform_config()`.

Control flow: probe or chip init calls `eprom_init()` before attempting EPROM-backed platform configuration. Configuration loading calls `eprom_read_platform_config()` and receives allocated data plus size.

State and persistence: no header-local state. The implementation records EPROM availability in `struct hfi1_devdata` and returns caller-owned buffers.

Dependencies and integration: lightweight interface used by platform configuration and chip initialization code.

Risks: callers must handle `-ENXIO` for unavailable EPROM and must free the returned buffer on success. The header has no include guard in this snapshot, so repeated direct inclusion relies on normal include ordering not to cause declaration conflicts; the declarations themselves are idempotent but a guard would be safer.

Test signals: compile coverage for multiple inclusion paths, EPROM absent/present probe, and successful platform config read/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.c

Purpose: expected receive TID group lifecycle for HFI1 contexts. It initializes free/used/full TID group lists, allocates group descriptors for a receive context, and frees them while clearing hardware TID state.

Important APIs/functions: `hfi1_exp_tid_group_init()` initializes `rcd->tid_group_list`, `rcd->tid_used_list`, and `rcd->tid_full_list`. `hfi1_alloc_ctxt_rcv_groups()` allocates `rcd->groups` on the context NUMA node and seeds free groups based on `expected_base`, `expected_count`, and `dd->rcv_entries.group_size`. `hfi1_free_ctxt_rcv_groups()` frees group storage, reinitializes lists, and calls `hfi1_clear_tids()`.

Control flow: allocation calculates `ngroups = expected_count / group_size`, allocates an array, then loops assigning each group a base TID, size, and list entry. Freeing drops the array, resets list heads/counts, and clears TIDs from hardware/software context state.

State and persistence: persistent context state includes `rcd->groups` and the three `exp_tid_set` lists. Hardware receive array/TID entries may persist until `hfi1_clear_tids()` clears them. Group fields track base, size, used count, and bitmap-like map state.

Dependencies and integration: depends on `exp_rcv.h`, `hfi.h`, list helpers, NUMA allocation, and chip receive-entry sizing. Higher-level TID RDMA/user memory registration code consumes these group lists to allocate expected receive entries.

Risks: allocation silently truncates if `expected_count` is not an exact multiple of `group_size`; the rest of the driver likely guarantees alignment, but that invariant matters. Freeing is documented for kernel and base user contexts; calling it on an active context would invalidate TID state. Group list counts must remain synchronized with list mutations in inline helpers.

Test signals: context allocation/free cycles, NUMA allocation failure, expected_count/group_size boundary cases, TID registration/unregistration stress, and verification that hardware TID entries are cleared during context teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.h

Purpose: expected receive/TID helper header. It defines TID field encoders, KDETH header field accessors, TID group data structures, list operations, write-combining receive-array fill helper, TID creation helper, and group index conversion APIs.

Important APIs/types: `struct tid_group` stores a list node, base receive entry, size, used count, and map. `EXP_TID_GET/SET/CLEAR/RESET` manipulate expected TID descriptor fields. `KDETH_GET/SET/RESET` manipulate little-endian KDETH dwords. `rcv_array_wc_fill()`, `tid_group_add_tail()`, `tid_group_remove()`, `tid_group_move()`, `tid_group_pop()`, `create_tid()`, `hfi1_tid_group_to_idx()`, and `hfi1_idx_to_tid_group()` are inline helpers. Prototypes mirror the implementation in `exp_rcv.c`.

Control flow: TID management code initializes lists, pops free groups, moves them between free/used/full sets as registrations consume entries, creates encoded TID values from receive-array indexes and page counts, updates KDETH templates, and optionally writes zero fills to the write-combined RcvArray mapping.

State and persistence: TID descriptor values are hardware-facing state. `struct tid_group` instances persist per receive context in `rcd->groups`; `exp_tid_set.count` mirrors each list. Write-combined RcvArray fills affect device-visible receive table memory and flush every fourth entry.

Dependencies and integration: includes `hfi.h` for core context/device structures and uses Linux list, endian, writeq, and WC flush primitives through that include chain. It is consumed by TID RDMA and expected receive code.

Risks: bitfield encoders must match hardware and KDETH ABI exactly. `tid_group_pop()` assumes the set is non-empty; callers must check `EXP_TID_SET_EMPTY()` or equivalent. `rcv_array_wc_fill()` only flushes on indexes where `(index & 3) == 3`, so callers ending on other indexes need a final flush elsewhere if ordering matters. Pointer arithmetic in group/index conversion assumes `grp` belongs to `rcd->groups`.

Test signals: TID encode/decode round trips, KDETH field mutation tests, registration stress with group moves, empty-set guard tests, WC fill ordering on real hardware, and teardown clearing expected receive entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/exp_rcv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.c

Purpose: HFI1 debug fault-injection support for transmit and receive packet paths. It creates a per-device debugfs `fault` directory, allows opcode and direction filtering, tracks injected fault counts, and provides fast-path helpers that decide whether to drop/fault a packet.

Important APIs/functions: `hfi1_fault_init_debugfs()`, `hfi1_fault_exit_debugfs()`, `hfi1_dbg_fault_suppress_err()`, `hfi1_dbg_should_fault_tx()`, and `hfi1_dbg_should_fault_rx()` are the public hooks. Internal helpers include seq-file `fault_stats`, `fault_opcodes_read()`, `fault_opcodes_write()`, and `__hfi1_should_fault()`.

Control flow: initialization allocates `struct fault`, seeds `fault_attr`, default direction `TXRX`, skip counters, booleans, and opcode bitmap, then creates debugfs controls (`enable`, `suppress_err`, `opcode_mode`, `opcodes`, `skip_pkts`, `skip_usec`, `direction`, `fault_stats`). The opcode writer parses comma-separated values/ranges, optional leading `-` removals, and `-1` as clear-all. Runtime checks require fault object, enable flag, matching direction, optional opcode bitmap match, skip time/count expiration, then delegate probability/interval logic to `should_fail()`. Successful injection resets skip state, traces, and increments opcode counters.

State and persistence: per-IB-device `ibd->fault` persists until debugfs exit. State includes Linux `fault_attr`, debugfs dentry, opcode bitmap, enable/suppress/opcode booleans, direction, skip counters, skip deadline in jiffies, and per-opcode RX/TX fault counters.

Dependencies and integration: depends on Linux fault-inject debugfs, bitmap helpers, seq_file, tracepoints, HFI1 packet/QP structures, and debugfs helper macros. Receive code calls `hfi1_dbg_should_fault_rx()` after packet setup; send paths call `hfi1_dbg_should_fault_tx()`.

Risks: debugfs controls intentionally alter packet behavior and should be available only in fault-injection debug builds. `fault_opcodes_read()` writes `data[size - 1] = '\n'` even if no opcodes are set, which can underflow the buffer index; an empty bitmap read should be tested. Opcode parsing returns success length even if parsing stops early, so invalid tail input may be silently ignored. Runtime fields are not explicitly locked, relying on debug/test usage and primitive atomicity.

Test signals: build with and without `CONFIG_FAULT_INJECTION_DEBUG_FS`, debugfs creation/removal, opcode add/remove/range/clear parsing, empty opcode read, direction filtering, skip packet/time behavior, `should_fail()` interval/probability behavior, TX/RX counter increments, and suppress-error behavior in receive error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.h

Purpose: conditional public interface and state definition for HFI1 packet fault injection.

Important APIs/types: when fault injection debugfs is enabled, `struct fault` contains `fault_attr`, debugfs dentry, per-opcode RX/TX counters, skip controls, opcode bitmap, enable/suppress/opcode flags, and direction. It declares `hfi1_fault_init_debugfs()`, `hfi1_fault_exit_debugfs()`, `hfi1_dbg_should_fault_tx()`, `hfi1_dbg_should_fault_rx()`, and `hfi1_dbg_fault_suppress_err()`. Otherwise it provides inline stubs returning no fault and success.

Control flow: callers can invoke the API unconditionally. Build configuration decides whether debugfs controls exist and whether runtime checks can inject faults.

State and persistence: with fault injection enabled, state persists per `struct hfi1_ibdev` through `ibd->fault`. With the stub configuration, no state exists and packet paths are unaffected.

Dependencies and integration: includes Linux fault injection, dcache, bitops, kernel, RDMA VT, and `hfi.h`. Integrated into debugfs setup and send/receive packet paths.

Risks: because the enabled structure is directly manipulated by debugfs files and fast paths, any layout or synchronization change affects packet processing. Stub behavior must remain semantically neutral so production builds do not pay behavior cost.

Test signals: both config variants compile, receive/send code links against stubs, debugfs-enabled builds allocate/free `ibd->fault`, and runtime helpers return false when disabled or not configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.h -->
