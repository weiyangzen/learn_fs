# sources/distributed-fs/ceph-client/arch/x86/kernel/vmlinux.lds.S

Purpose: defines the x86 kernel linker script, including image entry points, load segments, section ordering, alignment, runtime symbols, special metadata sections, discard rules, and build-time assertions.

Important APIs/types/functions: this is linker-script/preprocessor logic rather than C APIs. Important symbols include `phys_startup_32/64`, `_text`, `_stext`, `_etext`, `_sdata`, `_edata`, `__init_begin`, `__init_end`, `__bss_start`, `__bss_stop`, `__end_of_kernel_reserve`, `__brk_base`, `__brk_limit`, `_end`, ORC unwind table symbols, mitigation site symbols, and architecture-specific ELF note values.

Control flow: the script selects output format/architecture/entry by config, lays out `.text`, rodata, `.data`, bug table, ORC unwind tables, init text/data, CPU device tables, retpoline/IBT/FineIBT/alternative sections, APIC drivers, exit sections, percpu data, runtime constants, nosave data, BSS, brk, optional SME scratch, debug/modinfo/ELF details, and final discards. It then asserts image size, GOT/PLT/relocation emptiness, mitigation alignment, SRSO aliasing, and thunk placement properties.

State and persistence: the produced ELF layout is persistent boot ABI. Symbols exported here are consumed by early boot, memory reservation, alternatives, ORC unwinder, kexec, module/debug tooling, and mitigation patching.

Dependencies and integration: depends on generic linker-script macros, x86 page sizes, ORC lookup definitions, boot constants, kexec limits, retpoline/IBT/FineIBT/SRSO/ITS configs, SME, Xen/PVH notes, and exported startup symbols.

Risks: layout or alignment mistakes can break boot, large-page permissions, alternative patching, unwinding, kexec relocation, SME encryption, mitigation correctness, or module/debug metadata. Assertions intentionally fail the build for unexpected runtime relocations or unsafe thunk placement.

Test signals: successful x86 builds across 32-bit/64-bit and mitigation configs, `vmlinux` section inspection, ORC unwinder function, boot on KASLR/SME/kexec/Xen/PVH configs, and linker assertion failures when invariants are violated.
