# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/chdexcr.c

## Purpose
Command-line helper to change editable DEXCR aspects through prctl controls.

## Important APIs, Types, and Functions
Important functions are `die()`, `help()`, `apply_option()`, and `main()`. It uses `aspects[]`, `pr_set_dexcr()`, and option strings from `dexcr.h`.

## Control Flow
Main parses aspect options, maps them through `apply_option()`, and applies set/clear/onexec controls with prctl; help displays supported aspect names.

## State and Persistence
State changes are per-process DEXCR control bits and optional on-exec inheritance settings. No files are written.

## Dependencies and Integration Points
Depends on `dexcr.c` helpers, PowerPC prctl DEXCR API, and common parse/report helpers from `utils.h`.

## Risks and Test Signals
Risks are user confusion over current versus on-exec controls and unsupported aspects. Signals are prctl errors or updated values visible via `lsdexcr`.
