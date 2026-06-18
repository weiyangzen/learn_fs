# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/cmdq.rs

## Purpose

`gsp/cmdq.rs` implements the shared-memory command and message queues used for CPU-to-GSP RPCs and GSP-to-CPU events.

## Important APIs, Types, And Functions

Key traits are `CommandToGsp` and `MessageFromGsp`; marker `NoReply` represents fire-and-forget commands. Queue structures include `MsgqData`, `Msgq`, `GspMem`, `DmaGspMem`, `GspCommand`, `GspMessage`, `Cmdq`, and `CmdqInner`. Public methods include `Cmdq::new()`, `send_command()`, `send_command_no_wait()`, and `receive_msg()`.

## Control Flow

`DmaGspMem::new()` allocates coherent shared memory, writes self PTEs, and initializes CPU queue headers. Sending locks the queue, optionally splits large commands, waits for writable space, writes a `GspMsgElement`, initializes the typed command and variable payload, checks all bytes were written, computes checksum, advances CPU write pointer, and notifies GSP via `NV_PGSP_QUEUE_HEAD`. Receiving waits for readable GSP data, validates length and checksum, parses the expected typed message, advances CPU read pointer even on mismatch, and returns `ERANGE` for nonmatching functions.

## State And Persistence Behavior

`Cmdq` owns coherent `GspMem`, a mutex-protected sequence counter, and a DMA handle passed to GSP boot arguments. Ring read/write pointers are shared persistent state with explicit CPU/GSP ownership rules and memory fences in `gsp/fw.rs`.

## Dependencies And Integration Points

It depends on coherent DMA, typed GSP ABI wrappers, `SBufferIter`, continuation splitting, BAR0 notification register, polling, mutexes, and DMA read/write macros. `gsp/commands.rs`, `gsp/sequencer.rs`, and boot code use it for all RPCs.

## Risks And Test Signals

Risks include unsafe slice projection over circular buffers, pointer wrap/off-by-one bugs, checksum mismatch, element-count advancement errors, lock scope serializing send/receive, message consumption on unexpected functions, and timeout tuning. Test queue initialization, full/empty ring boundaries, wraparound send/receive, checksum corruption, continuation split commands, unexpected messages, and init-done/GPU-info RPCs on hardware.
