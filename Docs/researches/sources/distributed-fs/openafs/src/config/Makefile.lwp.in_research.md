# sources/distributed-fs/openafs/src/config/Makefile.lwp.in

Purpose: make fragment that selects LWP-flavored compile and link rules as the generic `AFS_*` rules.

Important APIs/types/functions: assigns `AFS_CFLAGS`, `AFS_LDFLAGS`, `AFS_CCRULE`, and `AFS_CCRULE_NOQ` from the LWP variables, and provides `.c.o`, `%.o: %.c`, and `.m.o` rules.

Control flow: after inclusion, ordinary object builds use the LWP compiler flags and `CCOBJ` wrapper path from `Makefile.config`.

State and persistence: creates standard `.o` files for LWP builds.

Dependencies and integration: depends on `LWP_CFLAGS`, `LWP_LDFLAGS`, and `LWP_CCRULE` from `Makefile.config`. Used by legacy single-threaded OpenAFS components and config tools.

Risks and test signals: risks are accidental inclusion in pthread-only modules and rule conflicts. Successful LWP object builds and links are the main signals.
