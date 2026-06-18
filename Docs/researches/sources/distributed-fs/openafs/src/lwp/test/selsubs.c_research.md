# sources/distributed-fs/openafs/src/lwp/test/selsubs.c

Purpose: shared utility functions for the select client/server tests.

Important APIs/types/functions: `sendOOB` and `recvOOB` send/receive one byte with `MSG_OOB`; `assertNullFDSet` clears one expected fd then asserts the rest of the fd set storage is zero; `OpenFDs` opens `/dev/null` until a requested fd threshold is reached; `Die` reports errors and exits or aborts; `Log` prints timestamped messages with current LWP process pointer.

Control flow: helpers are synchronous. `Log` calls `LWP_CurrentProcess`, so it expects LWP support to be initialized in normal use.

State and persistence: no persistent state; may leave dummy `/dev/null` descriptors open to influence subsequent socket fd allocation.

Dependencies/integration: depends on socket APIs, `lwp.h`, `seltest.h`, and IOMGR tests. `assertNullFDSet` assumes fd_set can be interpreted as an array of `int`.

Risks and test signals: fd_set layout assumptions are non-portable but intentional for this low-level test. `OpenFDs` relies on descriptor allocation order. Test failures generally surface as assertions or aborts.
