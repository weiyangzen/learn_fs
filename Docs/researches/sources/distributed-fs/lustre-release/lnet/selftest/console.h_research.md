# sources/distributed-fs/lustre-release/lnet/selftest/console.h

## Purpose
Defines the in-kernel console data model and declares console operations for LNet Selftest.

## Important APIs And Types
Primary types are `lstcon_node`, `lstcon_ndlink`, `lstcon_group`, `lstcon_tsb_hdr`, `lstcon_batch`, `lstcon_test`, and `lstcon_session`. The header declares APIs for session, group, node, batch, test, stat/debug, ioctl, console lifecycle, and netlink lifecycle.

## Control Flow
The model is hierarchical: a console session owns global nodes, groups, batches, and transactions; groups and batches hold node links; tests reference source/destination groups and belong to a batch; console RPC transactions operate over node lists.

## State And Persistence
State is runtime-only. `ses_mutex` serializes console operations. `ses_rpc_lock` protects RPC freelist/counter and feature synchronization. Session and batch state constants track lifecycle.

## Dependencies And Integration Points
Includes kernel user access, libcfs, LNet types, `selftest.h`, and `conrpc.h`. Exposes `console_session` to implementation files.

## Risks
Flexible-array allocations for group hash and test parameters must use exact sizes. Node state values are used as flags in cleaning paths. Public APIs accept user pointers requiring careful implementation.

## Test Signals
Validate object lifecycle, refcounts, state transitions, session cleanup assertions, and compile integration across console/conrpc/module files.
