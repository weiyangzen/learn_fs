# sources/distributed-fs/ceph-client/tools/accounting/Makefile

## Purpose
Builds task/accounting demonstration utilities.

## Important APIs, Types, And Functions
- `CC := $(CROSS_COMPILE)gcc` supports cross-compilation.
- `CFLAGS := -I../include/uapi/` points builds at local UAPI headers.
- `PROGS := getdelays procacct delaytop` lists the built programs.
- `all` builds all programs; `clean` removes them.

## Control Flow
Default implicit C build rules compile each program from its matching `.c` file. `clean` removes binaries.

## State And Persistence
No runtime state. Build outputs are the three binaries in the accounting directory.

## Dependencies And Integration Points
Depends on local UAPI headers and libc/system netlink headers. The programs interact with Linux taskstats/cgroupstats/PSI at runtime.

## Risks
Implicit rules mean per-program extra libraries or flags must be added explicitly if future code needs them. `clean` uses `rm -fr $(PROGS)`.

## Test Signals
Run `make -C tools/accounting` and `make clean`; execute each binary with `--help` or basic arguments on a kernel with taskstats enabled.
