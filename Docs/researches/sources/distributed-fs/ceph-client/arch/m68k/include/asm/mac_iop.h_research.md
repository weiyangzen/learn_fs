<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_iop.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_iop.h

## Purpose
`mac_iop.h` defines Apple Macintosh I/O Processor register layout, message protocol constants, and kernel message structures for SCC and ISM IOPs.

## Important APIs, Types, and Functions
It defines IOP base addresses for IIfx and Quadra, status/control bits, IOP counts, channel/message sizes, channel states, message statuses, shared-memory offsets, `struct mac_iop`, `struct iop_msg`, presence globals, and APIs for listening, sending, completing, uploading/downloading/comparing code, polling ISM IRQs, and registering interrupts.

## Control Flow, State, and Persistence
Message state persists in `struct iop_msg` queues and in IOP shared RAM. The control model sends messages by channel, waits for reply/complete states, and handles unsolicited messages through registered handlers.

## Dependencies and Integration Points
Mac serial, ADB/floppy/storage-management paths can use SCC and ISM IOPs. Interrupt registration integrates with Mac IRQ routing.

## Risks
The hardware has bypass and firmware-mediated modes; using the wrong register union can corrupt devices. Message queues require correct completion handling to avoid stuck channels. Shared-memory offsets are protocol ABI.

## Test Signals
Signals include SCC serial through IOP, ISM polling, message send/reply completion, unsolicited handler delivery, firmware upload/download comparison, and interrupt registration on IIfx/Quadra models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_iop.h -->
