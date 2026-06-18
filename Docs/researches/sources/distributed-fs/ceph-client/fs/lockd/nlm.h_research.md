# sources/distributed-fs/ceph-client/fs/lockd/nlm.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/nlm.h` declares Network Lock Manager protocol constants: maximum offsets, status values, program number, and procedure numbers. The source was read as a complete 56-line header.

## Important APIs, Types, and Functions

Important constants include `NLM_OFFSET_MAX`, `NLM4_OFFSET_MAX`, `NLM_PROGRAM`, `NLMPROC_*` procedure IDs, and status enum values such as `NLM_LCK_GRANTED`, `NLM_LCK_DENIED`, `NLM_LCK_BLOCKED`, `NLM_LCK_DENIED_GRACE_PERIOD`, and NLMv4-only errors.

## Control Flow

There is no runtime flow. These constants drive XDR procedure tables, status translation, client/server dispatch, and reboot notification handling.

## State and Persistence Behavior

No state is owned. The values are ABI-level protocol constants and must remain stable.

## Dependencies and Integration Points

The header is included by `lockd.h` and therefore by most lockd implementation files. `clntxdr.c`, `clnt4xdr.c`, server XDR, and service dispatch tables rely on these numbers matching the NLM wire protocol.

## Risks and Edge Cases

Changing any value breaks wire compatibility. NLMv4-only statuses are conditionally compiled, so code translating statuses must handle builds without `CONFIG_LOCKD_V4`.

## Test Signals

Signals include protocol table build checks, XDR encode/decode tests that compare procedure numbers, NLMv4 status translation tests, and interoperability tests with standard NFS/NLM clients and servers.
