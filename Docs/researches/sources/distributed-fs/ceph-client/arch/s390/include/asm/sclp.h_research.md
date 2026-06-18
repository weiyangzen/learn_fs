## sources/distributed-fs/ceph-client/arch/s390/include/asm/sclp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/sclp.h` is a Service Call Logical
Processor interface declarations in the s390 ceph-client Linux source snapshot. It has 203 lines and
5137 bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
early and runtime SCLP buffers, event buffers, machine information, CPU/core discovery, emergency
printing, PCI error reporting, and VM resource callbacks
Important macros/constants: `_ASM_S390_SCLP_H`, `SCLP_CHP_INFO_MASK_SIZE`, `EARLY_SCCB_SIZE`, `SCLP_MAX_CORES`, `EXT_SCCB_READ_SCP`, `EXT_SCCB_READ_CPU`, `SCLP_ERRNOTIFY_AQ_RESET`, `SCLP_ERRNOTIFY_AQ_REPAIR`, `SCLP_ERRNOTIFY_AQ_INFO_LOG`, `SCLP_ERRNOTIFY_AQ_OPTICS_DATA`, `LOADPARM_LEN`.
Important types/layouts: `sclp_chp_info`, `sclp_ipl_info`, `sclp_core_entry`, `sclp_core_info`, `sclp_info`, `sccb_header`, `evbuf_header`, `err_notify_evbuf`, `err_notify_sccb`, `zpci_report_error_header`, `chp_id`, `iov_iter`.
Important declarations or inline helpers: `sclp_early_adjust_va`, `sclp_early_set_buffer`, `sclp_early_read_info`, `sclp_early_read_storage_info`, `sclp_early_get_core_info`, `sclp_early_get_ipl_info`, `sclp_early_detect`, `sclp_early_detect_machine_features`, `sclp_early_printk`, `__sclp_early_printk`, `sclp_emergency_printk`, `sclp_init`, `sclp_early_get_memsize`, `sclp_early_get_hsa_size`, `_sclp_get_core_info`, `sclp_core_configure`, `sclp_core_deconfigure`, `sclp_sdias_blk_count`, `sclp_sdias_copy`, `sclp_chp_configure`; plus 10 more.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
early boot, console, CPU hotplug, memory sizing, PCI error notification, and the SCLP
character/event drivers. Direct include dependencies detected here: `linux/types.h`, `linux/uio.h`,
`asm/chpid.h`, `asm/cpu.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for early boot, console, CPU hotplug, memory
sizing, PCI error notification, and the SCLP character/event drivers. For UAPI files, the
integration point also includes headers_install and userspace programs compiled against the exported
layout.

### Risks
packed SCCB layout drift or early-buffer lifetime mistakes break boot-time discovery and operator
communication

### Test Signals
s390 boot logs, early printk, CPU/memory hotplug, and SCLP event injection tests
