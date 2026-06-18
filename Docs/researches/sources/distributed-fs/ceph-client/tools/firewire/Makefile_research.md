<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/Makefile -->
# sources/distributed-fs/ceph-client/tools/firewire/Makefile

Purpose: Builds, cleans, and installs the FireWire `nosy-dump` userspace sniffer tool.

Important APIs/types/functions: Make targets are `all`, `nosy-dump`, `clean`, and `install`. It sets `nosy-dump-version = 0.4`, compiles with `-Wall -O2 -g`, defines `VERSION`, includes `../../drivers/firewire`, links `nosy-dump.o` and `decode-fcp.o`, and links against `-lpopt`.

Control flow: Default target builds `nosy-dump`; object generation uses make built-ins plus the target-specific variables. `install` copies the binary to `$(prefix)/bin/nosy-dump`.

State and persistence: Build artifacts are `*.o` and `nosy-dump`; install persists a binary under `prefix`, default `/usr`.

Dependencies/integration: Depends on a C compiler, libpopt development files, kernel FireWire headers, `nosy-user.h`, and Linux FireWire constants. It is a standalone tools build rather than Kbuild proper.

Risks/tests: Risks include missing libpopt, stale include path to driver headers, and install without `DESTDIR`. Test signals are `make`, `make clean`, `make install DESTDIR=...`, and running `nosy-dump --version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/Makefile -->
