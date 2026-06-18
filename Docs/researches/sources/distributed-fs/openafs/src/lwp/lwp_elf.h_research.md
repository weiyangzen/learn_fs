# sources/distributed-fs/openafs/src/lwp/lwp_elf.h

Purpose: small assembler portability header that normalizes C symbol labels for ELF, SYSV, Sun, and underscore-prefixed platforms. Despite the file name, comments state it also serves a.out platforms.

Important APIs/types/functions: defines `_C_LABEL(name)` and `ENTRY(name)`. On ELF/SYSV/Sun these expand to plain labels. On older underscore platforms they prepend `_`, with token-pasting variants for ANSI C and pre-ANSI assemblers.

Control flow: no runtime control flow. Assembly files include it before declaring `savecontext`, `returnto`, `PRE_Block`, or abort-like symbols, so the same assembly source can target multiple symbol naming conventions.

State and persistence: no state and no persistence.

Dependencies/integration: included by `process.amd64.s`, `process.i386.s`, and related assembly context-switch implementations. It integrates build-time platform macros with assembler syntax.

Risks and test signals: breakage here causes link-time failures or wrong entry labels for all assembly context switchers. Validation is mostly compile/link coverage for each target architecture.
