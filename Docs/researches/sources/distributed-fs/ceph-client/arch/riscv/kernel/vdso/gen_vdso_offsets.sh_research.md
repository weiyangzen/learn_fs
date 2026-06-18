<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/gen_vdso_offsets.sh -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/gen_vdso_offsets.sh

Purpose: Generates C preprocessor offset macros for symbols in the RISC-V vDSO debug image.

Important APIs/types/functions: Shell script reads `nm` output and emits `#define vdso{suffix}_offset_<symbol> 0x<addr>`.

Control flow: Optional suffix argument changes macro names, then the script filters text/data symbols from stdin/object argument via `${NM}`.

State and persistence: Produces generated header content used at build time; no runtime state.

Dependencies and integration points: Invoked by the vDSO Makefile for native and CFI suffix variants.

Risks: Symbol filtering or suffix changes can break kernel references to vDSO offsets.

Test signals: Generated `include/generated/vdso*-offsets.h` contains expected symbols for vDSO build variants.

Source read size: 7 lines, 175 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/gen_vdso_offsets.sh -->
