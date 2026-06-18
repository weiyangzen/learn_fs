<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sim.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sim.h

Purpose: Provides assembler macros for simulator-oriented static function save metadata, allowing assembly code to emit named address/size records in a `.data` subsection.

Important APIs/types/functions: `save_static_function(symbol)` for 32-bit and 64-bit builds, stringification helpers `__str`/`__str2`, and offsets from `asm/asm-offsets.h`.

Control flow: Assembly code invokes the macro after a static function. The macro switches to `.data`, emits a symbol name string, aligns, stores start/end or size information, then returns to `.text`.

State and persistence: It emits object-file metadata consumed by simulator/debug tooling. No runtime mutable state is created by C code.

Dependencies and integration points: Depends on assembler context and `asm/asm-offsets.h`; uses MIPS assembler directives such as `.pushsection`, `.ascii`, `.align`, `.dword`, and `.word`.

Risks: The macro is assembler-only and layout-sensitive. Incorrect use around local labels or function boundaries will produce misleading metadata. The 32/64-bit forms differ in record width and alignment.

Test signals: Assembler build coverage and inspection of generated object sections in simulator-enabled MIPS builds are the main signals.

Source read size: 70 lines, 2070 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sim.h -->
