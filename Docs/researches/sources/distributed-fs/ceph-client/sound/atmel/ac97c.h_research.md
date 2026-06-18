# sources/distributed-fs/ceph-client/sound/atmel/ac97c.h

## Purpose
This header defines Atmel AC97C register offsets, PDC register aliases, channel/status/mode bit masks, and slot assignment helpers.

## Important APIs, Types, And Functions
Register offsets cover mode, input/output channel assignment, codec/channel holding registers, status and mode registers, interrupt enable/disable/mask, and version. PDC aliases map AC97C transmit/receive pointer/count registers to generic Atmel PDC names. Bit masks define controller enable/reset/VRA, channel ready/empty/overrun/underrun/end events, channel mode sample sizes/endian/channel enable/DMA enable, global status events, and `AC97C_CH_MASK()`/`AC97C_CH_ASSIGN()` helpers for AC97 slot-to-channel mapping.

## Control Flow
The file is declarative. `ac97c.c` uses it during prepare, trigger, IRQ handling, codec access, reset, and PDC programming.

## State And Persistence
No software state is stored. The definitions describe hardware register state persisted in AC97C and PDC MMIO.

## Dependencies And Integration Points
It depends on AC97 slot constants from ALSA AC97 headers and Atmel PDC offsets from kernel Atmel headers through the including source file. It is the local hardware contract for `ac97c.c`.

## Risks And Test Signals
Slot assignment macros assume AC97 slot numbering relative to slot 3. Tests should verify mono/stereo slot assignment, endian selection, DMA enable, and correct ENDTX/ENDRX interrupt behavior.
