# sources/distributed-fs/openafs/src/config/Makefile.config.in

Purpose: central Autoconf-generated make fragment that defines OpenAFS installation paths, tool substitutions, compiler/linker flags, pretty-build wrappers, and shared compile/link recipes.

Important APIs/types/functions: provides variables such as `TOP_OBJDIR`, `TOP_INCDIR`, `SYS_NAME`, `AFS_PARAM`, `COMPILE_ET`, `RXGEN`, `LWPTOOL`, `CC_WRAPPER`, and `LD_WRAPPER`; common flags `COMMON_CFLAGS`, `LWP_CFLAGS`, `PTH_CFLAGS`, and `COMMON_LDFLAGS`; command wrappers `RUNCMD`, `RUN_CC`, and `RUN_LD`; and build recipes `LWP_CCRULE`, `PTH_CCRULE`, `LT_CCRULE`, `LT_LDLIB_*`, `LT_LDRULE*`, and default `AFS_LDRULE`.

Control flow: makefiles include this first, then optionally include LWP, pthread, libtool, or lwptool fragments to bind generic `AFS_*` rules. The `V=0` path hides raw commands and emits concise `CC`/`LD` lines while preserving failure diagnostics. The file also creates independent `COMPILE_ET_H` and `COMPILE_ET_C` commands to support parallel error-table generation.

State and persistence: no state itself, but it controls where builds install headers/libraries, where generated helper binaries are found, and how objects/libraries/executables are produced.

Dependencies and integration: fed by `configure` substitutions and included throughout the OpenAFS tree. It integrates roken, hcrypto, Kerberos/GSSAPI, pthread, PAM, Linux kernel, libtool, LWP, CTF, and architecture flags.

Risks and test signals: a wrong substitution can break the whole tree. Risks include quoting in `RUNCMD`, duplicated flag ordering, incorrect wrapper selection, stale `AFS_PARAM`, and libtool symbol-list assumptions. Full-tree builds with `V=0` and `V=1`, LWP and pthread targets, shared-library targets, and generated `.et` sources are the main signals.
