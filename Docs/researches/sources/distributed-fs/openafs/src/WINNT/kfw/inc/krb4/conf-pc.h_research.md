## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/conf-pc.h

Purpose: Supplies PC, Windows, DOS, and OS/2 platform configuration for legacy Kerberos IV headers.

Important APIs/types/functions: Normalizes `_WIN32` to `WIN32`, Windows macro families to `WINDOWS`, and OS/2 macros to `OS2`; selects `BITS16` or `BITS32`; declares little-endian `LSBFIRST`; aliases BSD functions (`index`, `bcopy`, `bzero`) to C runtime calls; defines `u_char`, `u_long`, `u_short`, `u_int`, optional `DWORD`, and PC calling convention macros; includes `windows.h` and `windowsx.h` for Windows.

Control flow: Pure preprocessor configuration. It is included by `conf.h` through `osconf.h` before K4 types and prototypes are compiled.

State and persistence: No runtime state. It fixes build-time ABI assumptions such as byte order, pointer model, `MAXPATHLEN`, and random seed sources.

Dependencies and integration points: Depends on C runtime functions, Windows SDK headers, OS/2 `utils.h`, and `time`/`process` in WIN16 mode. DES and K4 API headers rely on its `FAR`, `PASCAL`, and integer definitions.

Risks: Global BSD macro aliases can conflict with modern libraries. `RANDOM_KRB_INT32_*` uses `time()` and `getpid()` as weak random seeds. The `DWORD` fallback may mismatch Windows SDK typedefs if include order is wrong.

Test signals: Preprocessor tests for `_WIN32`, `WIN16`, `MSDOS`, and `OS2`; compile DES/KRB headers after it; verify `LSBFIRST`, `BITS32`, `FAR`, `PASCAL`, and `MAXPATHLEN` definitions match the intended Windows ABI.
