# sources/distributed-fs/coda/coda-src/volutil/vol-rvmtrunc.cc

## Purpose

`vol-rvmtrunc.cc` implements asynchronous RVM log truncation for volutil. The complete 71-line file was read. It starts a separate LWP with a larger stack so the RPC can return while `rvm_truncate()` continues.

## Important APIs, Types, and Functions

`S_TruncateRVMLog(RPC2_Handle)` creates the LWP. `TruncProcess(void *)` calls `rvm_truncate()`, logs start/end, and destroys its own process. `rvm_truncate_stack` defaults to 1024 KB.

## Control Flow

The RPC logs the request, calls `LWP_CreateProcess()` with `TruncProcess`, and immediately returns that creation status. The worker performs synchronous truncation and exits.

## State and Persistence Behavior

The operation mutates the RVM log outside the caller's request path. There is no additional persistent state in this file and no result channel for truncation success after the worker starts.

## Dependencies and Integration Points

Dependencies include `rvm/rvm.h`, LWP, RPC2, `srv.h`, and `volutil.h`. The client command is `volutil truncatervmlog`.

## Risks and Test Signals

Risks include concurrent truncation requests, no completion/error reporting to the client, and global stack-size tuning. Tests should verify LWP creation failure handling, one successful truncate invocation, server logging, and behavior when a second truncate is requested while one is active.
