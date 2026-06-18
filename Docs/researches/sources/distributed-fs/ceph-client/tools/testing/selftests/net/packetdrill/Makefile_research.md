# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/Makefile

## Purpose
The packetdrill `Makefile` registers packetdrill scripts and their helper files with the kselftest framework.

## Important variables
- `TEST_INCLUDES` lists shared helpers required by packetdrill tests: `defaults.sh`, `ksft_runner.sh`, `set_sysctls.py`, and KTAP helpers.
- `TEST_PROGS := $(wildcard *.pkt)` makes every packetdrill script in the directory a test program.
- `include ../../lib.mk` delegates build/install/run mechanics to kselftest infrastructure.

## Control flow
There is no procedural logic beyond make expansion. At build or install time, `lib.mk` consumes `TEST_PROGS` and `TEST_INCLUDES`.

## State and persistence
The Makefile creates no runtime state. It controls which files are staged into the selftest output.

## Dependencies and integration points
It assumes packetdrill `.pkt` files in the same directory and helper scripts installed beside them. The actual runner is `ksft_runner.sh`, which invokes the external `packetdrill` binary.

## Risks and edge cases
Using `wildcard *.pkt` means new packetdrill scripts are automatically included, but accidentally staged or experimental `.pkt` files also become tests. Missing helper inclusion breaks installed-tree runs.

## Test signals
The Makefile's success signal is that kselftest lists and installs every `.pkt` script with the helper files required to execute them.
