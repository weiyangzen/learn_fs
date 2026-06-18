# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_esmt.c

## Purpose
`nand_esmt.c` provides ESMT manufacturer hooks for the raw NAND core. It customizes extended-ID decoding for SLC ESMT parts by extracting ECC requirements from the fifth ID byte and broadens bad-block marker scanning for known ESMT SLC marker placement variance.

## Important APIs, types, and functions
- `esmt_nand_decode_id()` calls the generic `nand_decode_ext_id()` and then, for SLC chips with at least five ID bytes, maps `chip->id.data[4] & 0x3` to ECC requirements of 4, 2, or 1 bit per 512-byte step.
- `esmt_nand_init()` sets `NAND_BBM_FIRSTPAGE`, `NAND_BBM_SECONDPAGE`, and `NAND_BBM_LASTPAGE` for SLC chips.
- `esmt_nand_manuf_ops` exports `.detect` and `.init` hooks to the manufacturer descriptor table in `nand_ids.c`.

## Control flow
During non-ONFI/non-JEDEC manufacturer detection, `nand_base.c` calls the ESMT `.detect` hook through the manufacturer descriptor. The hook first derives normal geometry through generic extended-ID decoding, then updates `nand_device` ECC requirements. Later, scan-tail manufacturer initialization calls `.init`, where SLC chips opt into checking all three common BBM locations before BBT creation.

## State and persistence behavior
The file does not allocate private state and has no cleanup hook. It mutates in-memory chip/device state: ECC requirement properties and `chip->options` BBM flags. Those flags affect later persistent behavior indirectly because BBT scans and bad-block marking may read or write markers in first, second, and last block pages.

## Dependencies and integration points
It depends on `nand_decode_ext_id()`, `nand_is_slc()`, `nanddev_set_ecc_requirements()`, and the raw NAND manufacturer-ops dispatch. Its only external integration is the `NAND_MFR_ESMT` entry in `nand_ids.c`.

## Risks and edge cases
- The ECC mapping is only applied to SLC chips with at least five ID bytes; other ESMT parts fall back to generic requirements.
- An unknown ECC code triggers `WARN(1)` and clears the requirement step size, which may force later ECC selection to maximize or use user/controller defaults.
- Checking first, second, and last BBM pages is conservative but may classify blocks bad if any one of the scanned locations contains non-`0xff` metadata on unusual layouts.

## Test signals
Useful tests include ESMT SLC IDs with fifth-byte ECC codes 0, 1, 2, and 3; BBT scanning against first-page, second-page, and last-page factory markers; non-SLC ESMT detection; and probe behavior when ECC requirements are absent and controller ECC caps must choose a fallback.
