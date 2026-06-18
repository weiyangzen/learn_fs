# sources/distributed-fs/ceph-client/drivers/mmc/core/card.h

## Purpose
Private card helpers for state flags, identity helpers, fixup table definitions, vendor IDs, and quirk manipulation.

## Important APIs, Types, And Functions
- State bits cover present, read-only, block addressing, SDXC, removed, suspended, and SDUC.
- `struct mmc_fixup` defines CID/CIS/OF-compatible matching and a `vendor_fixup()` callback.
- `MMC_FIXUP*`, `SDIO_FIXUP*`, and `END_FIXUP` build quirk tables.
- Inline helpers add/remove quirks, set rate limits, and model special devices like `wl1251`.

## Control Flow
Card identification fills fields, then fixup code walks tables and applies matched callbacks before higher-level drivers use the card.

## State And Persistence
Mutates `struct mmc_card` state, quirks, rate limits, CIS fields, and SDIO metadata for the card lifetime.

## Dependencies And Integration Points
Depends on public card definitions and SDIO IDs; used by protocol, quirk, and block code.

## Risks And Edge Cases
Overbroad fixups can disable features or enable unsafe commands. CID revision/date matching must account for vendor firmware variation.

## Test Signals
Expected debugfs `quirks`, probe behavior for known broken cards, and regression cases for CMD23, trim, secure erase, SDIO, and rate-limit quirks.
