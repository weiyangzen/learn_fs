# sources/distributed-fs/ceph-client/sound/core/seq/seq_ump_convert.h

## Purpose
`seq_ump_convert.h` declares the internal UMP conversion entry points used by the sequencer client delivery code.

## Important APIs, Types, and Functions
- `snd_seq_deliver_from_ump()` converts/delivers UMP-source events to a destination client/port.
- `snd_seq_deliver_to_ump()` converts/delivers legacy sequencer events to UMP destination clients.
- `snd_seq_ump_group_port()` extracts a 1-based group port from UMP events.

## Control Flow
The client manager can choose the appropriate delivery helper based on source/destination client capabilities. Both helpers receive source client, destination client, destination port, event pointer, atomic context flag, and hop count.

## State and Persistence
The header defines no state. Conversion state lives in destination ports and implementation-local stack variables.

## Dependencies and Integration Points
Includes `seq_clientmgr.h` and `seq_ports.h` to access client/port internals. Used only when sequencer UMP support is compiled.

## Risks
These helpers depend on internal client/port layouts and on the caller passing correctly referenced destination objects. Incorrect source/destination classification can skip conversion or deliver incompatible packets.

## Test Signals
Compile delivery paths with UMP enabled and verify both UMP-to-legacy and legacy-to-UMP clients route through the declared helpers.
