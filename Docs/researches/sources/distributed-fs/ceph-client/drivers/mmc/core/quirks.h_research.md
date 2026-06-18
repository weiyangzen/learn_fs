<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/quirks.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/quirks.h

## Purpose
`quirks.h` defines card-specific SD, MMC, eMMC EXT_CSD, and SDIO fixup tables plus the matcher that applies them to `struct mmc_card`. It centralizes known hardware and firmware workarounds for broken cache flush, power-off notification, tuning, discard, CMD23, read timeout, secure erase/trim, HPI, metadata reporting, SDIO byte mode, interrupt polling, and rate limits.

## Important APIs, Types, And Functions
Important data tables are `mmc_sd_fixups[]`, `mmc_blk_fixups[]`, `mmc_ext_csd_fixups[]`, `sdio_fixup_methods[]`, and `sdio_card_init_methods[]`. Helper functions are `mmc_fixup_of_compatible_match()` and `mmc_fixup_device()`. The tables use macros such as `MMC_FIXUP`, `_FIXUP_EXT`, `MMC_FIXUP_EXT_CSD_REV`, `SDIO_FIXUP`, and `SDIO_FIXUP_COMPATIBLE`, and call vendor fixup functions like `add_quirk`, `add_quirk_sd`, `add_quirk_mmc`, `add_limit_rate_quirk`, and `wl1251_quirk`.

## Control Flow
Callers pass a card and one of the fixup tables to `mmc_fixup_device()`. The function computes the card revision, iterates until `END_FIXUP`, and checks manufacturer, OEM, product name, SDIO CIS vendor/device, EXT_CSD revision, revision range, optional OF compatible child match, year, and month. Matching entries log the callback symbol and call the stored vendor fixup with the table data. OF-compatible matching scans child nodes under the host device node.

## State And Persistence
The tables are static read-only policy. Persistent effects are changes made by vendor fixup callbacks to `struct mmc_card`, such as setting quirk bits or limiting rates. These quirk bits later influence discard/trim, cache flush, CMD23 use, tuning, HPI enablement, SDIO behavior, and block-layer limits.

## Dependencies And Integration Points
The file depends on OF helpers, SDIO IDs, local card/fixup definitions, CID fields, CIS fields, EXT_CSD revision, and card quirk callbacks. It is included by core/card initialization code rather than compiled as an independent translation unit. `mmc.c` explicitly applies `mmc_ext_csd_fixups[]` after decoding the EXT_CSD revision, and other MMC/SD/SDIO paths use the other tables during card setup.

## Risks And Edge Cases
The tables encode real hardware errata, so overly broad matches can disable useful features or reduce performance on unaffected cards, while too-narrow matches leave data-corruption bugs active. Manufacturing-date and revision matching must handle vendor reporting errors. Product-name comparisons use fixed-size CID product names. OF-compatible quirks depend on board descriptions. Adding new quirks requires choosing the right table so required fields, especially EXT_CSD revision, are available at application time.

## Test Signals
Signals include matching known affected cards, non-matching adjacent card revisions/dates, expected quirk bits in debug output, changed block limits for broken discard/trim/cache/CMD23 cases, disabled HPI for affected eMMC revisions, SDIO quirks applied by vendor/device or compatible string, and no regressions on unaffected cards from the same manufacturer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/quirks.h -->
