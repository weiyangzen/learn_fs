# sources/distributed-fs/openafs/src/config/Makefile.pthread.in

Purpose: make fragment that selects pthread-aware compile and link rules as the generic `AFS_*` rules.

Important APIs/types/functions: assigns `AFS_CFLAGS`, `AFS_LDFLAGS`, `AFS_CCRULE`, and `AFS_LDRULE` from pthread variables and `MT_CC`, with quiet and non-quiet variants plus `.c.o`, `%.o: %.c`, and `.m.o` rules.

Control flow: modules including this fragment compile with `MT_CFLAGS` and link with `MT_CC`, overriding the default single-threaded link recipe from `Makefile.config`.

State and persistence: creates pthread-compatible object files and executables.

Dependencies and integration: depends on configured pthread compiler and flags from `Makefile.config`. Used by threaded OpenAFS daemons, libraries, and tools.

Risks and test signals: risks are missing thread flags at either compile or link time and inclusion order issues. Threaded component builds and runtime smoke tests for pthreaded daemons are the signals.
