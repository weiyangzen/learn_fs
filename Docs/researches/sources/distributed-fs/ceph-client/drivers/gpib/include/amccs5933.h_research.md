# sources/distributed-fs/ceph-client/drivers/gpib/include/amccs5933.h

## Purpose

`amccs5933.h` defines register offsets and mailbox/interrupt bit helpers for AMCC S5933 PCI bridge chips. This subset does not show a direct user, but it is part of the GPIB PCI bridge vocabulary.

## Important APIs and Constants

- `MBEF_REG`, `INTCSR_REG`, and `BMCSR_REG` identify mailbox empty/full, interrupt control/status, and bus-master control/status registers.
- `INCOMING_MAILBOX_REG(mailbox)` maps mailbox index to incoming mailbox register offset.
- `OUTBOX_EMPTY_INTR_BIT`, `INBOX_FULL_INTR_BIT`, `INBOX_INTR_CS_BIT`, and `INTR_ASSERTED_BIT` encode INTCSR interrupt controls/status.
- `INBOX_BYTE_BITS()`, `INBOX_SELECT_BITS()`, `OUTBOX_BYTE_BITS()`, and `OUTBOX_SELECT_BITS()` select mailbox bytes and mailbox numbers.
- `MBOX_FLAGS_RESET_BIT` resets mailbox flags in BMCSR.

## Control Flow and Integration

There is no runtime control flow. Drivers include this header when programming S5933 mailbox or interrupt registers.

## State and Persistence Behavior

No kernel state is declared. State lives in hardware mailbox, interrupt, and bus-master registers.

## Dependencies

The file uses `extern inline int` helper definitions without an include guard. It relies on C compiler/kernel build semantics for inline definitions and on including code to avoid duplicate-symbol surprises.

## Risks and Test Signals

Because helpers mask mailbox/byte numbers to two bits, invalid callers can silently wrap to a different mailbox. Test signals are bridge interrupt assertion/clear behavior, mailbox status transitions, and no duplicate inline-linkage build warnings across supported compiler modes.
