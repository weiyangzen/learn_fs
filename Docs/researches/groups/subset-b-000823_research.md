# subset-b-000823 Research

Grouped source research for subset B work item `subset-b-000823`. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime_instr.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime_instr.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime_instr.h` is a runtime-
instrumentation task state in the s390 ceph-client Linux source snapshot. It has 28 lines and 634
bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
the UAPI runtime-instruction control block plus task save/restore hooks that preserve
instrumentation state across scheduling and task teardown
Important macros/constants: `_RUNTIME_INSTR_H`.
Important types/layouts: `runtime_instr_cb`, `task_struct`.
Important declarations or inline helpers: `if`, `runtime_instr_release`, `save_ri_cb`, `restore_ri_cb`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
scheduler, ptrace/perf-style runtime-instrumentation users, and the low-level load/store runtime
instrumentation instructions. Direct include dependencies detected here: `uapi/asm/runtime_instr.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for scheduler, ptrace/perf-style runtime-
instrumentation users, and the low-level load/store runtime instrumentation instructions. For UAPI
files, the integration point also includes headers_install and userspace programs compiled against
the exported layout.

### Risks
incorrect save/restore can leak instrumentation controls between tasks or leave hardware runtime
tracing enabled after release

### Test Signals
runtime-instrumentation enable/disable tests, context-switch stress, and task-exit cleanup paths
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime_instr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/rwonce.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/rwonce.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/rwonce.h` is a s390 READ_ONCE extensions
in the s390 ceph-client Linux source snapshot. It has 31 lines and 689 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
a 128-bit aligned read helper layered on the generic rwonce implementation for lockless structures
that need atomic pair sampling
Important macros/constants: `__ASM_S390_RWONCE_H`, `READ_ONCE_ALIGNED_128(x)`.
Important types/layouts: none detected.
Important declarations or inline helpers: `volatile`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic compiler-barrier READ_ONCE users and architecture alignment assumptions. Direct include
dependencies detected here: `linux/compiler_types.h`, `asm-generic/rwonce.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic compiler-barrier READ_ONCE users and
architecture alignment assumptions. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
misaligned or non-atomic 128-bit reads can observe torn state in lockless algorithms

### Test Signals
KCSAN/lockless data-race tests and compile coverage for 128-bit consumers
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/rwonce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/schid.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/schid.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/schid.h` is a subchannel identifier
helpers in the s390 ceph-client Linux source snapshot. It has 22 lines and 525 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
small inline initializers/comparators for the UAPI subchannel_id layout used by channel-subsystem
drivers
Important macros/constants: `ASM_SCHID_H`.
Important types/layouts: `subchannel_id`.
Important declarations or inline helpers: `init_subchannel_id`, `schid_equal`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
cio, CHSC, TPI, KVM I/O interrupt encoding, and userspace ioctl structures. Direct include
dependencies detected here: `linux/string.h`, `uapi/asm/schid.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for cio, CHSC, TPI, KVM I/O interrupt encoding,
and userspace ioctl structures. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
wrong one/ssid/cssid handling can address the wrong subchannel

### Test Signals
channel-device enumeration, CHSC ioctls, and equality tests for all id fields
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/schid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sclp.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sclp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/scsw.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/scsw.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/scsw.h` is a subchannel status word
decoding in the s390 ceph-client Linux source snapshot. It has 1051 lines and 25665 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
packed command-mode, transport-mode, and EADM SCSW layouts plus inline accessors, validators, status
predicates, and mutators
Important macros/constants: `_ASM_S390_SCSW_H_`, `SCSW_FCTL_CLEAR_FUNC`, `SCSW_FCTL_HALT_FUNC`, `SCSW_FCTL_START_FUNC`, `SCSW_ACTL_SUSPENDED`, `SCSW_ACTL_DEVACT`, `SCSW_ACTL_SCHACT`, `SCSW_ACTL_CLEAR_PEND`, `SCSW_ACTL_HALT_PEND`, `SCSW_ACTL_START_PEND`, `SCSW_ACTL_RESUME_PEND`, `SCSW_STCTL_STATUS_PEND`, `SCSW_STCTL_SEC_STATUS`, `SCSW_STCTL_PRIM_STATUS`, `SCSW_STCTL_INTER_STATUS`, `SCSW_STCTL_ALERT_STATUS`, `DEV_STAT_ATTENTION`, `DEV_STAT_STAT_MOD`, `DEV_STAT_CU_END`, `DEV_STAT_BUSY`; plus 36 more.
Important types/layouts: `cmd_scsw`, `tm_scsw`, `eadm_scsw`, `scsw`.
Important declarations or inline helpers: `scsw_tm_is_valid_actl`, `scsw_cmd_is_valid_actl`, `scsw_tm_is_valid_cc`, `scsw_cmd_is_valid_cc`, `scsw_tm_is_valid_cstat`, `scsw_cmd_is_valid_cstat`, `scsw_tm_is_valid_dstat`, `scsw_cmd_is_valid_dstat`, `scsw_tm_is_valid_ectl`, `scsw_cmd_is_valid_ectl`, `scsw_tm_is_valid_eswf`, `scsw_cmd_is_valid_eswf`, `scsw_tm_is_valid_fctl`, `scsw_cmd_is_valid_fctl`, `scsw_tm_is_valid_key`, `scsw_cmd_is_valid_key`, `scsw_tm_is_valid_pno`, `scsw_cmd_is_valid_pno`, `scsw_tm_is_valid_stctl`, `scsw_cmd_is_valid_stctl`; plus 36 more.

### Control Flow
Callers receive an SCSW from channel hardware, use scsw_is_tm() to choose command versus transport
layout, then route all status queries through common accessors. Validator helpers check architected
masks before recovery code interprets activity, function, device, and subchannel status.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
common I/O, DASD/QETH/channel drivers, interrupt response blocks, and channel-status recovery paths.
Direct include dependencies detected here: `linux/types.h`, `asm/css_chars.h`, `asm/dma-types.h`,
`asm/cio.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for common I/O, DASD/QETH/channel drivers,
interrupt response blocks, and channel-status recovery paths. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
bitfield or mode-detection errors misinterpret channel status, causing lost interrupts, bogus
residual counts, or incorrect recovery

### Test Signals
channel I/O status decoding tests, DASD/QETH error injection, and transport-mode FCX coverage
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/scsw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/seccomp.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/seccomp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/seccomp.h` is a s390 seccomp syscall
metadata in the s390 ceph-client Linux source snapshot. It has 23 lines and 648 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
native and compat seccomp syscall numbers and AUDIT_ARCH mapping used by generic seccomp filtering
Important macros/constants: `_ASM_S390_SECCOMP_H`, `__NR_seccomp_read`, `__NR_seccomp_write`, `__NR_seccomp_exit`, `__NR_seccomp_sigreturn`, `__NR_seccomp_read_32`, `__NR_seccomp_write_32`, `__NR_seccomp_exit_32`, `__NR_seccomp_sigreturn_32`, `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_NATIVE_NAME`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic seccomp, audit, syscall numbering, and 31-bit compat task handling. Direct include
dependencies detected here: `linux/unistd.h`, `asm-generic/seccomp.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic seccomp, audit, syscall numbering,
and 31-bit compat task handling. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
wrong audit arch or compat syscall numbers can allow or block the wrong filtered operations

### Test Signals
seccomp BPF tests on native and compat processes
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sections.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/sections.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/sections.h` is a s390 linker section
symbols in the s390 ceph-client Linux source snapshot. It has 29 lines and 1054 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
boot-data section annotations that place early boot records in discardable or preserved linker
regions
Important macros/constants: `_S390_SECTIONS_H`, `__bootdata(var)`, `__bootdata_preserved(var)`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
vmlinux linker script, decompressor/early setup, and generic section symbol declarations. Direct
include dependencies detected here: `asm-generic/sections.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for vmlinux linker script, decompressor/early
setup, and generic section symbol declarations. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
misplaced boot data can be freed too early or retained unnecessarily

### Test Signals
link-map inspection and boot with initmem/debug section checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/set_memory.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/set_memory.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/set_memory.h` is a kernel mapping
permission changes in the s390 ceph-client Linux source snapshot. It has 68 lines and 2175 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
set_memory_* wrappers and direct-map validity helpers that batch page attribute changes under a
global mutex
Important macros/constants: `_ASMS390_SET_MEMORY_H`, `SET_MEMORY_RO`, `SET_MEMORY_RW`, `SET_MEMORY_NX`, `SET_MEMORY_X`, `SET_MEMORY_4K`, `SET_MEMORY_INV`, `SET_MEMORY_DEF`, `set_memory_rox`, `__SET_MEMORY_FUNC(fname, flags)`.
Important types/layouts: `mutex`, `page`.
Important declarations or inline helpers: `__set_memory`, `set_direct_map_invalid_noflush`, `set_direct_map_default_noflush`, `set_direct_map_valid_noflush`, `kernel_page_present`, `fname`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
module/text patching, STRICT_KERNEL_RWX, vmalloc, debug pagealloc, and direct-map manipulation.
Direct include dependencies detected here: `linux/mutex.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for module/text patching, STRICT_KERNEL_RWX,
vmalloc, debug pagealloc, and direct-map manipulation. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
missing TLB synchronization or wrong flag composition can leave executable/writable aliases

### Test Signals
STRICT_KERNEL_RWX tests, module load/unload, ftrace/static-key patching, and debug_pagealloc
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/setup.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/setup.h` is a s390 boot setup constants
and hooks in the s390 ceph-client Linux source snapshot. It has 105 lines and 2847 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
parmarea, lowcore startup offsets, machine flags, dump metadata, decompressor options, and early
console/fault helpers
Important macros/constants: `_ASM_S390_SETUP_H`, `PARMAREA`, `COMMAND_LINE_SIZE`, `LPP_MAGIC`, `LPP_PID_MASK`, `STARTUP_NORMAL_OFFSET`, `STARTUP_KDUMP_OFFSET`, `LEGACY_COMMAND_LINE_SIZE`, `ZLIB_DFLTCC_DISABLED`, `ZLIB_DFLTCC_FULL`, `ZLIB_DFLTCC_DEFLATE_ONLY`, `ZLIB_DFLTCC_INFLATE_ONLY`, `ZLIB_DFLTCC_FULL_DEBUG`, `CONSOLE_IS_UNDEFINED`, `CONSOLE_IS_SCLP`, `CONSOLE_IS_3215`, `CONSOLE_IS_3270`, `CONSOLE_IS_VT220`, `CONSOLE_IS_HVC`, `SET_CONSOLE_SCLP`; plus 4 more.
Important types/layouts: `parmarea`, `pt_regs`, `oldmem_data`.
Important declarations or inline helpers: `register_early_console`, `vmcp_cma_reserve`, `report_user_fault`, `void`, `gen_lpswe`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
IPL/startup assembly, boot command line parsing, kdump, VMCP CMA, and lowcore PSW loading. Direct
include dependencies detected here: `linux/bits.h`, `uapi/asm/setup.h`, `linux/build_bug.h`,
`asm/lowcore.h`, `asm/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for IPL/startup assembly, boot command line
parsing, kdump, VMCP CMA, and lowcore PSW loading. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
ABI-offset mismatches or command-line size drift can break early boot before diagnostics are
available

### Test Signals
boot variants for normal, kdump, z/VM, LPAR, and command-line edge cases
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/signal.h` is a kernel signal integration
in the s390 ceph-client Linux source snapshot. It has 26 lines and 644 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
s390 signal constants and SA_RESTORER exposure that bridge UAPI signal frames to generic signal code
Important macros/constants: `_ASMS390_SIGNAL_H`, `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, `__ARCH_HAS_SA_RESTORER`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
uapi signal.h, sigcontext, syscall restart, and vdso/restorer paths. Direct include dependencies
detected here: `uapi/asm/signal.h`, `asm/sigcontext.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for uapi signal.h, sigcontext, syscall restart,
and vdso/restorer paths. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
signal frame ABI mismatches break old userspace and compat signal delivery

### Test Signals
sigaltstack, rt-signal, ptrace signal injection, and compat tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sigp.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/sigp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/sigp.h` is a SIGP inter-processor
instruction wrappers in the s390 ceph-client Linux source snapshot. It has 73 lines and 1918 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
order-code constants and inline assembly helpers for issuing SIGP to other CPUs with condition-
code/result handling
Important macros/constants: `__S390_ASM_SIGP_H`, `SIGP_SENSE`, `SIGP_EXTERNAL_CALL`, `SIGP_EMERGENCY_SIGNAL`, `SIGP_START`, `SIGP_STOP`, `SIGP_RESTART`, `SIGP_STOP_AND_STORE_STATUS`, `SIGP_INITIAL_CPU_RESET`, `SIGP_CPU_RESET`, `SIGP_SET_PREFIX`, `SIGP_STORE_STATUS_AT_ADDRESS`, `SIGP_SET_ARCHITECTURE`, `SIGP_COND_EMERGENCY_SIGNAL`, `SIGP_SENSE_RUNNING`, `SIGP_SET_MULTI_THREADING`, `SIGP_STORE_ADDITIONAL_STATUS`, `SIGP_CC_ORDER_CODE_ACCEPTED`, `SIGP_CC_STATUS_STORED`, `SIGP_CC_BUSY`; plus 8 more.
Important types/layouts: `register_pair`.
Important declarations or inline helpers: `volatile`, `CC_TRANSFORM`, `____pcpu_sigp`, `__pcpu_sigp`.

### Control Flow
The header is mostly inline fast-path code: callers enter small assembly sequences, condition-code
extraction converts hardware results into C values, and fallback or wait loops are selected through
architecture facilities and alternative patching.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
SMP startup/stop, CPU reset, emergency signaling, hotplug, and dump paths. Direct include
dependencies detected here: `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for SMP startup/stop, CPU reset, emergency
signaling, hotplug, and dump paths. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect register pairing or condition-code translation can hang CPU bring-up or emergency stop

### Test Signals
CPU hotplug, IPL CPU calls, panic stop, and SIGP order fault-injection tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sigp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/skey.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/skey.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/skey.h` is a storage-key initialization in
the s390 ceph-client Linux source snapshot. It has 32 lines and 725 bytes; exported UAPI contract:
no.

### Important APIs, Types, And Functions
skey_region descriptors and initialization hooks for assigning hardware storage keys to memory
ranges
Important macros/constants: `__ASM_SKEY_H`, `SKEY_REGION(_start, _end)`.
Important types/layouts: `skey_region`.
Important declarations or inline helpers: `__skey_regions_initialize`, `skey_regions_initialize`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
early memory setup, protected/storage-key facilities, page protection, and rwonce region
publication. Direct include dependencies detected here: `asm/rwonce.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for early memory setup, protected/storage-key
facilities, page protection, and rwonce region publication. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
range arithmetic mistakes can leave pages with stale storage-key protection

### Test Signals
boot storage-key initialization and memory hotplug validation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/skey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/smp.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/smp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/smp.h` is a s390 SMP coordination
declarations in the s390 ceph-client Linux source snapshot. It has 90 lines and 2633 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
CPU bring-up, IPI, IPL CPU calls, emergency stop, CPU address lookup, topology/capacity,
polarization, and dump status hooks
Important macros/constants: `__ASM_SMP_H`, `arch_scale_cpu_capacity`.
Important types/layouts: `lowcore`, `mutex`, `task_struct`, `cpumask`.
Important declarations or inline helpers: `__cpu_up`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `smp_call_ipl_cpu`, `smp_emergency_stop`, `smp_find_processor_id`, `smp_store_status`, `smp_save_dump_ipl_cpu`, `smp_save_dump_secondary_cpus`, `smp_yield_cpu`, `smp_cpu_set_polarization`, `smp_cpu_get_polarization`, `smp_cpu_set_capacity`, `smp_set_core_capacity`, `smp_cpu_get_capacity`, `smp_cpu_get_cpu_address`, `smp_fill_possible_mask`, `smp_detect_cpus`, `smp_rescan_cpus`, `cpu_die`; plus 7 more.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic SMP, lowcore, SIGP, topology, hotplug, and scheduler capacity accounting. Direct include
dependencies detected here: `asm/processor.h`, `asm/lowcore.h`, `asm/machine.h`, `asm/sigp.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic SMP, lowcore, SIGP, topology,
hotplug, and scheduler capacity accounting. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
CPU-address mismatches or stale topology capacity can break IPI routing and scheduler placement

### Test Signals
CPU hotplug, smp_call_function, topology updates, polarization changes, and panic dump tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/softirq_stack.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/softirq_stack.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/softirq_stack.h` is a softirq alternate
stack execution in the s390 ceph-client Linux source snapshot. It has 14 lines and 372 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
do_softirq_own_stack() wrapper that switches to the lowcore async stack before running softirq work
Important macros/constants: `__ASM_S390_SOFTIRQ_STACK_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: `do_softirq_own_stack`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic softirq dispatch, lowcore stack fields, and stacktrace classification. Direct include
dependencies detected here: `asm/lowcore.h`, `asm/stacktrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic softirq dispatch, lowcore stack
fields, and stacktrace classification. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong stack selection can overflow task stacks or confuse unwinding

### Test Signals
network/storage interrupt load with stack overflow and stacktrace diagnostics
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/softirq_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sparsemem.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/sparsemem.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/sparsemem.h` is a s390 sparse-memory
geometry in the s390 ceph-client Linux source snapshot. It has 24 lines and 506 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
SECTION_SIZE_BITS/MAX_PHYSMEM_BITS and default node mapping macros for sparsemem
Important macros/constants: `_ASM_S390_SPARSEMEM_H`, `SECTION_SIZE_BITS`, `MAX_PHYSMEM_BITS`, `memory_add_physaddr_to_nid`, `phys_to_target_node`.
Important types/layouts: none detected.
Important declarations or inline helpers: `memory_add_physaddr_to_nid`, `phys_to_target_node`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
SPARSEMEM, memory hotplug, memblock, and NUMA target-node logic. Direct include dependencies
detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for SPARSEMEM, memory hotplug, memblock, and NUMA
target-node logic. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
incorrect geometry corrupts section-to-pfn mapping on large or hotplugged systems

### Test Signals
memory hotplug, large-memory boot, and sparsemem pfn validation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock.h` is a s390 queued spin/rw lock
operations in the s390 ceph-client Linux source snapshot. It has 168 lines and 3922 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
lock value helpers, optimistic trylock, wait loops, alternative-instruction relax handling, and vCPU
preemption hints
Important macros/constants: `__ASM_SPINLOCK_H`, `vcpu_is_preempted`, `arch_spin_relax`, `arch_read_relax(rw)`, `arch_write_relax(rw)`.
Important types/layouts: `lowcore`.
Important declarations or inline helpers: `arch_vcpu_is_preempted`, `arch_spin_relax`, `arch_spin_lock_wait`, `arch_spin_trylock_retry`, `arch_spin_lock_setup`, `likely`, `volatile`, `arch_read_lock_wait`, `arch_write_lock_wait`, `spinlock_lockval`, `arch_spin_lockval`, `arch_spin_value_unlocked`, `arch_spin_is_locked`, `arch_spin_trylock_once`, `arch_spin_lock`, `arch_spin_trylock`, `arch_spin_unlock`, `arch_read_lock`, `arch_read_unlock`, `arch_write_lock`; plus 3 more.

### Control Flow
The header is mostly inline fast-path code: callers enter small assembly sequences, condition-code
extraction converts hardware results into C values, and fallback or wait loops are selected through
architecture facilities and alternative patching.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic locking, paravirt/preemption detection, atomic operations, barriers, and scheduler spin
heuristics. Direct include dependencies detected here: `linux/smp.h`, `asm/atomic_ops.h`,
`asm/barrier.h`, `asm/processor.h`, `asm/alternative.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic locking, paravirt/preemption
detection, atomic operations, barriers, and scheduler spin heuristics. For UAPI files, the
integration point also includes headers_install and userspace programs compiled against the exported
layout.

### Risks
bad memory ordering or preemption detection can deadlock or starve under contention

### Test Signals
locktorture, qspinlock/rwlock stress, KVM overcommit, and PREEMPT builds
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock_types.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock_types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock_types.h` is a s390 spinlock
storage layout in the s390 ceph-client Linux source snapshot. It has 22 lines and 413 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
architecture lock initializer constants for spinlocks and rwlocks
Important macros/constants: `__ASM_SPINLOCK_TYPES_H`, `__ARCH_SPIN_LOCK_UNLOCKED`, `__ARCH_RW_LOCK_UNLOCKED`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic spinlock/rwlock code and assembly lock primitives. Direct include dependencies detected
here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic spinlock/rwlock code and assembly
lock primitives. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
initializer drift causes locks to start in a held or invalid state

### Test Signals
compile-time lock initializer checks and lockdep boot coverage
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/stackprotector.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/stackprotector.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/stackprotector.h` is a stack canary
initialization in the s390 ceph-client Linux source snapshot. It has 16 lines and 389 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
boot_init_stack_canary() copies the per-task canary into lowcore for stack protector checks
Important macros/constants: `_ASM_S390_STACKPROTECTOR_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: `boot_init_stack_canary`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
scheduler current task, lowcore, compiler stack-protector instrumentation, and fork/exec paths.
Direct include dependencies detected here: `linux/sched.h`, `asm/current.h`, `asm/lowcore.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for scheduler current task, lowcore, compiler
stack-protector instrumentation, and fork/exec paths. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
stale canary values reduce stack-smash detection or cause false positives

### Test Signals
stack protector boot coverage and task-switch canary tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/stacktrace.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/stacktrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/stacktrace.h` is a s390 stack walking
helpers in the s390 ceph-client Linux source snapshot. It has 261 lines and 8086 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
stack-frame layouts, stack type classification, inline stack pointer helpers, and call-with-return-
address assembly macros
Important macros/constants: `_ASM_S390_STACKTRACE_H`, `current_frame_address()`, `CALL_FMT_0`, `CALL_FMT_1`, `CALL_FMT_2`, `CALL_FMT_3`, `CALL_FMT_4`, `CALL_FMT_5`, `CALL_CLOBBER_5`, `CALL_CLOBBER_4`, `CALL_CLOBBER_3`, `CALL_CLOBBER_2`, `CALL_CLOBBER_1`, `CALL_CLOBBER_0`, `CALL_LARGS_0(...)`, `CALL_LARGS_1(t1, a1)`, `CALL_LARGS_2(t1, a1, t2, a2)`, `CALL_LARGS_3(t1, a1, t2, a2, t3, a3)`, `CALL_LARGS_4(t1, a1, t2, a2, t3, a3, t4, a4)`, `CALL_LARGS_5(t1, a1, t2, a2, t3, a3, t4, a4, t5, a5)`; plus 21 more.
Important types/layouts: `stack_frame_user`, `stack_frame_vdso_wrapper`, `perf_callchain_entry_ctx`, `pt_regs`, `stack_info`, `task_struct`, `stack_frame`, `stack_type`.
Important declarations or inline helpers: `arch_stack_walk_user_common`, `get_stack_info`, `current_frame_address`, `asm`, `volatile`, `on_stack`, `get_stack_pointer`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic stacktrace, perf callchains, user stack walking, unwinder, ftrace, and exception stacks.
Direct include dependencies detected here: `linux/stacktrace.h`, `linux/uaccess.h`,
`linux/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic stacktrace, perf callchains, user
stack walking, unwinder, ftrace, and exception stacks. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
frame-layout mismatches can hide callchain frames or unwind into invalid memory

### Test Signals
perf callchains, live stack traces, kprobes/ftrace, IRQ/NMI stack unwinding, and user unwinds
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/stp.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/stp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/stp.h` is a Server Time Protocol
interfaces in the s390 ceph-client Linux source snapshot. It has 99 lines and 1727 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
STP interrupt parameter blocks, time-zone/control structures, notifier hooks, enabled flag, and
work-queue entry points
Important macros/constants: `__S390_STP_H`, `STP_OP_SYNC`, `STP_OP_CTRL`.
Important types/layouts: `atomic_notifier_head`, `stp_irq_parm`, `stp_sstpi`, `stp_tzib`, `stp_tcpib`, `stp_lsoib`, `stp_stzi`.
Important declarations or inline helpers: `stp_sync_check`, `stp_island_check`, `stp_queue_work`, `stp_enabled`.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
timekeeping, clock sync, external interrupt handling, and sysfs/diagnostic STP consumers. Direct
include dependencies detected here: `linux/compiler.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for timekeeping, clock sync, external interrupt
handling, and sysfs/diagnostic STP consumers. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect packed layout or missed notifications can leave system time unsynchronized

### Test Signals
STP interrupt injection, time sync checks, notifier registration, and LPAR clock-change events
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/stp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/string.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/string.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/string.h` is a s390 optimized
string/memory primitives in the s390 ceph-client Linux source snapshot. It has 196 lines and 5153
bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
architecture declarations and inline fallbacks for memcpy/memmove/memset/memchr/memcmp/string
operations, including no-sanitize prefix helpers
Important macros/constants: `_S390_STRING_H_`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE`, `__HAVE_ARCH_MEMSET`, `__HAVE_ARCH_MEMCHR`, `__HAVE_ARCH_MEMCMP`, `__HAVE_ARCH_MEMSCAN`, `__HAVE_ARCH_STRCAT`, `__HAVE_ARCH_STRCMP`, `__HAVE_ARCH_STRLCAT`, `__HAVE_ARCH_STRLEN`, `__HAVE_ARCH_STRNCAT`, `__HAVE_ARCH_STRNLEN`, `__HAVE_ARCH_STRSTR`, `__HAVE_ARCH_MEMSET16`, `__HAVE_ARCH_MEMSET32`, `__HAVE_ARCH_MEMSET64`, `strlen(s)`, `__no_sanitize_prefix_strfunc(x)`, `__NO_FORTIFY`.
Important types/layouts: none detected.
Important declarations or inline helpers: `memcmp`, `strcmp`, `strlcat`, `__memset16`, `__memset32`, `__memset64`, `volatile`, `strlen`, `strnlen`, `__no_sanitize_prefix_strfunc`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
lib/string, compiler builtins, KASAN/KMSAN instrumentation, boot code, and every kernel subsystem
using memory helpers. Direct include dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for lib/string, compiler builtins, KASAN/KMSAN
instrumentation, boot code, and every kernel subsystem using memory helpers. For UAPI files, the
integration point also includes headers_install and userspace programs compiled against the exported
layout.

### Risks
prefix or inline assembly mistakes produce silent memory corruption across the kernel

### Test Signals
lib/string selftests, KASAN/KMSAN builds, boot-time memtest, and overlap/corner-size cases
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall.h` is a syscall register accessors
in the s390 ceph-client Linux source snapshot. It has 156 lines and 4017 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
helpers to read/write syscall numbers, arguments, return/error values, rollback state, audit
architecture, and vdso sigreturn recognition
Important macros/constants: `_ASM_SYSCALL_H`, `SYSCALL_FMT_0`, `SYSCALL_FMT_1`, `SYSCALL_FMT_2`, `SYSCALL_FMT_3`, `SYSCALL_FMT_4`, `SYSCALL_FMT_5`, `SYSCALL_FMT_6`, `SYSCALL_PARM_0`, `SYSCALL_PARM_1`, `SYSCALL_PARM_2`, `SYSCALL_PARM_3`, `SYSCALL_PARM_4`, `SYSCALL_PARM_5`, `SYSCALL_PARM_6`, `SYSCALL_REGS_0`, `SYSCALL_REGS_1`, `SYSCALL_REGS_2`, `SYSCALL_REGS_3`, `SYSCALL_REGS_4`; plus 3 more.
Important types/layouts: `task_struct`, `pt_regs`.
Important declarations or inline helpers: `asm`, `volatile`, `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`, `arch_syscall_is_vdso_sigreturn`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
ptrace, seccomp, audit, syscall tracing, restart handling, and compat mode. Direct include
dependencies detected here: `uapi/linux/audit.h`, `linux/sched.h`, `linux/err.h`, `asm/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for ptrace, seccomp, audit, syscall tracing,
restart handling, and compat mode. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong register mapping breaks tracing, seccomp, restart, and userspace ABI behavior

### Test Signals
ptrace/seccomp/audit tests, syscall restart, compat syscalls, and vdso sigreturn cases
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall_wrapper.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall_wrapper.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall_wrapper.h` is a s390 syscall entry
wrappers in the s390 ceph-client Linux source snapshot. It has 49 lines and 1741 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
macros that translate pt_regs into typed syscall arguments and create s390x/s390 compat syscall
stubs
Important macros/constants: `_ASM_S390_SYSCALL_WRAPPER_H`, `SC_S390_REGS_TO_ARGS(x, ...)`, `SYSCALL_DEFINE0(sname)`, `COND_SYSCALL(name)`, `__S390_SYS_STUBx(x, fullname, name, ...)`, `__SYSCALL_DEFINEx(x, name, ...)`.
Important types/layouts: `pt_regs`.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generated syscall tables, asmlinkage entry code, compat ABI, and generic SYSCALL_DEFINE macros.
Direct include dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generated syscall tables, asmlinkage entry
code, compat ABI, and generic SYSCALL_DEFINE macros. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
argument order/sign-extension mistakes surface as ABI corruption under tracing and compat

### Test Signals
syscall ABI tests, compat userland, and build coverage for conditional syscalls
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sysinfo.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/sysinfo.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/sysinfo.h` is a STSI/STHYI system
information layouts in the s390 ceph-client Linux source snapshot. It has 231 lines and 5077 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
packed STSI structures for machine/LPAR/topology/capacity data plus helpers for service-level
registration and topology nesting
Important macros/constants: `__ASM_S390_SYSINFO_H`, `LPAR_CHAR_DEDICATED`, `LPAR_CHAR_SHARED`, `LPAR_CHAR_LIMITED`, `TOPOLOGY_NR_MAG`.
Important types/layouts: `sysinfo_1_1_1`, `sysinfo_1_2_1`, `sysinfo_1_2_2`, `sysinfo_1_2_2_extension`, `sysinfo_2_2_1`, `sysinfo_2_2_2`, `sysinfo_3_2_2`, `topology_core`, `topology_container`, `topology_entry`, `sysinfo_15_1_x`, `service_level`, `list_head`, `seq_file`.
Important declarations or inline helpers: `volatile`, `min`, `stsi`, `register_service_level`, `unregister_service_level`, `sthyi_fill`, `topology_mnest_limit`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
topology, hypfs, CPU management, virtualization diagnostics, and machine capacity reporting. Direct
include dependencies detected here: `linux/uuid.h`, `asm/bitsperlong.h`, `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for topology, hypfs, CPU management,
virtualization diagnostics, and machine capacity reporting. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
bitfield layout drift misreports topology/capacity or corrupts hypervisor information

### Test Signals
STSI/STHYI tests, topology sysfs validation, LPAR/zVM boots, and service-level registration
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/sysinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/text-patching.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/text-patching.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/text-patching.h` is a text patch
synchronization in the s390 ceph-client Linux source snapshot. It has 16 lines and 301 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
sync_core aliases and text_poke synchronization lock declarations for instruction patching
Important macros/constants: `_ASM_S390_TEXT_PATCHING_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: `text_poke_sync`, `text_poke_sync_lock`, `sync_core`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
alternatives, static keys, ftrace, livepatch-like text modification, and CPU serialization. Direct
include dependencies detected here: `asm/barrier.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for alternatives, static keys, ftrace, livepatch-
like text modification, and CPU serialization. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
missing serialization can execute stale or partially patched instructions

### Test Signals
alternatives boot, ftrace toggling, static key stress, and SMP patch races
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/thread_info.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/thread_info.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/thread_info.h` is a thread-info flags and
stack sizing in the s390 ceph-client Linux source snapshot. It has 84 lines and 2493 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
thread_info layout, thread/boot stack sizes, TIF flag numbers, and arch exec setup hooks
Important macros/constants: `_ASM_THREAD_INFO_H`, `THREAD_SIZE_ORDER`, `BOOT_STACK_SIZE`, `THREAD_SIZE`, `STACK_INIT_OFFSET`, `INIT_THREAD_INFO(tsk)`, `arch_setup_new_exec`, `HAVE_TIF_NEED_RESCHED_LAZY`, `HAVE_TIF_RESTORE_SIGMASK`, `TIF_ASCE_PRIMARY`, `TIF_GUARDED_STORAGE`, `TIF_ISOLATE_BP_GUEST`, `TIF_PER_TRAP`, `TIF_SINGLE_STEP`, `TIF_BLOCK_STEP`, `TIF_UPROBE_SINGLESTEP`, `_TIF_ASCE_PRIMARY`, `_TIF_GUARDED_STORAGE`, `_TIF_ISOLATE_BP_GUEST`, `_TIF_PER_TRAP`; plus 3 more.
Important types/layouts: `should`, `shares`, `thread_info`, `task_struct`.
Important declarations or inline helpers: `arch_setup_new_exec`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
scheduler, entry code, signal restore, guarded storage, and low-level stack assumptions. Direct
include dependencies detected here: `linux/bits.h`, `vdso/page.h`, `asm-generic/thread_info_tif.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for scheduler, entry code, signal restore,
guarded storage, and low-level stack assumptions. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
flag-number drift breaks entry assembly work checks and signal/exec cleanup

### Test Signals
entry-path tests, signal restore, guarded-storage state reset, and stack-size build checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/timex.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/timex.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/timex.h` is a s390 TOD clock and timer
primitives in the s390 ceph-client Linux source snapshot. It has 289 lines and 6798 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
TOD/PTFF structures, inline STCK/STCKF/STCKE helpers, clock comparator programming, CPU timer setup,
and early time initialization declarations
Important macros/constants: `_ASM_S390_TIMEX_H`, `TOD_UNIX_EPOCH`, `PTFF_QAF`, `PTFF_QTO`, `PTFF_QSI`, `PTFF_QPT`, `PTFF_QUI`, `PTFF_ATO`, `PTFF_STO`, `PTFF_SFS`, `PTFF_SGS`, `ptff(ptff_block, len, func)`, `CLOCK_TICK_RATE`, `get_cycles`.
Important types/layouts: `tod_clock`, `ptff_qto`, `ptff_qui`, `addrtype`.
Important declarations or inline helpers: `volatile`, `CC_TRANSFORM`, `clock_comparator_work`, `time_early_init`, `get_phys_clock`, `init_cpu_timer`, `set_tod_clock`, `store_tod_clock_ext_cc`, `store_tod_clock_ext`, `set_clock_comparator`, `set_tod_programmable_field`, `ptff_query`, `local_tick_disable`, `local_tick_enable`, `get_tod_clock`, `get_tod_clock_fast`, `__get_tod_clock_monotonic`, `get_tod_clock_monotonic`, `get_cycles`, `tod_to_ns`; plus 3 more.

### Control Flow
The header is mostly inline fast-path code: callers enter small assembly sequences, condition-code
extraction converts hardware results into C values, and fallback or wait loops are selected through
architecture facilities and alternative patching.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
timekeeping, sched clock, vDSO time, CPU idle/tick handling, and machine facility detection. Direct
include dependencies detected here: `linux/preempt.h`, `linux/time64.h`, `asm/lowcore.h`,
`asm/machine.h`, `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for timekeeping, sched clock, vDSO time, CPU
idle/tick handling, and machine facility detection. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
wrong epoch conversion, mask handling, or comparator programming causes time jumps or lost timer
interrupts

### Test Signals
clocksource tests, vDSO time tests, suspend/idle tick tests, and STCK/STCKF facility coverage
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/tlb.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/tlb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/tlb.h` is a s390 mmu_gather integration in
the s390 ceph-client Linux source snapshot. It has 144 lines and 4657 bytes; exported UAPI contract:
no.

### Important APIs, Types, And Functions
TLB gather flush hooks and page-table free wrappers that combine generic batching with s390 table
invalidation
Important macros/constants: `_S390_TLB_H`, `tlb_flush`, `pte_free_tlb`, `pmd_free_tlb`, `p4d_free_tlb`, `pud_free_tlb`.
Important types/layouts: `therefore`, `mmu_gather`, `page`, `encoded_page`.
Important declarations or inline helpers: `tlb_flush`, `__tlb_remove_page_size`, `__tlb_remove_folio_pages`, `pte_free_tlb`, `pmd_free_tlb`, `p4d_free_tlb`, `pud_free_tlb`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic MM, page-table allocation, RCU table freeing, and s390 TLB flush primitives. Direct include
dependencies detected here: `asm/tlbflush.h`, `asm-generic/tlb.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic MM, page-table allocation, RCU table
freeing, and s390 TLB flush primitives. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
freeing page tables before global invalidation can create use-after-free translations

### Test Signals
munmap/mprotect stress, THP/split tests, KASAN, and CPU-hotplug TLB shootdowns
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/tlbflush.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/tlbflush.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/tlbflush.h` is a s390 TLB flush
declarations in the s390 ceph-client Linux source snapshot. It has 121 lines and 2945 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
local/global flush operations, IDTE-based invalidation, lazy-mm flush, and range/kernel flush
interfaces
Important macros/constants: `_S390_TLBFLUSH_H`, `flush_tlb_all()`, `flush_tlb_page(vma, addr)`.
Important types/layouts: `mm_struct`, `vm_area_struct`.
Important declarations or inline helpers: `volatile`, `__tlb_flush_local`, `__tlb_flush_idte`, `__tlb_flush_global`, `__tlb_flush_mm`, `__tlb_flush_kernel`, `__tlb_flush_mm_lazy`, `flush_tlb_mm`, `flush_tlb_range`, `flush_tlb_kernel_range`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic MM, ASCE/address-space control, machine facilities, and scheduler lazy TLB state. Direct
include dependencies detected here: `linux/cpufeature.h`, `linux/mm.h`, `linux/sched.h`,
`asm/processor.h`, `asm/machine.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic MM, ASCE/address-space control,
machine facilities, and scheduler lazy TLB state. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
choosing local instead of global invalidation can leave stale translations on other CPUs

### Test Signals
mprotect/munmap/fork stress, KVM guests, lazy TLB switches, and facility fallback tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/topology.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/topology.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/topology.h` is a s390 CPU topology model
in the s390 ceph-client Linux source snapshot. It has 110 lines and 3146 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
cpu_topology_s390 fields, topology cpumask macros, dedication/capacity accessors, node mapping, and
update scheduling declarations
Important macros/constants: `_ASM_S390_TOPOLOGY_H`, `topology_physical_package_id(cpu)`, `topology_thread_id(cpu)`, `topology_sibling_cpumask(cpu)`, `topology_core_id(cpu)`, `topology_core_cpumask(cpu)`, `topology_book_id(cpu)`, `topology_book_cpumask(cpu)`, `topology_drawer_id(cpu)`, `topology_drawer_cpumask(cpu)`, `topology_cpu_dedicated(cpu)`, `topology_booted_cores(cpu)`, `mc_capable()`, `topology_is_primary_thread`, `POLARIZATION_UNKNOWN`, `POLARIZATION_HRZ`, `POLARIZATION_VL`, `POLARIZATION_VM`, `POLARIZATION_VH`, `CPU_CAPACITY_HIGH`; plus 6 more.
Important types/layouts: `sysinfo_15_1_x`, `cpu`, `cpu_topology_s390`, `cpumask`.
Important declarations or inline helpers: `topology_init_early`, `topology_cpu_init`, `topology_set_cpu_management`, `topology_schedule_update`, `store_topology`, `update_cpu_masks`, `topology_expect_change`, `topology_cpu_dedicated`, `topology_booted_cores`, `topology_is_primary_thread`, `cpu_to_node`, `numa_node_id`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
STSI sysinfo, scheduler topology, NUMA, CPU hotplug, and polarization/management events. Direct
include dependencies detected here: `linux/cpumask.h`, `asm/numa.h`, `asm-generic/topology.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for STSI sysinfo, scheduler topology, NUMA, CPU
hotplug, and polarization/management events. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
stale topology masks or node ids degrade scheduling and can confuse CPU hotplug

### Test Signals
topology sysfs, CPU hotplug, capacity scaling, NUMA boots, and hypervisor topology-change events
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/tpi.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/tpi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/tpi.h` is a Test Pending Interruption
block in the s390 ceph-client Linux source snapshot. It has 37 lines and 738 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
tpi_info and adapter-interrupt fields used to decode pending I/O interrupts
Important macros/constants: `_ASM_S390_TPI_H`.
Important types/layouts: `tpi_info`, `subchannel_id`, `tpi_adapter_info`.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
channel-subsystem interrupt handling, TPI instruction users, and subchannel identifiers. Direct
include dependencies detected here: `linux/types.h`, `uapi/asm/schid.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for channel-subsystem interrupt handling, TPI
instruction users, and subchannel identifiers. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
packed layout mistakes lose adapter or subchannel interrupt details

### Test Signals
I/O interrupt injection, adapter interrupt tests, and channel-device bring-up
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/tpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/ap.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/ap.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/ap.h` is a s390 tracepoint
definitions in the s390 ceph-client Linux source snapshot. It has 87 lines and 2948 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
AP bus tracepoints for queue reset/interrupt/request/reply and APQN/card/domain identifiers
Important macros/constants: `TRACE_SYSTEM`, `_TRACE_S390_AP_H`, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Trace control flow is declarative: each TRACE_EVENT expands into tracepoint registration, fast-path
enable checks, and format metadata at build time. This file contributes events none detected, and
the runtime path is driven by subsystem callers invoking the generated trace hooks.

### State And Persistence
Tracepoint enable state, ring-buffer records, and format metadata are managed by the tracing core;
this header contributes event schemas but keeps no private persistent state.

### Dependencies
Linux tracepoint generation, ftrace/perf, subsystem drivers, and trace/define_trace.h. Direct
include dependencies detected here: `linux/tracepoint.h`, `trace/define_trace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/trace`
source-tree area and feeds the s390 architecture boundary for Linux tracepoint generation,
ftrace/perf, subsystem drivers, and trace/define_trace.h. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
trace format drift can break tooling that parses field names or event payloads

### Test Signals
tracefs format inspection, perf/ftrace event enablement, and subsystem event generation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/ap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/diag.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/diag.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/diag.h` is a s390 tracepoint
definitions in the s390 ceph-client Linux source snapshot. It has 44 lines and 950 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
diagnose-instruction tracepoints with a norecursion wrapper for low-level diagnostic calls
Important macros/constants: `TRACE_SYSTEM`, `_TRACE_S390_DIAG_H`, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`.
Important types/layouts: none detected.
Important declarations or inline helpers: `trace_s390_diagnose_norecursion`.
Trace events declared: `s390_diagnose`.

### Control Flow
Trace control flow is declarative: each TRACE_EVENT expands into tracepoint registration, fast-path
enable checks, and format metadata at build time. This file contributes events `s390_diagnose`, and
the runtime path is driven by subsystem callers invoking the generated trace hooks.

### State And Persistence
Tracepoint enable state, ring-buffer records, and format metadata are managed by the tracing core;
this header contributes event schemas but keeps no private persistent state.

### Dependencies
Linux tracepoint generation, ftrace/perf, subsystem drivers, and trace/define_trace.h. Direct
include dependencies detected here: `linux/tracepoint.h`, `trace/define_trace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/trace`
source-tree area and feeds the s390 architecture boundary for Linux tracepoint generation,
ftrace/perf, subsystem drivers, and trace/define_trace.h. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
trace format drift can break tooling that parses field names or event payloads

### Test Signals
tracefs format inspection, perf/ftrace event enablement, and subsystem event generation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/hiperdispatch.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/hiperdispatch.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/hiperdispatch.h` is a s390
tracepoint definitions in the s390 ceph-client Linux source snapshot. It has 58 lines and 1908
bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
CPU polarization and HiperDispatch management tracepoints
Important macros/constants: `TRACE_SYSTEM`, `_TRACE_S390_HIPERDISPATCH_H`, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.
Trace events declared: `s390_hd_work_fn`, `s390_hd_rebuild_domains`.

### Control Flow
Trace control flow is declarative: each TRACE_EVENT expands into tracepoint registration, fast-path
enable checks, and format metadata at build time. This file contributes events `s390_hd_work_fn`,
`s390_hd_rebuild_domains`, and the runtime path is driven by subsystem callers invoking the
generated trace hooks.

### State And Persistence
Tracepoint enable state, ring-buffer records, and format metadata are managed by the tracing core;
this header contributes event schemas but keeps no private persistent state.

### Dependencies
Linux tracepoint generation, ftrace/perf, subsystem drivers, and trace/define_trace.h. Direct
include dependencies detected here: `linux/tracepoint.h`, `trace/define_trace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/trace`
source-tree area and feeds the s390 architecture boundary for Linux tracepoint generation,
ftrace/perf, subsystem drivers, and trace/define_trace.h. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
trace format drift can break tooling that parses field names or event payloads

### Test Signals
tracefs format inspection, perf/ftrace event enablement, and subsystem event generation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/hiperdispatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/zcrypt.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/zcrypt.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/zcrypt.h` is a s390 tracepoint
definitions in the s390 ceph-client Linux source snapshot. It has 127 lines and 4394 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
zcrypt request/CPRB tracepoints that classify CCA, EP11, and HWRNG request types
Important macros/constants: `TRACE_SYSTEM`, `_TRACE_S390_ZCRYPT_H`, `TP_ICARSAMODEXPO`, `TP_ICARSACRT`, `TB_ZSECSENDCPRB`, `TP_ZSENDEP11CPRB`, `TP_HWRNGCPRB`, `show_zcrypt_tp_type(type)`, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.
Trace events declared: `s390_zcrypt_req`, `s390_zcrypt_rep`.

### Control Flow
Trace control flow is declarative: each TRACE_EVENT expands into tracepoint registration, fast-path
enable checks, and format metadata at build time. This file contributes events `s390_zcrypt_req`,
`s390_zcrypt_rep`, and the runtime path is driven by subsystem callers invoking the generated trace
hooks.

### State And Persistence
Tracepoint enable state, ring-buffer records, and format metadata are managed by the tracing core;
this header contributes event schemas but keeps no private persistent state.

### Dependencies
Linux tracepoint generation, ftrace/perf, subsystem drivers, and trace/define_trace.h. Direct
include dependencies detected here: `linux/tracepoint.h`, `trace/define_trace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/trace`
source-tree area and feeds the s390 architecture boundary for Linux tracepoint generation,
ftrace/perf, subsystem drivers, and trace/define_trace.h. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
trace format drift can break tooling that parses field names or event payloads

### Test Signals
tracefs format inspection, perf/ftrace event enablement, and subsystem event generation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/trace/zcrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/types.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/types.h` is a s390 kernel scalar type
extensions in the s390 ceph-client Linux source snapshot. It has 19 lines and 320 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
UAPI type inclusion plus register_pair for inline assembly operands that need even/odd register
pairs
Important macros/constants: `_ASM_S390_TYPES_H`.
Important types/layouts: `register_pair`.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
asm instruction wrappers such as SIGP/STSI/PTFF and generic type definitions. Direct include
dependencies detected here: `uapi/asm/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for asm instruction wrappers such as
SIGP/STSI/PTFF and generic type definitions. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect register-pair declaration can miscompile inline assembly constraints

### Test Signals
build coverage of low-level inline assembly wrappers
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/uaccess.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/uaccess.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/uaccess.h` is a user memory access
primitives in the s390 ceph-client Linux source snapshot. It has 485 lines and 13103 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
raw copy helpers, key-protected copy APIs, get_user/put_user macro families, string/clear helpers,
nofault kernel access, and cmpxchg with storage keys
Important macros/constants: `__S390_UACCESS_H`, `uaccess_kmsan_or_inline`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `DEFINE_PUT_USER_NOINSTR(type)`, `DEFINE_PUT_USER(type)`, `__put_user(x, ptr)`, `put_user(x, ptr)`, `DEFINE_GET_USER_NOINSTR(type)`, `DEFINE_GET_USER(type)`, `__get_user(x, ptr)`, `get_user(x, ptr)`, `__mvc_kernel_nofault(dst, src, type, err_label)`, `arch_get_kernel_nofault`, `arch_put_kernel_nofault`.
Important types/layouts: none detected.
Important declarations or inline helpers: `debug_user_asce`, `volatile`, `_copy_from_user_key`, `_copy_to_user_key`, `__put_user_bad`, `goto`, `__get_user_bad`, `strncpy_from_user`, `strnlen_user`, `__clear_user`, `memcpy`, `__s390_kernel_write`, `__mvc_kernel_nofault_bad`, `__cmpxchg_key1`, `__cmpxchg_key2`, `__cmpxchg_key4`, `__cmpxchg_key8`, `__cmpxchg_key16`, `copy_from_user_key`, `copy_to_user_key`; plus 1 more.

### Control Flow
Copy/get/put paths wrap mvcos or specialized inline assembly with exception-table fixups. The fast
path copies directly and returns zero residual/error; fault labels or condition codes compute
remaining bytes or -EFAULT, after which generic usercopy callers decide whether to zero, retry, or
report the fault.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic uaccess, exception tables, KMSAN/KASAN instrumentation, storage-key protection, futex/copy
paths, and hardened usercopy. Direct include dependencies detected here: `linux/pgtable.h`,
`asm/asm-extable.h`, `asm/processor.h`, `asm/extable.h`, `asm/facility.h`, `asm-
generic/access_ok.h`, `asm/asce.h`, `linux/instrumented.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic uaccess, exception tables,
KMSAN/KASAN instrumentation, storage-key protection, futex/copy paths, and hardened usercopy. For
UAPI files, the integration point also includes headers_install and userspace programs compiled
against the exported layout.

### Risks
exception-table, size accounting, or key mistakes can leak kernel data, corrupt userspace, or fault
recursively

### Test Signals
lib/usercopy tests, fault injection, KMSAN/KASAN builds, storage-key tests, and compat syscall
copies
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/unistd.h` is a s390 syscall-number
integration in the s390 ceph-client Linux source snapshot. It has 35 lines and 910 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
UAPI syscall inclusion plus architecture feature wants for legacy and compatibility syscalls
Important macros/constants: `_ASM_S390_UNISTD_H_`, `NR_syscalls`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`, `__ARCH_WANT_SYS_UTIME`, `__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_IPC`, `__ARCH_WANT_SYS_FADVISE64`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLD_GETRLIMIT`, `__ARCH_WANT_SYS_OLD_MMAP`, `__ARCH_WANT_SYS_OLDUMOUNT`, `__ARCH_WANT_SYS_SIGPENDING`, `__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_SYS_FORK`; plus 2 more.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generated syscall tables, seccomp, audit, and syscall wrappers. Direct include dependencies detected
here: `uapi/asm/unistd.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generated syscall tables, seccomp, audit, and
syscall wrappers. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
wrong NR_syscalls or __ARCH_WANT flags break userspace ABI compatibility

### Test Signals
syscall table generation, strace/seccomp tests, and compat userspace smoke tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/unwind.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/unwind.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/unwind.h` is a s390 unwinder API in the
s390 ceph-client Linux source snapshot. It has 98 lines and 3375 bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
unwind_state and helpers to iterate frames, recover return addresses, detect errors, and initialize
module unwind metadata
Important macros/constants: `_ASM_S390_UNWIND_H`, `unwind_for_each_frame(state, task, regs, first_frame)`.
Important types/layouts: `pt_regs`, `unwind_state`, `stack_info`, `task_struct`, `llist_node`, `module`.
Important declarations or inline helpers: `__unwind_start`, `unwind_next_frame`, `unwind_get_return_address`, `unwind_recover_ret_addr`, `unwind_done`, `unwind_error`, `unwind_start`, `unwind_init`, `unwind_module_init`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
stacktrace, ftrace, rethook, modules, perf, and exception-frame handling. Direct include
dependencies detected here: `linux/sched.h`, `linux/ftrace.h`, `linux/rethook.h`, `linux/llist.h`,
`asm/ptrace.h`, `asm/stacktrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for stacktrace, ftrace, rethook, modules, perf,
and exception-frame handling. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
ret-address recovery or stack-boundary mistakes produce bogus traces or miss hooks

### Test Signals
stacktrace/perf/ftrace tests, module unwind initialization, and IRQ/user frame unwinds
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/uprobes.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/uprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/uprobes.h` is a uprobes breakpoint ABI in
the s390 ceph-client Linux source snapshot. It has 33 lines and 588 bytes; exported UAPI contract:
no.

### Important APIs, Types, And Functions
architecture uprobe slot sizing and s390 breakpoint instruction encoding for execute-out-of-line
probes
Important macros/constants: `_ASM_UPROBES_H`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`.
Important types/layouts: `arch_uprobe`, `arch_uprobe_task`.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic uprobes, instruction decoding, notifier handling, and ptrace/debug paths. Direct include
dependencies detected here: `linux/notifier.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic uprobes, instruction decoding,
notifier handling, and ptrace/debug paths. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong breakpoint bytes or XOL size corrupt user instructions

### Test Signals
uprobes selftests, single-step emulation, and mixed 31/64-bit probe targets
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/user.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/user.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/user.h` is a legacy core-dump user layout
in the s390 ceph-client Linux source snapshot. It has 71 lines and 3237 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
struct user and register aliases used by ptrace/core-dump compatibility interfaces
Important macros/constants: `_S390_USER_H`.
Important types/layouts: `to`, `that`, `pt_regs`, `user`, `user_regs_struct`.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
ptrace, ELF core dumping, GDB expectations, and UAPI ptrace registers. Direct include dependencies
detected here: `asm/page.h`, `asm/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for ptrace, ELF core dumping, GDB expectations,
and UAPI ptrace registers. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
legacy layout changes can break debuggers and crash dump tooling

### Test Signals
ptrace register tests and GDB/core dump inspection
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/uv.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/uv.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/uv.h` is a Ultravisor protected-
virtualization interface in the s390 ceph-client Linux source snapshot. It has 641 lines and 16561
bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
UVC command codes, packed control blocks, feature bits, secure-guest lifecycle calls,
secret/attestation helpers, and secure/shared page conversion helpers
Important macros/constants: `_ASM_S390_UV_H`, `UVC_CC_OK`, `UVC_CC_ERROR`, `UVC_CC_BUSY`, `UVC_CC_PARTIAL`, `UVC_RC_EXECUTED`, `UVC_RC_INV_CMD`, `UVC_RC_INV_STATE`, `UVC_RC_INV_LEN`, `UVC_RC_NO_RESUME`, `UVC_RC_MORE_DATA`, `UVC_RC_NEED_DESTROY`, `UVC_CMD_QUI`, `UVC_CMD_QUERY_KEYS`, `UVC_CMD_INIT_UV`, `UVC_CMD_CREATE_SEC_CONF`, `UVC_CMD_DESTROY_SEC_CONF`, `UVC_CMD_DESTROY_SEC_CONF_FAST`, `UVC_CMD_CREATE_SEC_CPU`, `UVC_CMD_DESTROY_SEC_CPU`; plus 36 more.
Important types/layouts: `uv_cb_header`, `uv_cb_qui`, `uv_key_hash`, `uv_cb_query_keys`, `uv_cb_init`, `uv_cb_cgc`, `uv_cb_csc`, `uv_cb_cts`, `uv_cb_cfs`, `uv_cb_ssc`, `uv_cb_unp`, `uv_cb_cpu_set_state`, `for`, `uv_cb_nodata`, `uv_cb_destroy_fast`, `uv_cb_share`, `uv_cb_attest`, `uv_cb_dump_cpu`, `uv_cb_dump_stor_state`, `uv_cb_dump_complete`; plus 13 more.
Important declarations or inline helpers: `volatile`, `CC_TRANSFORM`, `test_bit_inv`, `share`, `uv_find_secret`, `uv_retrieve_secret`, `uv_pin_shared`, `uv_destroy_folio`, `uv_destroy_pte`, `uv_convert_from_secure_pte`, `s390_wiggle_split_folio`, `__make_folio_secure`, `uv_convert_from_secure`, `uv_convert_from_secure_folio`, `setup_uv`, `__uv_call`, `uv_call`, `uv_call_sched`, `uv_cmd_nodata`, `uv_list_secrets`; plus 5 more.

### Control Flow
Protected-virtualization callers fill an aligned control block, set a UVC command in the common
header, execute the Ultravisor call wrapper, then branch on condition code, response code, and
reason code. Page sharing helpers add memory-management state transitions around those calls.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
KVM protected virtualization, memory management, page sharing, attestation/secret drivers, and early
UV setup. Direct include dependencies detected here: `linux/types.h`, `linux/errno.h`,
`linux/bug.h`, `linux/sched.h`, `asm/page.h`, `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for KVM protected virtualization, memory
management, page sharing, attestation/secret drivers, and early UV setup. For UAPI files, the
integration point also includes headers_install and userspace programs compiled against the exported
layout.

### Risks
control-block layout or page-state bugs can leak protected guest memory or wedge secure guests

### Test Signals
PV guest lifecycle tests, UV query/secret/attestation tests, secure page conversion, and KVM
migration/dump paths
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/uv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso-symbols.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso-symbols.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso-symbols.h` is a vDSO symbol offset
helper in the s390 ceph-client Linux source snapshot. It has 9 lines and 264 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
VDSO_SYMBOL macro mapping generated offsets into task mm context fields
Important macros/constants: `__S390_VDSO_SYMBOLS_H__`, `VDSO_SYMBOL(tsk, name)`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
vDSO build, generated offsets, exec mapping, and gettimeofday/getcpu users. Direct include
dependencies detected here: `generated/vdso-offsets.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for vDSO build, generated offsets, exec mapping,
and gettimeofday/getcpu users. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
offset drift points userspace vDSO calls at the wrong symbol

### Test Signals
vDSO symbol-offset build checks and vdso selftests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso-symbols.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso.h` is a s390 vDSO metadata in the
s390 ceph-client Linux source snapshot. It has 17 lines and 291 bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
page count/version constants and getcpu initialization declaration
Important macros/constants: `__S390_VDSO_H__`, `__VDSO_PAGES`, `VDSO_VERSION_STRING`.
Important types/layouts: none detected.
Important declarations or inline helpers: `vdso_getcpu_init`.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
vDSO mapping, datapage layout, getcpu, and userspace time functions. Direct include dependencies
detected here: `vdso/datapage.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for vDSO mapping, datapage layout, getcpu, and
userspace time functions. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
page-count/version mismatch can map incomplete vDSO images

### Test Signals
vdso selftests and process exec/mmap inspection
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/clocksource.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/clocksource.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/clocksource.h` is a vDSO clocksource
mode selection in the s390 ceph-client Linux source snapshot. It has 8 lines and 196 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
declares that s390 vDSO uses the architecture TOD clock mode
Important macros/constants: `__ASM_VDSO_CLOCKSOURCE_H`, `VDSO_ARCH_CLOCKMODES`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic vDSO time code and s390 TOD clock readers. Direct include dependencies detected here: none
detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso`
source-tree area and feeds the s390 architecture boundary for generic vDSO time code and s390 TOD
clock readers. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
wrong clock mode makes vDSO time use incompatible datapage semantics

### Test Signals
vdso clock_gettime selftests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/getrandom.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/getrandom.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/getrandom.h` is a vDSO getrandom
syscall fallback in the s390 ceph-client Linux source snapshot. It has 28 lines and 787 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
inline wrapper that invokes the s390 getrandom syscall with vDSO datapage context
Important macros/constants: `__ASM_VDSO_GETRANDOM_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: `syscall3`, `getrandom_syscall`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic vDSO getrandom implementation, syscall wrappers, and random subsystem. Direct include
dependencies detected here: `vdso/datapage.h`, `asm/vdso/vsyscall.h`, `asm/syscall.h`,
`asm/unistd.h`, `asm/page.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso`
source-tree area and feeds the s390 architecture boundary for generic vDSO getrandom implementation,
syscall wrappers, and random subsystem. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
argument-register mistakes return wrong entropy or error codes

### Test Signals
getrandom vdso/selftest fallback coverage
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/getrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/gettimeofday.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/gettimeofday.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/gettimeofday.h` is a vDSO time read
hooks in the s390 ceph-client Linux source snapshot. It has 41 lines and 961 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
hardware counter reader plus syscall fallbacks for clock_gettime, gettimeofday, and clock_getres
Important macros/constants: `ASM_VDSO_GETTIMEOFDAY_H`, `VDSO_HAS_TIME`, `VDSO_HAS_CLOCK_GETRES`, `VDSO_DELTA_NOMASK`.
Important types/layouts: `vdso_time_data`, `__kernel_timespec`, `__kernel_old_timeval`, `timezone`.
Important declarations or inline helpers: `syscall2`, `__arch_get_hw_counter`, `clock_gettime_fallback`, `gettimeofday_fallback`, `clock_getres_fallback`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic vDSO timekeeping, TOD clock, syscall wrappers, and libc vDSO calls. Direct include
dependencies detected here: `asm/syscall.h`, `asm/timex.h`, `asm/unistd.h`, `linux/compiler.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso`
source-tree area and feeds the s390 architecture boundary for generic vDSO timekeeping, TOD clock,
syscall wrappers, and libc vDSO calls. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
counter or fallback ABI mistakes produce time regressions in userspace

### Test Signals
vdso clock_gettime/gettimeofday/clock_getres tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/processor.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/processor.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/processor.h` is a vDSO CPU relax hook
in the s390 ceph-client Linux source snapshot. It has 7 lines and 174 bytes; exported UAPI contract:
no.

### Important APIs, Types, And Functions
defines cpu_relax() for vDSO polling loops
Important macros/constants: `__ASM_VDSO_PROCESSOR_H`, `cpu_relax()`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic vDSO processor hooks and userspace-visible helper code. Direct include dependencies detected
here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso`
source-tree area and feeds the s390 architecture boundary for generic vDSO processor hooks and
userspace-visible helper code. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
overly heavy relax code can hurt vDSO spin loops

### Test Signals
vDSO build and stress loops using generic helpers
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/time_data.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/time_data.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/time_data.h` is a s390 vDSO
architecture time data in the s390 ceph-client Linux source snapshot. It has 11 lines and 230 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
arch_vdso_time_data extension slot, currently empty/reserved
Important macros/constants: `__S390_ASM_VDSO_TIME_DATA_H`.
Important types/layouts: `arch_vdso_time_data`.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic vDSO datapage layout and future s390 time extensions. Direct include dependencies detected
here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso`
source-tree area and feeds the s390 architecture boundary for generic vDSO datapage layout and
future s390 time extensions. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
layout changes must preserve userspace datapage compatibility

### Test Signals
vDSO datapage size/layout tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/time_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/vsyscall.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/vsyscall.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/vsyscall.h` is a vDSO data update
integration in the s390 ceph-client Linux source snapshot. It has 16 lines and 382 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
includes the generic vDSO vsyscall update helpers with s390 page-count metadata
Important macros/constants: `__ASM_VDSO_VSYSCALL_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
timekeeper updates, hrtimer code, and vDSO datapage publication. Direct include dependencies
detected here: `linux/hrtimer.h`, `vdso/datapage.h`, `asm/vdso.h`, `asm-generic/vdso/vsyscall.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso`
source-tree area and feeds the s390 architecture boundary for timekeeper updates, hrtimer code, and
vDSO datapage publication. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
incorrect data update ordering can expose inconsistent time data to userspace

### Test Signals
vDSO timekeeping selftests and seqlock consistency checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vmalloc.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vmalloc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vmalloc.h` is a vmalloc architecture
policy in the s390 ceph-client Linux source snapshot. It has 4 lines and 90 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
empty s390 override header that accepts generic vmalloc behavior
Important macros/constants: `_ASM_S390_VMALLOC_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic vmalloc/ioremap and architecture include selection. Direct include dependencies detected
here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic vmalloc/ioremap and architecture
include selection. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
future s390-specific vmalloc constraints would need to be introduced here

### Test Signals
generic vmalloc tests and build coverage
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vmlinux.lds.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vmlinux.lds.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vmlinux.lds.h` is a s390 linker-script
fragments in the s390 ceph-client Linux source snapshot. It has 33 lines and 1167 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
BOOT_DATA and BOOT_DATA_PRESERVED output sections for early boot data placement
Important macros/constants: `BOOT_DATA`, `BOOT_DATA_PRESERVED`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
vmlinux.lds.S, setup/sections.h boot-data annotations, and initmem freeing. Direct include
dependencies detected here: `asm/page.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for vmlinux.lds.S, setup/sections.h boot-data
annotations, and initmem freeing. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect section attributes can discard needed boot state or retain discardable memory

### Test Signals
link-map inspection and boot with initmem poisoning
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vmlinux.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vtime.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vtime.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vtime.h` is a virtual CPU accounting hooks
in the s390 ceph-client Linux source snapshot. It has 57 lines and 1783 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
timer update declarations for system, machine-check, and idle accounting plus idle-data access
Important macros/constants: `_S390_VTIME_H`.
Important types/layouts: `lowcore`, `s390_idle_data`.
Important declarations or inline helpers: `update_timer_sys`, `update_timer_mcck`, `update_timer_idle`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
CPU measurement facility, lowcore timers, idle accounting, and scheduler time accounting. Direct
include dependencies detected here: `asm/lowcore.h`, `asm/cpu_mf.h`, `asm/idle.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for CPU measurement facility, lowcore timers,
idle accounting, and scheduler time accounting. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
missed accounting updates skew CPU time and idle statistics

### Test Signals
vtime accounting tests, idle stress, machine-check paths, and cpuacct counters
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vtime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vtimer.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/vtimer.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vtimer.h` is a s390 virtual timer API in
the s390 ceph-client Linux source snapshot. It has 30 lines and 830 bytes; exported UAPI contract:
no.

### Important APIs, Types, And Functions
vtimer_list state and add/mod/delete helpers for one-shot and periodic virtual CPU timers
Important macros/constants: `_ASM_S390_TIMER_H`, `VTIMER_MAX_SLICE`.
Important types/layouts: `vtimer_list`, `list_head`.
Important declarations or inline helpers: `init_virt_timer`, `add_virt_timer`, `add_virt_timer_periodic`, `mod_virt_timer`, `mod_virt_timer_periodic`, `del_virt_timer`, `vtime_init`.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
CPU timer interrupt handling, vtime initialization, and list-based timer management. Direct include
dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for CPU timer interrupt handling, vtime
initialization, and list-based timer management. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
racey deletion or period updates can fire stale callbacks

### Test Signals
timer selftests, periodic timer stress, and CPU hotplug/tick tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/vtimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/word-at-a-time.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/asm/word-at-a-time.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/word-at-a-time.h` is a word-at-a-time
zero-byte scanning in the s390 ceph-client Linux source snapshot. It has 65 lines and 1564 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
s390 constants and helpers for has_zero/find_zero/zero_bytemask plus exception-safe unaligned loads
Important macros/constants: `_ASM_WORD_AT_A_TIME_H`, `WORD_AT_A_TIME_CONSTANTS`.
Important types/layouts: `word_at_a_time`.
Important declarations or inline helpers: `__fls`, `volatile`, `prep_zero_mask`, `create_zero_mask`, `find_zero`, `has_zero`, `zero_bytemask`, `load_unaligned_zeropad`.

### Control Flow
The header is mostly inline fast-path code: callers enter small assembly sequences, condition-code
extraction converts hardware results into C values, and fallback or wait loops are selected through
architecture facilities and alternative patching.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic string scanning, strncpy/strnlen, uaccess/string code, and exception-table handling. Direct
include dependencies detected here: `linux/bitops.h`, `linux/wordpart.h`, `asm/asm-extable.h`,
`asm/bitsperlong.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic string scanning, strncpy/strnlen,
uaccess/string code, and exception-table handling. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect byte-order masks break string termination and bounds handling

### Test Signals
word-at-a-time selftests, unaligned fault tests, and big-endian string cases
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/Kbuild

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/Kbuild` is a UAPI export manifest in
the s390 ceph-client Linux source snapshot. It has 4 lines and 90 bytes; exported UAPI contract:
yes.

### Important APIs, Types, And Functions
the generated-y and generic-y lists controlling which s390 asm headers are exported or generated
during headers_install
Important macros/constants: none detected.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
UAPI header installation, syscall-header generation, and userspace build environments. Direct
include dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for UAPI header installation, syscall-
header generation, and userspace build environments. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
missing entries break userspace compilation or omit generated syscall headers

### Test Signals
make headers_install and userspace include smoke tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/auxvec.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/auxvec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/auxvec.h` is a s390 auxiliary vector
constants in the s390 ceph-client Linux source snapshot. It has 9 lines and 214 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
AT_SYSINFO_EHDR and vector sizing constants used to expose the vDSO to userspace loaders
Important macros/constants: `__ASMS390_AUXVEC_H`, `AT_SYSINFO_EHDR`, `AT_VECTOR_SIZE_ARCH`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
ELF exec, glibc/musl startup, vDSO mapping, and process auxiliary vectors. Direct include
dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for ELF exec, glibc/musl startup, vDSO
mapping, and process auxiliary vectors. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong constants make runtimes miss or misread the vDSO

### Test Signals
getauxval/ld.so startup and vdso selftests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bitsperlong.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bitsperlong.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bitsperlong.h` is a userspace word-
size constants in the s390 ceph-client Linux source snapshot. It has 10 lines and 235 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
__BITS_PER_LONG selection for s390 UAPI with generic fallback inclusion
Important macros/constants: `__ASM_S390_BITSPERLONG_H`, `__BITS_PER_LONG`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
userspace ABI type sizing and generic asm headers. Direct include dependencies detected here: `asm-
generic/bitsperlong.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for userspace ABI type sizing and generic
asm headers. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
word-size drift breaks ioctl structure layout on 31/64-bit ABIs

### Test Signals
headers_install and compat userspace compile tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bpf_perf_event.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bpf_perf_event.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bpf_perf_event.h` is a BPF perf
register binding in the s390 ceph-client Linux source snapshot. It has 9 lines and 250 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
ptrace-register inclusion used by BPF perf-event programs on s390
Important macros/constants: `_UAPI__ASM_BPF_PERF_EVENT_H__`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
perf, eBPF helpers, ptrace register layout, and userspace BPF tooling. Direct include dependencies
detected here: `asm/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf, eBPF helpers, ptrace register
layout, and userspace BPF tooling. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
register layout mismatch yields wrong BPF context reads

### Test Signals
BPF perf_event selftests on s390
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/byteorder.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/byteorder.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/byteorder.h` is a s390 exported byte
order in the s390 ceph-client Linux source snapshot. It has 7 lines and 188 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
big-endian byteorder selection for userspace asm headers
Important macros/constants: `_S390_BYTEORDER_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
networking, filesystem on-disk structures, and generic endian helpers. Direct include dependencies
detected here: `linux/byteorder/big_endian.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for networking, filesystem on-disk
structures, and generic endian helpers. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong endian header silently corrupts cross-platform structure interpretation

### Test Signals
headers_install and endian conversion compile tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chpid.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chpid.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chpid.h` is a channel-path identifier
ABI in the s390 ceph-client Linux source snapshot. It has 23 lines and 456 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
chp_id layout and maximum channel-path id constant shared with channel-subsystem ioctls
Important macros/constants: `_UAPI_ASM_S390_CHPID_H`, `__MAX_CHPID`.
Important types/layouts: `chp_id`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
CHSC, SCLP, cio tooling, and userspace channel path management. Direct include dependencies detected
here: `linux/string.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for CHSC, SCLP, cio tooling, and userspace
channel path management. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
layout changes break management tools and kernel/user ioctl copies

### Test Signals
CHSC userspace tools and ioctl ABI checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chpid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chsc.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chsc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chsc.h` is a Channel-Subsystem Call
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 144 lines and 2903 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
async/sync CHSC areas, response structures, configuration descriptors, and CHSC ioctl numbers
Important macros/constants: `_ASM_CHSC_H`, `CHSC_SIZE`, `CHSC_IOCTL_MAGIC`, `CHSC_START`, `CHSC_INFO_CHANNEL_PATH`, `CHSC_INFO_CU`, `CHSC_INFO_SCH_CU`, `CHSC_INFO_CI`, `CHSC_INFO_CCL`, `CHSC_INFO_CPD`, `CHSC_INFO_DCAL`, `CHSC_START_SYNC`, `CHSC_ON_CLOSE_SET`, `CHSC_ON_CLOSE_REMOVE`.
Important types/layouts: `chsc_async_header`, `subchannel_id`, `chsc_async_area`, `chsc_header`, `chsc_sync_area`, `chsc_response_struct`, `chsc_chp_cd`, `chp_id`, `chsc_cu_cd`, `chsc_sch_cud`, `conf_id`, `chsc_conf_info`, `ccl_parm_chpid`, `ccl_parm_cssids`, `chsc_comp_list`, `chsc_dcal`, `chsc_cpd_info`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 11.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
cio userspace tools, subchannel/channel-path discovery, and hardware configuration queries. Direct
include dependencies detected here: `linux/types.h`, `linux/ioctl.h`, `asm/chpid.h`, `asm/schid.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for cio userspace tools,
subchannel/channel-path discovery, and hardware configuration queries. For UAPI files, the
integration point also includes headers_install and userspace programs compiled against the exported
layout.

### Risks
packed structure or ioctl-number drift breaks channel management utilities

### Test Signals
CHSC ioctl tests across channel path, CU, SCH-CU, CCL, and configuration queries
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/clp.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/clp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/clp.h` is a Command Logical Processor
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 29 lines and 549 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
CLP request buffer structure and synchronous CLP ioctl number
Important macros/constants: `_ASM_CLP_H`, `CLP_IOCTL_MAGIC`, `CLP_SYNC`.
Important types/layouts: `clp_req`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 1.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
PCI/zPCI and system-management userspace using CLP requests. Direct include dependencies detected
here: `linux/types.h`, `linux/ioctl.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for PCI/zPCI and system-management
userspace using CLP requests. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
size or ioctl mismatches can truncate command buffers

### Test Signals
CLP_SYNC userspace smoke tests and headers_install
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/clp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/cmb.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/cmb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/cmb.h` is a Channel Measurement Block
ABI in the s390 ceph-client Linux source snapshot. It has 54 lines and 1920 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
DASD CMB ioctl numbers and cmbdata counter structure
Important macros/constants: `_UAPIS390_CMB_H`, `BIODASDCMFENABLE`, `BIODASDCMFDISABLE`, `BIODASDREADALLCMB`.
Important types/layouts: `cmbdata`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 3.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
DASD performance monitoring tools and channel measurement collection. Direct include dependencies
detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for DASD performance monitoring tools and
channel measurement collection. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
counter layout drift corrupts performance statistics

### Test Signals
DASD CMB enable/read/disable tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/cmb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/dasd.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/dasd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/dasd.h` is a DASD block-device ioctl
ABI in the s390 ceph-client Linux source snapshot. It has 354 lines and 13078 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
DASD information, format, feature, profile, copy-pair, timeout, reservation, and UID structures plus
ioctl codes
Important macros/constants: `DASD_H`, `DASD_IOCTL_LETTER`, `DASD_API_VERSION`, `DASD_FORMAT_NONE`, `DASD_FORMAT_LDL`, `DASD_FORMAT_CDL`, `DASD_FEATURE_READONLY`, `DASD_FEATURE_USEDIAG`, `DASD_FEATURE_INITIAL_ONLINE`, `DASD_FEATURE_ERPLOG`, `DASD_FEATURE_FAILFAST`, `DASD_FEATURE_FAILONSLCK`, `DASD_FEATURE_USERAW`, `DASD_FEATURE_DISCARD`, `DASD_FEATURE_PATH_AUTODISABLE`, `DASD_FEATURE_REQUEUEQUIESCE`, `DASD_FEATURE_DEFAULT`, `DASD_PARTN_BITS`, `DASD_FMT_INT_FMT_R0`, `DASD_FMT_INT_FMT_HA`; plus 38 more.
Important types/layouts: `dasd_information2_t`, `dasd_information_t`, `dasd_rssd_perf_stats_t`, `profile_info_t`, `dasd_profile_info_t`, `format_data_t`, `dasd_copypair_swap_data_t`, `format_check_t`, `attrib_data_t`, `dasd_symmio_parms`, `dasd_snid_data`, `dasd_snid_ioctl_data`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 24.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
DASD block driver, formatting tools, storage-management utilities, and PPRC/safe-offline workflows.
Direct include dependencies detected here: `linux/types.h`, `linux/ioctl.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for DASD block driver, formatting tools,
storage-management utilities, and PPRC/safe-offline workflows. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
ABI changes risk destructive formatting or incorrect storage feature control

### Test Signals
dasdfmt/dasdview tooling, ioctl ABI tests, and feature/profile readback
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/dasd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/diag.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/diag.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/diag.h` is a diagnose ioctl payload
ABI in the s390 ceph-client Linux source snapshot. It has 32 lines and 811 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
DIAG 324 program information block and DIAG 310 memory-top buffers plus ioctl request codes
Important macros/constants: `__S390_UAPI_ASM_DIAG_H`, `DIAG_MAGIC_STR`, `DIAG324_GET_PIBBUF`, `DIAG324_GET_PIBLEN`, `DIAG310_GET_STRIDE`, `DIAG310_GET_MEMTOPLEN`, `DIAG310_GET_MEMTOPBUF`.
Important types/layouts: `diag324_pib`, `diag310_memtop`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 5.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
z/VM/LPAR diagnostic drivers and userspace management tools. Direct include dependencies detected
here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for z/VM/LPAR diagnostic drivers and
userspace management tools. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
wrong lengths or magic values produce invalid hypervisor diagnostic calls

### Test Signals
diagnose ioctl tests under z/VM and LPAR
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/fs3270.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/fs3270.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/fs3270.h` is a full-screen 3270 ioctl
ABI in the s390 ceph-client Linux source snapshot. It has 25 lines and 729 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
TUB ioctl numbers and raw3270_iocb reference for full-screen terminal buffers
Important macros/constants: `__ASM_S390_UAPI_FS3270_H`, `TUBICMD`, `TUBOCMD`, `TUBGETI`, `TUBGETO`, `TUBGETMOD`.
Important types/layouts: `raw3270_iocb`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 5.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
3270 terminal drivers and userspace terminal applications. Direct include dependencies detected
here: `linux/types.h`, `asm/ioctl.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for 3270 terminal drivers and userspace
terminal applications. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
ioctl drift breaks terminal command and buffer exchange

### Test Signals
fs3270 terminal open/ioctl tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/fs3270.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/guarded_storage.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/guarded_storage.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/guarded_storage.h` is a guarded-
storage userspace ABI in the s390 ceph-client Linux source snapshot. It has 78 lines and 1208 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
guarded-storage control block, event parameter list, control flags, and inline
load/store/save/restore helpers
Important macros/constants: `_GUARDED_STORAGE_H`, `GS_ENABLE`, `GS_DISABLE`, `GS_SET_BC_CB`, `GS_CLEAR_BC_CB`, `GS_BROADCAST`.
Important types/layouts: `gs_cb`, `gs_epl`.
Important declarations or inline helpers: `volatile`, `load_gs_cb`, `store_gs_cb`, `save_gs_cb`, `restore_gs_cb`.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
signal frames, thread context switching, and userspace guarded-storage enablement. Direct include
dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for signal frames, thread context
switching, and userspace guarded-storage enablement. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
context layout mistakes lose guarded-storage state across signal or context switches

### Test Signals
guarded-storage selftests and signal/context-switch coverage
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/guarded_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hwctrset.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hwctrset.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hwctrset.h` is a hardware counter-set
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 51 lines and 1686 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
start/read/stop structures and ioctls for CPU counter-set diagnostic access
Important macros/constants: `_PERF_CPUM_CF_DIAG_H`, `S390_HWCTR_DEVICE`, `S390_HWCTR_START_VERSION`, `S390_HWCTR_MAGIC`, `S390_HWCTR_START`, `S390_HWCTR_STOP`, `S390_HWCTR_READ`.
Important types/layouts: `s390_ctrset_start`, `s390_ctrset_setdata`, `s390_ctrset_cpudata`, `s390_ctrset_read`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 3.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
perf tooling, CPU measurement facility diagnostics, and privileged monitoring. Direct include
dependencies detected here: `linux/ioctl.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf tooling, CPU measurement facility
diagnostics, and privileged monitoring. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
counter-set version or buffer-size mismatches corrupt measurement data

### Test Signals
S390_HWCTR_* ioctl tests and perf counter validation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hwctrset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hypfs.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hypfs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hypfs.h` is a hypervisor filesystem
diagnostic ABI in the s390 ceph-client Linux source snapshot. It has 55 lines and 1382 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
DIAG 304 and DIAG 0C data layouts exported for hypfs users
Important macros/constants: `_ASM_HYPFS_H`, `HYPFS_IOCTL_MAGIC`, `HYPFS_DIAG304`.
Important types/layouts: `hypfs_diag304`, `hypfs_diag0c_hdr`, `hypfs_diag0c_entry`, `hypfs_diag0c_data`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 1.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
hypfs, z/VM/LPAR metadata reporting, and userspace virtualization inventory tools. Direct include
dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for hypfs, z/VM/LPAR metadata reporting,
and userspace virtualization inventory tools. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
layout drift misreports hypervisor CPU and partition data

### Test Signals
hypfs reads under z/VM/LPAR and ioctl structure checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/hypfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ioctls.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ioctls.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ioctls.h` is a s390 ioctl additions
in the s390 ceph-client Linux source snapshot. It has 9 lines and 191 bytes; exported UAPI contract:
yes.

### Important APIs, Types, And Functions
FIOQSIZE definition layered on generic ioctl numbers
Important macros/constants: `__ARCH_S390_IOCTLS_H__`, `FIOQSIZE`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
terminal/file ioctl users and generic asm-generic/ioctls.h inclusion. Direct include dependencies
detected here: `asm-generic/ioctls.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for terminal/file ioctl users and generic
asm-generic/ioctls.h inclusion. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
number collisions can break userspace ioctl dispatch

### Test Signals
headers_install and ioctl-number ABI checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipcbuf.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipcbuf.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipcbuf.h` is a SysV IPC permission
ABI in the s390 ceph-client Linux source snapshot. It has 31 lines and 702 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
ipc64_perm layout with s390-specific padding and type choices
Important macros/constants: `__S390_IPCBUF_H__`.
Important types/layouts: `ipc64_perm`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
SysV IPC syscalls, glibc headers, and 31/64-bit ABI compatibility. Direct include dependencies
detected here: `linux/posix_types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for SysV IPC syscalls, glibc headers, and
31/64-bit ABI compatibility. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
layout changes break shm/msg/sem permission queries

### Test Signals
ipc syscall ABI tests and compat userspace checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipcbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipl.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipl.h` is a IPL/re-IPL parameter
block ABI in the s390 ceph-client Linux source snapshot. It has 209 lines and 3849 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
IPL/re-IPL headers and FCP/NVMe/CCW/ECKD/NSS/DUMP/certificate structures used for boot and dump
control
Important macros/constants: `_ASM_S390_UAPI_IPL_H`, `IPL_PL_FLAG_IPLPS`, `IPL_PL_FLAG_SIPL`, `IPL_PL_FLAG_IPLSR`, `IPL_PL_FLAG_SBP`, `IPL_PB0_FLAG_LOADPARM`, `IPL_PB0_FCP_OPT_IPL`, `IPL_PB0_FCP_OPT_DUMP`, `IPL_PB0_NVME_OPT_IPL`, `IPL_PB0_NVME_OPT_DUMP`, `IPL_PB0_ECKD_OPT_IPL`, `IPL_PB0_ECKD_OPT_DUMP`, `IPL_PB0_CCW_VM_FLAG_NSS`, `IPL_PB0_CCW_VM_FLAG_VP`, `IPL_RB_COMPONENT_FLAG_SIGNED`, `IPL_RB_COMPONENT_FLAG_VERIFIED`.
Important types/layouts: `ipl_pl_hdr`, `ipl_pb_hdr`, `ipl_pb0_common`, `ipl_pb0_fcp`, `ipl_pb0_nvme`, `ipl_pb0_ccw`, `ipl_pb0_eckd`, `ipl_pb1_scp_data`, `ipl_rl_hdr`, `ipl_rb_hdr`, `ipl_rb_certificate_entry`, `ipl_rb_certificates`, `ipl_rb_component_entry`, `ipl_rb_components`, `ipl_pbt`, `ipl_rbt`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
s390 boot loader, sysfs reipl/dump controls, firmware IPL records, and userspace boot management.
Direct include dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for s390 boot loader, sysfs reipl/dump
controls, firmware IPL records, and userspace boot management. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
packed block drift can boot from the wrong device or lose dump configuration

### Test Signals
IPL/reipl sysfs tests across FCP, NVMe, CCW, ECKD, and dump configurations
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm.h` is a s390 KVM userspace ABI in
the s390 ceph-client Linux source snapshot. It has 622 lines and 15885 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
VM/vCPU state, interrupt, memory operation, CMMA, SIE, protected virtualization, CPU model,
migration, and crypto structures
Important macros/constants: `__LINUX_KVM_S390_H`, `__KVM_S390`, `KVM_S390_CMMA_PEEK`, `KVM_S390_RESET_POR`, `KVM_S390_RESET_CLEAR`, `KVM_S390_RESET_SUBSYSTEM`, `KVM_S390_RESET_CPU_INIT`, `KVM_S390_RESET_IPL`, `KVM_S390_MEMOP_LOGICAL_READ`, `KVM_S390_MEMOP_LOGICAL_WRITE`, `KVM_S390_MEMOP_SIDA_READ`, `KVM_S390_MEMOP_SIDA_WRITE`, `KVM_S390_MEMOP_ABSOLUTE_READ`, `KVM_S390_MEMOP_ABSOLUTE_WRITE`, `KVM_S390_MEMOP_ABSOLUTE_CMPXCHG`, `KVM_S390_MEMOP_F_CHECK_ONLY`, `KVM_S390_MEMOP_F_INJECT_EXCEPTION`, `KVM_S390_MEMOP_F_SKEY_PROTECTION`, `KVM_S390_MEMOP_EXTENSION_CAP_BASE`, `KVM_S390_MEMOP_EXTENSION_CAP_CMPXCHG`; plus 119 more.
Important types/layouts: `kvm_s390_skeys`, `kvm_s390_cmma_log`, `kvm_s390_mem_op`, `kvm_s390_psw`, `kvm_s390_interrupt`, `kvm_s390_io_info`, `kvm_s390_ext_info`, `kvm_s390_pgm_info`, `kvm_s390_prefix_info`, `kvm_s390_extcall_info`, `kvm_s390_emerg_info`, `kvm_s390_stop_info`, `kvm_s390_mchk_info`, `kvm_s390_irq`, `kvm_s390_irq_state`, `kvm_s390_ucas_mapping`, `kvm_s390_pv_sec_parm`, `kvm_s390_pv_unp`, `kvm_s390_pv_dmp`, `kvm_s390_pv_info_dump`; plus 25 more.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 1.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
QEMU/KVM, libvirt, migration tooling, protected virtualization, and KVM ioctls. Direct include
dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for QEMU/KVM, libvirt, migration tooling,
protected virtualization, and KVM ioctls. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
ABI drift breaks virtual machines, migration streams, or protected-guest isolation

### Test Signals
KVM selftests, QEMU boot/migration, PV guest tests, and ioctl layout checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_para.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_para.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_para.h` is a s390 KVM paravirtual
header placeholder in the s390 ceph-client Linux source snapshot. It has 8 lines and 224 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
an intentionally empty exported header reserved for s390 paravirtual definitions
Important macros/constants: none detected.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
generic KVM para include paths and userspace build compatibility. Direct include dependencies
detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for generic KVM para include paths and
userspace build compatibility. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
adding ABI here requires stable definitions and headers_install validation

### Test Signals
headers_install and userspace include tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_perf.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_perf.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_perf.h` is a s390 KVM perf trace
ABI in the s390 ceph-client Linux source snapshot. It has 22 lines and 474 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
decode string length and trace-field index constants for KVM entry/exit perf events
Important macros/constants: `__LINUX_KVM_PERF_S390_H`, `DECODE_STR_LEN`, `VCPU_ID`, `KVM_ENTRY_TRACE`, `KVM_EXIT_TRACE`, `KVM_EXIT_REASON`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
perf trace decoding, KVM tracepoints, and SIE intercept definitions. Direct include dependencies
detected here: `asm/sie.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf trace decoding, KVM tracepoints,
and SIE intercept definitions. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
index drift makes perf decode the wrong vCPU or exit reason fields

### Test Signals
perf kvm trace tests and tracepoint format inspection
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/monwriter.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/monwriter.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/monwriter.h` is a z/VM monitor writer
ABI in the s390 ceph-client Linux source snapshot. It has 32 lines and 939 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
monitor event header and ioctl constants for interval/config/event writes
Important macros/constants: `_ASM_390_MONWRITER_H`, `MONWRITE_START_INTERVAL`, `MONWRITE_STOP_INTERVAL`, `MONWRITE_GEN_EVENT`, `MONWRITE_START_CONFIG`.
Important types/layouts: `monwrite_hdr`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
monwriter character device and z/VM monitor-stream consumers. Direct include dependencies detected
here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for monwriter character device and z/VM
monitor-stream consumers. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
header or ioctl drift corrupts monitor records delivered to z/VM

### Test Signals
monwriter ioctl smoke tests and z/VM monitor record validation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/monwriter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/perf_regs.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/perf_regs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/perf_regs.h` is a perf register
enumeration in the s390 ceph-client Linux source snapshot. It has 44 lines and 887 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
s390 perf_event register ids for general, mask, and address registers
Important macros/constants: `_ASM_S390_PERF_REGS_H`.
Important types/layouts: `perf_event_s390_regs`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
perf sampling, BPF stack/register capture, and userspace unwinding tools. Direct include
dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf sampling, BPF stack/register
capture, and userspace unwinding tools. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
renumbering breaks perf sample decoding and BPF register access

### Test Signals
perf regs selftests and sample register dumps
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/pkey.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/pkey.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/pkey.h` is a protected-key crypto
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 473 lines and 21097 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
APQN identifiers, secure/protected/clear key blobs, EP11/CCA metadata, key-type flags, and pkey
ioctl request structures
Important macros/constants: `_UAPI_PKEY_H`, `PKEY_IOCTL_MAGIC`, `SECKEYBLOBSIZE`, `PROTKEYBLOBSIZE`, `MAXPROTKEYSIZE`, `MAXCLRKEYSIZE`, `MAXAESCIPHERKEYSIZE`, `MINEP11AESKEYBLOBSIZE`, `MAXEP11AESKEYBLOBSIZE`, `MINKEYBLOBSIZE`, `PKEY_KEYTYPE_AES_128`, `PKEY_KEYTYPE_AES_192`, `PKEY_KEYTYPE_AES_256`, `PKEY_KEYTYPE_ECC`, `PKEY_KEYTYPE_ECC_P256`, `PKEY_KEYTYPE_ECC_P384`, `PKEY_KEYTYPE_ECC_P521`, `PKEY_KEYTYPE_ECC_ED25519`, `PKEY_KEYTYPE_ECC_ED448`, `PKEY_KEYTYPE_AES_XTS_128`; plus 32 more.
Important types/layouts: `pkey_apqn`, `pkey_seckey`, `pkey_protkey`, `pkey_clrkey`, `ep11kblob_header`, `pkey_genseck`, `pkey_clr2seck`, `pkey_sec2protk`, `pkey_clr2protk`, `pkey_findcard`, `pkey_skey2pkey`, `pkey_verifykey`, `pkey_genprotk`, `pkey_verifyprotk`, `pkey_kblob2pkey`, `pkey_genseck2`, `pkey_clr2seck2`, `pkey_verifykey2`, `pkey_kblob2pkey2`, `pkey_apqns4key`; plus 5 more.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 17.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
pkey device, zcrypt/AP cards, dm-crypt protected-key flows, and userspace key-management tools.
Direct include dependencies detected here: `linux/ioctl.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for pkey device, zcrypt/AP cards, dm-crypt
protected-key flows, and userspace key-management tools. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
size/flag mistakes can expose key material or select the wrong crypto adapter/domain

### Test Signals
pkey ioctl selftests, AP queue selection tests, EP11/CCA key conversion, and negative size checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/pkey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/posix_types.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/posix_types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/posix_types.h` is a s390 POSIX type
ABI in the s390 ceph-client Linux source snapshot. It has 45 lines and 1278 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
kernel typedef overrides for size, dev, uid/gid, ino, mode, and ipc pid before generic POSIX types
Important macros/constants: `__ARCH_S390_POSIX_TYPES_H`, `__kernel_size_t`, `__kernel_old_dev_t`, `__kernel_old_uid_t`, `__kernel_ino_t`, `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_uid_t`, `__kernel_gid_t`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
glibc/musl headers, syscall structures, and compat ABI. Direct include dependencies detected here:
`asm-generic/posix_types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for glibc/musl headers, syscall
structures, and compat ABI. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
type-size changes break stat/ipc/ioctl structures

### Test Signals
headers_install and 31/64-bit userspace ABI checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ptrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ptrace.h` is a s390 ptrace/register
ABI in the s390 ceph-client Linux source snapshot. It has 332 lines and 8724 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
pt_regs offsets, PSW/GPR/ACR/FPR/PER constants, and user_regs_struct layout
Important macros/constants: `_UAPI_S390_PTRACE_H`, `PT_PSWMASK`, `PT_PSWADDR`, `PT_GPR0`, `PT_GPR1`, `PT_GPR2`, `PT_GPR3`, `PT_GPR4`, `PT_GPR5`, `PT_GPR6`, `PT_GPR7`, `PT_GPR8`, `PT_GPR9`, `PT_GPR10`, `PT_GPR11`, `PT_GPR12`, `PT_GPR13`, `PT_GPR14`, `PT_GPR15`, `PT_ACR0`; plus 99 more.
Important types/layouts: `user_regs_struct`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
ptrace, core dumps, debuggers, seccomp/audit register access, and perf. Direct include dependencies
detected here: `linux/const.h`, `linux/stddef.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for ptrace, core dumps, debuggers,
seccomp/audit register access, and perf. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
offset drift breaks debuggers and syscall tracing

### Test Signals
ptrace selftests, GDB register dumps, core-file validation, and compat debug sessions
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/qeth.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/qeth.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/qeth.h` is a qeth network ioctl ABI
in the s390 ceph-client Linux source snapshot. It has 116 lines and 3119 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
ARP cache/query and OAT data structures plus qeth-specific SIOC ioctl numbers
Important macros/constants: `__ASM_S390_QETH_IOCTL_H__`, `SIOC_QETH_ARP_SET_NO_ENTRIES`, `SIOC_QETH_ARP_QUERY_INFO`, `SIOC_QETH_ARP_ADD_ENTRY`, `SIOC_QETH_ARP_REMOVE_ENTRY`, `SIOC_QETH_ARP_FLUSH_CACHE`, `SIOC_QETH_ADP_SET_SNMP_CONTROL`, `SIOC_QETH_GET_CARD_TYPE`, `SIOC_QETH_QUERY_OAT`, `QETH_QARP_MEDIASPECIFIC_BYTES`, `QETH_QARP_MACADDRTYPE_BYTES`, `QETH_QARP_STRIP_ENTRIES`, `QETH_QARP_WITH_IPV6`, `QETH_QARP_REQUEST_MASK`, `QETH_QARP_USER_DATA_SIZE`, `QETH_QARP_MASK_OFFSET`, `QETH_QARP_ENTRIES_OFFSET`.
Important types/layouts: `qeth_arp_cache_entry`, `qeth_arp_entrytype`, `qeth_arp_qi_entry7`, `qeth_arp_qi_entry7_ipv6`, `qeth_arp_qi_entry7_short`, `qeth_arp_qi_entry7_short_ipv6`, `qeth_arp_qi_entry5`, `qeth_arp_qi_entry5_ipv6`, `qeth_arp_qi_entry5_short`, `qeth_arp_qi_entry5_short_ipv6`, `qeth_arp_query_user_data`, `qeth_query_oat_data`, `qeth_arp_ipaddrtype`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
qeth L2/L3 network driver and userspace network management tools. Direct include dependencies
detected here: `linux/types.h`, `linux/ioctl.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for qeth L2/L3 network driver and
userspace network management tools. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
structure drift breaks ARP/OAT diagnostics or adapter-control commands

### Test Signals
qeth ioctl tests, ARP query/add/remove, and OAT readback
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/qeth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/raw3270.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/raw3270.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/raw3270.h` is a raw 3270 terminal
command ABI in the s390 ceph-client Linux source snapshot. It has 75 lines and 2168 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
3270 command/order byte constants and buffer-size limits used by raw/full-screen terminal clients
Important macros/constants: `__ASM_S390_UAPI_RAW3270_H`, `TC_WRITE`, `TC_RDBUF`, `TC_EWRITE`, `TC_READMOD`, `TC_EWRITEA`, `TC_WRITESF`, `TO_GE`, `TO_SF`, `TO_SBA`, `TO_IC`, `TO_PT`, `TO_RA`, `TO_SFE`, `TO_EUA`, `TO_MF`, `TO_SA`, `TF_INPUT`, `TF_INPUTN`, `TF_INMDT`; plus 33 more.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
raw3270/fs3270 drivers and terminal emulators. Direct include dependencies detected here: none
detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for raw3270/fs3270 drivers and terminal
emulators. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
wrong command constants corrupt terminal protocol streams

### Test Signals
3270 terminal command tests and emulator interop
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/raw3270.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/runtime_instr.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/runtime_instr.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/runtime_instr.h` is a runtime-
instrumentation userspace ABI in the s390 ceph-client Linux source snapshot. It has 74 lines and
1424 bytes; exported UAPI contract: yes.

### Important APIs, Types, And Functions
runtime-instrumentation start/stop commands, control block layout, and inline load/store control-
block helpers
Important macros/constants: `_S390_UAPI_RUNTIME_INSTR_H`, `S390_RUNTIME_INSTR_START`, `S390_RUNTIME_INSTR_STOP`.
Important types/layouts: `runtime_instr_cb`.
Important declarations or inline helpers: `volatile`, `load_runtime_instr_cb`, `store_runtime_instr_cb`.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
runtime_instr syscall/device paths, task context management, and performance/debug tooling. Direct
include dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for runtime_instr syscall/device paths,
task context management, and performance/debug tooling. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
control-block layout mistakes misprogram hardware runtime instrumentation

### Test Signals
runtime-instrumentation start/stop and context-switch tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/runtime_instr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/schid.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/schid.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/schid.h` is a subchannel-id userspace
ABI in the s390 ceph-client Linux source snapshot. It has 20 lines and 382 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
subchannel_id bitfield layout shared with CHSC and KVM I/O interrupt APIs
Important macros/constants: `_UAPIASM_SCHID_H`.
Important types/layouts: `subchannel_id`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
cio ioctls, userspace channel tooling, and KVM I/O injection. Direct include dependencies detected
here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for cio ioctls, userspace channel tooling,
and KVM I/O injection. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
bitfield drift addresses the wrong channel device

### Test Signals
CHSC/KVM subchannel id encode/decode tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/schid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sclp_ctl.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sclp_ctl.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sclp_ctl.h` is a SCLP control-device
ioctl ABI in the s390 ceph-client Linux source snapshot. It has 25 lines and 465 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
sclp_ctl_sccb pointer/length wrapper and ioctl number for submitting SCCBs
Important macros/constants: `_ASM_SCLP_CTL_H`, `SCLP_CTL_IOCTL_MAGIC`, `SCLP_CTL_SCCB`.
Important types/layouts: `sclp_ctl_sccb`.
Important declarations or inline helpers: none detected.
Detected ioctl-style command definitions: 1.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
sclp_ctl userspace tooling and SCLP event/service-call paths. Direct include dependencies detected
here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for sclp_ctl userspace tooling and SCLP
event/service-call paths. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
pointer/length mismatch can submit malformed SCCBs to firmware

### Test Signals
SCLP_CTL_SCCB ioctl tests and SCCB length validation
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sclp_ctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/setup.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/setup.h` is a exported setup
placeholder in the s390 ceph-client Linux source snapshot. It has 1 lines and 63 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
an empty UAPI header kept for include compatibility with generic setup consumers
Important macros/constants: none detected.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
headers_install and userspace code including asm/setup.h. Direct include dependencies detected here:
none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for headers_install and userspace code
including asm/setup.h. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
removal can break source compatibility even though it defines no constants

### Test Signals
headers_install and userspace include smoke tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sie.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sie.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sie.h` is a SIE intercept decode ABI
in the s390 ceph-client Linux source snapshot. It has 252 lines and 9469 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
diagnose, SIGP, program-interrupt, and instruction-intercept macro tables plus decoding helpers used
by KVM trace tooling
Important macros/constants: `_UAPI_ASM_S390_SIE_H`, `diagnose_codes`, `sigp_order_codes`, `icpt_prog_codes`, `exit_code_ipa0(ipa0, opcode, mnemonic)`, `exit_code(opcode, mnemonic)`, `icpt_insn_codes`, `sie_intercept_code`, `INSN_DECODE_IPA0(ipa0, insn, rshift, mask)`, `INSN_DECODE(insn)`, `icpt_insn_decoder(insn)`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
KVM, perf trace decoding, QEMU diagnostics, and SIE intercept reporting. Direct include dependencies
detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for KVM, perf trace decoding, QEMU
diagnostics, and SIE intercept reporting. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
decode macro drift makes userspace misclassify guest exits

### Test Signals
KVM tracepoint decode tests and intercepted instruction coverage
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sigcontext.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sigcontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sigcontext.h` is a s390 signal-
context ABI in the s390 ceph-client Linux source snapshot. It has 70 lines and 1432 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
saved PSW/GPR/ACR/FPR/vector register pointers, signal mask sizing, and frame-size constants
Important macros/constants: `_ASM_S390_SIGCONTEXT_H`, `__NUM_GPRS`, `__NUM_FPRS`, `__NUM_ACRS`, `__NUM_VXRS`, `__NUM_VXRS_LOW`, `__NUM_VXRS_HIGH`, `_SIGCONTEXT_NSIG`, `_SIGCONTEXT_NSIG_BPW`, `__SIGNAL_FRAMESIZE`, `_SIGCONTEXT_NSIG_WORDS`, `_SIGMASK_COPY_SIZE`.
Important types/layouts: `sigcontext`.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
signal delivery/return, glibc sigcontext, ptrace, and core dumps. Direct include dependencies
detected here: `linux/compiler.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for signal delivery/return, glibc
sigcontext, ptrace, and core dumps. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
layout changes break signal return and debugger signal-frame decoding

### Test Signals
rt-signal selftests, vector-register signal tests, and compat signal frames
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/signal.h` is a s390 signal userspace
ABI in the s390 ceph-client Linux source snapshot. It has 115 lines and 3058 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
signal numbers, sigaction/old_sigaction/sigaltstack declarations, mask sizing, and SA_RESTORER
support
Important macros/constants: `_UAPI_ASMS390_SIGNAL_H`, `NSIG`, `SIGHUP`, `SIGINT`, `SIGQUIT`, `SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGKILL`, `SIGUSR1`, `SIGSEGV`, `SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, `SIGSTKFLT`, `SIGCHLD`; plus 24 more.
Important types/layouts: `siginfo`, `pt_regs`, `old_sigaction`, `sigaction`, `sigaltstack`.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
glibc signal headers, kernel signal delivery, and compat userland. Direct include dependencies
detected here: `linux/types.h`, `linux/time.h`, `asm-generic/signal-defs.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for glibc signal headers, kernel signal
delivery, and compat userland. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
renumbering or struct layout changes are userspace ABI breaks

### Test Signals
signal selftests, sigaltstack, and old/new sigaction compatibility
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/stat.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/stat.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/stat.h` is a s390 stat structure ABI
in the s390 ceph-client Linux source snapshot. It has 34 lines and 809 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
struct stat layout with nanosecond timestamp support
Important macros/constants: `_S390_STAT_H`, `STAT_HAVE_NSEC`.
Important types/layouts: `stat`.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
stat/fstat/lstat syscalls, libc, and filesystem tooling. Direct include dependencies detected here:
none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for stat/fstat/lstat syscalls, libc, and
filesystem tooling. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
field alignment drift breaks file metadata reads

### Test Signals
stat syscall ABI tests and 31/64-bit userspace checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/statfs.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/statfs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/statfs.h` is a s390 statfs ABI in the
s390 ceph-client Linux source snapshot. It has 51 lines and 1058 bytes; exported UAPI contract: yes.

### Important APIs, Types, And Functions
statfs/statfs64 layout for filesystem statistics
Important macros/constants: `_S390_STATFS_H`.
Important types/layouts: `statfs`, `statfs64`.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
statfs syscalls, libc, and filesystem utilities. Direct include dependencies detected here:
`linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for statfs syscalls, libc, and filesystem
utilities. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
padding or type-size drift breaks filesystem capacity reporting

### Test Signals
statfs syscall ABI tests across filesystems
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sthyi.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sthyi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sthyi.h` is a STHYI function-code ABI
in the s390 ceph-client Linux source snapshot. It has 7 lines and 178 bytes; exported UAPI contract:
yes.

### Important APIs, Types, And Functions
capacity-information function code exported to userspace
Important macros/constants: `_UAPI_ASM_STHYI_H`, `STHYI_FC_CP_IFL_CAP`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
STHYI diagnostics, hypfs, and virtualization inventory tools. Direct include dependencies detected
here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for STHYI diagnostics, hypfs, and
virtualization inventory tools. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
wrong function code returns invalid capacity information

### Test Signals
STHYI userspace calls under supported hypervisors
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sthyi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/types.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/types.h` is a s390 exported integer
types in the s390 ceph-client Linux source snapshot. It has 30 lines and 513 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
generic int-ll64 type inclusion for UAPI consumers
Important macros/constants: `_UAPI_S390_TYPES_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
all exported asm headers and libc/kernel type consistency. Direct include dependencies detected
here: `asm-generic/int-ll64.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for all exported asm headers and
libc/kernel type consistency. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
type model drift breaks ioctl and syscall structures

### Test Signals
headers_install and ABI layout checks
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ucontext.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ucontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ucontext.h` is a s390 ucontext ABI in
the s390 ceph-client Linux source snapshot. It has 41 lines and 1207 bytes; exported UAPI contract:
yes.

### Important APIs, Types, And Functions
ucontext and ucontext_extended layouts with high-GPR and vector-register flags
Important macros/constants: `_ASM_S390_UCONTEXT_H`, `UC_GPRS_HIGH`, `UC_VXRS`.
Important types/layouts: `ucontext_extended`, `ucontext`.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
signal frames, getcontext/setcontext, libc, and vector-register restore. Direct include dependencies
detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for signal frames, getcontext/setcontext,
libc, and vector-register restore. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
layout drift corrupts user context switching and signal restore

### Test Signals
libc context tests, signal ucontext inspection, and vector-register cases
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/unistd.h` is a s390 syscall header
export in the s390 ceph-client Linux source snapshot. It has 13 lines and 269 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
generated 64-bit syscall numbers and guard for userspace asm/unistd.h
Important macros/constants: `_UAPI_ASM_S390_UNISTD_H_`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
libc syscall wrappers, seccomp/audit tooling, and headers_install. Direct include dependencies
detected here: `asm/unistd_64.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for libc syscall wrappers, seccomp/audit
tooling, and headers_install. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
stale generated inclusion breaks syscall numbering

### Test Signals
headers_install, syscall-number comparison, and seccomp user tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/unistd.h -->
