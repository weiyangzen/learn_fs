# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/lsdexcr.c

## Purpose
Command-line utility that displays DEXCR, HDEXCR, effective DEXCR bits, and prctl aspect configuration.

## Important APIs, Types, and Functions
Functions include `print_list()`, `print_dexcr()`, `print_aspect()`, `print_aspect_config()`, and `main()`, using `aspects[]`, `get_dexcr()`, and prctl helper functions.

## Control Flow
Main probes DEXCR support, prints raw/effective bit state, iterates known aspects, and reports support/editability/current/onexec controls.

## State and Persistence
Read-only except for transient output; it does not modify DEXCR state.

## Dependencies and Integration Points
Depends on `dexcr.c`, `dexcr.h`, SPR accessors, and prctl DEXCR API.

## Risks and Test Signals
Risks are reporting stale/unknown aspects if ABI evolves. Test signal is diagnostic output useful for interpreting DEXCR test skips/failures.
