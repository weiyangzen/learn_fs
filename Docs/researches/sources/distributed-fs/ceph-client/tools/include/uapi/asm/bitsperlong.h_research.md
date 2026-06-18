# sources/distributed-fs/ceph-client/tools/include/uapi/asm/bitsperlong.h

## Purpose
Selects the correct architecture-specific `bitsperlong.h` for tools builds, falling back to the generic definition when no specialized architecture branch matches.

## Important APIs, Types, and Functions
Uses preprocessor architecture tests for x86, powerpc, s390, sparc, mips, ia64, and alpha, then includes the matching `arch/*/include/uapi/asm/bitsperlong.h`; otherwise includes `<asm-generic/bitsperlong.h>`.

## Control Flow, State, and Persistence
Preprocessor include routing only. No runtime state exists.

## Dependencies and Integration
Depends on relative paths into the source tree and compiler-defined architecture macros. It integrates with generic UAPI headers that include `<asm/bitsperlong.h>` from the tools include path.

## Risks and Test Signals
Risks include broken relative include paths after tree moves, missing architecture branches, and host-vs-target confusion during cross-compilation. Test signals are preprocessing checks for each supported architecture macro and fallback builds for generic targets.
