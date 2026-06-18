<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw.c

## Purpose

`hw/debug_hw.c` provides common command decoding and gather-dump helpers for host1x debug output, then includes either the pre-HW6 or HW6+ register-specific debug implementation.

## Important APIs, Types, And Functions

- `show_channel_command()` decodes host1x opcodes such as SETCLASS, INCR, NONINCR, MASK, IMM, RESTART, GATHER, stream-ID/payload/wide variants, and MLOCK extend opcodes.
- `show_gather()` prints decoded words from a mapped pushbuffer or gather buffer, following pushbuffer wrap at the restart word.
- `show_channel_gathers()` walks queued jobs and dumps their pushbuffer slots and gather command buffers.
- Conditional include selects `debug_hw_1x06.c` for `HOST1X_HW >= 6`, otherwise `debug_hw_1x01.c`.

## Control Flow

Hardware debug ops call into this shared decoder while `debug.c` holds CDMA/debug locks. The decoder tracks how many payload words follow an opcode and prints continuations until the command is complete. Gather dumps map BOs unless the job already has a firewall gather copy.

## State And Persistence Behavior

This file observes CDMA queues, pushbuffers, gather buffers, and register snapshots. It does not intentionally mutate state except through BO mapping side effects and output emission.

## Dependencies And Integration Points

Depends on generated opcode/register definitions, CDMA/job/channel structures, host1x BO mapping, and `struct output`. Included generation build units install the resulting `host1x_debug_ops`.

## Risks And Test Signals

Debug decoding must match opcode encodings used by `channel_hw.c`; otherwise timeout dumps mislead recovery. Address mismatch protection avoids dumping unrelated memory when physical addresses alias unexpectedly. Test signals are debugfs/status dumps for active older and newer hardware, wide opcode decoding, gather-copy firewall jobs, and unmappable BO handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/debug_hw.c -->
