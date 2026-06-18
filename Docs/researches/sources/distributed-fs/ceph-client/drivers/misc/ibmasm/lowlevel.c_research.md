# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/lowlevel.c

## Purpose
`lowlevel.c` implements the IBM ASM Condor mailbox transport. It sends current commands as I2O-wrapped dot-command messages and handles service-processor interrupts.

## Important APIs, Types, and Functions
Public functions are `ibmasm_send_i2o_message()` and `ibmasm_interrupt_handler()`. A static `i2o_header` initialized from `I2O_HEADER_TEMPLATE` is reused for outgoing messages.

## Control Flow
Sending computes the dot-command size, rejects commands larger than their allocated buffer, caps to I2O payload size, obtains an inbound MFA, copies the I2O header and command payload into MMIO message memory, and posts the MFA back inbound. The IRQ handler first verifies SP interrupt status, handles pending remote input and clears the mouse interrupt, reads an outbound MFA, dispatches its message data through `ibmasm_receive_message()`, returns the MFA, and reports handled.

## State and Persistence
Transport state is in hardware mailbox queues and the service processor's current command. The static header's `message_size` is updated for each send.

## Dependencies and Integration Points
It depends on `lowlevel.h` mailbox helpers, `i2o.h`, `dot_command.h`, `remote.h`, and the command/event/heartbeat dispatcher. It is registered as the shared IRQ handler by `module.c`.

## Risks and Edge Cases
The static header is shared across all service processors, which is harmless only if sends are serialized or the field is not concurrently observed. If no valid outbound MFA is returned, the handler still calls `set_mfa_outbound()` with the invalid value. Incoming message sizes are hardware-derived and passed through only later dot-command validation.

## Test Signals
Validate inbound MFA unavailable failure, oversized command rejection/capping, exact MMIO bytes for header and payload, interrupt `IRQ_NONE` when not pending, remote-input predispatch, invalid outbound MFA handling, and shared IRQ behavior with UART.
