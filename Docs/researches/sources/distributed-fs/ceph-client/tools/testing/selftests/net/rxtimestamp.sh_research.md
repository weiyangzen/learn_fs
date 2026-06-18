<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.sh

## Purpose

`rxtimestamp.sh` is the namespace wrapper for the `rxtimestamp` receive timestamp test binary.

## Important APIs, Types, and Functions

The script is four lines: bash shebang, SPDX tag, and `./in_netns.sh ./rxtimestamp $@`. It forwards all caller arguments to the compiled C test.

## Control Flow

Execution immediately enters `in_netns.sh`, which provides isolation, then runs `rxtimestamp` with unchanged options. The wrapper exit status is the child status.

## State and Persistence Behavior

No local state is persisted. Network namespace setup and teardown are delegated to `in_netns.sh`; timestamp sockets are owned by the child process.

## Dependencies and Integration Points

It depends on `in_netns.sh` and `rxtimestamp` being present in the current directory. It integrates the C test into the net selftest namespace convention.

## Risks and Edge Cases

Argument forwarding is unquoted as `$@`; in shell this still expands positional parameters as separate words only when quoted, so arguments with spaces would be split. Normal kselftest options are simple and unaffected.

## Test Signals

Signals are inherited from `rxtimestamp`: zero exit and `PASSED.` indicate success; any child error fails the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rxtimestamp.sh -->
