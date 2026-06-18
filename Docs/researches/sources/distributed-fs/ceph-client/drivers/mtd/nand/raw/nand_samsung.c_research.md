# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_samsung.c

Purpose: this manufacturer file decodes Samsung raw NAND IDs and applies Samsung-specific initialization options for page/OOB/block geometry, ECC requirements, subpage-write restrictions, and bad-block marker placement.

Important APIs, types, and functions: `samsung_nand_manuf_ops` provides `.detect` and `.init`. `samsung_nand_decode_id()` handles both newer 6-byte MLC Samsung IDs and the generic extended-ID path. `samsung_nand_init()` applies large-page and BBM options.

Control flow: detect chooses the Samsung 6-byte MLC decode when ID length is 6 and the sixth byte is nonzero; it extracts page size, OOB size, eraseblock size, and ECC strength from extended ID bytes. Other devices use `nand_decode_ext_id()`, with special SLC cases for K9F4G08U0D ECC and K9F1G08U0E 21 nm no-subpage-write detection. Init then sets Samsung large-page options and chooses last-page BBM for MLC or first/second-page BBM for SLC.

State and persistence: no private state is allocated. The file updates memory geometry, MTD sizes, ECC requirements, and `chip->options`.

Dependencies and integration points: it relies on raw NAND ID bytes, `nand_is_slc()`, generic extended-ID decoding, `nanddev_set_ecc_requirements()`, and MTD geometry fields consumed later by core attach and controller ECC setup.

Risks: invalid or future Samsung extended-ID encodings trigger warnings and may leave incomplete OOB/ECC interpretation. The MLC ECC mapping includes high strengths at 1024-byte steps, which controller support must later satisfy. Subpage-write suppression is narrow to a specific ID pattern.

Test signals: verify decoding for 6-byte Samsung MLC IDs, SLC fallback IDs, ECC requirement propagation, OOB and eraseblock sizes, BBM option selection, large-page options, and no-subpage-write behavior for K9F1G08U0E 21 nm devices.
