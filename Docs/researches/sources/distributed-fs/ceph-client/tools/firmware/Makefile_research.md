<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/Makefile -->
# sources/distributed-fs/ceph-client/tools/firmware/Makefile

Purpose: Builds and cleans the `ihex2fw` firmware conversion utility.

Important APIs/types/functions: Targets are `all`, pattern rule `%: %.c`, and `clean`. It uses `CFLAGS = -Wall -Wextra -g`, builds `ihex2fw` from `ihex2fw.c`, and removes the binary via `$(RM)`.

Control flow: Default `all` depends on `ihex2fw`; the generic C pattern invokes `$(CC) $(CFLAGS) -o $@ $^`.

State and persistence: Build output is the `ihex2fw` binary. No install target is present.

Dependencies/integration: Depends only on a C compiler and standard C/POSIX headers used by `ihex2fw.c`.

Risks/tests: Risks are limited to generic pattern-rule collisions and missing custom `LDFLAGS`. Test signals are `make`, `make clean`, and running conversion fixtures through the built binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/Makefile -->
