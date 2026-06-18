# sources/distributed-fs/ceph-client/fs/dlm/midcomms.h

## Purpose
`midcomms.h` declares the reliable DLM messaging layer interface between lock/rcom code and lowcomms transport.

## Important APIs, Types, And Functions
The header forward-declares `struct midcomms_node` and exports receive validation/processing, message-handle allocation/commit, address setup, version wait, node close, lifecycle functions, member notifications, resend trigger, debug accessors, raw-message send, and cache constructor.

## Control Flow
Senders obtain a `dlm_mhandle`, fill the returned payload pointer, then must commit with `dlm_midcomms_commit_mhandle()`. Lowcomms calls validation and processing functions for incoming buffers. Membership code calls add/remove and close functions around recovery events.

## State And Persistence
No header-owned state. It exposes operations over per-node midcomms state held in `midcomms.c`.

## Dependencies And Integration Points
It integrates lock/rcom/recovery code with DLM communications while hiding lowcomms `struct dlm_msg` details. Debugfs uses the accessor functions for state, flags, version, and queue count.

## Risks
The get/commit contract is strict: failing to commit a successful handle leaks the SRCU read-side state and message resources. Callers must not send after member removal unless they intentionally use raw debug facilities.

## Test Signals
Compile coverage and send-path tests should verify all callers commit or abandon handles only through valid error paths. Debugfs output should reflect live node state.
