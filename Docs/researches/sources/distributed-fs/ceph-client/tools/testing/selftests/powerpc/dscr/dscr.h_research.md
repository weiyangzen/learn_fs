# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr.h

## Purpose
Shared DSCR constants and helpers for reading/writing privileged, problem-state, and sysfs default DSCR values.

## Important APIs, Types, and Functions
Defines `THREADS`, `COUNT`, `DSCR_MAX`, paths `DSCR_DEFAULT` and `CPU_PATH`, barriers `rmb/wmb`, `READ_ONCE`, inline `get_dscr()`, `set_dscr()`, `get_dscr_usr()`, `set_dscr_usr()`, plus `get_default_dscr()` and `set_default_dscr()`.

## Control Flow
Inline helpers directly emit SPR reads/writes; sysfs helpers parse or write hex values and exit on I/O failure.

## State and Persistence
DSCR SPR and system default DSCR sysfs state can be modified by callers. The header itself stores no durable state.

## Dependencies and Integration Points
Depends on `reg.h` SPR macros and `utils.h` read/write helpers. Included by all DSCR tests.

## Risks and Test Signals
Risks include modifying global sysfs default DSCR without restoration and requiring DSCR hardware support. Tests guard with `PPC_FEATURE2_DSCR`.
