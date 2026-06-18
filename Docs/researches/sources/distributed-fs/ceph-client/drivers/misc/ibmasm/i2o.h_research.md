# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/i2o.h

## Purpose
`i2o.h` defines the I2O message wrapper used by the IBM ASM low-level mailbox transport.

## Important APIs, Types, and Functions
Packed `struct i2o_header` contains version, flags, size, target/initiator fields, function, and context. `I2O_HEADER_TEMPLATE` supplies default values. `struct i2o_message` combines the header and payload pointer field. Inline helpers are `outgoing_message_size()` and `incoming_data_size()`.

## Control Flow
Outgoing command code calculates a 32-bit-word message size from payload length, capped at `I2O_COMMAND_SIZE`. Incoming interrupt code multiplies the header message-size field by four to get payload span passed to dot-command dispatch.

## State and Persistence
No state is stored. Structures map transient MMIO mailbox frames.

## Dependencies and Integration Points
It is consumed by `lowlevel.c` and depends on packed layout matching the service processor mailbox protocol.

## Risks and Edge Cases
`struct i2o_message` represents `data` as a pointer even though low-level code copies payload bytes to `&message->data`; this relies on the historical memory layout rather than normal pointer semantics. Incoming size calculation trusts hardware-provided `message_size`.

## Test Signals
Validate outgoing word-size rounding, max payload capping, header bytes written to MMIO, and incoming size handling for minimum and maximum mailbox frames.
