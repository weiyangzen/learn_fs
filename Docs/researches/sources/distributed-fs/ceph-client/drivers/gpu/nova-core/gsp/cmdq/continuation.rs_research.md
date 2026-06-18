# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq/continuation.rs

## Purpose

`gsp/cmdq/continuation.rs` supports splitting oversized GSP commands into a first truncated command plus continuation-record commands.

## Important APIs, Types, And Functions

Important items are `MAX_CMD_SIZE`, `ContinuationRecords`, `ContinuationRecord`, `SplitState<C>`, and `SplitCommand<C>`. `ContinuationRecord` implements `CommandToGsp` with function `ContinuationRecord` and no reply. `SplitState::new()` decides whether and how to split a command.

## Control Flow

When command size exceeds one queue element, `SplitState::new()` allocates two buffers: the maximum payload fitting beside the original command header and the remaining continuation payload. It asks the original command to write its variable payload across both buffers, then wraps the first part in `SplitCommand` and exposes an iterator over chunks of the rest. `CmdqInner::send_command()` sends the first command followed by each continuation record.

## State And Persistence Behavior

Split payload data is copied into kernel vectors owned by `SplitCommand` and `ContinuationRecords` until sent. No persistent state remains after queue submission, except the queued GSP messages.

## Dependencies And Integration Points

It depends on `CommandToGsp`, `NoReply`, `MsgFunction`, max queue element size, `GspMsgElement`, and `SBufferIter`. It is used internally by `cmdq.rs`.

## Risks And Test Signals

Risks include duplicating payload initialization for split commands, allocation failures for large payloads, boundary errors at exact maximum sizes, and GSP expectations for continuation ordering. KUnit tests cover zero-sized, boundary, one-continuation, and multi-continuation payloads; hardware tests should send a real large registry/control payload and verify GSP accepts it.
