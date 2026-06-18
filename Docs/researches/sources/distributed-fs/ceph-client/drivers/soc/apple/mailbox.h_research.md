# sources/distributed-fs/ceph-client/drivers/soc/apple/mailbox.h

## Purpose
This private Apple mailbox header declares the message format, mailbox state, and exported mailbox helper APIs used by Apple coprocessor protocol drivers.

## Important APIs, Types, And Functions
`struct apple_mbox_msg` encodes a 64-bit `msg0` and 32-bit `msg1`. `struct apple_mbox` stores device/MMIO/hardware data, active state, IRQs, RX/TX locks, TX completion, and the receive callback. Function declarations cover mailbox lookup, start/stop, polling, and sending.

## Control Flow
The header defines the callback control contract: users install `mbox->rx` and `mbox->cookie`, call `apple_mbox_start()`, then receive callbacks for incoming FIFO messages. Outgoing messages flow through `apple_mbox_send()`.

## State, Persistence, And Dependencies
State is runtime-only and owned by `mailbox.c`. The header depends on Linux device and type definitions.

## Integration Points
Included by Apple RTKit and mailbox implementation files. It is private to the Apple SoC driver folder rather than a public mailbox framework API.

## Risks
The exposed `struct apple_mbox` lets consumers mutate callbacks and state directly, so concurrent consumers are not supported. It does not encode ownership beyond DT device links.

## Test Signals
Compile coverage for RTKit and mailbox, plus runtime tests that install callbacks before start and validate send/receive message field preservation.
