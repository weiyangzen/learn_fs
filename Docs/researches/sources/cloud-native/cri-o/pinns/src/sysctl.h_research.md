# sources/cloud-native/cri-o/pinns/src/sysctl.h

Purpose: declares the sysctl configuration entry point for the `pinns` C helper.

Important APIs/types/functions: `int configure_sysctls(char ** const sysctls, int size);`

Control flow: none; header guard only.

State and persistence: none directly; implementation writes `/proc/sys`.

Dependencies/integration: included by `pinns.c` and implemented in `sysctl.c`.

Risks: API documents no ownership/mutation semantics, although implementation mutates strings in place.

Test signals: compile-time linkage between `pinns.c` and `sysctl.c`.
