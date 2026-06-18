# sources/distributed-fs/ceph-client/arch/arm64/kernel/reloc_test_syms.S

Purpose: this assembly file emits the relocation forms consumed by `reloc_test_core.c`. Each symbol returns a value that should reflect the linker/module loader's handling of a specific ARM64 relocation type.

Important symbols: functions include `absolute_data64`, `absolute_data32`, `absolute_data16`, `signed_movw`, `unsigned_movw`, `relative_adrp`, `relative_adrp_far`, `relative_adr`, `relative_data64`, `relative_data32`, and `relative_data16`.

Control flow: absolute-data helpers load embedded `.quad`, `.long`, or `.short` values referring to absolute symbols. MOVW helpers construct an absolute symbol address via `movz/movk` relocation modifiers. ADRP/ADR helpers materialize addresses of `sym64_rel` or `memstart_addr`. PREL helpers load signed relative data from inline constants and add the location address to reconstruct the target.

Dependencies and integration: assembled into the relocation test module. It depends on AArch64 relocation syntax supported by the assembler and on symbol definitions in `reloc_test_core.c`.

Risks: alignment and `.space` directives intentionally shape ADRP reach and page boundaries; changing them can weaken the test. Return values are raw `x0` results and must match the expectations table exactly.

Test signals: used only through the module init log in `reloc_test_core.c`. Disassembly and `readelf -r` should show the relocation classes named in the C table.
