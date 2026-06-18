# sources/distributed-fs/ceph-client/tools/include/tools/dis-asm-compat.h

## Purpose
Hides binutils `dis-asm.h` API differences so tools can initialize disassembler state across older and newer libopcodes versions.

## Important APIs, Types, and Functions
Provides fallback `enum disassembler_style` and `fprintf_styled_ftype` when `DISASM_INIT_STYLED` is absent. Defines `fprintf_styled()` as a varargs adapter around `vfprintf()` and `init_disassemble_info_compat()` as the compatibility wrapper for `init_disassemble_info()`.

## Control Flow, State, and Persistence
`fprintf_styled()` ignores style and forwards formatted output to the supplied stream. `init_disassemble_info_compat()` chooses the four-argument or three-argument binutils initializer at compile time. No state is retained by this header itself.

## Dependencies and Integration
Depends on `<stdio.h>` and `<dis-asm.h>`. It integrates with perf disassembly and annotation code that must build against multiple distro binutils releases.

## Risks and Test Signals
Risks include missing `<stdarg.h>` through transitive includes, ABI changes in libopcodes, and losing styled output on old binutils. Test signals are build matrix coverage against old/new binutils and smoke disassembly that verifies output callbacks are invoked.
