<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/Makefile

Purpose: Builds the RISC-V vDSO shared object, debug image, offset header, and wrapper object for native or CFI vDSO variants.

Important APIs/types/functions: Defines `vdso-syms`, C/assembly object lists, `vdso_offsets`, `vdso_o`, `vdso_so`, `vdso_so_dbg`, custom `vdsosym` and `vdsold_and_check` rules, and flags that disable profiling/sanitizers.

Control flow: Kbuild compiles selected vDSO C and assembly with freestanding flags, links `vdso.so.dbg` using `vdso.lds`, strips/debug-links the runtime image, generates offset headers, and embeds the binary through `vdso.S`.

State and persistence: No runtime state; outputs build artifacts consumed by `vdso.c`.

Dependencies and integration points: Works with `gen_vdso_offsets.sh`, vDSO linker script, CFI variant Makefile, getrandom support, compat/nonnative configs, and the top-level architecture build.

Risks: Toolchain flags must prevent instrumentation unsupported in vDSO. Missing offset generation or symbol filtering breaks kernel references to vDSO symbols.

Test signals: vDSO build under RV32/RV64, compat and CFI variants, symbol table inspection, and runtime libc vDSO calls.

Source read size: 105 lines, 3202 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/Makefile -->
