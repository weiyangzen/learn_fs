# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/regs.h

## Purpose
This header is the ZL3073x register map contract. It encodes logical register descriptors, hardware limits, bit masks, mode constants, mailbox registers, HWREG access registers, and flash utility registers.

## Important APIs and constants
Hardware limits include maximum channels, references, outputs, synths, and pin counts. `ZL_REG()` and `ZL_REG_IDX()` encode page, offset, byte size, and maximum indexed offset into one integer consumed by `core.c`. Macros decode offset, page, size, max offset, and physical register address. The header defines page 0 identity/status registers, page 2 monitor/status registers, page 4 measurement controls, page 5 DPLL controls, page 9 synth/output controls, pages 10/12/13/14 mailboxes, page 255 HWREG access, and flash-mode registers.

## Control flow and state
There is no executable control flow, but every register access helper validates descriptor size and index range against these encodings. Mailbox constants define which multi-register operations need `multiop_lock`.

## Dependencies and integration points
All ZL3073x source files consume this header either directly or through state headers. It depends on Linux bitfield and bit macros.

## Risks and tests
Wrong register sizes, page numbers, masks, or indexed strides would corrupt hardware access. The encoded `max_offset` field is a key safety check. Tests should include compile-time mask use, runtime invalid-index detection, register size mismatch fault paths, and hardware smoke tests for each mailbox page and flash-mode register group.
