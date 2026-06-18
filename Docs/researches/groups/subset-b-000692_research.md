# subset-b-000692 Research

Grouped source research for subset B work item `subset-b-000692`. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit_comp.c -->
# sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit_comp.c

## Purpose

implements the arm64 eBPF JIT backend, including instruction selection, BPF program
prologue/epilogue generation, tail calls, exception-table fixups, trampoline generation, text
patching, and capability reporting to the generic BPF core

## Important APIs, Types, and Functions

Source read size: 3161 lines, 87356 bytes. Includes: `linux/arm-smccc.h`, `linux/bitfield.h`,
`linux/bpf.h`, `linux/cfi.h`, `linux/filter.h`, `linux/memory.h`, `linux/printk.h`, `linux/slab.h`,
`asm/asm-extable.h`, `asm/byteorder.h`; plus 6 more. Functions: `emit`, `emit_u32_data`,
`emit_a64_mov_i`, `i64_i16_blocks`, `emit_a64_mov_i64`, `emit_bti`, `emit_kcfi`,
`emit_addr_mov_i64`, `should_emit_indirect_call`, `emit_direct_call`, `emit_indirect_call`,
`emit_call`, `bpf2a64_offset`, `jit_fill_hole`, `bpf_arch_text_invalidate`, `epilogue_offset`,
`is_addsub_imm`, `emit_a64_add_i`; plus 54 more. Key macros/defines: `pr_fmt(fmt)`, `TMP_REG_1`,
`TMP_REG_2`, `TCCNT_PTR`, `TMP_REG_3`, `PRIVATE_SP`, `ARENA_VM_START`, `check_imm(bits, imm)`,
`check_imm19(imm)`, `check_imm26(imm)`, `PLT_TARGET_SIZE`, `PLT_TARGET_OFFSET`,
`PRIV_STACK_GUARD_SZ`, `PRIV_STACK_GUARD_VAL`, `BTI_INSNS`, `PAC_INSNS`, `POKE_OFFSET`,
`PROLOGUE_OFFSET`; plus 5 more. Local structs: `jit_ctx`, `bpf_plt`, `bpf_prog_aux`, `pt_regs`,
`exception_table_entry`, `bpf_prog`, `arm64_jit_data`, `bpf_binary_header`; plus 3 more.

## Control Flow and Behavior

the compiler performs size estimation, offset discovery, final emission, validation, executable pack
finalization, and optional multi-function extra passes; instruction emission maps BPF registers onto
AArch64 registers and lowers ALU, jump, load/store, atomic, helper-call, arena, percpu, and timed-
may-goto operations

## State and Persistence

persistent effects are the generated read-only executable image, BPF line-info offsets,
aux->jit_data during subprogram linking, exception-table entries, optional per-CPU private stack
allocation guarded by sentinel values, and trampoline patch sites/PLT targets

## Dependencies and Integration Points

depends on the BPF verifier/core, arm64 instruction encoding and text patching APIs, BTI/PAC/KCFI
controls, cpufeature detection, executable BPF program packs, exception tables, ftrace-style
trampoline attachment, and arm64 speculation mitigations

## Risks and Test Signals

branch offset ranges, stack layout, register save/restore order, exception metadata encoding,
private-stack guard accounting, long-jump PLT patching, and LSE versus LL/SC atomic selection are
correctness-critical; test signals are BPF selftests, JIT dump validation, verifier JIT coverage,
trampoline/fentry/fexit tests, kprobe/fprobe exercises, and boot/runtime warnings from validate_ctx
or text poke failures
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/bpf_timed_may_goto.S -->
# sources/distributed-fs/ceph-client/arch/arm64/net/bpf_timed_may_goto.S

## Purpose

provides the arm64 assembly implementation of arch_bpf_timed_may_goto(), a helper target emitted by
the BPF verifier for bounded timed loop continuation

## Important APIs, Types, and Functions

Source read size: 40 lines, 1150 bytes. Includes: `linux/linkage.h`. Assembly/global entries:
`arch_bpf_timed_may_goto`.

## Control Flow and Behavior

the routine uses the BPF custom convention with BPF_REG_AX in x9, reads the virtual counter,
compares elapsed time against the supplied budget, and returns whether execution may branch to the
loop target

## State and Persistence

it keeps no persistent state and only consumes architectural counter state at runtime

## Dependencies and Integration Points

integrates with arm64 BPF JIT helper-call lowering and the generic verifier's timed may-goto
transformation

## Risks and Test Signals

the custom register convention and counter arithmetic must match bpf_jit_comp.c; BPF verifier/JIT
selftests that exercise timed loops are the main signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/bpf_timed_may_goto.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/tools/Makefile

## Purpose

coordinates generated arm64 architecture headers produced from cpucaps, syscall, HWCAP, and sysreg
description inputs

## Important APIs, Types, and Functions

Source read size: 34 lines, 1004 bytes. Build selections: `kapisyshdr-y -> cpucap-defs.h kernel-
hwcap.h sysreg-defs.h`, `kapi-hdrs-y -> $(addprefix $(kapi)/, $(kapisyshdr-y))`.

## Control Flow and Behavior

Kbuild rules invoke local scripts and generated-header targets before dependent arm64 code is
compiled

## State and Persistence

state is generated header output under the build tree, not runtime kernel state

## Dependencies and Integration Points

depends on AWK/shell generators, source description files, and the kernel generated-header pipeline

## Risks and Test Signals

stale generated headers or missing tool dependencies break arm64 builds; clean rebuilds and
generated header diffs are the test signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/gen-cpucaps.awk -->
# sources/distributed-fs/ceph-client/arch/arm64/tools/gen-cpucaps.awk

## Purpose

generates arm64 CPU capability constants from a sorted textual capability list

## Important APIs, Types, and Functions

Source read size: 40 lines, 773 bytes. Functions: `fatal`.

## Control Flow and Behavior

the AWK script validates numbering/order, emits C preprocessor defines, and terminates through
fatal() on malformed input

## State and Persistence

state is limited to AWK counters while generating a header during the build

## Dependencies and Integration Points

integrates with arch/arm64/tools/Makefile and generated asm/cpucaps.h consumers in cpufeature code

## Risks and Test Signals

bad sorting or duplicate capability names shift feature-bit ABI inside the kernel; build
regeneration and cpufeature compilation are the test signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/gen-cpucaps.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/gen-kernel-hwcaps.sh -->
# sources/distributed-fs/ceph-client/arch/arm64/tools/gen-kernel-hwcaps.sh

## Purpose

generates kernel HWCAP metadata headers from arm64 CPU feature descriptions

## Important APIs, Types, and Functions

Source read size: 23 lines, 545 bytes.

## Control Flow and Behavior

the shell pipeline invokes the arm64 sysreg/hwcap generation tooling and forwards arguments from
Kbuild

## State and Persistence

it has no persistent runtime state beyond generated header files

## Dependencies and Integration Points

integrates with arch/arm64/tools/Makefile and ELF HWCAP reporting used by cpu feature and userspace
capability paths

## Risks and Test Signals

script portability, input ordering, and regenerated constants are the risk points; test signals are
clean header regeneration and boot-time HWCAP exposure
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/gen-kernel-hwcaps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/gen-sysreg.awk -->
# sources/distributed-fs/ceph-client/arch/arm64/tools/gen-sysreg.awk

## Purpose

parses the arm64 sysreg description DSL and emits C preprocessor definitions for registers, fields,
field masks, and RES0/RES1/unknown bit metadata

## Important APIs, Types, and Functions

Source read size: 411 lines, 8629 bytes. Functions: `block_current`, `fatal`, `block_push`,
`block_pop`, `expect_fields`, `define`, `define_reg`, `define_field`, `define_field_sign`,
`define_resx_unkn`, `parse_bitdef`.

## Control Flow and Behavior

important routines include block_push/pop, define_reg, define_field, define_resx_unkn, parse_bitdef,
and fatal; the parser tracks nested register/field blocks and validates field counts and bit ranges

## State and Persistence

state is in AWK block stacks, current register names, and emitted definition ordering during header
generation only

## Dependencies and Integration Points

integrates with Kbuild-generated arm64 sysreg headers and many low-level cpufeature, system-
register, and trap handlers

## Risks and Test Signals

malformed descriptors can silently misdescribe architectural registers if validation is weakened;
build-time generation and compile users of generated macros are the primary tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/tools/gen-sysreg.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/xen/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/xen/Makefile

## Purpose

builds objects or generated artifacts for `sources/distributed-fs/ceph-client/arch/arm64/xen`

## Important APIs, Types, and Functions

Source read size: 3 lines, 151 bytes. Build selections: `xen-arm-y -> $(addprefix ../../arm/xen/,
enlighten.o grant-table.o p2m.o mm.o)`, `obj-y -> xen-arm.o hypercall.o`.

## Control Flow and Behavior

Kbuild variables select object files, subdirectories, generated headers, or boot targets

## State and Persistence

state is build output only

## Dependencies and Integration Points

integrates with parent Kbuild recursion and configuration symbols

## Risks and Test Signals

wrong dependencies or object lists cause missing code or stale generated artifacts; clean builds are
the signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/xen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/xen/hypercall.S -->
# sources/distributed-fs/ceph-client/arch/arm64/xen/hypercall.S

## Purpose

implements arm64 Xen hypercall stubs used by the Xen guest front-end and privcmd paths

## Important APIs, Types, and Functions

Source read size: 130 lines, 4332 bytes. Includes: `linux/linkage.h`, `asm/assembler.h`, `asm/asm-
uaccess.h`, `xen/interface/xen.h`. Assembly/global entries: `HYPERVISOR_##hypercall`,
`HYPERVISOR_dm_op`, `privcmd_call`. Key macros/defines: `XEN_IMM`, `HYPERCALL_SIMPLE(hypercall)`,
`HYPERCALL0`, `HYPERCALL1`, `HYPERCALL2`, `HYPERCALL3`, `HYPERCALL4`, `HYPERCALL5`.

## Control Flow and Behavior

HYPERCALL_SIMPLE emits wrappers that load a Xen immediate and trap via hvc; HYPERVISOR_dm_op and
privcmd_call provide argument reshuffling and return handling for special hypercall forms

## State and Persistence

no kernel state is persisted by the assembly itself; state changes occur in the hypervisor as a
result of the trap

## Dependencies and Integration Points

depends on Xen public hypercall numbering, arm64 calling convention, and linkage macros used by
arch/arm64 Xen support

## Risks and Test Signals

register ordering and hvc immediate values are ABI-critical; Xen guest boot, grant/device
operations, and privcmd tests exercise this code
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/xen/hypercall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/Kbuild -->
# sources/distributed-fs/ceph-client/arch/csky/Kbuild

## Purpose

selects the top-level C-SKY architecture subdirectories that participate in the kernel build

## Important APIs, Types, and Functions

Source read size: 6 lines, 94 bytes. Build selections: `obj-y -> kernel/ mm/`.

## Control Flow and Behavior

Kbuild descends into kernel, mm, boot, and ABI-specific object directories according to the object
list

## State and Persistence

there is no runtime state

## Dependencies and Integration Points

integrates the C-SKY architecture tree into the generic recursive Kbuild system

## Risks and Test Signals

missing directories omit boot-critical code; allmodconfig/defconfig build coverage is the main
signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/Kconfig -->
# sources/distributed-fs/ceph-client/arch/csky/Kconfig

## Purpose

declares the C-SKY architecture configuration surface, CPU variants, MMU/cache/FPU/SMP/highmem/TCM
options, and generic kernel feature selections

## Important APIs, Types, and Functions

Source read size: 355 lines, 8599 bytes. Kconfig symbols: `CSKY`, `LOCKDEP_SUPPORT`,
`ARCH_SUPPORTS_UPROBES`, `CPU_HAS_CACHEV2`, `CPU_HAS_FPUV2`, `CPU_HAS_HILO`, `CPU_HAS_TLBI`,
`CPU_HAS_LDSTEX`, `CPU_NEED_TLBSYNC`, `CPU_NEED_SOFTALIGN`, `CPU_NO_USER_BKPT`,
`GENERIC_CALIBRATE_DELAY`, `GENERIC_CSUM`, `GENERIC_HWEIGHT`, `MMU`, `STACKTRACE_SUPPORT`,
`TIME_LOW_RES`, `CPU_ASID_BITS`; plus 32 more.

## Control Flow and Behavior

menu/config entries choose ABI, page offset, CPU features, PMU, power management, TCM, SMP, highmem,
and architecture capability defaults

## State and Persistence

persistent effects are compile-time configuration symbols that shape the built kernel

## Dependencies and Integration Points

integrates with the top-level Kconfig, generic MM/IRQ/time/ftrace/perf options, and C-SKY Makefile
object selection

## Risks and Test Signals

bad defaults can build incompatible kernels for a CPU; defconfig, randconfig, and boot tests across
CK610/CK807/CK810/CK860 are the signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/Makefile

## Purpose

sets C-SKY architecture compiler flags, ABI-specific include paths, image targets, and boot/install
helpers

## Important APIs, Types, and Functions

Source read size: 78 lines, 1530 bytes. Build selections: `core-y -> arch/csky/$(CSKYABI)/`, `libs-y
-> arch/csky/lib/ \`.

## Control Flow and Behavior

the file selects ABI v1/v2 options, CPU tuning flags, Kbuild image names, head objects, and archhelp
text

## State and Persistence

state is build configuration only

## Dependencies and Integration Points

integrates Kconfig selections with compiler, linker, boot image, and dtb build rules

## Risks and Test Signals

wrong flags or head object ordering can make kernels unbootable; defconfig image builds and linker
checks are the primary tests
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/Makefile

## Purpose

builds C-SKY ABI v1 support objects for alignment handling, cache flushing, mmap policy, and byte-
swap helpers

## Important APIs, Types, and Functions

Source read size: 6 lines, 180 bytes. Build selections: `obj-y -> bswapdi.o`, `obj-y -> bswapsi.o`,
`obj-y -> cacheflush.o`, `obj-y -> mmap.o`.

## Control Flow and Behavior

object selection adds small ABI compatibility routines into the architecture build

## State and Persistence

state is build output only

## Dependencies and Integration Points

integrates ABI v1 C files with the top-level C-SKY Makefile include path

## Risks and Test Signals

omitting an object breaks ABI v1 runtime traps or helper symbols; ABI v1 build and boot tests cover
it
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/alignment.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/alignment.c

## Purpose

handles C-SKY ABI v1 unaligned access traps by decoding selected load/store opcodes and emulating
them byte-by-byte when enabled

## Important APIs, Types, and Functions

Source read size: 340 lines, 5881 bytes. Includes: `linux/kernel.h`, `linux/uaccess.h`,
`linux/ptrace.h`. Functions: `get_ptreg`, `put_ptreg`, `ldb_asm`, `stb_asm`, `ldh_c`, `sth_c`,
`ldw_c`, `stw_c`, `csky_alignment`, `csky_alignment_init`. Key macros/defines: `OP_LDH`, `OP_STH`,
`OP_LDW`, `OP_STW`.

## Control Flow and Behavior

get_ptreg/put_ptreg access saved registers; ldb_asm/stb_asm use exception-table protected byte
accesses; ldh_c/sth_c/ldw_c/stw_c emulate halfword and word operations; csky_alignment() decodes the
faulting instruction, counts kernel/user events, and either fixes the access or delegates to
fixup_exception/signals

## State and Persistence

persistent state is the static enable flags and counters for kernel/user alignment handling

## Dependencies and Integration Points

integrates with trap handling, pt_regs layout, user access exception tables, and ABI v1 instruction
encoding

## Risks and Test Signals

incorrect opcode decoding or register mapping can corrupt user state or hide real faults; alignment-
trap tests, unaligned user loads/stores, and exception-fixup paths are key signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/alignment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/bswapdi.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/bswapdi.c

## Purpose

provides the C-SKY ABI v1 libgcc-style 64-bit byte-swap helper expected by compiler-generated code

## Important APIs, Types, and Functions

Source read size: 12 lines, 302 bytes. Includes: `linux/export.h`, `linux/compiler.h`,
`uapi/linux/swab.h`. Functions: `__bswapdi2`. Exported symbols: `__bswapdi2`.

## Control Flow and Behavior

the helper reverses byte order for integer values and supplies a symbol that may be emitted by the
compiler or linked by kernel code

## State and Persistence

there is no persistent state

## Dependencies and Integration Points

integrates with compiler runtime expectations and any generic code using byte-swap operations on ABI
v1

## Risks and Test Signals

wrong symbol semantics corrupt endian conversions; build/link tests and byte-order selftests cover
it
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/bswapdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/bswapsi.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/bswapsi.c

## Purpose

provides the C-SKY ABI v1 libgcc-style 32-bit byte-swap helper expected by compiler-generated code

## Important APIs, Types, and Functions

Source read size: 12 lines, 290 bytes. Includes: `linux/export.h`, `linux/compiler.h`,
`uapi/linux/swab.h`. Functions: `__bswapsi2`. Exported symbols: `__bswapsi2`.

## Control Flow and Behavior

the helper reverses byte order for integer values and supplies a symbol that may be emitted by the
compiler or linked by kernel code

## State and Persistence

there is no persistent state

## Dependencies and Integration Points

integrates with compiler runtime expectations and any generic code using byte-swap operations on ABI
v1

## Risks and Test Signals

wrong symbol semantics corrupt endian conversions; build/link tests and byte-order selftests cover
it
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/bswapsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/cacheflush.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/cacheflush.c

## Purpose

implements C-SKY ABI v1 cache maintenance hooks for MMU cache updates and instruction-cache
synchronization

## Important APIs, Types, and Functions

Source read size: 75 lines, 1604 bytes. Includes: `linux/kernel.h`, `linux/mm.h`, `linux/fs.h`,
`linux/pagemap.h`, `linux/syscalls.h`, `linux/spinlock.h`, `asm/page.h`, `asm/cache.h`,
`asm/cacheflush.h`, `asm/cachectl.h`; plus 1 more. Functions: `flush_dcache_folio`,
`flush_dcache_page`, `update_mmu_cache_range`, `flush_cache_range`. Key macros/defines:
`PG_dcache_clean`. Local structs: `address_space`, `folio`. Exported symbols: `flush_dcache_folio`,
`flush_dcache_page`.

## Control Flow and Behavior

functions flush or defer I-cache maintenance around executable mappings, user pages, and MMU updates
according to ABI cache instructions

## State and Persistence

runtime state may include mm context flags that defer I-cache flushing until return to user or
context activation

## Dependencies and Integration Points

integrates with mm fault handling, set_pte/update_mmu_cache, flush_icache_* APIs, and ABI cacheflush
instructions

## Risks and Test Signals

stale I-cache after writing executable code causes user/kernel execution of old instructions;
mmap/mprotect, BPF/JIT-like code, and self-modifying-code tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/cacheflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/cacheflush.h

## Purpose

defines ABI-specific cache flush primitives and aliases used by generic C-SKY cache maintenance code
for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 64 lines, 1980 bytes. Includes: `linux/mm.h`, `asm/string.h`, `asm/cache.h`.
Functions: `flush_kernel_vmap_range`, `invalidate_kernel_vmap_range`, `flush_anon_page`. Key
macros/defines: `__ABI_CSKY_CACHEFLUSH_H`, `ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`,
`flush_dcache_folio`, `flush_cache_mm(mm)`, `flush_cache_page(vma, page, pfn)`,
`flush_cache_dup_mm(mm)`, `flush_dcache_mmap_lock(mapping)`, `flush_dcache_mmap_unlock(mapping)`,
`ARCH_IMPLEMENTS_FLUSH_KERNEL_VMAP_RANGE`, `ARCH_HAS_FLUSH_ANON_PAGE`, `flush_cache_vmap(start,
end)`, `flush_cache_vmap_early(start, end)`, `flush_cache_vunmap(start, end)`,
`flush_icache_range(start, end)`, `flush_icache_mm_range(mm, start, end)`,
`flush_icache_deferred(mm)`, `copy_from_user_page(vma, page, vaddr, dst, src, len)`,
`copy_to_user_page(vma, page, vaddr, dst, src, len)`. Local structs: `page`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/ckmmu.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/ckmmu.h

## Purpose

defines C-SKY MMU/TLB register constants and helper macros for ABI-specific page-table and TLB
management for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 101 lines, 1594 bytes. Includes: `abi/reg_ops.h`. Functions: `read_mmu_index`,
`write_mmu_index`, `read_mmu_entrylo0`, `read_mmu_entrylo1`, `write_mmu_pagemask`,
`read_mmu_entryhi`, `write_mmu_entryhi`, `read_mmu_msa0`, `write_mmu_msa0`, `read_mmu_msa1`,
`write_mmu_msa1`, `tlb_probe`, `tlb_read`, `tlb_invalid_all`, `local_tlb_invalid_all`,
`tlb_invalid_indexed`, `setup_pgd`. Key macros/defines: `__ASM_CSKY_CKMMUV1_H`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/ckmmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/elf.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/elf.h

## Purpose

defines ABI-specific ELF flags, register constants, and process personality details for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 26 lines, 717 bytes. Key macros/defines: `__ABI_CSKY_ELF_H`,
`ELF_CORE_COPY_REGS(pr_reg, regs)`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/entry.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/entry.h

## Purpose

defines low-level ABI entry/exit, register save, restore, and trap frame assembly macros for C-SKY
ABI v1

## Important APIs, Types, and Functions

Source read size: 176 lines, 2527 bytes. Includes: `asm/setup.h`, `abi/regdef.h`. Key
macros/defines: `__ASM_CSKY_ENTRY_H`, `LSAVE_PC`, `LSAVE_PSR`, `LSAVE_A0`, `LSAVE_A1`, `LSAVE_A2`,
`LSAVE_A3`, `LSAVE_A4`, `LSAVE_A5`, `usp`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/page.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/page.h

## Purpose

defines ABI-specific page constants and address translation helpers for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 28 lines, 716 bytes. Includes: `asm/shmparam.h`. Functions: `pages_do_alias`,
`clear_user_page`, `copy_user_page`. Key macros/defines: `clear_user_page`. Local structs: `page`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/pgtable-bits.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/pgtable-bits.h

## Purpose

defines page-table bit assignments, cacheability encodings, swap encodings, and protection bits for
C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 55 lines, 1558 bytes. Key macros/defines: `__ASM_CSKY_PGTABLE_BITS_H`,
`_PAGE_PRESENT`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_ACCESSED`, `_PAGE_MODIFIED`,
`_PAGE_SWP_EXCLUSIVE`, `_PAGE_GLOBAL`, `_PAGE_VALID`, `_PAGE_DIRTY`, `_PAGE_CACHE`, `_PAGE_UNCACHE`,
`_PAGE_SO`, `_CACHE_MASK`, `_CACHE_CACHED`, `_CACHE_UNCACHED`, `_PAGE_PROT_NONE`, `__swp_type(x)`;
plus 3 more.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/pgtable-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/reg_ops.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/reg_ops.h

## Purpose

provides inline helpers or macros for reading and writing C-SKY control registers for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 26 lines, 489 bytes. Includes: `asm/reg_ops.h`. Functions: `mfcr_hint`,
`mfcr_ccr2`. Key macros/defines: `__ABI_REG_OPS_H`, `cprcr(reg)`, `cpwcr(reg, val)`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/reg_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/regdef.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/regdef.h

## Purpose

names C-SKY architectural registers for assembly and inline assembly consumers for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 31 lines, 582 bytes. Key macros/defines: `__ASM_CSKY_REGDEF_H`, `syscallid`,
`regs_syscallid(regs)`, `regs_fp(regs)`, `DEFAULT_PSR_VALUE`, `SYSTRACE_SAVENUM`, `TRAP0_SIZE`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/regdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/string.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/string.h

## Purpose

selects ABI-optimized string routine declarations or aliases for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 15 lines, 388 bytes. Key macros/defines: `__ABI_CSKY_STRING_H`,
`__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE`, `__HAVE_ARCH_MEMSET`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/switch_context.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/switch_context.h

## Purpose

defines ABI-specific context switch save/restore contracts for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 16 lines, 313 bytes. Key macros/defines: `__ABI_CSKY_PTRACE_H`. Local structs:
`switch_stack`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/switch_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/vdso.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/vdso.h

## Purpose

declares ABI-specific VDSO data and mapping details for C-SKY ABI v1

## Important APIs, Types, and Functions

Source read size: 9 lines, 206 bytes. Key macros/defines: `__ABI_CSKY_VDSO_H`, `SET_SYSCALL_ID`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/inc/abi/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/mmap.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv1/mmap.c

## Purpose

implements C-SKY ABI v1 mmap address selection and cache-colour alignment policy

## Important APIs, Types, and Functions

Source read size: 72 lines, 1757 bytes. Includes: `linux/fs.h`, `linux/mm.h`, `linux/mman.h`,
`linux/shm.h`, `linux/sched.h`, `linux/random.h`, `linux/io.h`. Functions: `arch_get_unmapped_area`.
Key macros/defines: `COLOUR_ALIGN(addr,pgoff)`. Local structs: `mm_struct`, `vm_area_struct`,
`vm_unmapped_area_info`.

## Control Flow and Behavior

arch_get_unmapped_area() style logic aligns shared mappings to reduce VIPT cache aliasing and
validates address/length constraints

## State and Persistence

state is the selected virtual address returned to the caller; no private persistent state is kept

## Dependencies and Integration Points

integrates with generic mmap, file mappings, stack randomization, and cache alias rules

## Risks and Test Signals

bad colour alignment can trigger cache synonyms or reduce ASLR entropy; mmap layout tests and shared
mapping stress are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv1/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/Makefile

## Purpose

builds C-SKY ABI v2 support objects, optimized string routines, mcount, cache flushing, and optional
FPU support

## Important APIs, Types, and Functions

Source read size: 14 lines, 375 bytes. Build selections: `obj-y -> cacheflush.o`, `obj-y ->
memcmp.o`, `obj-y -> memcpy.o`, `obj-y -> memmove.o`, `obj-y -> memset.o`, `obj-y -> strcmp.o`,
`obj-y -> strcpy.o`, `obj-y -> strlen.o`, `obj-y -> strksyms.o`.

## Control Flow and Behavior

Kbuild includes assembly implementations for memcpy/memmove/memset/strcmp/strcpy/strlen/memcmp plus
conditional fpu.o

## State and Persistence

state is build output only

## Dependencies and Integration Points

integrates ABI v2 optimized routines and ftrace/FPU support with kernel linkage

## Risks and Test Signals

bad object selection affects core string semantics or tracing; ABI v2 builds, boot, lib/string
tests, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/cacheflush.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/cacheflush.c

## Purpose

implements C-SKY ABI v2 cache maintenance hooks for MMU cache updates and instruction-cache
synchronization

## Important APIs, Types, and Functions

Source read size: 92 lines, 2218 bytes. Includes: `linux/cache.h`, `linux/highmem.h`, `linux/mm.h`,
`asm/cache.h`, `asm/tlbflush.h`. Functions: `update_mmu_cache_range`, `flush_icache_deferred`,
`flush_icache_mm_range`. Local structs: `folio`.

## Control Flow and Behavior

functions flush or defer I-cache maintenance around executable mappings, user pages, and MMU updates
according to ABI cache instructions

## State and Persistence

runtime state may include mm context flags that defer I-cache flushing until return to user or
context activation

## Dependencies and Integration Points

integrates with mm fault handling, set_pte/update_mmu_cache, flush_icache_* APIs, and ABI cacheflush
instructions

## Risks and Test Signals

stale I-cache after writing executable code causes user/kernel execution of old instructions;
mmap/mprotect, BPF/JIT-like code, and self-modifying-code tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/cacheflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/fpu.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/fpu.c

## Purpose

implements C-SKY ABI v2 FPU exception support, libc compatibility handling for FPU control-register
instructions, and save/restore helpers for user floating-point state

## Important APIs, Types, and Functions

Source read size: 270 lines, 5431 bytes. Includes: `linux/ptrace.h`, `linux/uaccess.h`,
`abi/reg_ops.h`. Functions: `fpu_libc_helper`, `fpu_fpe`, `save_to_user_fp`, `restore_from_user_fp`.
Key macros/defines: `MTCR_MASK`, `MFCR_MASK`, `MTCR_DIST`, `MFCR_DIST`, `FMFVR_FPU_REGS(vrx, vry)`,
`FMTVR_FPU_REGS(vrx, vry)`, `STW_FPU_REGS(a, b, c, d)`, `LDW_FPU_REGS(a, b, c, d)`.

## Control Flow and Behavior

fpu_libc_helper() emulates selected mfcr/mtcr encodings, fpu_fpe() maps FESR bits to SIGILL/SIGFPE
codes, and save_to_user_fp()/restore_from_user_fp() move FCR/FESR and VR registers with
CPU_HAS_FPUV2/VDSP-specific assembly

## State and Persistence

persistent effects are updates to pt_regs pc/general registers during emulation and saved user_fp
images used by signal/core/ptrace-style paths

## Dependencies and Integration Points

depends on ABI register layout, FPU control registers cr<1,2>/cr<2,2>, CONFIG_CPU_HAS_FPUV2,
CONFIG_CPU_HAS_VDSP, interrupt masking, and signal delivery

## Risks and Test Signals

instruction decode, register count, and interrupt-disabled FPU transfer sequences are fragile; FPU
exception, signal frame, ptrace, and libc compatibility tests are the useful signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/cacheflush.h

## Purpose

defines ABI-specific cache flush primitives and aliases used by generic C-SKY cache maintenance code
for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 61 lines, 1906 bytes. Includes: `linux/mm.h`. Functions: `flush_dcache_folio`,
`flush_dcache_page`. Key macros/defines: `__ABI_CSKY_CACHEFLUSH_H`, `flush_cache_all()`,
`flush_cache_mm(mm)`, `flush_cache_dup_mm(mm)`, `flush_cache_range(vma, start, end)`,
`flush_cache_page(vma, vmaddr, pfn)`, `PG_dcache_clean`, `flush_dcache_folio`,
`ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_dcache_mmap_lock(mapping)`,
`flush_dcache_mmap_unlock(mapping)`, `flush_icache_range(start, end)`, `flush_cache_vmap(start,
end)`, `flush_cache_vmap_early(start, end)`, `flush_cache_vunmap(start, end)`,
`copy_to_user_page(vma, page, vaddr, dst, src, len)`, `copy_from_user_page(vma, page, vaddr, dst,
src, len)`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/ckmmu.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/ckmmu.h

## Purpose

defines C-SKY MMU/TLB register constants and helper macros for ABI-specific page-table and TLB
management for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 139 lines, 2157 bytes. Includes: `abi/reg_ops.h`, `asm/barrier.h`. Functions:
`read_mmu_index`, `write_mmu_index`, `read_mmu_entrylo0`, `read_mmu_entrylo1`, `write_mmu_pagemask`,
`read_mmu_entryhi`, `write_mmu_entryhi`, `read_mmu_msa0`, `write_mmu_msa0`, `read_mmu_msa1`,
`write_mmu_msa1`, `tlb_probe`, `tlb_read`, `tlb_invalid_all`, `local_tlb_invalid_all`,
`tlb_invalid_indexed`, `setup_pgd`. Key macros/defines: `__ASM_CSKY_CKMMUV2_H`, `NOP32`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/ckmmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/elf.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/elf.h

## Purpose

defines ABI-specific ELF flags, register constants, and process personality details for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 43 lines, 1321 bytes. Key macros/defines: `__ABI_CSKY_ELF_H`,
`ELF_CORE_COPY_REGS(pr_reg, regs)`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/entry.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/entry.h

## Purpose

defines low-level ABI entry/exit, register save, restore, and trap frame assembly macros for C-SKY
ABI v2

## Important APIs, Types, and Functions

Source read size: 314 lines, 4885 bytes. Includes: `asm/setup.h`, `abi/regdef.h`. Key
macros/defines: `__ASM_CSKY_ENTRY_H`, `LSAVE_PC`, `LSAVE_PSR`, `LSAVE_A0`, `LSAVE_A1`, `LSAVE_A2`,
`LSAVE_A3`, `LSAVE_A4`, `LSAVE_A5`, `KSPTOUSP`, `USPTOKSP`, `usp`, `MSA_SET`, `MSA_CLR`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/fpu.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/fpu.h

## Purpose

defines ABI v2 floating-point state structures and FPU status/control bit masks for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 66 lines, 1585 bytes. Includes: `asm/sigcontext.h`, `asm/ptrace.h`. Functions:
`init_fpu`. Key macros/defines: `__ASM_CSKY_FPU_H`, `FPE_ILLE`, `FPE_FEC`, `FPE_IDC`, `FPE_IXC`,
`FPE_UFC`, `FPE_OFC`, `FPE_DZC`, `FPE_IOC`, `FPE_REGULAR_EXCEPTION`, `IDE_STAT`, `IXE_STAT`,
`UFE_STAT`, `OFE_STAT`, `DZE_STAT`, `IOE_STAT`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/page.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/page.h

## Purpose

defines ABI-specific page constants and address translation helpers for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 6 lines, 167 bytes. Functions: `copy_user_page`. Local structs: `page`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/pgtable-bits.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/pgtable-bits.h

## Purpose

defines page-table bit assignments, cacheability encodings, swap encodings, and protection bits for
C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 53 lines, 1556 bytes. Key macros/defines: `__ASM_CSKY_PGTABLE_BITS_H`,
`_PAGE_ACCESSED`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_PRESENT`, `_PAGE_MODIFIED`,
`_PAGE_SWP_EXCLUSIVE`, `_PAGE_GLOBAL`, `_PAGE_VALID`, `_PAGE_DIRTY`, `_PAGE_SO`, `_PAGE_BUF`,
`_PAGE_CACHE`, `_CACHE_MASK`, `_CACHE_CACHED`, `_CACHE_UNCACHED`, `_PAGE_PROT_NONE`,
`__swp_type(x)`; plus 2 more.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/pgtable-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/reg_ops.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/reg_ops.h

## Purpose

provides inline helpers or macros for reading and writing C-SKY control registers for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 16 lines, 282 bytes. Includes: `asm/reg_ops.h`. Functions: `mfcr_hint`,
`mfcr_ccr2`. Key macros/defines: `__ABI_REG_OPS_H`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/reg_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/regdef.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/regdef.h

## Purpose

names C-SKY architectural registers for assembly and inline assembly consumers for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 31 lines, 600 bytes. Key macros/defines: `__ASM_CSKY_REGDEF_H`, `syscallid`,
`regs_syscallid(regs)`, `regs_fp(regs)`, `DEFAULT_PSR_VALUE`, `SYSTRACE_SAVENUM`, `TRAP0_SIZE`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/regdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/string.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/string.h

## Purpose

selects ABI-optimized string routine declarations or aliases for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 27 lines, 699 bytes. Key macros/defines: `__ABI_CSKY_STRING_H`,
`__HAVE_ARCH_MEMCMP`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE`, `__HAVE_ARCH_MEMSET`,
`__HAVE_ARCH_STRCMP`, `__HAVE_ARCH_STRCPY`, `__HAVE_ARCH_STRLEN`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/switch_context.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/switch_context.h

## Purpose

defines ABI-specific context switch save/restore contracts for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 31 lines, 585 bytes. Key macros/defines: `__ABI_CSKY_PTRACE_H`. Local structs:
`switch_stack`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/switch_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/vdso.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/vdso.h

## Purpose

declares ABI-specific VDSO data and mapping details for C-SKY ABI v2

## Important APIs, Types, and Functions

Source read size: 9 lines, 184 bytes. Key macros/defines: `__ABI_CSKY_VDSO_H`, `SET_SYSCALL_ID`.

## Control Flow and Behavior

the header is selected through the architecture include path and supplies the ABI-specific side of
otherwise common C-SKY kernel interfaces

## State and Persistence

state is compile-time definitions; entry, MMU, cache, FPU, and register helpers can directly affect
runtime CPU state when expanded

## Dependencies and Integration Points

integrates with arch/csky/include/asm wrappers, low-level assembly, MM, signal/ELF, cacheflush, and
context-switch code

## Risks and Test Signals

ABI drift between v1 and v2 breaks register frames, page tables, or user-visible behavior; ABI-
specific builds and boot/runtime smoke tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/inc/abi/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/mcount.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/mcount.S

## Purpose

implements the C-SKY ABI v2 optimized `mcount` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 211 lines, 3565 bytes. Includes: `linux/linkage.h`, `asm/ftrace.h`, `abi/entry.h`,
`asm/asm-offsets.h`. Assembly/global entries: `ftrace_stub`, `_mcount`, `ftrace_caller`,
`ftrace_call`, `ftrace_graph_call`, `ftrace_graph_caller`, `return_to_handler`,
`ftrace_regs_caller`, `ftrace_regs_call`, `ftrace_graph_regs_call`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memcmp.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/memcmp.S

## Purpose

implements the C-SKY ABI v2 optimized `memcmp` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 152 lines, 2929 bytes. Includes: `linux/linkage.h`, `sysdep.h`. Assembly/global
entries: `memcmp`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/memcpy.S

## Purpose

implements the C-SKY ABI v2 optimized `memcpy` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 104 lines, 1945 bytes. Includes: `linux/linkage.h`, `sysdep.h`. Assembly/global
entries: `__memcpy`, `memcpy`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memmove.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/memmove.S

## Purpose

implements the C-SKY ABI v2 optimized `memmove` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 104 lines, 2017 bytes. Includes: `linux/linkage.h`, `sysdep.h`. Assembly/global
entries: `__memmove`, `memmove`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memmove.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memset.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/memset.S

## Purpose

implements the C-SKY ABI v2 optimized `memset` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 83 lines, 1705 bytes. Includes: `linux/linkage.h`, `sysdep.h`. Assembly/global
entries: `__memset`, `memset`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strcmp.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/strcmp.S

## Purpose

implements the C-SKY ABI v2 optimized `strcmp` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 168 lines, 2334 bytes. Includes: `linux/linkage.h`, `sysdep.h`. Assembly/global
entries: `strcmp`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strcpy.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/strcpy.S

## Purpose

implements the C-SKY ABI v2 optimized `strcpy` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 123 lines, 1498 bytes. Includes: `linux/linkage.h`, `sysdep.h`. Assembly/global
entries: `strcpy`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strksyms.c -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/strksyms.c

## Purpose

exports C-SKY ABI v2 optimized string/memory symbols for modules

## Important APIs, Types, and Functions

Source read size: 14 lines, 342 bytes. Includes: `linux/module.h`. Exported symbols: `memcpy`,
`memset`, `memmove`, `memcmp`, `strcmp`, `strcpy`, `strlen`.

## Control Flow and Behavior

EXPORT_SYMBOL entries make architecture string routines available outside vmlinux

## State and Persistence

persistent state is the module symbol table generated at build/link time

## Dependencies and Integration Points

integrates with loadable modules and optimized assembly string implementations

## Risks and Test Signals

missing exports break module linking; module build/load tests are the signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strlen.S -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/strlen.S

## Purpose

implements the C-SKY ABI v2 optimized `strlen` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 97 lines, 1481 bytes. Includes: `linux/linkage.h`, `sysdep.h`. Assembly/global
entries: `strlen`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/strlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/sysdep.h -->
# sources/distributed-fs/ceph-client/arch/csky/abiv2/sysdep.h

## Purpose

provides assembly support macros used by C-SKY ABI v2 low-level string and tracing routines

## Important APIs, Types, and Functions

Source read size: 29 lines, 369 bytes. Key macros/defines: `__SYSDEP_H`, `LABLE_ALIGN`,
`PRE_BNEZAD(R)`, `BNEZAD(R, L)`.

## Control Flow and Behavior

macros define alignment, entry, register, and conditional assembly conveniences shared by nearby .S
files

## State and Persistence

state is compile-time assembly expansion only

## Dependencies and Integration Points

integrates with ABI v2 hand-written assembly sources

## Risks and Test Signals

macro changes can alter every optimized routine; assembling all ABI v2 .S files and lib/string tests
are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/abiv2/sysdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/boot/Makefile

## Purpose

builds C-SKY boot images and delegates devicetree blob generation

## Important APIs, Types, and Functions

Source read size: 24 lines, 674 bytes.

## Control Flow and Behavior

rules create Image/vmlinuz-style targets and wire install/clean behavior into the architecture build

## State and Persistence

state is generated boot artifacts

## Dependencies and Integration Points

integrates vmlinux, compression, dtb, and install targets for C-SKY

## Risks and Test Signals

incorrect target dependencies produce stale or missing boot images; make Image, make dtbs, and
install tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/boot/dts/Makefile

## Purpose

declares C-SKY devicetree build participation for board dtb files

## Important APIs, Types, and Functions

Source read size: 2 lines, 106 bytes. Build selections: `dtb-y -> $(patsubst $(src)/%.dts,%.dtb,
$(wildcard $(src)/*.dts))`.

## Control Flow and Behavior

the Makefile is intentionally minimal and lets parent boot rules discover dtb targets

## State and Persistence

there is no runtime state in the file

## Dependencies and Integration Points

integrates with arch/csky/boot/Makefile and generic dtbs targets

## Risks and Test Signals

missing dtb entries prevent board image generation; dtbs target builds are the signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/Kbuild

## Purpose

selects generated and generic C-SKY asm headers exported through Kbuild

## Important APIs, Types, and Functions

Source read size: 14 lines, 346 bytes. Build selections: `syscall-y -> syscall_table_32.h`,
`generic-y -> asm-offsets.h`, `generic-y -> extable.h`, `generic-y -> kvm_para.h`, `generic-y ->
mcs_spinlock.h`, `generic-y -> qrwlock.h`, `generic-y -> qrwlock_types.h`, `generic-y ->
qspinlock.h`, `generic-y -> parport.h`, `generic-y -> user.h`, `generic-y -> vmlinux.lds.h`,
`generic-y -> text-patching.h`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/addrspace.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/addrspace.h

## Purpose

defines C-SKY virtual/physical address-space segment conversion helpers

## Important APIs, Types, and Functions

Source read size: 9 lines, 231 bytes. Key macros/defines: `__ASM_CSKY_ADDRSPACE_H`, `KSEG0`,
`KSEG0ADDR(a)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/addrspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/asid.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/asid.h

## Purpose

declares ASID allocator state and inline context rollover checks

## Important APIs, Types, and Functions

Source read size: 78 lines, 2440 bytes. Includes: `linux/atomic.h`, `linux/compiler.h`,
`linux/cpumask.h`, `linux/percpu.h`, `linux/spinlock.h`. Functions: `asid_check_context`. Key
macros/defines: `__ASM_ASM_ASID_H`, `NUM_ASIDS(info)`, `NUM_CTXT_ASIDS(info)`, `active_asid(info,
cpu)`. Local structs: `asid_info`, `mm_struct`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/asid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/atomic.h

## Purpose

implements C-SKY atomic_t/atomic64_t operations and memory-order variants

## Important APIs, Types, and Functions

Source read size: 202 lines, 4363 bytes. Includes: `asm-generic/atomic64.h`, `asm/cmpxchg.h`,
`asm/barrier.h`, `asm-generic/atomic.h`. Functions: `arch_atomic_read`, `arch_atomic_set`,
`arch_atomic_fetch_add_unless`, `arch_atomic_inc_unless_negative`,
`arch_atomic_dec_unless_positive`, `arch_atomic_dec_if_positive`. Key macros/defines:
`__ASM_CSKY_ATOMIC_H`, `__atomic_acquire_fence()`, `__atomic_release_fence()`, `ATOMIC_OP(op)`,
`ATOMIC_FETCH_OP(op)`, `ATOMIC_OP_RETURN(op, c_op)`, `ATOMIC_OPS(op, c_op)`,
`arch_atomic_fetch_add_relaxed`, `arch_atomic_fetch_sub_relaxed`, `arch_atomic_add_return_relaxed`,
`arch_atomic_sub_return_relaxed`, `ATOMIC_OPS(op)`, `arch_atomic_fetch_and_relaxed`,
`arch_atomic_fetch_or_relaxed`, `arch_atomic_fetch_xor_relaxed`, `arch_atomic_fetch_add_unless`,
`arch_atomic_inc_unless_negative`, `arch_atomic_dec_unless_positive`; plus 1 more.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/barrier.h

## Purpose

defines C-SKY memory barrier, acquire/release, and SMP ordering primitives

## Important APIs, Types, and Functions

Source read size: 88 lines, 2597 bytes. Includes: `asm-generic/barrier.h`. Key macros/defines:
`__ASM_CSKY_BARRIER_H`, `nop()`, `FULL_FENCE`, `ACQUIRE_FENCE`, `RELEASE_FENCE`, `__bar_brw()`,
`__bar_br()`, `__bar_bw()`, `__bar_arw()`, `__bar_ar()`, `__bar_aw()`, `__bar_brwarw()`,
`__bar_brarw()`, `__bar_bwarw()`, `__bar_brwar()`, `__bar_brwaw()`, `__bar_brar()`, `__bar_bwaw()`;
plus 7 more.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/bitops.h

## Purpose

provides architecture bit operations and delegates generic helpers where appropriate

## Important APIs, Types, and Functions

Source read size: 79 lines, 1406 bytes. Includes: `linux/compiler.h`, `asm/barrier.h`, `asm-
generic/bitops/ffz.h`, `asm-generic/bitops/fls64.h`, `asm-generic/bitops/sched.h`, `asm-
generic/bitops/hweight.h`, `asm-generic/bitops/lock.h`, `asm-generic/bitops/atomic.h`, `asm-
generic/bitops/non-atomic.h`, `asm-generic/bitops/le.h`; plus 1 more. Functions: `ffs`, `__ffs`,
`fls`, `__fls`. Key macros/defines: `__ASM_CSKY_BITOPS_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/bug.h

## Purpose

defines BUG/WARN trap encoding details for C-SKY

## Important APIs, Types, and Functions

Source read size: 28 lines, 565 bytes. Includes: `linux/compiler.h`, `linux/const.h`,
`linux/types.h`, `asm-generic/bug.h`. Key macros/defines: `__ASM_CSKY_BUG_H`, `BUG()`,
`HAVE_ARCH_BUG`. Local structs: `pt_regs`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/cache.h

## Purpose

declares cache-line sizing and alignment constants

## Important APIs, Types, and Functions

Source read size: 32 lines, 862 bytes. Key macros/defines: `__ASM_CSKY_CACHE_H`, `L1_CACHE_SHIFT`,
`L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/cacheflush.h

## Purpose

routes generic cacheflush interfaces to ABI-specific implementations

## Important APIs, Types, and Functions

Source read size: 9 lines, 193 bytes. Includes: `linux/mm.h`, `abi/cacheflush.h`. Key
macros/defines: `__ASM_CSKY_CACHEFLUSH_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cachetype.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/cachetype.h

## Purpose

exposes cache type helpers used by cache and MMU setup code

## Important APIs, Types, and Functions

Source read size: 9 lines, 174 bytes. Includes: `linux/types.h`. Key macros/defines:
`__ASM_CSKY_CACHETYPE_H`, `cpu_dcache_is_aliasing()`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/checksum.h

## Purpose

declares or selects checksum helpers for networking and generic checksum code

## Important APIs, Types, and Functions

Source read size: 49 lines, 944 bytes. Includes: `linux/in6.h`, `asm/byteorder.h`, `asm-
generic/checksum.h`. Functions: `csum_fold`, `csum_tcpudp_nofold`. Key macros/defines:
`__ASM_CSKY_CHECKSUM_H`, `csum_fold`, `csum_tcpudp_nofold`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/clocksource.h

## Purpose

declares clocksource access hooks for C-SKY timekeeping

## Important APIs, Types, and Functions

Source read size: 8 lines, 159 bytes. Includes: `asm/vdso/clocksource.h`. Key macros/defines:
`__ASM_VDSO_CSKY_CLOCKSOURCE_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/cmpxchg.h

## Purpose

implements cmpxchg/xchg helpers and atomic exchange contracts

## Important APIs, Types, and Functions

Source read size: 165 lines, 4256 bytes. Includes: `linux/bug.h`, `asm/barrier.h`, `linux/cmpxchg-
emu.h`, `asm-generic/cmpxchg.h`. Key macros/defines: `__ASM_CSKY_CMPXCHG_H`, `__xchg_relaxed(new,
ptr, size)`, `arch_xchg_relaxed(ptr, x)`, `__cmpxchg_relaxed(ptr, old, new, size)`,
`arch_cmpxchg_relaxed(ptr, o, n)`, `__cmpxchg_acquire(ptr, old, new, size)`,
`arch_cmpxchg_acquire(ptr, o, n)`, `__cmpxchg(ptr, old, new, size)`, `arch_cmpxchg(ptr, o, n)`,
`arch_cmpxchg_local(ptr, o, n)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/elf.h

## Purpose

assembles C-SKY ELF core dump, loader, and HWCAP behavior from ABI-specific definitions

## Important APIs, Types, and Functions

Source read size: 90 lines, 2723 bytes. Includes: `asm/ptrace.h`, `abi/regdef.h`, `abi/elf.h`. Key
macros/defines: `__ASM_CSKY_ELF_H`, `ELF_ARCH`, `EM_CSKY_OLD`, `R_CSKY_NONE`, `R_CSKY_32`,
`R_CSKY_PCIMM8BY4`, `R_CSKY_PCIMM11BY2`, `R_CSKY_PCIMM4BY2`, `R_CSKY_PC32`,
`R_CSKY_PCRELJSR_IMM11BY2`, `R_CSKY_GNU_VTINHERIT`, `R_CSKY_GNU_VTENTRY`, `R_CSKY_RELATIVE`,
`R_CSKY_COPY`, `R_CSKY_GLOB_DAT`, `R_CSKY_JUMP_SLOT`, `R_CSKY_ADDR_HI16`, `R_CSKY_ADDR_LO16`; plus
13 more. Local structs: `task_struct`, `linux_binprm`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/fixmap.h

## Purpose

defines fixed virtual mapping slots and address bounds

## Important APIs, Types, and Functions

Source read size: 33 lines, 747 bytes. Includes: `asm/page.h`, `asm/memory.h`, `linux/threads.h`,
`asm/kmap_size.h`, `asm-generic/fixmap.h`. Key macros/defines: `__ASM_CSKY_FIXMAP_H`,
`FIXADDR_SIZE`, `FIXADDR_START`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/ftrace.h

## Purpose

defines ftrace call-site and graph tracing architecture hooks

## Important APIs, Types, and Functions

Source read size: 32 lines, 631 bytes. Functions: `ftrace_call_adjust`. Key macros/defines:
`__ASM_CSKY_FTRACE_H`, `MCOUNT_INSN_SIZE`, `HAVE_FUNCTION_GRAPH_FP_TEST`,
`ARCH_SUPPORTS_FTRACE_OPS`, `MCOUNT_ADDR`. Local structs: `dyn_arch_ftrace`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/futex.h

## Purpose

implements futex atomic operations for user memory

## Important APIs, Types, and Functions

Source read size: 121 lines, 2605 bytes. Includes: `asm-generic/futex.h`, `linux/atomic.h`,
`linux/futex.h`, `linux/uaccess.h`, `linux/errno.h`. Functions: `arch_futex_atomic_op_inuser`,
`futex_atomic_cmpxchg_inatomic`. Key macros/defines: `__ASM_CSKY_FUTEX_H`, `__futex_atomic_op(insn,
ret, oldval, uaddr, oparg)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/highmem.h

## Purpose

defines highmem kmap helpers and address limits

## Important APIs, Types, and Functions

Source read size: 44 lines, 1114 bytes. Includes: `linux/init.h`, `linux/interrupt.h`,
`linux/uaccess.h`, `asm/kmap_size.h`, `asm/cache.h`. Key macros/defines: `__ASM_CSKY_HIGHMEM_H`,
`HIGHMEM_DEBUG`, `LAST_PKMAP`, `LAST_PKMAP_MASK`, `PKMAP_NR(virt)`, `PKMAP_ADDR(nr)`,
`ARCH_HAS_KMAP_FLUSH_TLB`, `flush_cache_kmaps()`, `arch_kmap_local_post_map(vaddr, pteval)`,
`arch_kmap_local_post_unmap(vaddr)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/io.h

## Purpose

defines MMIO, port I/O, and memory mapping helpers

## Important APIs, Types, and Functions

Source read size: 43 lines, 1367 bytes. Includes: `linux/pgtable.h`, `linux/types.h`, `asm-
generic/io.h`. Key macros/defines: `__ASM_CSKY_IO_H`, `readb(c)`, `readw(c)`, `readl(c)`,
`writeb(v,c)`, `writew(v,c)`, `writel(v,c)`, `ioremap_wc(addr, size)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/irq_work.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/irq_work.h

## Purpose

declares irq_work availability for C-SKY

## Important APIs, Types, and Functions

Source read size: 11 lines, 208 bytes. Functions: `arch_irq_work_has_interrupt`. Key macros/defines:
`__ASM_CSKY_IRQ_WORK_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/irqflags.h

## Purpose

implements local interrupt enable/disable/save/restore primitives

## Important APIs, Types, and Functions

Source read size: 49 lines, 1132 bytes. Includes: `abi/reg_ops.h`, `asm-generic/irqflags.h`.
Functions: `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_irq_disable`,
`arch_local_save_flags`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`. Key macros/defines:
`__ASM_CSKY_IRQFLAGS_H`, `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_irq_disable`,
`arch_local_save_flags`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/jump_label.h

## Purpose

defines static-key patching instruction details

## Important APIs, Types, and Functions

Source read size: 52 lines, 1193 bytes. Includes: `linux/types.h`. Functions: `arch_static_branch`,
`arch_static_branch_jump`. Key macros/defines: `__ASM_CSKY_JUMP_LABEL_H`, `JUMP_LABEL_NOP_SIZE`,
`arch_jump_label_transform_static`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/kprobes.h

## Purpose

declares kprobe instruction slots, breakpoint opcodes, and arch hooks

## Important APIs, Types, and Functions

Source read size: 48 lines, 1158 bytes. Includes: `asm-generic/kprobes.h`, `linux/types.h`,
`linux/ptrace.h`, `linux/percpu.h`, `asm/probes.h`. Key macros/defines: `__ASM_CSKY_KPROBES_H`,
`__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot(p)`, `kretprobe_blacklist_size`.
Local structs: `prev_kprobe`, `kprobe`, `kprobe_step_ctx`, `kprobe_ctlblk`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/memory.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/memory.h

## Purpose

defines kernel/user virtual memory layout constants

## Important APIs, Types, and Functions

Source read size: 25 lines, 657 bytes. Includes: `linux/compiler.h`, `linux/const.h`,
`linux/types.h`, `linux/sizes.h`. Key macros/defines: `__ASM_CSKY_MEMORY_H`, `FIXADDR_TOP`,
`PKMAP_BASE`, `VMALLOC_START`, `VMALLOC_END`, `TCM_NR_PAGES`, `FIXADDR_TCM`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/mmu.h

## Purpose

declares the C-SKY mm_context type

## Important APIs, Types, and Functions

Source read size: 12 lines, 216 bytes. Key macros/defines: `__ASM_CSKY_MMU_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/mmu_context.h

## Purpose

implements MMU context activation, ASID switching, and lazy TLB hooks

## Important APIs, Types, and Functions

Source read size: 39 lines, 959 bytes. Includes: `asm-generic/mm_hooks.h`, `asm/setup.h`,
`asm/page.h`, `asm/cacheflush.h`, `asm/tlbflush.h`, `linux/errno.h`, `linux/sched.h`, `abi/ckmmu.h`,
`asm-generic/mmu_context.h`. Functions: `switch_mm`. Key macros/defines: `__ASM_CSKY_MMU_CONTEXT_H`,
`ASID_MASK`, `cpu_asid(mm)`, `init_new_context(tsk,mm)`. Local structs: `task_struct`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/page.h

## Purpose

defines C-SKY page, pfn, virt/phys, clear/copy page, and memory validity helpers

## Important APIs, Types, and Functions

Source read size: 88 lines, 2395 bytes. Includes: `asm/setup.h`, `asm/cache.h`, `linux/const.h`,
`vdso/page.h`, `linux/pfn.h`, `abi/page.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`.
Functions: `virt_to_pfn`. Key macros/defines: `__ASM_CSKY_PAGE_H`, `THREAD_SIZE`, `THREAD_MASK`,
`THREAD_SHIFT`, `PAGE_OFFSET`, `SSEG_SIZE`, `LOWMEM_LIMIT`, `PHYS_OFFSET_OFFSET`,
`virt_addr_valid(kaddr)`, `clear_page(page)`, `copy_page(to, from)`, `pte_val(x)`, `pgd_val(x)`,
`pgprot_val(x)`, `ptep_buddy(x)`, `__pte(x)`, `__pgd(x)`, `__pgprot(x)`; plus 7 more. Local structs:
`page`, `vm_area_struct`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/pci.h

## Purpose

declares C-SKY PCI integration defaults

## Important APIs, Types, and Functions

Source read size: 15 lines, 277 bytes. Includes: `linux/types.h`, `linux/slab.h`, `linux/dma-
mapping.h`, `asm/io.h`, `asm-generic/pci.h`. Key macros/defines: `__ASM_CSKY_PCI_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/perf_event.h

## Purpose

declares perf architecture support limits

## Important APIs, Types, and Functions

Source read size: 14 lines, 359 bytes. Includes: `abi/regdef.h`. Key macros/defines:
`__ASM_CSKY_PERF_EVENT_H`, `perf_arch_fetch_caller_regs(regs, __ip)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/pgalloc.h

## Purpose

implements page-table page allocation and freeing helpers

## Important APIs, Types, and Functions

Source read size: 71 lines, 1568 bytes. Includes: `linux/highmem.h`, `linux/mm.h`, `linux/sched.h`,
`asm-generic/pgalloc.h`. Functions: `pmd_populate_kernel`, `pmd_populate`. Key macros/defines:
`__ASM_CSKY_PGALLOC_H`, `__HAVE_ARCH_PTE_ALLOC_ONE_KERNEL`, `__pte_free_tlb(tlb, pte, address)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/pgtable.h

## Purpose

defines C-SKY page table layout, PTE/PMD helpers, protection macros, and cacheability
transformations

## Important APIs, Types, and Functions

Source read size: 263 lines, 6420 bytes. Includes: `asm/fixmap.h`, `asm/memory.h`,
`asm/addrspace.h`, `abi/pgtable-bits.h`, `asm-generic/pgtable-nopmd.h`. Functions: `set_pte`,
`set_pmd`, `pmd_none`, `pmd_present`, `pmd_clear`, `pte_present`, `pte_write`, `pte_dirty`,
`pte_young`, `pte_wrprotect`, `pte_mkclean`, `pte_mkold`, `pte_mkwrite_novma`, `pte_mkdirty`,
`pte_mkyoung`, `pte_swp_exclusive`, `pte_swp_mkexclusive`, `pte_swp_clear_exclusive`; plus 3 more.
Key macros/defines: `__ASM_CSKY_PGTABLE_H`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`,
`USER_PTRS_PER_PGD`, `PTRS_PER_PGD`, `PTRS_PER_PMD`, `PTRS_PER_PTE`, `pte_ERROR(e)`, `pgd_ERROR(e)`,
`PFN_PTE_SHIFT`, `pmd_pfn(pmd)`, `pmd_page(pmd)`, `pte_clear(mm, addr, ptep)`, `pte_none(pte)`,
`pte_present(pte)`, `pte_pfn(x)`, `pfn_pte(pfn, prot)`; plus 19 more. Local structs: `file`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/probes.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/probes.h

## Purpose

declares instruction decode helpers shared by kprobes/uprobes

## Important APIs, Types, and Functions

Source read size: 24 lines, 554 bytes. Key macros/defines: `__ASM_CSKY_PROBES_H`. Local structs:
`arch_probe_insn`, `arch_specific_insn`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/probes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/processor.h

## Purpose

defines thread_struct, CPU idle, process start, and task register helpers

## Important APIs, Types, and Functions

Source read size: 87 lines, 2322 bytes. Includes: `linux/bitops.h`, `linux/cache.h`, `asm/ptrace.h`,
`asm/current.h`, `abi/reg_ops.h`, `abi/regdef.h`, `abi/switch_context.h`, `abi/fpu.h`. Key
macros/defines: `__ASM_CSKY_PROCESSOR_H`, `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`,
`TASK_UNMAPPED_BASE`, `INIT_THREAD`, `start_thread(_regs, _pc, _usp)`, `prepare_to_copy(tsk)`,
`KSTK_EIP(tsk)`, `KSTK_ESP(tsk)`, `task_pt_regs(p)`, `cpu_relax()`. Local structs: `cpuinfo_csky`,
`thread_struct`, `user_fp`, `task_struct`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/ptrace.h

## Purpose

defines kernel pt_regs accessors and register helpers

## Important APIs, Types, and Functions

Source read size: 102 lines, 2594 bytes. Includes: `uapi/asm/ptrace.h`, `asm/traps.h`,
`linux/types.h`, `linux/compiler.h`. Functions: `instruction_pointer_set`, `in_syscall`,
`forget_syscall`, `regs_return_value`, `regs_set_return_value`, `kernel_stack_pointer`,
`frame_pointer`, `frame_pointer_set`, `regs_get_register`. Key macros/defines:
`__ASM_CSKY_PTRACE_H`, `PS_S`, `USR_BKPT`, `arch_has_single_step()`, `current_pt_regs()`,
`user_stack_pointer(regs)`, `user_mode(regs)`, `instruction_pointer(regs)`, `profile_pc(regs)`,
`trap_no(regs)`, `MAX_REG_OFFSET`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/reg_ops.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/reg_ops.h

## Purpose

includes the selected ABI control-register helper implementation

## Important APIs, Types, and Functions

Source read size: 26 lines, 382 bytes. Key macros/defines: `__ASM_REGS_OPS_H`, `mfcr(reg)`,
`mtcr(reg, val)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/reg_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/seccomp.h

## Purpose

selects seccomp syscall architecture data

## Important APIs, Types, and Functions

Source read size: 11 lines, 283 bytes. Includes: `asm-generic/seccomp.h`. Key macros/defines:
`_ASM_SECCOMP_H`, `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_NATIVE_NAME`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/sections.h

## Purpose

declares architecture section symbols

## Important APIs, Types, and Functions

Source read size: 13 lines, 290 bytes. Includes: `asm-generic/sections.h`. Key macros/defines:
`__ASM_SECTIONS_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/shmparam.h

## Purpose

defines shared-memory alignment policy

## Important APIs, Types, and Functions

Source read size: 10 lines, 197 bytes. Key macros/defines: `__ASM_CSKY_SHMPARAM_H`, `SHMLBA`,
`__ARCH_FORCE_SHMLBA`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/smp.h

## Purpose

declares SMP boot, IPI, and CPU topology hooks

## Important APIs, Types, and Functions

Source read size: 30 lines, 643 bytes. Includes: `linux/cpumask.h`, `linux/irqreturn.h`,
`linux/threads.h`. Functions: `__cpu_die`. Key macros/defines: `__ASM_CSKY_SMP_H`,
`raw_smp_processor_id()`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/spinlock.h

## Purpose

selects C-SKY spinlock barrier behavior

## Important APIs, Types, and Functions

Source read size: 12 lines, 267 bytes. Includes: `asm/qspinlock.h`, `asm/qrwlock.h`. Key
macros/defines: `__ASM_CSKY_SPINLOCK_H`, `smp_mb__after_spinlock()`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/spinlock_types.h

## Purpose

defines spinlock raw type aliases

## Important APIs, Types, and Functions

Source read size: 9 lines, 235 bytes. Includes: `asm-generic/qspinlock_types.h`, `asm-
generic/qrwlock_types.h`. Key macros/defines: `__ASM_CSKY_SPINLOCK_TYPES_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/stackprotector.h

## Purpose

defines stack canary initialization support

## Important APIs, Types, and Functions

Source read size: 21 lines, 526 bytes. Functions: `boot_init_stack_canary`. Key macros/defines:
`_ASM_STACKPROTECTOR_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/string.h

## Purpose

selects architecture string routines and generic fallbacks

## Important APIs, Types, and Functions

Source read size: 12 lines, 234 bytes. Includes: `linux/types.h`, `linux/compiler.h`,
`abi/string.h`. Key macros/defines: `_CSKY_STRING_MM_H_`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/switch_to.h

## Purpose

declares context-switch entry points and switch_to wrapper

## Important APIs, Types, and Functions

Source read size: 35 lines, 923 bytes. Includes: `linux/thread_info.h`, `abi/fpu.h`. Functions:
`__switch_to_fpu`. Key macros/defines: `__ASM_CSKY_SWITCH_TO_H`, `switch_to(prev, next, last)`.
Local structs: `task_struct`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/syscall.h

## Purpose

defines syscall argument, number, rollback, and return-value accessors

## Important APIs, Types, and Functions

Source read size: 81 lines, 1697 bytes. Includes: `linux/sched.h`, `linux/err.h`, `abi/regdef.h`,
`uapi/linux/audit.h`. Functions: `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`,
`syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`,
`syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`. Key macros/defines:
`__ASM_SYSCALL_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/syscalls.h

## Purpose

declares architecture-specific syscall entry points

## Important APIs, Types, and Functions

Source read size: 14 lines, 351 bytes. Includes: `asm-generic/syscalls.h`. Key macros/defines:
`__ASM_CSKY_SYSCALLS_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/tcm.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/tcm.h

## Purpose

declares tightly-coupled-memory section and allocator helpers

## Important APIs, Types, and Functions

Source read size: 24 lines, 665 bytes. Includes: `linux/compiler.h`. Key macros/defines:
`__ASM_CSKY_TCM_H`, `__tcmdata`, `__tcmconst`, `__tcmfunc`, `__tcmlocalfunc`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/tcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/thread_info.h

## Purpose

defines C-SKY thread_info flags, layout, and current-thread access

## Important APIs, Types, and Functions

Source read size: 89 lines, 2808 bytes. Includes: `asm/types.h`, `asm/page.h`, `asm/processor.h`,
`abi/switch_context.h`. Key macros/defines: `_ASM_CSKY_THREAD_INFO_H`, `INIT_THREAD_INFO(tsk)`,
`THREAD_SIZE_ORDER`, `thread_saved_fp(tsk)`, `thread_saved_sp(tsk)`, `thread_saved_lr(tsk)`,
`TIF_SIGPENDING`, `TIF_NOTIFY_RESUME`, `TIF_NEED_RESCHED`, `TIF_UPROBE`, `TIF_SYSCALL_TRACE`,
`TIF_SYSCALL_TRACEPOINT`, `TIF_SYSCALL_AUDIT`, `TIF_NOTIFY_SIGNAL`, `TIF_POLLING_NRFLAG`,
`TIF_MEMDIE`, `TIF_RESTORE_SIGMASK`, `TIF_SECCOMP`; plus 14 more. Local structs: `thread_info`,
`task_struct`, `restart_block`, `pt_regs`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/tlb.h

## Purpose

connects C-SKY to generic TLB gather/free logic

## Important APIs, Types, and Functions

Source read size: 9 lines, 179 bytes. Includes: `asm/cacheflush.h`, `asm-generic/tlb.h`. Key
macros/defines: `__ASM_CSKY_TLB_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/tlbflush.h

## Purpose

declares and implements TLB flush operations

## Important APIs, Types, and Functions

Source read size: 24 lines, 824 bytes. Key macros/defines: `__ASM_TLBFLUSH_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/traps.h

## Purpose

declares trap initialization and exception C handlers

## Important APIs, Types, and Functions

Source read size: 60 lines, 1447 bytes. Includes: `linux/linkage.h`. Key macros/defines:
`__ASM_CSKY_TRAPS_H`, `VEC_RESET`, `VEC_ALIGN`, `VEC_ACCESS`, `VEC_ZERODIV`, `VEC_ILLEGAL`,
`VEC_PRIV`, `VEC_TRACE`, `VEC_BREAKPOINT`, `VEC_UNRECOVER`, `VEC_SOFTRESET`, `VEC_AUTOVEC`,
`VEC_FAUTOVEC`, `VEC_HWACCEL`, `VEC_TLBMISS`, `VEC_TLBMODIFIED`, `VEC_TRAP0`, `VEC_TRAP1`; plus 7
more.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/uaccess.h

## Purpose

implements user memory access, copying, and exception-table helpers

## Important APIs, Types, and Functions

Source read size: 203 lines, 4980 bytes. Includes: `asm-generic/uaccess.h`. Functions:
`__put_user_fn`, `__get_user_fn`. Key macros/defines: `__ASM_CSKY_UACCESS_H`, `__put_user_asm_b(x,
ptr, err)`, `__put_user_asm_h(x, ptr, err)`, `__put_user_asm_w(x, ptr, err)`, `__put_user_asm_64(x,
ptr, err)`, `__put_user_fn`, `__get_user_asm_common(x, ptr, ins, err)`, `__get_user_asm_64(x, ptr,
err)`, `__get_user_fn`, `__clear_user`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/unistd.h

## Purpose

connects C-SKY syscall numbering to generic syscall headers

## Important APIs, Types, and Functions

Source read size: 8 lines, 164 bytes. Includes: `uapi/asm/unistd.h`. Key macros/defines:
`__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_CLONE`, `NR_syscalls`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/uprobes.h

## Purpose

defines uprobes breakpoint and instruction slot constants

## Important APIs, Types, and Functions

Source read size: 33 lines, 669 bytes. Includes: `asm/probes.h`. Key macros/defines:
`__ASM_CSKY_UPROBES_H`, `MAX_UINSN_BYTES`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`,
`UPROBE_XOL_SLOT_BYTES`. Local structs: `arch_uprobe_task`, `arch_uprobe`, `arch_probe_insn`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/vdso.h

## Purpose

declares C-SKY VDSO mapping and data helpers

## Important APIs, Types, and Functions

Source read size: 22 lines, 724 bytes. Includes: `linux/types.h`. Key macros/defines:
`__ASM_CSKY_VDSO_H`, `VDSO_SYMBOL(base, name)`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/asm/vmalloc.h

## Purpose

defines vmalloc address range policy

## Important APIs, Types, and Functions

Source read size: 4 lines, 90 bytes. Key macros/defines: `_ASM_CSKY_VMALLOC_H`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/Kbuild

## Purpose

declares C-SKY UAPI headers exported to userspace

## Important APIs, Types, and Functions

Source read size: 4 lines, 85 bytes. Build selections: `syscall-y -> unistd_32.h`, `generic-y ->
ucontext.h`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/byteorder.h

## Purpose

selects little-endian byte-order helpers for exported C-SKY headers

## Important APIs, Types, and Functions

Source read size: 8 lines, 207 bytes. Includes: `linux/byteorder/little_endian.h`. Key
macros/defines: `__ASM_CSKY_BYTEORDER_H`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/cachectl.h

## Purpose

defines cacheflush/cachectl syscall operation constants visible to userspace

## Important APIs, Types, and Functions

Source read size: 13 lines, 270 bytes. Key macros/defines: `__ASM_CSKY_CACHECTL_H`, `ICACHE`,
`DCACHE`, `BCACHE`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/cachectl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/perf_regs.h

## Purpose

enumerates C-SKY register IDs for perf sample register masks

## Important APIs, Types, and Functions

Source read size: 50 lines, 1115 bytes. Key macros/defines: `_ASM_CSKY_PERF_REGS_H`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/ptrace.h

## Purpose

defines user-visible register structures and ptrace constants

## Important APIs, Types, and Functions

Source read size: 51 lines, 839 bytes. Key macros/defines: `_CSKY_PTRACE_H`. Local structs:
`pt_regs`, `user_fp`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/sigcontext.h

## Purpose

defines the signal-frame machine context saved and restored by sigreturn

## Important APIs, Types, and Functions

Source read size: 13 lines, 271 bytes. Includes: `asm/ptrace.h`. Key macros/defines:
`__ASM_CSKY_SIGCONTEXT_H`. Local structs: `sigcontext`, `pt_regs`, `user_fp`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/unistd.h

## Purpose

selects generic syscall numbering and C-SKY syscall count exports

## Important APIs, Types, and Functions

Source read size: 6 lines, 153 bytes. Includes: `asm/unistd_32.h`. Key macros/defines:
`__NR_sync_file_range2`.

## Control Flow and Behavior

the file is consumed by userspace-visible kernel headers and must preserve numeric constants,
structure layout, and include order

## State and Persistence

there is no kernel runtime state, but compiled userspace and kernel UAPI copies persist these
definitions as ABI

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, libc, perf/ptrace/signal tooling, and syscall wrappers

## Risks and Test Signals

renumbering constants or changing layouts breaks existing binaries; headers_install, libc builds,
perf/ptrace, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/Makefile

## Purpose

builds objects or generated artifacts for `sources/distributed-fs/ceph-client/arch/csky/kernel`

## Important APIs, Types, and Functions

Source read size: 20 lines, 696 bytes. Build selections: `obj-y -> head.o entry.o atomic.o signal.o
traps.o irq.o time.o vdso.o vdso/`, `obj-y -> power.o syscall.o syscall_table.o setup.o`, `obj-y ->
process.o cpu-probe.o ptrace.o stacktrace.o`, `obj-y -> probes/`.

## Control Flow and Behavior

Kbuild variables select object files, subdirectories, generated headers, or boot targets

## State and Persistence

state is build output only

## Dependencies and Integration Points

integrates with parent Kbuild recursion and configuration symbols

## Risks and Test Signals

wrong dependencies or object lists cause missing code or stale generated artifacts; clean builds are
the signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/asm-offsets.c

## Purpose

generates assembler-visible offsets for C-SKY task, thread, pt_regs, signal, and ABI structures

## Important APIs, Types, and Functions

Source read size: 84 lines, 3971 bytes. Includes: `linux/sched.h`, `linux/kernel_stat.h`,
`linux/kbuild.h`, `abi/regdef.h`. Functions: `main`. Key macros/defines: `COMPILE_OFFSETS`.

## Control Flow and Behavior

DEFINE/OFFSET entries are compiled by Kbuild into asm-offsets.h for assembly files such as entry.S
and context-switch code

## State and Persistence

there is no runtime state; the generated header is build output that must match compiled C layouts

## Dependencies and Integration Points

integrates with Kbuild, ABI entry macros, signal frame code, and low-level assembly save/restore
paths

## Risks and Test Signals

layout drift breaks assembly at runtime; the offsets build step and any code using
pt_regs/thread_info are the validation signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/atomic.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/atomic.S

## Purpose

provides the C-SKY cmpxchg trap helper used where atomic compare/exchange must be performed from a
controlled exception context

## Important APIs, Types, and Functions

Source read size: 61 lines, 894 bytes. Includes: `linux/linkage.h`, `abi/entry.h`. Assembly/global
entries: `csky_cmpxchg`, `csky_cmpxchg_ldw`, `csky_cmpxchg_stw`.

## Control Flow and Behavior

csky_cmpxchg saves EPC/EPSR/USP, performs ldex/stex when available or exposes ldw/stw patch labels
for fallback handling, restores state, and returns through rte

## State and Persistence

state changes are limited to the memory word being conditionally exchanged and restored control
registers

## Dependencies and Integration Points

depends on ABI entry macros, CPU_HAS_LDSTEX, trap sizing, exception return semantics, and
atomic/cmpxchg callers

## Risks and Test Signals

exclusive-store retry logic and fallback labels must be exact; atomic API tests and SMP stress are
the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/atomic.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/cpu-probe.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/cpu-probe.c

## Purpose

detects C-SKY CPU identity and feature flags from processor registers during early CPU setup

## Important APIs, Types, and Functions

Source read size: 79 lines, 1709 bytes. Includes: `linux/of.h`, `linux/init.h`, `linux/seq_file.h`,
`linux/memblock.h`, `abi/reg_ops.h`. Functions: `percpu_print`, `c_show`, `c_stop`. Local structs:
`seq_file`.

## Control Flow and Behavior

the probe reads implementation/configuration registers, derives cache/MMU/FPU/DSP/ISA capabilities,
and publishes the result for feature-dependent arch code

## State and Persistence

persistent state is the probed CPU capability data used after boot

## Dependencies and Integration Points

depends on ABI register accessors, Kconfig CPU feature symbols, and early setup ordering

## Risks and Test Signals

bad detection enables unsupported instructions or cache/MMU paths; boot logs, feature-dependent
selftests, and CPU hotplug paths provide signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/cpu-probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/entry.S

## Purpose

implements C-SKY exception, syscall, trap, fork-return, work-pending, TLS, and interrupt return
assembly paths

## Important APIs, Types, and Functions

Source read size: 274 lines, 5019 bytes. Includes: `linux/linkage.h`, `abi/entry.h`, `abi/pgtable-
bits.h`, `asm/errno.h`, `asm/setup.h`, `asm/unistd.h`, `asm/asm-offsets.h`, `linux/threads.h`,
`asm/page.h`, `asm/thread_info.h`. Assembly/global entries: `csky_pagefault`, `csky_systemcall`,
`ret_from_kernel_thread`, `ret_from_fork`, `csky_trap`, `csky_get_tls`, `csky_irq`, `__switch_to`.

## Control Flow and Behavior

entries include csky_pagefault, csky_systemcall, ret_from_kernel_thread, ret_from_fork,
ret_from_exception, csky_trap, csky_get_tls, and interrupt/NMI-style save/restore flows built from
ABI SAVE_ALL/RESTORE_ALL macros

## State and Persistence

runtime state is the saved pt_regs frame on the kernel stack, thread_info flags/preempt counters,
EPC/EPSR/USP control registers, syscall return value slots, and context-tracking state

## Dependencies and Integration Points

depends on ABI entry macros, asm-offsets constants, syscall table layout, context tracking,
preemption, signal notification, page fault/trap C handlers, and thread_info flags

## Risks and Test Signals

stack-frame offsets, user/kernel mode tests, syscall argument placement for ABI v1/v2, and interrupt
enable ordering are critical; boot, syscall tracing/seccomp, signal, page-fault, and preemption
tests are the test signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/entry.S -->
