## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf.h

Purpose: Central Kerberos IV configuration wrapper for OS, CPU, compiler, and C-library compatibility.

Important APIs/types/functions: Includes `osconf.h`, optionally `names.h` for `SHORTNAMES`, compensates for non-ANSI compilers by defining `const`, `volatile`, and `signed`, defines generic `pointer`, and supplies `PROTOTYPE(p)` to support old-style versus ANSI declarations.

Control flow: Compile-time only. It chooses prototype syntax and validates that byte order (`MSBFIRST` or `LSBFIRST`) and word size (`BITS16` or `BITS32`) have been set by platform headers.

State and persistence: No runtime state. It persists platform assumptions into all downstream declarations.

Dependencies and integration points: Included by `des.h` and `krb.h`; `osconf.h` routes to `conf-pc.h` for Windows/OpenAFS builds.

Risks: Compatibility macros can hide compiler diagnostics by redefining language keywords on non-ANSI builds. The hard `#error` checks are valuable but can break unusual cross-compilation environments where byte order or bitness is not predeclared.

Test signals: Compile K4 headers on the target Windows toolchain and on any compatibility toolchain; verify `PROTOTYPE` expands correctly for function declarations and that exactly one byte-order and bitness path is selected.
