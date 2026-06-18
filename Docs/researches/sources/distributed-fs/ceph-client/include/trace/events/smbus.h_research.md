
# sources/distributed-fs/ceph-client/include/trace/events/smbus.h

## Purpose
Defines SMBus tracepoints for controller operations, reads, replies, and final results, including SMBus protocol type and transfer payloads.

## Important APIs, Types, and Functions
Events are `smbus_write`, `smbus_read`, `smbus_reply`, and `smbus_result`. The first three are `TRACE_EVENT_CONDITION` events that suppress unsupported protocol encodings. Fields cover adapter number/name, address, flags, read/write direction, command, protocol, length, and data bytes. Helper formatting maps SMBus protocol constants to names and prints values conditionally by transfer type.

## Control Flow
I2C/SMBus core code emits write/read request traces before operations, reply traces after read data is available, and result traces with return status. Conditional tracepoints prevent malformed protocol categories from being logged through the detailed format path.

## State and Persistence
No adapter or transfer state is persisted by the header. Trace records copy adapter identity, command metadata, payload bytes, and result codes into trace buffers.

## Dependencies and Integration Points
Depends on I2C/SMBus constants and `linux/tracepoint.h`. Integrates with the I2C core, SMBus host controller drivers, client drivers, and bus-debug tooling.

## Risks
SMBus payloads may contain device configuration or sensor data. Protocol-specific length handling must stay aligned with SMBus core semantics. Conditional filtering means some invalid inputs produce no detailed event, which tooling must account for.

## Test Signals
Signals include SMBus byte/word/block transfers, read/write result traces, invalid protocol tests, adapter-name formatting, PEC/flag coverage, and bus fault injection.
