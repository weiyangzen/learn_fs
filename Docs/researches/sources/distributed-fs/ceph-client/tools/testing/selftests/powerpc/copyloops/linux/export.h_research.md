# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/linux/export.h

## Purpose
Stub Linux export header for userspace assembly builds.

## Important APIs, Types, and Functions
Defines `EXPORT_SYMBOL(x)`, `EXPORT_SYMBOL_GPL(x)`, and `EXPORT_SYMBOL_KASAN(x)` as empty macros.

## Control Flow
No control flow; macros erase kernel export annotations during preprocessing.

## State and Persistence
No state.

## Dependencies and Integration Points
Included by copied kernel assembly sources that retain export annotations.

## Risks and Test Signals
Risk is low; if future assembly needs export side effects, the stub would need updating. Current signal is successful preprocessing/linking.
