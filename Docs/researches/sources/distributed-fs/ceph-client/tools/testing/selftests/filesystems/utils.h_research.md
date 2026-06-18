<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.h

## Purpose
This header declares the filesystem selftest helper API implemented by `utils.c` and provides the inline `switch_userns()` convenience wrapper.

## Important APIs, Types, And Functions
It exposes namespace helpers `get_userns_fd()`, `setup_userns()`, `enter_userns()`, `switch_userns()`, credential helper `switch_ids()`, capability helpers `caps_down()` and `cap_down()`, process helper `wait_for_pid()`, file helper `write_file()`, and mount identifier helper `get_unique_mnt_id()`. It imports libcap's `cap_value_t` and Linux/user namespace types.

## Control Flow
`switch_userns()` calls `setns(fd, CLONE_NEWUSER)`, switches uid/gid with `switch_ids()`, and optionally drops all effective capabilities through `caps_down()`. Other functions are declarations for callers that include this header in selftest binaries.

## State And Persistence
The header has no mutable state. Its inline wrapper changes caller process namespace, credentials, and effective capabilities when invoked.

## Dependencies And Integration Points
It depends on `_GNU_SOURCE`, `<sys/capability.h>`, Linux namespace headers, and the implementation in `utils.c`. It is intended for tools under `tools/testing/selftests/filesystems`.

## Risks
The bool return from `switch_userns()` hides detailed errno from the failing substep. Callers must understand that namespace and credential changes are process-global and not automatically reversible.

## Test Signals
Compilation with libcap headers, successful linkage with `utils.o`, and tests that can switch to a prepared namespace and then access proc files are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/utils.h -->
