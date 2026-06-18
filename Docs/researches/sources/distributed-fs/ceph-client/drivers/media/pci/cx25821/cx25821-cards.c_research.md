# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-cards.c

Purpose: declares the cx25821 board table used by core device setup and V4L2 capability reporting.

Important APIs and data: `cx25821_boards[]` contains `UNKNOWN_BOARD` with safe zero clock default and `CX25821_BOARD` named `"CX25821"` with `portb = CX25821_RAW` and `portc = CX25821_264`.

Control flow: `cx25821_dev_setup` selects board index 1 and later reports `cx25821_boards[dev->board].name`. The table does not perform autodetection logic itself.

State and persistence: static board metadata only. It is process-global driver data and not mutated at runtime.

Dependencies and integration points: depends on `cx25821.h` for board enum values and structure definitions. The core driver and V4L2 querycap path consume this table.

Risks: the core currently hard-codes `dev->board = 1`, so table expansion alone will not add real board autodetection. Unknown board has safe clock but may not be reachable because incorrect hardware is rejected earlier.

Test signals: probe logs and `VIDIOC_QUERYCAP` card names should reflect expected board table entries. Build coverage catches structure drift.
