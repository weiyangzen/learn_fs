
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dwarf2.h

Purpose: assembly-only aliases for DWARF CFI directives and section selection.

Important APIs and control flow: maps `CFI_*` macros to `.cfi_*` assembler directives and warns if included from C. Non-vDSO builds emit CFI into `.debug_frame`; vDSO builds emit both `.eh_frame` and `.debug_frame` so runtime and debug unwind data are available.

State, dependencies, and risks: state is emitted unwind/debug metadata in object files. Dependencies include assembler CFI support and vDSO build mode. Risks include including from C, missing unwind data for offline debugging, and unwanted runtime `.eh_frame` in kernel objects. Test signals are assembly builds, unwind/debug validation, and vDSO unwind tests.
