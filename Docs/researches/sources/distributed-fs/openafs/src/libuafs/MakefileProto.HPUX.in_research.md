## sources/distributed-fs/openafs/src/libuafs/MakefileProto.HPUX.in

Purpose: Supplies HP-UX and IA64 HP-UX specific compiler and linker settings for libuafs.

Important variables: `CC=/opt/ansic/bin/cc`, `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, platform-filtered `KOPTS`, platform-filtered `TEST_CFLAGS`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lnsl -lm -lpthread -ldld -lc`.

Control flow: Uses OpenAFS prototype tags such as `<hp_ux102 hp_ux110 hp_ux11i>`, `<ia64_hpux1122 ia64_hpux1123>`, and `<all>` to select proper options before including `Makefile.common`.

State and persistence: Only controls build outputs.

Dependencies and integration: Integrates with HP ANSI C compiler, HP-UX linker archive/shared modes, POSIX thread macros, network services libraries, and dynamic loader library.

Risks: Hard-coded compiler path and legacy `+DA1.0`, `+z`, and `-Wp,-H200000` flags are fragile on modern HP-UX or cross-build setups. Prototype filtering must select exactly one viable branch.

Test signals: HP-UX PA-RISC and IA64 builds, linktest, prototype filtering, static/PIC archive creation, and runtime symbol resolution for pthread/nsl/dld dependencies.
