# sources/distributed-fs/ceph-client/tools/arch/x86/kcpuid/Makefile

## Purpose
Builds and installs the `kcpuid` CPUID inspection tool and its `cpuid.csv` data file.

## APIs, Types, and Functions
Targets are `kcpuid`, pattern rule `%: %.c`, `clean`, and `install`. Variables include `BINDIR ?= /usr/sbin`, `HWDATADIR ?= /usr/share/misc/`, `CFLAGS`, `DESTDIR`, `CC`, and `LDFLAGS`.

## Control Flow, State, and Persistence
The build compiles `kcpuid.c` with `-O2 -Wall -Wextra -I../../../include`. Install creates binary and hardware-data directories, installs the executable, and installs `cpuid.csv` read-only into the hardware data directory.

## Dependencies and Integration
Depends on a C compiler, tool headers under `tools/include`, and the local CSV metadata file. Integrated with Linux tools installation conventions.

## Risks and Test Signals
Risks include stale `cpuid.csv` installation, missing include path in out-of-tree builds, and default install paths requiring privileges. Test signals are `make`, `make install DESTDIR=...`, and running the installed binary with the installed CSV.
