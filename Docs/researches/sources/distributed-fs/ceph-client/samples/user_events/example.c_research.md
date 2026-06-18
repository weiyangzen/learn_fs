# sources/distributed-fs/ceph-client/samples/user_events/example.c

## Purpose

This user-space program demonstrates the `user_events` tracing ABI by registering an event and writing records only when tracing is attached.

## Important APIs, Types, and Functions

It uses `/sys/kernel/tracing/user_events_data`, `struct user_reg`, ioctl `DIAG_IOCSREG`, `writev`, `struct iovec`, and a global `enabled` bit. `event_reg()` sets registration fields, including `enable_bit=31`, `enable_addr`, and event command string.

## Control Flow

`main()` opens the data file, registers event `"test u32 count"`, builds an iovec containing the write index and a count payload, then loops waiting for Enter. If the kernel has set the enabled bit, it writes the event record with `writev`, increments the count, and prints a message.

## State and Persistence Behavior

Process state includes `enabled`, write index, and `count`. The registered user event persists while the fd/process registration remains active in tracing infrastructure.

## Dependencies and Integration Points

It depends on tracingfs mounted at `/sys/kernel/tracing`, user_events support, and trace consumers enabling the event.

## Risks and Edge Cases

The program does not check `open()` failure before ioctl. It loops forever via `goto ask`. Event writes are skipped unless tracing is attached, which is intended but can look idle.

## Test Signals

Run the program, enable the corresponding user event in tracing, press Enter repeatedly, and confirm count records appear in trace output.
