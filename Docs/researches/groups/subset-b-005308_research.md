# subset-b-005308 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_transport.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_transport.c

Purpose: implements the Broadcom MPI3MR driver's Linux SAS transport integration. It builds and maintains the `sas_host`, `sas_phy`, `sas_port`, and `sas_rphy` topology exposed to the SCSI/SAS transport class, translates MPI3 firmware discovery/configuration pages into kernel SAS objects, handles expander add/remove and reset refresh, routes target devices into SAS transport ports, and provides transport callbacks for link errors, enclosure/bay identifiers, phy reset/enable/speed control, and SMP passthrough.

Important APIs/types/functions: the central command helper is `mpi3mr_post_transport_req()`, which serializes admin transport commands through `mrioc->transport_cmds`, waits for completion, returns firmware IOC status, and faults the controller on timeout. Discovery and topology helpers include `mpi3mr_sas_host_add()`, `mpi3mr_sas_host_refresh()`, `mpi3mr_update_links()`, `mpi3mr_sas_port_add()`, `mpi3mr_sas_port_remove()`, `mpi3mr_expander_add()`, `mpi3mr_expander_remove()`, `mpi3mr_expander_node_remove()`, `mpi3mr_refresh_sas_ports()`, `mpi3mr_refresh_expanders()`, `mpi3mr_report_tgtdev_to_sas_transport()`, and `mpi3mr_remove_tgtdev_from_sas_transport()`. Lookup/reference helpers include `__mpi3mr_expander_find_by_handle()`, `mpi3mr_is_expander_device()`, `mpi3mr_get_hba_port_by_id()`, `__mpi3mr_get_tgtdev_by_addr_and_rphy()`, and internal SAS-address/HBA-port searches. Transport operation callbacks are collected in `mpi3mr_transport_functions`; the global `mpi3mr_transport_template` is the registered SCSI transport template.

Control flow: target exposure starts with `mpi3mr_report_tgtdev_to_sas_transport()`, which ensures the HBA SAS host exists or is refreshed, finds the parent SAS address and HBA port, updates the parent phy link state, marks the target host-exposed, and creates a SAS port/rphy. Host initialization reads SAS IO Unit Page 0 to determine phys and port IDs, allocates HBA-port entries, reads SAS Phy Page 0 and Device Page 0 for identity, then registers each host phy with the SAS class. Expander addition reads Expander Page 0, recursively adds missing parent expanders, creates the parent SAS port, allocates expander phys from Expander Page 1, registers the expander node, and fills SMP report-manufacture data. Removal walks child ports first, removes attached end devices or child expanders, deletes SAS transport objects, clears phy ownership, and frees in-memory nodes. Reset refresh builds a temporary host-port table from firmware pages, marks existing host ports dirty, matches by SAS address/lowest phy/phy mask, updates port IDs and phy membership, and removes non-responding expanders.

State and persistence: state is runtime-only inside `struct mpi3mr_ioc` and attached objects: `sas_hba`, `sas_expander_list`, `hba_port_table_list`, target device references, `phy_belongs_to_port`, `phy_mask`, `lowest_phy`, `remote_identify`, `rphy`, `parent_dev`, and current-event `pending_at_sml` markers. Firmware-derived state is repeatedly read from MPI3 configuration pages and SMP replies, while hardware-visible changes happen through MPI3 IO Unit Control, SAS IO Unit Page 1 writes, and SMP phy-control requests. The file does not persist data on disk; persistence across reset is reconstructed from firmware pages.

Dependencies and integration points: depends on `mpi3mr.h`, MPI3 config/admin request helpers, DMA coherent allocation and SG mapping, SCSI host private data, Linux SAS transport class APIs, BSG SMP passthrough, spinlocks and mutex/completion synchronization, target-device reference helpers in the core driver, and firmware page formats from the MPI3 headers. It integrates with device event processing through `mrioc->current_event`, with target host exposure/removal via `mpi3mr_remove_tgtdev_from_host()`, and with sysfs/SAS management tools through the transport function template.

Risks: topology mutation spans driver lists and SAS transport objects, so lock ordering and object lifetime are critical. Several paths drop `sas_node_lock` before calling into SAS transport or recursive expander removal, which avoids sleeping under spinlock but requires the objects to remain valid. `mpi3mr_sas_port_remove()` frees an HBA-port entry when removing a host-node port; consumers must not retain stale `hba_port` pointers. SMP helpers subtract four bytes from BSG payload lengths, so short or malformed payloads are a boundary risk. Transport commands are single-slot serialized; concurrent sysfs/SMP operations can receive command-in-use failures. Reset and PCI error recovery short-circuit many paths, so partial add/remove sequences need careful unwind coverage.

Test signals: exercise direct-attached SAS/SATA targets, expander cascades, multi-phy wide ports, HBA port ID changes across reset, cable moves during reset, non-responding expander cleanup, target add followed by missing `starget`, and target removal while host exposure is pending. Validate sysfs link-error reads for HBA and expander phys, enclosure and bay identifier callbacks, hard/link reset, phy disable/enable, speed changes with min/max clamping, discovery-active rejection, SMP passthrough for single- and multi-segment BSG buffers, transport-command timeout faulting, and behavior under `reset_in_progress`, `pci_err_recovery`, and `stop_drv_processing`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Kconfig

Purpose: declares the kernel configuration interface for the MPT3SAS driver family. It exposes the main `SCSI_MPT3SAS` tristate option, tunable maximum scatter-gather entry counts for SAS 2.0 and SAS 3.0 devices, and a legacy `SCSI_MPT2SAS` compatibility symbol that selects the unified MPT3SAS driver.

Important APIs/types/functions: this is Kconfig metadata, not executable C. `config SCSI_MPT3SAS` depends on `PCI && SCSI` and selects `SCSI_SAS_ATTRS`, `RAID_ATTRS`, and `IRQ_POLL`. `config SCSI_MPT2SAS_MAX_SGE` and `config SCSI_MPT3SAS_MAX_SGE` are integer symbols with default `128` and range `16 256`. `config SCSI_MPT2SAS` is a dummy legacy tristate that defaults to `n`, depends on `PCI && SCSI`, and selects `SCSI_MPT3SAS`.

Control flow: build configuration flows from user or defconfig selection. Enabling `SCSI_MPT3SAS` makes the driver eligible for module or built-in compilation and automatically enables SAS transport attributes, RAID attributes, and IRQ polling support. The max-SGE symbols become available only when PCI, SCSI, and MPT3SAS are enabled. Selecting the legacy MPT2SAS option redirects users to the MPT3SAS implementation by selecting the unified driver.

State and persistence: selected Kconfig symbols persist in the kernel `.config` and influence compile-time constants and object inclusion. There is no runtime state in this file.

Dependencies and integration points: integrates with the kernel Kconfig system and the SCSI subsystem's build graph. The selected helper symbols are required by code that exposes SAS transport attributes, RAID class attributes, and IRQ polling behavior. The SGE options are consumed by the MPT3SAS driver sources at compile time to size I/O scatter-gather handling.

Risks: changing dependencies or selected symbols can silently break builds where the driver expects SAS, RAID, or IRQ polling infrastructure. Reducing max-SGE below workload expectations can increase I/O splitting, while increasing it can increase per-controller memory use. The legacy MPT2SAS symbol must remain a compatibility alias rather than building a separate driver.

Test signals: run Kconfig coverage for built-in, module, and disabled combinations; verify old configs containing `CONFIG_SCSI_MPT2SAS` still enable `CONFIG_SCSI_MPT3SAS`; validate boundary values `16`, `128`, and `256` for both max-SGE symbols; and compile with `PCI` or `SCSI` disabled to confirm options disappear cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Makefile

Purpose: defines how the kernel build system links the MPT3SAS driver object when `CONFIG_SCSI_MPT3SAS` is enabled.

Important APIs/types/functions: the makefile adds `mpt3sas.o` to `obj-$(CONFIG_SCSI_MPT3SAS)` and composes that aggregate object from `mpt3sas_base.o`, `mpt3sas_config.o`, `mpt3sas_scsih.o`, `mpt3sas_transport.o`, `mpt3sas_ctl.o`, `mpt3sas_trigger_diag.o`, `mpt3sas_warpdrive.o`, and `mpt3sas_debugfs.o`.

Control flow: when the Kconfig symbol is `y`, these objects are built into the kernel; when `m`, they are linked into the `mpt3sas` module; when unset, none are built. Link order places base/config/SCSI host logic before transport, control, diagnostics, WarpDrive, and debugfs support inside the aggregate object.

State and persistence: this file has no runtime state. Its persistent effect is build-system metadata that determines which translation units are included in the final driver artifact.

Dependencies and integration points: integrates with the kernel kbuild object aggregation convention. It must stay aligned with exported symbols and initialization ordering across the MPT3SAS source files and with `drivers/scsi/mpt3sas/Kconfig`.

Risks: omitting a source object can produce missing symbols or silently remove functionality such as SAS transport, ioctl/control support, trigger diagnostics, WarpDrive handling, or debugfs observability. Adding objects without Kconfig/resource dependencies can introduce unwanted build requirements.

Test signals: build `CONFIG_SCSI_MPT3SAS=y` and `=m`, verify `mpt3sas_transport.o` and `mpt3sas_debugfs.o` are included, run `modpost` for unresolved symbols, and smoke-test module load/unload when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpi/mpi2.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpi/mpi2.h

Purpose: provides the core Fusion-MPT MPI v2.x wire-format definitions used by the MPT3SAS driver and companion MPI headers. It defines MPI version constants, IOC states and registers, request/reply descriptor layouts, function codes, IOC status values, common request/reply headers, LUN masks, and MPI/IEEE scatter-gather element formats and helper macros.

Important APIs/types/functions: this header is all type and macro definitions. Key structures include `MPI2_SYSTEM_INTERFACE_REGS`, request descriptor structs/unions such as `MPI2_DEFAULT_REQUEST_DESCRIPTOR`, `MPI2_SCSI_IO_REQUEST_DESCRIPTOR`, `MPI2_REQUEST_DESCRIPTOR_UNION`, `MPI26_ATOMIC_REQUEST_DESCRIPTOR`, reply descriptors such as `MPI2_DEFAULT_REPLY_DESCRIPTOR`, `MPI2_ADDRESS_REPLY_DESCRIPTOR`, `MPI2_SCSI_IO_SUCCESS_REPLY_DESCRIPTOR`, `MPI2_REPLY_DESCRIPTORS_UNION`, common `MPI2_REQUEST_HEADER`, `MPI2_DEFAULT_REPLY`, `MPI2_VERSION_STRUCT`, `MPI2_VERSION_UNION`, MPI SGE structures/unions, IEEE SGE structures/unions, and `MPI2_SGE_IO_UNION`. Important constants include version/header values, doorbell/write-sequence/diagnostic/interrupt register bits, request and reply descriptor flag encodings, `MPI2_FUNCTION_*` message codes including MCTP passthrough, `MPI2_IOCSTATUS_*` status codes, and SGE flag/length manipulation macros.

Control flow: there is no executable flow, but driver code uses these definitions to format host-to-controller messages, interpret reply descriptors, manipulate MMIO registers, issue doorbell/handshake/reset operations, decode IOC status, and build scatter-gather lists. The SGE helper macros pack flags into the high byte of `FlagsLength` and lengths into the low 24 bits, matching the firmware ABI.

State and persistence: the header defines hardware/firmware ABI state layouts rather than owning state itself. Its structures map persistent controller register offsets and transient request/reply queue entries; correctness depends on field widths, offsets, and endian handling in the consuming code.

Dependencies and integration points: guarded by `MPI2_H` and depends on MPI scalar typedefs such as `U8`, `U16`, `U32`, and `U64` from adjacent MPI type headers. It is included by MPT3SAS source and MPI-specific headers that need common message, descriptor, register, and SGL definitions. Names prefixed `MPI25` and `MPI26` extend the same ABI for MPI v2.5/v2.6-capable products.

Risks: this is an ABI contract with controller firmware; layout or constant changes can break hardware communication. Read-modify-write SGE macros only OR fields into existing values, so callers must initialize `FlagsLength` before using them. Version history indicates long-lived compatibility pressure; changing values for legacy MPI2/MPI25/MPI26 symbols can affect multiple controller generations. Register definitions expose reset and diagnostic controls, so misuse in consumers can fault or reset adapters.

Test signals: compile all MPT3SAS objects with structure size/offset assumptions intact, run sparse/endian checks in consumers, validate SCSI I/O, task management, config, SMP passthrough, NVMe encapsulated, and MCTP passthrough message paths, exercise reply descriptor decoding for success and address replies, and test SGL construction for 32-bit/64-bit MPI, IEEE simple, IEEE chain, and chained transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpi/mpi2.h -->
