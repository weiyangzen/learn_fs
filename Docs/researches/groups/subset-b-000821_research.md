# subset-b-000821 research

Grouped source-tree-aligned research for s390 hypfs and architecture headers. Each source file section is delimited for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/inode.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/inode.c

Purpose: Implements the s390 hypervisor filesystem `s390_hypfs`, a single-instance pseudo filesystem exposing VM or LPAR hypervisor data and a writable `update` trigger.

Important APIs/types/functions: `hypfs_sb_info`, mount option parsing for `uid` and `gid`, inode/dentry creation helpers, `hypfs_read_iter()`, `hypfs_write_iter()`, `hypfs_create_u64()`, `hypfs_create_str()`, and filesystem registration through `__hypfs_fs_init()`. Source-visible declarations include: #define pr_fmt(fmt) "hypfs: " fmt; #define HYPFS_MAGIC 0x687970 /* ASCII 'hyp' */; #define TMP_SIZE 64 /* size of temporary buffers */; struct hypfs_sb_info {; struct dentry *update_file; /* file to trigger update */; struct mutex lock; /* lock to protect update process */; struct hypfs_sb_info *sb_info = sb->s_fs_info;; struct inode *inode = d_inode(sb_info->update_file);; struct dentry *next_dentry = hypfs_last_dentry->d_fsdata;; struct inode *ret = new_inode(sb);.

Control flow: Mount setup creates the root, asks the VM or DIAG backend to populate files, creates `update`, and records a monotonic timestamp. Regular file open snapshots `i_private` data under the superblock mutex. Writes to `update` are rate limited to one per second, delete the tracked top-level generated tree, repopulate from backend data, and advance the timestamp.

State and persistence behavior: Persistent state is per-superblock uid/gid, last-update time, update dentry, and generated inode `i_private` strings; `hypfs_last_dentry` globally tracks top-level generated dentries for update removal.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/errno.h>, #include <linux/fs.h>, #include <linux/fs_context.h>, #include <linux/fs_parser.h>, #include <linux/namei.h>, #include <linux/vfs.h>, #include <linux/slab.h>. Integrated with The file integrates VFS/fs_context/simplefs helpers, sysfs mount-point creation below `hypervisor_kobj`, s390 VM detection, EBCDIC conversion, and backend helpers from `hypfs.h`..

Risks: The global deletion list is not per-superblock even though the filesystem type uses `get_tree_single`; changing mount semantics would make this unsafe. Update repopulation is expensive and can race readers unless callers use the timestamp protocol.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 448 lines, 10904 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/Kbuild

Purpose: Controls generated asm-generic wrapper headers exported for s390 asm includes.

Important APIs/types/functions: `generic-y` entries for `early_ioremap.h`, `mcs_spinlock.h`, `qspinlock.h`, `qspinlock_types.h`, `qrwlock.h`, `qrwlock_types.h`, `user.h`, and `vmlinux.lds.h`. Source-visible declarations include: no direct declarations beyond include guards or build directives.

Control flow: Kbuild reads this file during header generation and emits wrappers for generic asm headers that s390 does not override locally.

State and persistence behavior: No runtime state; it shapes the generated include tree and therefore build-time ABI surface.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates with the Linux Kbuild asm-generic wrapper mechanism and any source including the listed asm headers..

Risks: Removing or renaming entries can break architecture builds or silently switch code away from generic lock/header implementations.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 9 lines, 228 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/abs_lowcore.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/abs_lowcore.h

Purpose: Declares absolute lowcore mapping helpers for accessing per-CPU lowcore memory at fixed absolute addresses.

Important APIs/types/functions: `ABS_LOWCORE_MAP_SIZE`, `__abs_lowcore`, `abs_lowcore_map()`, `abs_lowcore_unmap()`, `get_abs_lowcore()`, and `put_abs_lowcore()`. Source-visible declarations include: #define _ASM_S390_ABS_LOWCORE_H; #define ABS_LOWCORE_MAP_SIZE (NR_CPUS * sizeof(struct lowcore)); extern unsigned long __abs_lowcore;; int abs_lowcore_map(int cpu, struct lowcore *lc, bool alloc);; void abs_lowcore_unmap(int cpu);; static inline struct lowcore *get_abs_lowcore(void); int cpu;; static inline void put_abs_lowcore(struct lowcore *lc).

Control flow: `get_abs_lowcore()` maps the current CPU lowcore into the absolute-lowcore window, disables preemption to pin the CPU, and returns a typed pointer; `put_abs_lowcore()` unmaps and reenables preemption.

State and persistence behavior: State is the architecture-managed absolute lowcore mapping and the preemption-disabled critical section around a caller's access.

Dependencies and integration points: Direct includes are #include <linux/smp.h>, #include <asm/lowcore.h>. Integrated with Depends on `struct lowcore`, CPU IDs, `preempt_disable/enable`, and low-level memory mapping implementation..

Risks: Callers must pair get/put and keep access short; CPU migration or stale mappings would expose the wrong lowcore.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 28 lines, 595 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/abs_lowcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/access-regs.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/access-regs.h

Purpose: Provides helpers for saving and restoring s390 access registers.

Important APIs/types/functions: `struct access_regs`, `save_access_regs()`, and `restore_access_regs()` using `stam` and `lam` instructions. Source-visible declarations include: #define __ASM_S390_ACCESS_REGS_H; struct access_regs {; unsigned int regs[NUM_ACRS];; static inline void save_access_regs(unsigned int *acrs); struct access_regs *regs = (struct access_regs *)acrs;; static inline void restore_access_regs(unsigned int *acrs); struct access_regs *regs = (struct access_regs *)acrs;.

Control flow: Inline assembly stores or loads access registers 0 through 15 to caller-provided memory.

State and persistence behavior: No header-owned state; it serializes register state into caller storage.

Dependencies and integration points: Direct includes are #include <linux/instrumented.h>, #include <asm/sigcontext.h>. Integrated with Used by low-level context switch, signal, ptrace, and address-space-control code that needs access-register preservation..

Risks: The memory layout must match hardware register order; wrong buffers or missing clobbers corrupt task address-space state.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 38 lines, 806 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/access-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/airq.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/airq.h

Purpose: Declares adapter interrupt registration and interrupt-vector management for s390 I/O adapters.

Important APIs/types/functions: `airq_struct`, `airq_iv`, `register_adapter_interrupt()`, `unregister_adapter_interrupt()`, allocation/scan/free helpers, bit locks, per-bit data, and pointer tagging helpers. Source-visible declarations include: #define _ASM_S390_AIRQ_H; struct airq_struct {; struct hlist_node list; /* Handler queueing. */; void (*handler)(struct airq_struct *airq, struct tpi_info *tpi_info);; #define AIRQ_PTR_ALLOCATED 0x01; int register_adapter_interrupt(struct airq_struct *airq);; void unregister_adapter_interrupt(struct airq_struct *airq);; struct airq_iv {; unsigned long *vector; /* Adapter interrupt bit vector */; unsigned long *avail; /* Allocation bit mask for the bit vector */.

Control flow: Drivers register an adapter interrupt descriptor with a handler and summary indicator, allocate bits from an interrupt vector, lock or unlock bit ownership, and scan for pending interrupt indicators.

State and persistence behavior: Persistent state is vector memory, allocation and lock bitmaps, optional per-bit data/pointer arrays, and registered adapter interrupt descriptors.

Dependencies and integration points: Direct includes are #include <linux/bit_spinlock.h>, #include <linux/dma-mapping.h>, #include <asm/tpi.h>. Integrated with Integrates with PCI, AP, virtio, and other adapter-interrupt users plus s390 interrupt delivery..

Risks: Bit allocation, guest-pinned vectors, and pointer tagging are concurrency-sensitive; lost unlocks or stale bit metadata can drop interrupts or leak pinned memory.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 110 lines, 3370 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/airq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/alternative.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/alternative.h

Purpose: Defines the s390 alternative-instruction metadata format and assembly macros for CPU/facility/speculation patching.

Important APIs/types/functions: `struct alt_instr`, `ALT_FACILITY()`, `ALT_FEATURE()`, `ALT_SPEC()`, `apply_alternative_instructions()`, `ALTERNATIVE`, and `ALTERNATIVE_2` C and assembler macros. Source-visible declarations include: #define _ASM_S390_ALTERNATIVE_H; #define ALT_CTX_EARLY 1; #define ALT_CTX_LATE 2; #define ALT_CTX_ALL (ALT_CTX_EARLY | ALT_CTX_LATE); #define ALT_TYPE_FACILITY 0; #define ALT_TYPE_FEATURE 1; #define ALT_TYPE_SPEC 2; #define ALT_DATA_SHIFT 0; #define ALT_TYPE_SHIFT 20; #define ALT_CTX_SHIFT 28.

Control flow: Compile-time macros place old instructions in text, replacement bytes in `.altinstr_replacement`, and descriptors in `.altinstructions`; early or late patching walks descriptor ranges and overwrites text when feature predicates match.

State and persistence behavior: State is linker-emitted patch metadata and patched kernel text; replacements persist for the running image.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/stddef.h>, #include <linux/stringify.h>. Integrated with Integrates CPU facility probing, decompressor and early kernel patching, speculation mitigations, assembly code, and runtime text patching..

Risks: Descriptor length, alignment, and context bits are text-patching ABI. Bad alternatives can execute partial instructions or apply too early/late.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 238 lines, 7424 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/alternative.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ap.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ap.h

Purpose: Exposes inline instruction wrappers and data structures for s390 Adjunct Processor crypto queues.

Important APIs/types/functions: `ap_qid_t`, queue status unions, TAPQ/QCI/AQIC/QACT config structures, AP bind/associate helpers, `ap_nqap()`, and `ap_dqap()`. Source-visible declarations include: #define _ASM_S390_AP_H_; typedef unsigned int ap_qid_t;; #define AP_MKQID(_card, _queue) (((_card) & 0xff) << 8 | ((_queue) & 0xff)); #define AP_QID_CARD(_qid) (((_qid) >> 8) & 0xff); #define AP_QID_QUEUE(_qid) ((_qid) & 0xff); struct ap_queue_status {; union {; unsigned int value : 32;; struct {; unsigned int status_bits : 8;.

Control flow: Wrappers load AP queue IDs and control blocks into fixed general registers, issue PQAP/NQAP/DQAP instructions, loop on partial completion where required, and return hardware queue status words to AP bus and crypto drivers.

State and persistence behavior: State lives in AP hardware queues, configuration masks, interrupt indicators, message buffers, residual receive state, and caller-supplied control blocks.

Dependencies and integration points: Direct includes are #include <linux/io.h>, #include <asm/asm-extable.h>. Integrated with Integrates with s390 AP bus, zcrypt, vfio-ap, protected/secure execution queue handling, adapter interrupts, and exception-table recovery..

Risks: Register conventions and partial-completion handling are critical. `ap_dqap()` truncation uses response code `0xff` and residual GR0 handoff, so callers must preserve continuation state correctly.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 566 lines, 16432 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/appldata.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/appldata.h

Purpose: Defines the VM DIAG X'DC' application-data parameter block and call helper.

Important APIs/types/functions: `APPLDATA_*` function codes, `appldata_parameter_list`, `appldata_product_id`, and `appldata_asm()`. Source-visible declarations include: #define _ASM_S390_APPLDATA_H; #define APPLDATA_START_INTERVAL_REC 0x80; #define APPLDATA_STOP_REC 0x81; #define APPLDATA_GEN_EVENT_REC 0x82; #define APPLDATA_START_CONFIG_REC 0x83; struct appldata_parameter_list {; u64 product_id_addr;; u64 buffer_addr;; struct appldata_product_id {; static inline int appldata_asm(struct appldata_parameter_list *parm_list,.

Control flow: `appldata_asm()` refuses non-VM environments, fills physical addresses for the product ID and data buffer, increments DIAG statistics, and executes `diag 0xdc`.

State and persistence behavior: State is CP/VM application-data monitor state plus caller buffers visible through physical addresses.

Dependencies and integration points: Direct includes are #include <linux/io.h>, #include <asm/machine.h>, #include <asm/diag.h>. Integrated with Integrates with z/VM, machine detection, DIAG statistics, and monitoring record producers..

Risks: Buffer lengths and physical address translation must match the packed firmware contract; invoking outside VM correctly returns unsupported.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 69 lines, 1634 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/appldata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch-stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/arch-stackprotector.h

Purpose: Declares s390 stack protector guard patching for early and regular kernel code.

Important APIs/types/functions: `__stack_chk_guard`, `stack_protector_debug`, `__stack_protector_apply_early()`, `__stack_protector_apply()`, and inline wrappers. Source-visible declarations include: #define _ASM_S390_ARCH_STACKPROTECTOR_H; extern unsigned long __stack_chk_guard;; extern int stack_protector_debug;; void __stack_protector_apply_early(unsigned long kernel_start);; int __stack_protector_apply(unsigned long *start, unsigned long *end, unsigned long kernel_start);; static inline void stack_protector_apply_early(unsigned long kernel_start); static inline int stack_protector_apply(unsigned long *start, unsigned long *end).

Control flow: Early setup applies the guard using the kernel start address; the later helper patches a supplied memory range with the runtime kernel base.

State and persistence behavior: The global canary and patched instruction/data references persist for the booted kernel.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates compiler stack protector output, early boot relocation, alternatives/text patching, and per-build security configuration..

Risks: Incorrect kernel-start offsets or range bounds can leave stale canaries or corrupt text/data during early boot.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 25 lines, 759 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch-stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch_hweight.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/arch_hweight.h

Purpose: Provides s390 accelerated Hamming-weight/popcount helpers.

Important APIs/types/functions: `arch_hweight8/16/32/64()` plus constant folding and runtime instruction paths. Source-visible declarations include: #define _ASM_S390_ARCH_HWEIGHT_H; static __always_inline unsigned long popcnt_z196(unsigned long w); unsigned long cnt;; static __always_inline unsigned long popcnt_z15(unsigned long w); unsigned long cnt;; static __always_inline unsigned long __arch_hweight64(__u64 w); static __always_inline unsigned int __arch_hweight32(unsigned int w); static __always_inline unsigned int __arch_hweight16(unsigned int w); static __always_inline unsigned int __arch_hweight8(unsigned int w).

Control flow: For compile-time constants the compiler can fold the result; otherwise inline assembly uses s390 population-count support when available by build target.

State and persistence behavior: No persistent state; helpers compute bit counts from input values.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <asm/march.h>. Integrated with Integrates with generic bitops, bitmap code, networking masks, sched masks, and CPU facility/build-level assumptions..

Risks: Instruction availability must match the selected march/facility support, and helper signatures must preserve generic hweight semantics.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 77 lines, 1695 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/archrandom.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/archrandom.h

Purpose: Declares s390 architecture random-number support using CPACF PRNO/TRNG capabilities.

Important APIs/types/functions: `s390_arch_random_available()`, `s390_arch_get_random_*()`, and `s390_arch_get_seed_*()` style hooks for random core integration. Source-visible declarations include: #define _ASM_S390_ARCHRANDOM_H; extern atomic64_t s390_arch_random_counter;; static inline size_t __must_check arch_get_random_longs(unsigned long *v, size_t max_longs); static inline size_t __must_check arch_get_random_seed_longs(unsigned long *v, size_t max_longs).

Control flow: The random core probes availability and uses CPACF-backed helpers to fill caller-provided words or seed buffers.

State and persistence behavior: State is CPACF hardware RNG/DRNG state and any implementation-side reseed state, not this header.

Dependencies and integration points: Direct includes are #include <linux/static_key.h>, #include <linux/preempt.h>, #include <linux/atomic.h>, #include <asm/cpacf.h>. Integrated with Integrates with `random.h`, CPACF PRNO/TRNG, CPU facility detection, and kernel entropy seeding..

Risks: Availability and blocking semantics must be conservative; exposing weak or unavailable hardware randomness would affect system entropy.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 38 lines, 947 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asce.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asce.h

Purpose: Defines address-space-control element flags and helpers for s390 dynamic address translation roots.

Important APIs/types/functions: `_ASCE_*` bit definitions and masks for region/table type, private-space, real-space, origin, and limit fields. Source-visible declarations include: #define _ASM_S390_ASCE_H; static inline bool enable_sacf_uaccess(void); unsigned long flags;; static inline void disable_sacf_uaccess(bool previous); unsigned long flags;.

Control flow: MM and low-level DAT code compose ASCE values and load them into control registers to select address translation roots.

State and persistence behavior: ASCE values persist in mm context, lowcore, and control-register state for active address spaces.

Dependencies and integration points: Direct includes are #include <linux/thread_info.h>, #include <linux/irqflags.h>, #include <asm/lowcore.h>, #include <asm/ctlreg.h>. Integrated with Integrates page table setup, KVM/SIE, lowcore, control-register management, and DAT bit definitions..

Risks: Bitfield mistakes are MMU-critical and can select the wrong table level, private-space mode, or address-space origin.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 36 lines, 754 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-const.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-const.h

Purpose: Provides assembly-friendly constant emission wrappers for s390 headers.

Important APIs/types/functions: `__ASM_CONST`, `_AC`, and related include support inherited from generic constant headers. Source-visible declarations include: #define _ASM_S390_ASM_CONST_H.

Control flow: Assembly and C preprocessing use these macros to form correctly typed constants in mixed C/asm headers.

State and persistence behavior: No runtime state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates with low-level assembly headers and generated offsets..

Risks: Changing constant typing can break assembly parsing or sign/width assumptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 12 lines, 377 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-extable.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-extable.h

Purpose: Defines s390 assembly exception-table entry encodings and helper macros.

Important APIs/types/functions: `EX_TYPE_*`, `EX_DATA_*` fields, `__EX_TABLE()`, `EX_TABLE()`, user-access fixup variants, zeropad, FPC, and MVCOS fixups. Source-visible declarations include: #define __ASM_EXTABLE_H; #define EX_TYPE_NONE 0; #define EX_TYPE_FIXUP 1; #define EX_TYPE_BPF 2; #define EX_TYPE_UA_FAULT 3; #define EX_TYPE_UA_LOAD_REG 5; #define EX_TYPE_UA_LOAD_REGPAIR 6; #define EX_TYPE_ZEROPAD 7; #define EX_TYPE_FPC 8; #define EX_TYPE_UA_MVCOS_TO 9.

Control flow: Assembly sites emit relative fault/target pairs plus encoded type and register metadata into exception table sections; fault handlers decode them to recover from expected traps.

State and persistence behavior: State is linker-collected exception-table metadata used at runtime for fault fixups.

Dependencies and integration points: Direct includes are #include <linux/stringify.h>, #include <linux/bits.h>, #include <asm/asm-const.h>. Integrated with Integrates user access, FPU control validation, BPF/extable handlers, AP/DIAG probing, and low-level assembly..

Risks: The encoded register fields must match handler decoding. Bad entries can recover to wrong PCs or corrupt registers after faults.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 95 lines, 3742 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-prototypes.h

Purpose: Collects C prototypes needed by assembly-generated calls and modversions.

Important APIs/types/functions: Includes `asm/ftrace.h`, `asm-generic/asm-prototypes.h`, and s390-specific exported assembly helper declarations where configured. Source-visible declarations include: no direct declarations beyond include guards or build directives.

Control flow: Build tooling includes this so assembly-visible symbols have prototypes for checksums and linkage.

State and persistence behavior: No runtime state.

Dependencies and integration points: Direct includes are #include <linux/kvm_host.h>, #include <linux/ftrace.h>, #include <asm/bug.h>, #include <asm/fpu.h>, #include <asm/nospec-branch.h>, #include <asm-generic/asm-prototypes.h>. Integrated with Integrates module versioning, assembly helper exports, ftrace, and generic asm prototype handling..

Risks: Missing prototypes can break modversion CRCs or hide calling convention mismatches.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 15 lines, 405 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm.h

Purpose: Provides common s390 inline-assembly helper macros.

Important APIs/types/functions: `__HAVE_ASM_FLAG_OUTPUTS__`, `CC_IPM`, `CC_OUT`, `CC_TRANSFORM`, `CC_CLOBBER`, and `CC_CLOBBER_LIST` variants. Source-visible declarations include: #define _ASM_S390_ASM_H; #define __HAVE_ASM_FLAG_OUTPUTS__ 1; #define CC_IPM(sym); #define CC_OUT(sym, var) "=@cc" (var); #define CC_TRANSFORM(cc) ({ cc; }); #define CC_CLOBBER; #define CC_CLOBBER_LIST(...) __VA_ARGS__; #define CC_IPM(sym) " ipm %[" __stringify(sym) "]\n"; #define CC_OUT(sym, var) [sym] "=d" (var); #define CC_TRANSFORM(cc) ({ (cc) >> 28; }).

Control flow: When compiler condition-code outputs are available, helpers bind directly to `=@cc`; otherwise they emit `ipm` and transform the upper condition-code bits.

State and persistence behavior: No state; it abstracts compiler and assembler capability differences.

Dependencies and integration points: Direct includes are #include <linux/stringify.h>. Integrated with Used by cmpxchg, CPACF, CPU-MF, and other instruction wrappers that need condition-code results..

Risks: Condition-code extraction must be consistent across compiler feature combinations or wrappers return wrong statuses.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 51 lines, 1890 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic.h

Purpose: Implements the s390 `atomic_t` and `atomic64_t` architecture API.

Important APIs/types/functions: `arch_atomic_*`, `arch_atomic64_*`, fetch/add/sub/test/bitwise operations, exchange, compare-exchange, and try-cmpxchg wrappers. Source-visible declarations include: #define __ARCH_S390_ATOMIC__; static __always_inline int arch_atomic_read(const atomic_t *v); #define arch_atomic_read arch_atomic_read; static __always_inline void arch_atomic_set(atomic_t *v, int i); #define arch_atomic_set arch_atomic_set; static __always_inline int arch_atomic_add_return(int i, atomic_t *v); #define arch_atomic_add_return arch_atomic_add_return; static __always_inline int arch_atomic_fetch_add(int i, atomic_t *v); #define arch_atomic_fetch_add arch_atomic_fetch_add; static __always_inline void arch_atomic_add(int i, atomic_t *v).

Control flow: Public atomic helpers delegate to `atomic_ops.h` load-and-op instructions or compare-and-swap loops and add barriers on return/fetch/test variants.

State and persistence behavior: State is caller-owned atomic counters; this header defines their concurrency semantics.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/types.h>, #include <asm/atomic_ops.h>, #include <asm/barrier.h>, #include <asm/cmpxchg.h>. Integrated with Integrates generic atomic API, locking, refcounts, scheduler, memory model barriers, and cmpxchg primitives..

Risks: Barrier choice and old/new return semantics are concurrency ABI; mismatches cause rare SMP bugs.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 230 lines, 6770 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic_ops.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic_ops.h

Purpose: Contains low-level s390 atomic instruction implementations.

Important APIs/types/functions: `__atomic_read/set`, 32/64-bit add/and/or/xor helpers, constant add helpers, and add-and-test variants. Source-visible declarations include: #define __ARCH_S390_ATOMIC_OPS__; static __always_inline int __atomic_read(const int *ptr); int val;; static __always_inline void __atomic_set(int *ptr, int val); static __always_inline long __atomic64_read(const long *ptr); long val;; static __always_inline void __atomic64_set(long *ptr, long val); #define __ATOMIC_OP(op_name, op_type, op_string, op_barrier) \; static __always_inline op_type op_name(op_type val, op_type *ptr) \; #define __ATOMIC_OPS(op_name, op_type, op_string) \.

Control flow: On z196-capable builds it uses load-and-op instructions; older builds use `cs`/`csg` retry loops. Optional flag-output paths derive zero/nonzero results directly from condition codes.

State and persistence behavior: No owned state; it mutates caller memory atomically.

Dependencies and integration points: Direct includes are #include <linux/limits.h>, #include <asm/march.h>, #include <asm/asm.h>. Integrated with Used by `atomic.h`, FPU state flags, refcount-like users, and low-level synchronization..

Risks: Instruction constraints, memory clobbers, and fallback loops must preserve atomicity across supported march levels.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 245 lines, 7302 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/atomic_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/barrier.h

Purpose: Defines s390 memory barriers, acquire/release helpers, and nospec masking.

Important APIs/types/functions: `bcr_serialize()`, `__mb`, `__dma_mb`, `__smp_*`, `__smp_store_release`, `__smp_load_acquire`, and `array_index_mask_nospec()`. Source-visible declarations include: #define __ASM_BARRIER_H; #define __ASM_BCR_SERIALIZE "bcr 14,0"; #define __ASM_BCR_SERIALIZE "bcr 15,0"; static __always_inline void bcr_serialize(void); #define __mb() bcr_serialize(); #define __rmb() barrier(); #define __wmb() barrier(); #define __dma_rmb() __mb(); #define __dma_wmb() __mb(); #define __smp_mb() __mb().

Control flow: Full barriers emit the serializing `bcr` sequence while read/write barriers rely on compiler barriers where the s390 memory model permits it; nospec masks protect array indices.

State and persistence behavior: No state; it enforces ordering around shared memory and MMIO/DMA.

Dependencies and integration points: Direct includes are #include <asm/march.h>, #include <asm-generic/barrier.h>. Integrated with Integrates the Linux memory model, atomics, DMA, user-copy/speculation mitigations, and lockless code..

Risks: Over-weak barriers break lockless algorithms and device ordering; over-strong barriers hurt performance but are safer.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 84 lines, 1976 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/bitops.h

Purpose: Implements s390 bit testing, inverted bit numbering helpers, and find/ffs primitives.

Important APIs/types/functions: `arch_test_bit()`, inverted bitmap helpers, `find_first_bit_inv()`, `find_next_bit_inv()`, `__flogr()`, `ffs()`, and generic non-atomic bitop mappings. Source-visible declarations include: #define _S390_BITOPS_H; #define arch___set_bit generic___set_bit; #define arch___clear_bit generic___clear_bit; #define arch___change_bit generic___change_bit; #define arch___test_and_set_bit generic___test_and_set_bit; #define arch___test_and_clear_bit generic___test_and_clear_bit; #define arch___test_and_change_bit generic___test_and_change_bit; #define arch_test_bit_acquire generic_test_bit_acquire; static __always_inline bool arch_test_bit(unsigned long nr, const volatile unsigned long *ptr); unsigned long mask;.

Control flow: Regular bitops mostly use generic helpers; inverted helpers translate bit numbers for s390/MSB-oriented hardware masks; `flogr`-based helpers find leading set bits.

State and persistence behavior: State is caller-owned bitmap memory.

Dependencies and integration points: Direct includes are #include <linux/typecheck.h>, #include <linux/compiler.h>, #include <linux/types.h>, #include <asm/asm.h>, #include <asm-generic/bitops/atomic.h>, #include <asm-generic/bitops/non-instrumented-non-atomic.h>, #include <asm-generic/bitops/lock.h>, #include <asm-generic/bitops/builtin-ffs.h>. Integrated with Integrates channel masks, facility masks, CPU masks, generic bitmap code, and architecture instruction helpers..

Risks: Inverted bit numbering is easy to misuse; mixing normal and inverted helpers corrupts hardware-visible masks.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 216 lines, 6073 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/boot_data.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/boot_data.h

Purpose: Declares early boot data buffers and boot debug filtering helpers.

Important APIs/types/functions: `early_command_line`, IPL block globals, secure IPL certificate/component list addresses, boot ring buffer state, `boot_rb_foreach()`, `bootdebug_filter_match()`, and `skip_timestamp()`. Source-visible declarations include: extern char early_command_line[COMMAND_LINE_SIZE];; extern struct ipl_parameter_block ipl_block;; extern int ipl_block_valid;; extern int ipl_secure_flag;; extern unsigned long ipl_cert_list_addr;; extern unsigned long ipl_cert_list_size;; extern unsigned long early_ipl_comp_list_addr;; extern unsigned long early_ipl_comp_list_size;; extern char boot_rb[PAGE_SIZE * 2];; extern bool boot_earlyprintk;.

Control flow: Early boot appends messages to a ring buffer, optional debug filters test message text after timestamps, and later code iterates buffered output.

State and persistence behavior: Persistent early state includes command line, IPL metadata, secure boot flags, certificate/component list addresses, and boot debug ring buffer content.

Dependencies and integration points: Direct includes are #include <linux/string.h>, #include <asm/setup.h>, #include <asm/ipl.h>. Integrated with Integrates IPL parsing, secure boot, early printk, boot debug, and s390 setup code..

Risks: Ring-buffer offsets and filter matching run early with limited facilities; bad bounds or stale IPL metadata can misreport boot security state.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 69 lines, 1662 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/boot_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/bug.h

Purpose: Defines s390 BUG/WARN trap emission and bug-table metadata.

Important APIs/types/functions: `BUG()`, `__WARN_FLAGS()`, verbose bug entries, monitor-call trap encodings, vararg warning helpers, and `__WARN_trap()` plumbing. Source-visible declarations include: #define _ASM_S390_BUG_H; #define MONCODE_BUG _AC(0, U); #define MONCODE_BUG_ARG _AC(1, U); #define __BUG_ENTRY_VERBOSE(format, file, line) \; #define __BUG_ENTRY_VERBOSE(format, file, line); #define WARN_CONDITION_STR(cond_str) cond_str; #define WARN_CONDITION_STR(cond_str) ""; #define __BUG_ENTRY(format, file, line, flags, size) \; #define __BUG_ASM(cond_str, flags) \; #define BUG() \.

Control flow: Macros emit bug table records and inline trap/monitor-call sequences; warning paths package format arguments for runtime decoding.

State and persistence behavior: State is linker-collected bug-table metadata and transient pt_regs/argument records during traps.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/const.h>, #include <asm-generic/bug.h>. Integrated with Integrates generic bug handling, traps, lockdep/warnings, module bug tables, and optional verbose file/line records..

Risks: Trap encodings and metadata sizes must match runtime bug decoding. Format-argument capture is ABI-sensitive for warning printing.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 129 lines, 3398 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cache.h

Purpose: Defines s390 cache-line constants and read-mostly placement.

Important APIs/types/functions: `L1_CACHE_BYTES`, `L1_CACHE_SHIFT`, `NET_SKB_PAD`, and `__read_mostly` section annotation. Source-visible declarations include: #define __ARCH_S390_CACHE_H; #define L1_CACHE_BYTES 256; #define L1_CACHE_SHIFT 8; #define NET_SKB_PAD 32; #define __read_mostly __section(".data..read_mostly").

Control flow: Generic code uses these constants for alignment, padding, and section placement.

State and persistence behavior: No runtime state beyond linker section placement of annotated objects.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates networking skb allocation, percpu/cache alignment, and linker script sections..

Risks: Changing line size or padding affects performance and potentially DMA/network headroom assumptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 19 lines, 389 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwdev.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwdev.h

Purpose: Declares the public CCW device and driver API for the s390 channel subsystem.

Important APIs/types/functions: `ccw_device_id`, `ccw_device`, `ccw_driver`, match helpers, online/offline/start/halt/clear/resume APIs, options flags, DMA helpers, console helpers, and path/query helpers. Source-visible declarations include: #define _S390_CCWDEV_H_; struct irb;; struct ccw1;; struct ccw_dev_id;; #define CCW_DEVICE(cu, cum) \; #define CCW_DEVICE_DEVTYPE(cu, cum, dev, devm) \; static inline const struct ccw_device_id *; struct ccw_device {; struct ccw_device_private *private; /* cio private information */; struct mutex reg_mutex;.

Control flow: Drivers register ID tables and callbacks, the CSS bus matches devices, and CCW/TM start helpers issue channel programs or transport-control words with interruption parameters and path masks.

State and persistence behavior: Persistent state is `ccw_device` private CSS state, locks, online flags, path state, DMA allocations, and driver registration.

Dependencies and integration points: Direct includes are #include <linux/device.h>, #include <linux/mod_devicetable.h>, #include <asm/chsc.h>, #include <asm/fcx.h>, #include <asm/irq.h>, #include <asm/schid.h>, #include <linux/mutex.h>. Integrated with Integrates channel subsystem core, device model, DASD/tape/net CCW drivers, console devices, DMA pools, FCX/TCW support, and CHSC path queries..

Risks: Path masks, interruption parameters, forced starts, and DMA ownership are hardware-facing; bad lifetimes can wedge subchannels or corrupt DMA.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 238 lines, 8532 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwgroup.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwgroup.h

Purpose: Declares grouped CCW device support for multi-subchannel logical devices.

Important APIs/types/functions: `ccwgroup_device`, `ccwgroup_driver`, device states, online/offline registration helpers, and root-device creation/removal APIs. Source-visible declarations include: #define S390_CCWGROUP_H; struct ccw_device;; struct ccw_driver;; struct ccwgroup_device {; enum {; struct mutex reg_mutex;; unsigned int count;; struct device dev;; struct work_struct ungroup_work;; struct ccw_device *cdev[];.

Control flow: A group driver binds several `ccw_device` instances into one device-model object, manages online/offline transitions, and routes callbacks through the group driver.

State and persistence behavior: State persists in group device membership arrays, driver data, online state, and device-model references.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates qeth and other grouped CCW drivers, driver core, sysfs, and CCW bus matching..

Risks: Reference management and partial online failures are risky because multiple subchannels must transition consistently.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 75 lines, 2300 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/checksum.h

Purpose: Implements s390 IP checksum helpers.

Important APIs/types/functions: `cksm()`, `csum_fold()`, `ip_fast_csum()`, `csum_tcpudp_nofold()`, `csum_tcpudp_magic()`, `ip_compute_csum()`, and IPv6 checksum hooks. Source-visible declarations include: #define _S390_CHECKSUM_H; static inline __wsum cksm(const void *buff, int len, __wsum sum); union register_pair rp = {; #define _HAVE_ARCH_CSUM_AND_COPY; static inline __sum16 csum_fold(__wsum sum); static inline __sum16 ip_fast_csum(const void *iph, unsigned int ihl); static inline __wsum csum_tcpudp_nofold(__be32 saddr, __be32 daddr, __u32 len,; static inline __sum16 csum_tcpudp_magic(__be32 saddr, __be32 daddr, __u32 len,; static inline __sum16 ip_compute_csum(const void *buff, int len); #define _HAVE_ARCH_IPV6_CSUM.

Control flow: Inline assembly and arithmetic helpers compute Internet checksums and pseudo-header checksums, folding carries to 16-bit sums.

State and persistence behavior: No persistent state; functions consume packet/header buffers.

Dependencies and integration points: Direct includes are #include <linux/instrumented.h>, #include <linux/kmsan-checks.h>, #include <linux/in6.h>. Integrated with Integrates IPv4/IPv6, TCP/UDP, skb checksum offload fallback, and generic checksum API..

Risks: Endianness, odd lengths, carry folding, and copy-and-checksum semantics are packet-corruption sensitive.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 128 lines, 3250 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chpid.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/chpid.h

Purpose: Defines channel-path ID descriptors and iteration helpers.

Important APIs/types/functions: `channel_path_desc_fmt0`, `chp_id_init()`, equality, increment, validity, and `chp_id_for_each()`. Source-visible declarations include: #define _ASM_S390_CHPID_H; struct channel_path_desc_fmt0 {; static inline void chp_id_init(struct chp_id *chpid); static inline int chp_id_is_equal(struct chp_id *a, struct chp_id *b); static inline void chp_id_next(struct chp_id *chpid); static inline int chp_id_is_valid(struct chp_id *chpid); #define chp_id_for_each(c) \.

Control flow: Helpers walk CSSID/ID combinations and compare or validate channel path identifiers.

State and persistence behavior: State is caller-owned channel-path ID values and hardware-provided descriptors.

Dependencies and integration points: Direct includes are #include <uapi/asm/chpid.h>, #include <asm/cio.h>. Integrated with Integrates CHSC, CSS path management, sysfs, and CCW path lookup..

Risks: Iteration bounds must match channel subsystem limits or path discovery misses valid paths.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 51 lines, 979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chpid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chsc.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/chsc.h

Purpose: Declares CHSC notification and network-address-information structures.

Important APIs/types/functions: PNSO operation codes, packed NAI/resume-token/area structures, notify types, and CHSC notifier registration. Source-visible declarations include: #define _ASM_S390_CHSC_H; struct notifier_block;; #define PNSO_OC_NET_BRIDGE_INFO 0; #define PNSO_OC_NET_ADDR_INFO 3; struct chsc_pnso_naid_l2 {; u64 nit;; struct { u8 mac[6]; u16 lnid; } addr_lnid;; struct chsc_pnso_resume_token {; u64 t1;; u64 t2;.

Control flow: Channel subsystem code fills request areas, receives CHSC response records, and notifies registered listeners on CSS or channel-path changes.

State and persistence behavior: State is hardware CHSC response data and notifier-chain registrations.

Dependencies and integration points: Direct includes are #include <uapi/asm/chsc.h>. Integrated with Integrates CCW device path information, network bridge/address queries, notifier blocks, and CSS reconfiguration..

Risks: Packed layouts and resume tokens are firmware ABI; incorrect parsing can lose path/network topology updates.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 84 lines, 1744 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/chsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cio.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cio.h

Purpose: Defines core channel I/O command, status, interruption, and DMA interfaces.

Important APIs/types/functions: `ccw0`, `ccw1`, ERW/ESW/IRB structures, CIW/node descriptors, `ccw_dev_id`, path helpers, CIO status flags, DMA allocator APIs, and CHSC helper declarations. Source-visible declarations include: #define _ASM_S390_CIO_H_; #define LPM_ANYPATH 0xff; #define __MAX_CSSID 0; #define __MAX_SUBCHANNEL 65535; #define __MAX_SSID 3; #define CCW_MAX_BYTE_COUNT 65535; struct ccw1 {; struct ccw0 {; #define CCW_FLAG_DC 0x80; #define CCW_FLAG_CC 0x40.

Control flow: CCW drivers construct channel command words and the CSS returns interruption response blocks with status and extended-status words; helpers allocate DMA-safe memory and schedule reprobes.

State and persistence behavior: Persistent state includes channel program buffers, subchannel/device IDs, DMA pools, path masks, and hardware status captured in IRBs.

Dependencies and integration points: Direct includes are #include <linux/bitops.h>, #include <linux/genalloc.h>, #include <asm/dma-types.h>, #include <asm/types.h>, #include <asm/tpi.h>, #include <asm/scsw.h>. Integrated with Integrates CCW bus, CSS, CHSC, FCX, EADM, DASD/tape/net drivers, and device DMA handling..

Risks: All packed status layouts are hardware ABI. Incorrect byte counts, flags, or path masks can hang I/O or mis-handle device errors.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 383 lines, 9263 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/clocksource.h

Purpose: Provides the s390 architecture clocksource include point.

Important APIs/types/functions: Include guard only in this snapshot, relying on implementation elsewhere. Source-visible declarations include: #define _ASM_S390_CLOCKSOURCE_H.

Control flow: Generic clocksource code can include it for architecture-specific hooks without adding declarations here.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates timekeeping and s390 clocksource implementation files..

Risks: Minimal wrapper; adding declarations must stay compatible with generic clocksource expectations.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 7 lines, 184 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clp.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/clp.h

Purpose: Defines command-list processor request/response headers and selected command structures.

Important APIs/types/functions: `CLP_BLK_SIZE`, command codes, `clp_req_hdr`, `clp_rsp_hdr`, return codes, and SLPC request/response blocks. Source-visible declarations include: #define _ASM_S390_CLP_H; #define CLP_BLK_SIZE PAGE_SIZE; #define CLP_SLPC 0x0001; #define CLP_LPS_BASE 0; #define CLP_LPS_PCI 2; struct clp_req_hdr {; u64 reserved2;; struct clp_rsp_hdr {; u64 reserved2;; #define CLP_RC_OK 0x0010 /* Command request successfully */.

Control flow: Callers build a page-sized CLP block with request headers, issue CLP firmware commands, and parse response headers/status codes.

State and persistence behavior: State is firmware command/response memory supplied by callers.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates s390 firmware/platform discovery, PCI logical partition services, and channel subsystem setup..

Risks: Return codes are firmware-specific and structures must remain packed/aligned to CLP block rules.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 59 lines, 1426 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/clp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmb.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cmb.h

Purpose: Declares channel-measurement facility operations for CCW devices.

Important APIs/types/functions: `enable_cmf()`, `disable_cmf()`, `__disable_cmf()`, `cmf_read()`, and `cmf_readall()`. Source-visible declarations include: #define S390_CMB_H; struct ccw_device;; extern int enable_cmf(struct ccw_device *cdev);; extern int disable_cmf(struct ccw_device *cdev);; extern int __disable_cmf(struct ccw_device *cdev);; extern u64 cmf_read(struct ccw_device *cdev, int index);; extern int cmf_readall(struct ccw_device *cdev, struct cmbdata *data);.

Control flow: Drivers enable measurement collection for a CCW device, read individual counters or full `cmbdata`, and disable collection on teardown.

State and persistence behavior: Persistent state lives in channel measurement blocks and CCW device measurement configuration.

Dependencies and integration points: Direct includes are #include <uapi/asm/cmb.h>. Integrated with Integrates CCW devices, performance accounting, and channel subsystem measurement support..

Risks: Measurement enable/disable must be synchronized with device lifetime to avoid reading freed or stale CMB data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 14 lines, 425 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cmpxchg.h

Purpose: Implements s390 compare-exchange, exchange, try-cmpxchg, and 128-bit cmpxchg primitives.

Important APIs/types/functions: `arch_cmpxchg()`, `arch_try_cmpxchg()`, `arch_xchg()`, byte/halfword emulation using containing-word CAS, and `arch_cmpxchg128()`/`arch_try_cmpxchg128()`. Source-visible declarations include: #define __ASM_CMPXCHG_H; void __cmpxchg_called_with_bad_pointer(void);; static __always_inline u32 __cs_asm(u64 ptr, u32 old, u32 new); static __always_inline u64 __csg_asm(u64 ptr, u64 old, u64 new); static inline u8 __arch_cmpxchg1(u64 ptr, u8 old, u8 new); union {; int i;; static inline u16 __arch_cmpxchg2(u64 ptr, u16 old, u16 new); union {; int i;.

Control flow: 1/2-byte operations align to containing words and retry with shifted masks; 4/8-byte operations use `cs`/`csg`; 16-byte operations use `cdsg` on aligned `u128` data.

State and persistence behavior: State is caller-owned memory modified atomically.

Dependencies and integration points: Direct includes are #include <linux/mmdebug.h>, #include <linux/types.h>, #include <linux/bug.h>, #include <asm/asm.h>. Integrated with Integrates atomics, locking, qspinlocks, refcounts, lockless data structures, and generic cmpxchg API..

Risks: Alignment, endian shifts, and retry updates to `oldp` are subtle; wrong handling breaks lockless algorithms.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 273 lines, 6171 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpacf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpacf.h

Purpose: Defines CP Assist for Cryptographic Functions opcodes, function codes, query helpers, and inline instruction wrappers.

Important APIs/types/functions: `cpacf_mask_t`, `cpacf_qai_t`, `cpacf_query()`, `cpacf_query_func()`, `cpacf_qai()`, and wrappers for KM/KMC/KIMD/KLMD/KMAC/KMCTR/PRNO/TRNG/PCC/PCKMO/KMA. Source-visible declarations include: #define _ASM_S390_CPACF_H; #define CPACF_KMAC 0xb91e /* MSA */; #define CPACF_KM 0xb92e /* MSA */; #define CPACF_KMC 0xb92f /* MSA */; #define CPACF_KIMD 0xb93e /* MSA */; #define CPACF_KLMD 0xb93f /* MSA */; #define CPACF_PCKMO 0xb928 /* MSA3 */; #define CPACF_KMF 0xb92a /* MSA4 */; #define CPACF_KMO 0xb92b /* MSA4 */; #define CPACF_PCC 0xb92c /* MSA4 */.

Control flow: Query helpers validate the opcode against facility bits, execute the query subfunction, and test function-code masks. Operation wrappers load fixed GR pairs, issue CPACF instructions, and loop on partial completion condition codes.

State and persistence behavior: State is CPACF hardware state, parameter blocks, source/destination buffers, and crypto context data supplied by callers.

Dependencies and integration points: Direct includes are #include <asm/facility.h>, #include <linux/kmsan-checks.h>. Integrated with Integrates kernel crypto drivers, protected-key support, random/entropy code, facility probing, KMSAN annotations, and condition-code helper macros..

Risks: Opcode/function availability must be checked before use. Partial-completion loops, parameter-block layouts, and KMSAN unpoisoning for TRNG are correctness and security critical.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 736 lines, 22050 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpacf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpcmd.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpcmd.h

Purpose: Declares helpers for issuing z/VM CP commands.

Important APIs/types/functions: `__cpcmd()` low-level command execution and `cpcmd()` wrapper with response buffer and response-code pointer. Source-visible declarations include: #define _ASM_S390_CPCMD_H; int __cpcmd(const char *cmd, char *response, int rlen, int *response_code);; int cpcmd(const char *cmd, char *response, int rlen, int *response_code);.

Control flow: Callers pass a CP command string and optional response buffer; implementation issues the hypervisor command and returns CP response status.

State and persistence behavior: State is z/VM control program state and caller response buffers.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates VM-only management paths, hypfs, diagnostics, and s390 virtualization support..

Risks: Command strings are privileged hypervisor interface inputs; response buffer lengths and non-VM behavior must be handled carefully.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 32 lines, 1135 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu.h

Purpose: Declares s390 CPU identification data and static CPU feature keys.

Important APIs/types/functions: `struct cpuid` and `DECLARE_STATIC_KEY_FALSE(cpu_has_bear)`. Source-visible declarations include: #define _ASM_S390_CPU_H; struct cpuid; unsigned int version : 8;; unsigned int ident : 24;; unsigned int machine : 16;; unsigned int unused : 16;.

Control flow: CPU detection fills CPUID/facility data and static keys allow hot paths to branch on CPU features.

State and persistence behavior: Persistent state is CPU identity and static-key patching state.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/jump_label.h>. Integrated with Integrates CPU setup, facility detection, alternatives/static branches, and feature users such as BEAR support..

Risks: Static-key default and feature discovery must align or hot paths execute unsupported instructions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 28 lines, 622 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf-insn.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf-insn.h

Purpose: Provides assembler include guards for CPU Measurement Facility instruction support.

Important APIs/types/functions: This snapshot only exposes the guarded include point for instruction-level definitions used elsewhere. Source-visible declarations include: #define _ASM_S390_CPU_MF_INSN_H.

Control flow: Assembly sources include it to share CPU-MF instruction naming and build context.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates CPU-MF assembly implementations and perf support..

Risks: Minimal wrapper; future instruction macros must match hardware encodings.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 22 lines, 480 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf.h

Purpose: Defines s390 CPU Measurement Facility counter and sampling structures plus instruction wrappers.

Important APIs/types/functions: Interrupt masks, `cpumf_ctr_info`, sampling info/request/entry/trailer structures, `cpum_cf_avail()`, `cpum_sf_avail()`, `qctri()`, `lcctl()`, `ecctr()`, `stcctm()`, `qsi()`, and `lsctl()`. Source-visible declarations include: #define _ASM_S390_CPU_MF_H; #define CPU_MF_INT_SF_IAE (1 << 31) /* invalid entry address */; #define CPU_MF_INT_SF_ISE (1 << 30) /* incorrect SDBT entry */; #define CPU_MF_INT_SF_PRA (1 << 29) /* program request alert */; #define CPU_MF_INT_SF_SACA (1 << 23) /* sampler auth. change alert */; #define CPU_MF_INT_SF_LSDA (1 << 22) /* loss of sample data alert */; #define CPU_MF_INT_CF_MTDA (1 << 15) /* loss of MT ctr. data alert */; #define CPU_MF_INT_CF_CACA (1 << 7) /* counter auth. change alert */; #define CPU_MF_INT_CF_LCDA (1 << 6) /* loss of counter data alert */; #define CPU_MF_INT_CF_MASK (CPU_MF_INT_CF_MTDA|CPU_MF_INT_CF_CACA| \.

Control flow: Availability helpers test facilities, instruction wrappers execute CPU-MF operations and return condition-code status, and perf sampling code consumes packed hardware entry formats.

State and persistence behavior: Persistent state is CPU-MF control registers, counter sets, sampling buffers, and trailer metadata.

Dependencies and integration points: Direct includes are #include <linux/errno.h>, #include <linux/kmsan-checks.h>, #include <asm/asm-extable.h>, #include <asm/facility.h>, #include <asm/asm.h>. Integrated with Integrates perf events, hardware sampling, PMU interrupts, facility bits, and low-level condition-code handling..

Risks: Packed layouts and condition-code meanings are hardware ABI. Sampling loss/alert bits require careful interpretation to avoid misleading perf data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 286 lines, 8717 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpufeature.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpufeature.h

Purpose: Declares s390 CPU feature IDs and facility-backed convenience predicates.

Important APIs/types/functions: `enum` feature IDs, `cpu_feature()`, `cpu_have_feature()`, and helpers such as `cpu_has_vx()`, `cpu_has_nx()`, `cpu_has_gs()`, `cpu_has_edat*()`, and `cpu_has_topology()`. Source-visible declarations include: #define __ASM_S390_CPUFEATURE_H; enum {; #define cpu_feature(feature) (feature); int cpu_have_feature(unsigned int nr);; #define cpu_has_bear() test_facility(193); #define cpu_has_edat1() test_facility(8); #define cpu_has_edat2() test_facility(78); #define cpu_has_gs() test_facility(133); #define cpu_has_nx() test_facility(130); #define cpu_has_rdp() test_facility(194).

Control flow: Feature users query indexed software features or direct facility bits to select instructions and code paths.

State and persistence behavior: Persistent state is CPU feature/facility discovery data initialized at boot.

Dependencies and integration points: Direct includes are #include <asm/facility.h>. Integrated with Integrates cpufeature core, alternatives, crypto, MM, vector/FPU, and topology code..

Risks: Feature IDs and facility numbers must remain stable; false positives lead to illegal instructions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 37 lines, 942 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cputime.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cputime.h

Purpose: Maps s390 CPU time accounting to TOD-clock nanoseconds and declares idle IRQ accounting.

Important APIs/types/functions: `cputime_to_nsecs()` and `account_idle_time_irq()`. Source-visible declarations include: #define _S390_CPUTIME_H; #define cputime_to_nsecs(cputime) tod_to_ns(cputime); void account_idle_time_irq(void);.

Control flow: Generic scheduler accounting converts hardware cputime through `tod_to_ns()` and calls the IRQ idle accounting hook.

State and persistence behavior: State is scheduler/accounting counters maintained elsewhere.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <asm/timex.h>. Integrated with Integrates TOD clock helpers, scheduler CPU accounting, and interrupt entry paths..

Risks: Time conversion errors affect accounting, profiling, and cgroup CPU usage.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 21 lines, 393 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cputime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/crw.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/crw.h

Purpose: Defines channel-report-word structures and handler registration.

Important APIs/types/functions: `struct crw`, `crw_handler_t`, `crw_register_handler()`, `crw_unregister_handler()`, `crw_handle_channel_report()`, resource codes, and event reporting codes. Source-visible declarations include: #define _ASM_S390_CRW_H; struct crw {; typedef void (*crw_handler_t)(struct crw *, struct crw *, int);; extern int crw_register_handler(int rsc, crw_handler_t handler);; extern void crw_unregister_handler(int rsc);; extern void crw_handle_channel_report(void);; void crw_wait_for_channel_report(void);; #define NR_RSCS 16; #define CRW_RSC_MONITOR 0x2 /* monitoring facility */; #define CRW_RSC_SCH 0x3 /* subchannel */.

Control flow: Machine-check/channel-report handling decodes one or two CRWs and dispatches to resource-specific registered handlers.

State and persistence behavior: Persistent state is the handler table and pending hardware report state.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with Integrates CSS, channel path, subchannel, monitoring, and configuration-alert handling..

Risks: Handlers must tolerate chained reports and asynchronous hardware change; wrong resource codes can miss reconfiguration events.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 55 lines, 1858 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/crw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/css_chars.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/css_chars.h

Purpose: Defines channel-subsystem characteristics returned by STSCH/CHSC discovery.

Important APIs/types/functions: `struct css_general_char` and `struct css_chsc_char` style bitfields for CSS feature availability. Source-visible declarations include: #define _ASM_CSS_CHARS_H; struct css_general_char {; u64 : 12;; u64 dynio : 1; /* bit 12 */; u64 : 4;; u64 eadm : 1; /* bit 17 */; u64 : 23;; u64 aif : 1; /* bit 41 */; u64 : 3;; u64 mcss : 1; /* bit 45 */.

Control flow: Discovery code stores hardware characteristic blocks and drivers test feature bits to select optional channel functions.

State and persistence behavior: Persistent state is probed CSS feature data.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with Integrates channel subsystem initialization, CHSC, path management, and I/O feature gating..

Risks: Bit numbering and packed layout must match the architecture or features will be incorrectly enabled.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 47 lines, 904 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/css_chars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ctlreg.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ctlreg.h

Purpose: Provides typed helpers for reading, writing, setting, and clearing s390 control registers.

Important APIs/types/functions: `__ctl_load()`, `__ctl_store()`, `local_ctl_*`, `system_ctl_*`, and bit operation wrappers around control register fields. Source-visible declarations include: #define __ASM_S390_CTLREG_H; #define CR0_TRANSACTIONAL_EXECUTION_BIT (63 - 8); #define CR0_CLOCK_COMPARATOR_SIGN_BIT (63 - 10); #define CR0_CRYPTOGRAPHY_COUNTER_BIT (63 - 13); #define CR0_PAI_EXTENSION_BIT (63 - 14); #define CR0_CPUMF_EXTRACTION_AUTH_BIT (63 - 15); #define CR0_WARNING_TRACK_BIT (63 - 30); #define CR0_LOW_ADDRESS_PROTECTION_BIT (63 - 35); #define CR0_FETCH_PROTECTION_OVERRIDE_BIT (63 - 38); #define CR0_STORAGE_PROTECTION_OVERRIDE_BIT (63 - 39).

Control flow: Inline assembly stores or loads control registers, while system-wide helpers coordinate updates across CPUs where implemented.

State and persistence behavior: State is CPU control-register contents and any global synchronization around system updates.

Dependencies and integration points: Direct includes are #include <linux/bits.h>, #include <linux/bug.h>. Integrated with Integrates MMU/DAT, interrupt subclasses, lowcore, SMP, and feature control paths..

Risks: Control-register changes are privileged and CPU-local unless explicitly broadcast; incorrect masks can break address translation or interrupt delivery.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 256 lines, 8004 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ctlreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/current.h

Purpose: Defines how s390 obtains the current task pointer.

Important APIs/types/functions: `get_current()` and `current` macro using lowcore/predefined register state. Source-visible declarations include: #define _S390_CURRENT_H; struct task_struct;; static __always_inline struct task_struct *get_current(void); unsigned long ptr, lc_current;; #define current get_current().

Control flow: Hot paths read the current task from s390 lowcore or register-backed storage.

State and persistence behavior: State is per-CPU current task pointer maintained by context switch.

Dependencies and integration points: Direct includes are #include <asm/lowcore.h>, #include <asm/machine.h>. Integrated with Integrates scheduler, lowcore layout, thread_info, and all generic code using `current`..

Risks: The access sequence must match lowcore offsets and context-switch updates or every task-local access is unsafe.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 35 lines, 821 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dat-bits.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dat-bits.h

Purpose: Defines s390 Dynamic Address Translation bitfield layouts for virtual addresses, ASCEs, region/segment tables, and PTEs.

Important APIs/types/functions: `union vaddress`, `union asce`, region table entry unions, segment table entry unions, `union page_table_entry`, and DAT bit enumerations. Source-visible declarations include: #define _S390_DAT_BITS_H; union vaddress {; unsigned long addr;; struct {; unsigned long rfx : 11;; unsigned long rsx : 11;; unsigned long rtx : 11;; unsigned long sx : 11;; unsigned long px : 8;; unsigned long bx : 12;.

Control flow: MM code composes table entries and ASCEs using these packed bitfields and hardware page-table walkers interpret the resulting words.

State and persistence behavior: Persistent state is page-table memory, mm context ASCEs, and hardware translation state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates low-level MM, KVM, page table allocation, fault handling, and control-register loading..

Risks: Every bit position is hardware ABI; C bitfield endianness/packing assumptions must remain valid for s390.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 198 lines, 5691 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dat-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/debug.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/debug.h

Purpose: Declares the s390 debug feature (`s390dbf`) ring-buffer API and early static debug support.

Important APIs/types/functions: `debug_info_t`, `debug_entry_t`, `debug_view`, register/unregister/view APIs, event/exception helpers, sprintf helpers, dump, level control, and `DEFINE_STATIC_DEBUG_INFO()`. Source-visible declarations include: #define _ASM_S390_DEBUG_H; #define DEBUG_MAX_LEVEL 6 /* debug levels range from 0 to 6 */; #define DEBUG_OFF_LEVEL -1 /* level where debug is switched off */; #define DEBUG_FLUSH_ALL -1 /* parameter to flush all areas */; #define DEBUG_MAX_VIEWS 10 /* max number of views in proc fs */; #define DEBUG_MAX_NAME_LEN 64 /* max length for a debugfs file name */; #define DEBUG_DEFAULT_LEVEL 3 /* initial debug level */; #define DEBUG_DIR_ROOT "s390dbf" /* name of debug root directory in proc fs */; #define DEBUG_DATA(entry) (char *)(entry + 1) /* data is stored behind */; #define __DEBUG_FEATURE_VERSION 3 /* version of debug feature */.

Control flow: Callers register debug areas and views, log level-filtered events into active ring areas, optionally switch areas on exceptions, and expose formatted output through debugfs/proc-style views.

State and persistence behavior: Persistent state includes per-debug-area ring pages, active page/entry indices, views, dentry handles, locks, levels, and early static buffers later replaced during init.

Dependencies and integration points: Direct includes are #include <linux/string.h>, #include <linux/spinlock.h>, #include <linux/kernel.h>, #include <linux/time.h>, #include <linux/refcount.h>, #include <linux/fs.h>, #include <linux/init.h>. Integrated with Integrates many s390 drivers, debugfs, early boot tracing, panic/critical paths, and documentation-defined formatting views..

Risks: `%s` sprintf entries store pointers rather than copying strings; lifetimes matter. Ring sizing, refcounts, and static registration must avoid use-after-free and lost diagnostic data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 499 lines, 14707 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/delay.h

Purpose: Declares s390 busy-wait delay helpers.

Important APIs/types/functions: `__ndelay()`, `__udelay()`, `__delay()`, and `ndelay/udelay/mdelay` macros. Source-visible declarations include: #define _S390_DELAY_H; void __ndelay(unsigned long nsecs);; void __udelay(unsigned long usecs);; void __delay(unsigned long loops);; #define ndelay(n) __ndelay((unsigned long)(n)); #define udelay(n) __udelay((unsigned long)(n)); #define mdelay(n) __udelay((unsigned long)(n) * 1000).

Control flow: Callers request nanosecond/microsecond/millisecond busy waits that implementation calibrates against s390 timers.

State and persistence behavior: No state in this header; calibration state lives in implementation/time code.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates driver polling, early boot waits, and generic delay API..

Risks: Busy waits are timing-sensitive and can overflow if macro arguments are too large.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 24 lines, 647 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/diag.h

Purpose: Defines s390 DIAGNOSE instruction numbers, statistics IDs, and inline DIAG helpers.

Important APIs/types/functions: `enum diag_stat_enum`, `diag_stat_inc()`, and helper wrappers for selected DIAG calls such as time, VM, and hypervisor interactions. Source-visible declarations include: #define _ASM_S390_DIAG_H; enum diag_stat_enum {; void diag_stat_inc(enum diag_stat_enum nr);; void diag_stat_inc_norecursion(enum diag_stat_enum nr);; struct hypfs_diag0c_entry;; void diag0c(struct hypfs_diag0c_entry *data);; static inline void diag10_range(unsigned long start_pfn, unsigned long num_pfn); unsigned long start_addr, end_addr;; extern int diag14(unsigned long rx, unsigned long ry1, unsigned long subcode);; struct diag210 {.

Control flow: Call sites increment per-DIAG statistics and issue `diag` instructions with fixed register conventions, often only under VM/LPAR feature checks.

State and persistence behavior: State is hypervisor/firmware state plus diagnostic statistics counters.

Dependencies and integration points: Direct includes are #include <linux/if_ether.h>, #include <linux/percpu.h>, #include <asm/asm-extable.h>, #include <asm/sclp.h>, #include <asm/cio.h>. Integrated with Integrates hypfs, appldata, watchdog, cpcmd, VM detection, and low-level virtualization services..

Risks: DIAG availability is environment-specific. Incorrect register setup or calling outside supported hypervisors can trap or return misleading data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 377 lines, 7913 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag288.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/diag288.h

Purpose: Provides inline support for DIAG 288 watchdog control.

Important APIs/types/functions: Watchdog intervals, function codes, restart action constants, and `__diag288()`. Source-visible declarations include: #define _ASM_S390_DIAG288_H; #define MIN_INTERVAL 15 /* Minimal time supported by diag288 */; #define MAX_INTERVAL 3600 /* One hour should be enough - pure estimation */; #define WDT_DEFAULT_TIMEOUT 30; #define WDT_FUNC_INIT 0; #define WDT_FUNC_CHANGE 1; #define WDT_FUNC_CANCEL 2; #define WDT_FUNC_CONCEAL 0x80000000; #define LPARWDT_RESTART 0; static inline int __diag288(unsigned int func, unsigned int timeout,.

Control flow: `__diag288()` passes function, timeout, action, and command length/address operands to the DIAG 288 instruction and returns the condition/result code.

State and persistence behavior: State is hypervisor watchdog configuration and caller command buffers.

Dependencies and integration points: Direct includes are #include <asm/asm-extable.h>, #include <asm/types.h>. Integrated with Integrates s390 watchdog drivers, LPAR/z/VM firmware, and reboot/restart policy..

Risks: Timeout bounds must follow DIAG support; wrong conceal/cancel/change function use can leave watchdogs armed unexpectedly.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 41 lines, 1031 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag288.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dis.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dis.h

Purpose: Declares s390 instruction-disassembly helpers.

Important APIs/types/functions: `insn_length()`, `show_code()`, `print_fn_code()`, `find_insn()`, and `is_known_insn()`. Source-visible declarations include: #define __ASM_S390_DIS_H__; static inline int insn_length(unsigned char code); struct pt_regs;; void show_code(struct pt_regs *regs);; void print_fn_code(unsigned char *code, unsigned long len);; struct s390_insn *find_insn(unsigned char *code);; static inline int is_known_insn(unsigned char *code).

Control flow: `insn_length()` derives length from the first opcode bits; other helpers decode and print code around registers or functions.

State and persistence behavior: No persistent state; decoding consumes text bytes.

Dependencies and integration points: Direct includes are #include <asm/dis-defs.h>. Integrated with Integrates oops reporting, kprobes/ftrace validation, instruction patching, and debug output..

Risks: Instruction length decoding must match z/Architecture formats or diagnostics and patch validators misparse text.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 30 lines, 636 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma-types.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dma-types.h

Purpose: Defines type-safe s390 32-bit and 64-bit DMA address wrappers.

Important APIs/types/functions: `dma32_t`, `dma64_t`, conversion helpers to/from virtual addresses and integers, and add/and helpers. Source-visible declarations include: #define _ASM_S390_DMA_TYPES_H_; typedef u32 __bitwise dma32_t;; typedef u64 __bitwise dma64_t;; static inline dma32_t virt_to_dma32(void *ptr); static inline void *dma32_to_virt(dma32_t addr); static inline dma32_t u32_to_dma32(u32 addr); static inline u32 dma32_to_u32(dma32_t addr); static inline dma32_t dma32_add(dma32_t a, u32 b); static inline dma32_t dma32_and(dma32_t a, u32 b); static inline dma64_t virt_to_dma64(void *ptr).

Control flow: Inline helpers cast physical/virtual addresses into bitwise-distinct DMA types so sparse can catch accidental mixing.

State and persistence behavior: No state; values represent DMA-visible addresses.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/io.h>. Integrated with Integrates CIO/CCW/EADM DMA pools, device drivers, and sparse checking..

Risks: Truncation in 32-bit DMA helpers or bypassing bitwise types can corrupt device address programming.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 103 lines, 2563 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dma.h

Purpose: Provides minimal s390 DMA address constants.

Important APIs/types/functions: `MAX_DMA_ADDRESS` as the 2 GiB virtual boundary. Source-visible declarations include: #define _ASM_S390_DMA_H; #define MAX_DMA_ADDRESS __va(0x80000000).

Control flow: Generic DMA code includes the architecture limit for low DMA allocations.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are #include <linux/io.h>. Integrated with Integrates DMA mapping and legacy low-memory allocation assumptions..

Risks: The boundary must match devices or subsystems requiring below-2G DMA memory.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 14 lines, 359 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dwarf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dwarf.h

Purpose: Defines assembler CFI macro aliases for s390 assembly.

Important APIs/types/functions: `CFI_STARTPROC`, `CFI_ENDPROC`, `CFI_DEF_CFA_OFFSET`, `CFI_ADJUST_CFA_OFFSET`, `CFI_RESTORE`, `CFI_REL_OFFSET`, and conditional `CFI_VAL_OFFSET`. Source-visible declarations include: #define _ASM_S390_DWARF_H; #define CFI_STARTPROC .cfi_startproc; #define CFI_ENDPROC .cfi_endproc; #define CFI_DEF_CFA_OFFSET .cfi_def_cfa_offset; #define CFI_ADJUST_CFA_OFFSET .cfi_adjust_cfa_offset; #define CFI_RESTORE .cfi_restore; #define CFI_REL_OFFSET .cfi_rel_offset; #define CFI_VAL_OFFSET .cfi_val_offset; #define CFI_VAL_OFFSET #.

Control flow: Assembly files use these aliases to emit DWARF call-frame information, with optional macros becoming no-ops when unsupported.

State and persistence behavior: State is debug/unwind metadata emitted into object files.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates unwinder, objtool-like validation, crash dumps, and assembly entry code..

Risks: Wrong CFI causes unreliable stack traces and exception unwinding.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 38 lines, 954 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dwarf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/eadm.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/eadm.h

Purpose: Defines Extended Asynchronous Data Mover structures and SCM device driver hooks.

Important APIs/types/functions: `arqb`, `arsb`, `msb`, `aidaw`, `aob`, `scm_device`, `scm_driver`, `scm_driver_register()`, `eadm_start_aob()`, and `scm_irq_handler()`. Source-visible declarations include: #define _ASM_S390_EADM_H; struct arqb {; u64 data;; #define ARQB_CMD_MOVE 1; struct arsb {; u64 fail_msb;; u64 fail_aidaw;; u64 fail_ms;; u64 fail_scm;; #define EQC_WR_PROHIBIT 22.

Control flow: SCM drivers build asynchronous operation blocks with move specification blocks and AIDAWs, submit them through EADM, and receive completion/error callbacks from IRQ handling.

State and persistence behavior: Persistent state includes SCM device objects, operation blocks, block queues, request references, and hardware operation state.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/device.h>, #include <linux/blk_types.h>, #include <asm/dma-types.h>. Integrated with Integrates storage class memory drivers, block layer completions, CIO interrupt handling, and DMA address wrappers..

Risks: Packed operation blocks and request lifetimes are hardware-facing; bad block counts or completion handling can corrupt SCM I/O.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 121 lines, 2116 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/eadm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ebcdic.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ebcdic.h

Purpose: Declares EBCDIC/ASCII conversion tables and inline conversion helpers.

Important APIs/types/functions: `_ascebc*`, `_ebcasc*`, `_ebc_tolower`, `_ebc_toupper`, `codepage_convert()`, and `ASCEBC/EBCASC` macros. Source-visible declarations include: #define _EBCDIC_H; extern __u8 _ascebc_500[256]; /* ASCII -> EBCDIC 500 conversion table */; extern __u8 _ebcasc_500[256]; /* EBCDIC 500 -> ASCII conversion table */; extern __u8 _ascebc[256]; /* ASCII -> EBCDIC conversion table */; extern __u8 _ebcasc[256]; /* EBCDIC -> ASCII conversion table */; extern __u8 _ebc_tolower[256]; /* EBCDIC -> lowercase */; extern __u8 _ebc_toupper[256]; /* EBCDIC -> uppercase */; static inline void; #define ASCEBC(addr,nr) codepage_convert(_ascebc, addr, nr); #define EBCASC(addr,nr) codepage_convert(_ebcasc, addr, nr).

Control flow: Conversion helpers walk a byte buffer in place and translate each byte through the selected 256-entry table.

State and persistence behavior: Persistent state is read-only conversion tables defined elsewhere; caller buffers are modified in place.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with Integrates hypfs, IPL/firmware strings, device identifiers, and z/VM/firmware text handling..

Risks: Callers must pass correct buffer lengths because conversion is in-place and binary data would be mangled.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 47 lines, 1431 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ebcdic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/elf.h

Purpose: Defines s390 ELF relocation constants, HWCAP bits, core/register ABI types, and executable personality setup.

Important APIs/types/functions: `R_390_*` relocations, HWCAP bit definitions, ELF class/data/arch macros, greg/fpreg types, `ELF_PLAT_INIT`, `ELF_ET_DYN_BASE`, `ARCH_DLINFO`, and `arch_setup_additional_pages()`. Source-visible declarations include: #define __ASMS390_ELF_H; #define R_390_NONE 0 /* No reloc. */; #define R_390_8 1 /* Direct 8 bit. */; #define R_390_12 2 /* Direct 12 bit. */; #define R_390_16 3 /* Direct 16 bit. */; #define R_390_32 4 /* Direct 32 bit. */; #define R_390_PC32 5 /* PC relative 32 bit. */; #define R_390_GOT12 6 /* 12 bit GOT offset. */; #define R_390_GOT32 7 /* 32 bit GOT offset. */; #define R_390_PLT32 8 /* 32 bit PC relative PLT address. */.

Control flow: The ELF loader validates machine type, initializes registers, chooses randomized mapping bases, exports auxv hardware/platform data, and maps additional vDSO pages.

State and persistence behavior: Persistent ABI state includes auxv HWCAP/platform strings, process personality, mapped vDSO, and core dump register layout.

Dependencies and integration points: Direct includes are #include <asm/ptrace.h>, #include <asm/syscall.h>, #include <asm/user.h>, #include <linux/sched/mm.h>	/* for task_struct */, #include <asm/mmu_context.h>. Integrated with Integrates binfmt_elf, dynamic linker ABI, ptrace/core dumps, vDSO, ASLR, and CPU feature discovery..

Risks: Relocation numbers and HWCAP bits are user ABI; changing them breaks loaders, libc, or feature dispatch.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 245 lines, 9476 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/entry-common.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/entry-common.h

Purpose: Customizes generic entry/exit handling for s390.

Important APIs/types/functions: `ARCH_EXIT_TO_USER_MODE_WORK`, `do_per_trap()`, `arch_enter_from_user_mode()`, `arch_exit_to_user_mode_work()`, `arch_exit_to_user_mode()`, and `arch_in_rcu_eqs()`. Source-visible declarations include: #define ARCH_S390_ENTRY_COMMON_H; #define ARCH_EXIT_TO_USER_MODE_WORK (_TIF_GUARDED_STORAGE | _TIF_PER_TRAP); void do_per_trap(struct pt_regs *regs);; static __always_inline void arch_enter_from_user_mode(struct pt_regs *regs); #define arch_enter_from_user_mode arch_enter_from_user_mode; static __always_inline void arch_exit_to_user_mode_work(struct pt_regs *regs,; unsigned long ti_work); #define arch_exit_to_user_mode_work arch_exit_to_user_mode_work; static __always_inline void arch_exit_to_user_mode(void); #define arch_exit_to_user_mode arch_exit_to_user_mode.

Control flow: Entry code marks context tracking transitions, handles guarded-storage/per-event trap work before returning to user mode, and exposes RCU EQS state tests.

State and persistence behavior: State is task thread flags, context tracking/RCU state, and pt_regs for the current transition.

Dependencies and integration points: Direct includes are #include <linux/sched.h>, #include <linux/audit.h>, #include <linux/randomize_kstack.h>, #include <linux/processor.h>, #include <linux/uaccess.h>, #include <asm/timex.h>, #include <asm/fpu.h>, #include <asm/pai.h>. Integrated with Integrates generic entry code, RCU/context tracking, guarded storage, PER tracing, and syscall/interrupt exit paths..

Risks: Ordering with RCU and thread flag clearing is critical; missed PER/GS work leaks traps to the wrong user context.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 64 lines, 1409 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/entry-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/exec.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/exec.h

Purpose: Declares s390 exec stack alignment policy.

Important APIs/types/functions: `arch_align_stack(unsigned long sp)`. Source-visible declarations include: #define __ASM_EXEC_H; extern unsigned long arch_align_stack(unsigned long sp);.

Control flow: Exec and stack setup call the arch helper to perturb or align the initial user stack pointer.

State and persistence behavior: State is the computed user stack pointer in a new process image.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates binfmt loaders, ASLR, and process setup..

Risks: Stack alignment is user ABI and affects libc/startup assumptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 13 lines, 269 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/extable.h

Purpose: Defines runtime exception-table entry layout and fixup helpers.

Important APIs/types/functions: `struct exception_table_entry`, amode31 extable bounds, `extable_fixup()`, `swap_ex_entry_fixup()`, `ex_handler_bpf()`, and `fixup_exception()`. Source-visible declarations include: #define __S390_EXTABLE_H; struct exception_table_entry; int insn, fixup;; extern struct exception_table_entry *__start_amode31_ex_table;; extern struct exception_table_entry *__stop_amode31_ex_table;; static inline unsigned long extable_fixup(const struct exception_table_entry *x); #define ARCH_HAS_RELATIVE_EXTABLE; static inline void swap_ex_entry_fixup(struct exception_table_entry *a,; struct exception_table_entry *b,; struct exception_table_entry tmp,.

Control flow: Fault handling searches relative extable entries, decodes the fixup address and type/data fields, and either applies specialized handlers or redirects execution.

State and persistence behavior: State is linker-built exception tables and transient pt_regs during fault recovery.

Dependencies and integration points: Direct includes are #include <asm/ptrace.h>, #include <linux/compiler.h>. Integrated with Integrates user access, BPF, amode31 code, module extables, sorting, and low-level fault handling..

Risks: Relative offsets and swap logic must preserve sort order and fixup semantics across modules and built-in code.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 72 lines, 1924 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extmem.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/extmem.h

Purpose: Declares z/VM DCSS/extmem segment management APIs.

Important APIs/types/functions: Segment type/sharing constants, `segment_load()`, `segment_unload()`, `segment_save()`, `segment_type()`, `segment_modify_shared()`, and `segment_warning()`. Source-visible declarations include: #define _ASM_S390X_DCSS_H; #define MAX_DCSS_ADDR (512UL * SZ_1G); #define SEG_TYPE_SW 0; #define SEG_TYPE_EW 1; #define SEG_TYPE_SR 2; #define SEG_TYPE_ER 3; #define SEG_TYPE_SN 4; #define SEG_TYPE_EN 5; #define SEG_TYPE_SC 6; #define SEG_TYPE_EWEN 7.

Control flow: Callers load named DCSS segments with requested sharing/type, receive address/length, and later save, unload, or change sharing.

State and persistence behavior: Persistent state is hypervisor segment mapping and kernel mappings of loaded segments.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates z/VM DCSS, xip/extmem drivers, module-like shared segment users, and VM-specific diagnostics..

Risks: Segment names/types are hypervisor ABI; incorrect sharing changes can affect other guests or mappings.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 39 lines, 1066 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/extmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/facility.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/facility.h

Purpose: Implements s390 facility-bit manipulation and STFLE probing.

Important APIs/types/functions: `stfle_fac_list`, `__set_facility()`, `__clear_facility()`, `__test_facility()`, constant optimized tests, `test_facility()`, `__stfle()`, `stfle()`, and `stfle_size()`. Source-visible declarations include: #define __ASM_FACILITY_H; #define MAX_FACILITY_BIT (sizeof(stfle_fac_list) * 8); extern u64 stfle_fac_list[16];; static inline void __set_facility(unsigned long nr, void *facilities); unsigned char *ptr = (unsigned char *) facilities;; static inline void __clear_facility(unsigned long nr, void *facilities); unsigned char *ptr = (unsigned char *) facilities;; static __always_inline bool __test_facility(unsigned long nr, void *facilities); unsigned char *ptr;; static __always_inline bool __test_facility_constant(unsigned long nr).

Control flow: Boot code stores facility lists with STFLE, helpers test MSB-numbered facility bits, and optimized constant tests read the global list directly when in range.

State and persistence behavior: Persistent state is global probed facility list and caller-provided STFLE buffers.

Dependencies and integration points: Direct includes are #include <asm/facility-defs.h>, #include <linux/minmax.h>, #include <linux/string.h>, #include <linux/types.h>, #include <linux/preempt.h>, #include <asm/alternative.h>, #include <asm/lowcore.h>. Integrated with Integrates CPU feature detection, alternatives, CPACF, vector/FPU, MM, and virtualization feature gating..

Risks: Facility bit numbering is MSB-oriented and easy to invert; false feature tests lead to illegal instructions or disabled optimizations.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 142 lines, 3491 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/facility.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fault.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fault.h

Purpose: Defines translation-exception identification decoding helpers.

Important APIs/types/functions: `union teid` and TEID-related fault type bits. Source-visible declarations include: #define _ASM_S390_FAULT_H; union teid {; unsigned long val;; struct {; unsigned long addr : 52; /* Translation-exception Address */; unsigned long fsi : 2; /* Access Exception Fetch/Store Indication */; unsigned long : 2;; unsigned long b56 : 1;; unsigned long : 3;; unsigned long b60 : 1;.

Control flow: Fault handlers decode the hardware TEID word to determine address, protection, store/fetch, and translation details.

State and persistence behavior: State is transient fault metadata captured by low-level exception code.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates page fault handling, KVM, user access recovery, and MM diagnostics..

Risks: Bitfield layout is hardware ABI; wrong decoding misclassifies page faults or protection exceptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 28 lines, 730 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fcx.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fcx.h

Purpose: Defines Fibre Channel Extensions/transport-command-word data structures and helper APIs.

Important APIs/types/functions: `tcw`, `tidaw`, TSA/TSB formats, `dcw`, `tccb`, flag constants, and helpers to initialize/finalize TCWs, TCCBs, TSBs, DCWs, and TIDAWs. Source-visible declarations include: #define _ASM_S390_FCX_H; #define TCW_FORMAT_DEFAULT 0; #define TCW_TIDAW_FORMAT_DEFAULT 0; #define TCW_FLAGS_INPUT_TIDA (1 << (23 - 5)); #define TCW_FLAGS_TCCB_TIDA (1 << (23 - 6)); #define TCW_FLAGS_OUTPUT_TIDA (1 << (23 - 7)); #define TCW_FLAGS_TIDAW_FORMAT(x) ((x) & 3) << (23 - 9); #define TCW_FLAGS_GET_TIDAW_FORMAT(x) (((x) >> (23 - 9)) & 3); struct tcw {; #define TIDAW_FLAGS_LAST (1 << (7 - 0)).

Control flow: CCW transport-mode users build TCWs referencing TCCB command blocks, TSB status blocks, optional TIDAL data lists, and interrogation TCWs, then submit them through CCW device TM start APIs.

State and persistence behavior: Persistent state is caller-allocated channel program memory, transport status, and DMA-visible data-address lists.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <asm/dma-types.h>. Integrated with Integrates CCW transport mode, FICON/DASD, CIO status handling, DMA pools, and `ccwdev.h` APIs..

Risks: Structure packing, data-address flags, and finalization counts are hardware ABI; errors can break channel programs or lose status.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 313 lines, 8150 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fcx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fprobe.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fprobe.h

Purpose: Provides s390 fprobe arch constants.

Important APIs/types/functions: `FPROBE_HEADER_MSB_PATTERN`. Source-visible declarations include: #define _ASM_S390_FPROBE_H; #define FPROBE_HEADER_MSB_PATTERN 0.

Control flow: Fprobe/kprobe code uses the pattern constant when interpreting s390 function entry bytes.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are #include <asm-generic/fprobe.h>. Integrated with Integrates fprobe, kprobes, and function-entry instrumentation..

Risks: Instruction pattern constants must match actual compiler/assembler function prologues.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 10 lines, 229 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn-asm.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn-asm.h

Purpose: Defines assembler macros that emit vector instruction encodings for toolchains lacking direct mnemonic support.

Important APIs/types/functions: `GR_NUM`, `VX_NUM`, `RXB`, `MRXB`, and vector instruction macros for load/store, permute, arithmetic, Galois-field, shift, replicate, merge, and zero/one generation. Source-visible declarations include: #define __ASM_S390_FPU_INSN_ASM_H.

Control flow: Assembler macros map register names to numeric fields, compute RXB extension bits for vector registers 16-31, and emit `.word`/`.byte` instruction encodings.

State and persistence behavior: State is generated machine code in assembly objects, not runtime data.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates `fpu-insn.h`, crypto/vector assembly, binutils compatibility, and kernel FPU sections..

Risks: Encoding bugs are catastrophic and may only appear on older assembler configurations; RXB and operand field placement are the key risk.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 754 lines, 15770 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn.h

Purpose: Provides C-callable wrappers around individual s390 floating-point and vector instructions.

Important APIs/types/functions: `fpu_ld/std`, FPC load/store helpers, safe `fpu_lfpc_safe()`, vector load/store/multiple/permute/GF/logic/arithmetic helpers, and KASAN/KMSAN instrumentation hooks. Source-visible declarations include: #define __ASM_S390_FPU_INSN_H; static __always_inline void fpu_cefbr(u8 f1, s32 val); static __always_inline unsigned long fpu_cgebr(u8 f2, u8 mode); unsigned long val;; static __always_inline void fpu_debr(u8 f1, u8 f2); static __always_inline void fpu_ld(unsigned short fpr, freg_t *reg); static __always_inline void fpu_ldgr(u8 f1, u32 val); static __always_inline void fpu_lfpc(unsigned int *fpc); static inline void fpu_lfpc_safe(unsigned int *fpc); static __always_inline void fpu_std(unsigned short fpr, freg_t *reg).

Control flow: Each inline emits exactly the targeted FP/vector instruction with memory barriers; memory operands call instrumentation helpers, and fault-prone FPC loading uses exception-table recovery.

State and persistence behavior: State is FP/vector registers, FPC, and caller-provided save/load buffers.

Dependencies and integration points: Direct includes are #include <asm/fpu-insn-asm.h>, #include <linux/instrumented.h>, #include <linux/kmsan.h>, #include <asm/asm-extable.h>. Integrated with Integrates kernel FPU sections, crypto vector code, checksum/vector helpers, KASAN/KMSAN, and `fpu-insn-asm.h` macro encodings..

Risks: Callers must be inside `kernel_fpu_begin/end`; otherwise user FP/vector state can be corrupted. Partial vector length helpers must unpoison exactly written bytes.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 482 lines, 11681 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-types.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-types.h

Purpose: Defines s390 FPU and kernel-FPU save-area structures.

Important APIs/types/functions: `struct fpu`, `struct kernel_fpu_hdr`, `struct kernel_fpu`, `KERNEL_FPU_STRUCT()`, and stack declaration macros for 8/16/32 vector registers. Source-visible declarations include: #define _ASM_S390_FPU_TYPES_H; struct fpu {; struct kernel_fpu_hdr {; struct kernel_fpu {; struct kernel_fpu_hdr hdr;; #define KERNEL_FPU_STRUCT(vxr_size) \; struct kernel_fpu_##vxr_size { \; struct kernel_fpu_hdr hdr; \; #define DECLARE_KERNEL_FPU_ONSTACK(vxr_size, name) \; struct kernel_fpu_##vxr_size name __uninitialized.

Control flow: Kernel code declares save areas sized for the vector ranges it will use; `fpu.h` checks those sizes before saving/restoring.

State and persistence behavior: Persistent state is task user-FPU and kernel-FPU save areas embedded in thread structures or caller stacks.

Dependencies and integration points: Direct includes are #include <asm/sigcontext.h>. Integrated with Integrates thread state, signal/ptrace FPU formats, in-kernel vector users, and compile-time size checking..

Risks: Save-area sizing must match flag ranges; too-small stack structures would corrupt memory during FPU nesting.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 51 lines, 1085 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu.h

Purpose: Implements the high-level s390 in-kernel FPU/vector state management API.

Important APIs/types/functions: `KERNEL_FPC`, `KERNEL_VXR_*`, `KERNEL_FPR`, save/load helpers, `load_user_fpu_regs()`, `save_user_fpu_regs()`, `kernel_fpu_begin/end()`, and FP/VX conversion helpers. Source-visible declarations include: #define _ASM_S390_FPU_H; enum {; #define KERNEL_FPC BIT(KERNEL_FPC_BIT); #define KERNEL_VXR_V0V7 BIT(KERNEL_VXR_V0V7_BIT); #define KERNEL_VXR_V8V15 BIT(KERNEL_VXR_V8V15_BIT); #define KERNEL_VXR_V16V23 BIT(KERNEL_VXR_V16V23_BIT); #define KERNEL_VXR_V24V31 BIT(KERNEL_VXR_V24V31_BIT); #define KERNEL_VXR_LOW (KERNEL_VXR_V0V7 | KERNEL_VXR_V8V15); #define KERNEL_VXR_MID (KERNEL_VXR_V8V15 | KERNEL_VXR_V16V23); #define KERNEL_VXR_HIGH (KERNEL_VXR_V16V23 | KERNEL_VXR_V24V31).

Control flow: The API marks kernel-owned register ranges in thread flags, saves user state for ranges about to be used, optionally saves nested kernel ranges, and restores previous ownership on end.

State and persistence behavior: Persistent state lives in `thread_struct` user/kernel FPU save areas plus `ufpu_flags` and `kfpu_flags`; stack save areas hold nested kernel state.

Dependencies and integration points: Direct includes are #include <linux/cpufeature.h>, #include <linux/processor.h>, #include <linux/preempt.h>, #include <linux/string.h>, #include <linux/sched.h>, #include <asm/sigcontext.h>, #include <asm/fpu-types.h>, #include <asm/fpu-insn.h>. Integrated with Integrates scheduler context switch, signal/ptrace FP register ABI, vector crypto/checksum users, preemption assumptions, and low-level instruction wrappers..

Risks: Kernel FPU sections must use matching flags and save-area sizes. Nested or interrupt-context use depends on disjoint vector ranges to avoid unnecessary or missing saves.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 290 lines, 8301 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu.h -->
