<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.h

## Purpose
`mmc_ops.h` declares the low-level MMC command helper interface used inside the MMC core and by a few GPL-exported consumers. It is the contract between enumeration, block, tuning, maintenance, and test code and the command implementation in `mmc_ops.c`.

## Important APIs, Types, And Functions
The header defines `enum mmc_busy_cmd` with busy contexts for CMD6 switch, erase, HPI, reliable single operations, and generic I/O. It forward-declares `struct mmc_host`, `struct mmc_card`, and `struct mmc_command`, then declares helpers for card select/deselect, DSR, GO_IDLE, OP_COND, RCA, ADTC data, CSD/CID/EXT_CSD/OCR/SPI CRC, bus tests, switch status, busy command preparation/polling, EXT_CSD switching, BKOPS, CMDQ, sanitize, and the inline `unstuff_bits()`.

## Control Flow
This file has no runtime flow except `unstuff_bits()`, which extracts a bitfield from a 128-bit big-endian-style MMC response array. Callers pass response words, start bit, and size; the helper computes the response word offset, shifts the selected bits, pulls from the previous word when the field crosses a 32-bit boundary, and masks the final value.

## State And Persistence
The header owns no persistent state. Its declarations enable command helpers that mutate host/card/hardware state in other files. The inline bit extraction is deterministic and only reads the provided response buffer.

## Dependencies And Integration Points
`mmc.c`, `mmc_test.c`, block code, SD operation helpers, and host logic include this header to avoid duplicating command construction. The `unstuff_bits()` inline is especially important for CID and CSD decoding in `mmc.c`. The busy command enum is interpreted by `mmc_poll_for_busy()` in `mmc_ops.c`.

## Risks And Edge Cases
The `unstuff_bits()` helper assumes valid field sizes and valid response layout; misuse with a zero or oversized range, wrong start bit, or a short response buffer would silently decode bad card metadata. Header/API drift between declarations and exported symbols would break consumers. The busy enum must stay synchronized with `mmc_busy_cb()` switch handling.

## Test Signals
Compile coverage across MMC core users is the primary signal. Functional signals include correct CID/CSD decoding through `unstuff_bits()`, successful calls to all declared helpers from enumeration and block paths, and no missing-prototype or enum-handling warnings when adding new busy command types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/mmc_ops.h -->
