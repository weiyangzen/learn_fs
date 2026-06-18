# sources/distributed-fs/ceph-client/drivers/tty/serial/sunsab.h

## Purpose
This header models the SAB82532 asynchronous register layout and names the bit fields used by `sunsab.c`.

## Important APIs, Types, And Functions
`struct sab82532_async_rd_regs`, `struct sab82532_async_wr_regs`, and `struct sab82532_async_rw_regs` describe read-only, write-only, and read/write views over the same register block. `union sab82532_async_regs` lets the driver access the correct semantic view. `union sab82532_irq_status` overlays ISR0/ISR1 as a 16-bit status word for compact interrupt dispatch.

The rest of the header defines command bits, mode bits, data-format fields, FIFO settings, baud/config registers, version/status bits, global interrupt bits, interrupt masks/status, port interrupt bits, and internal software irqflag bits.

## Control Flow
There is no executable flow. The C driver uses the register structures for MMIO offsets and the macros to build startup, interrupt, termios, transmit, receive, and modem-control programming sequences.

## State And Persistence
The header does not store state. Its software flag definitions, especially `SAB82532_ALLS`, `SAB82532_XPR`, and `SAB82532_REGS_PENDING`, define how `sunsab.c` persists channel status in memory.

## Dependencies And Integration Points
It depends on Linux integer aliases such as `u8` being available in the including file. It is private to the SAB driver and tightly coupled to the Siemens SAB82532 async register map.

## Risks
The register structs depend on exact padding and byte offsets. Any mistake changes every MMIO access. The same numeric bits are reused in different register contexts, so caller-side register selection must be correct. The volatile union exposes raw hardware state without additional type safety.

## Test Signals
Compile-time use through `sunsab.c`, runtime channel initialization, interrupt masking/acknowledgment, FIFO read/write, modem status, and termios conversion are the practical validation signals for this header.
