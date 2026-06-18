# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_toshiba.c

Purpose: this manufacturer file decodes Toshiba raw NAND IDs, configures Toshiba SLC ECC requirements, supports BENAND on-die ECC reads, and applies model-specific timing/scrambling/pairing quirks.

Important APIs, types, and functions: `toshiba_nand_manuf_ops` exposes `.detect` and `.init`. BENAND support is implemented by `toshiba_nand_benand_init()`, `toshiba_nand_read_page_benand()`, `toshiba_nand_read_subpage_benand()`, and `toshiba_nand_benand_eccstatus()`. Model-specific interface choosers cover `TC58TEG5DCLTA00`, `TC58NVG0S3E`, and `TH58NVG2S3HBAI4` families.

Control flow: detect runs generic extended-ID decode, adjusts 24 nm raw SLC OOB size, and derives SLC ECC strength from the sixth ID byte. Init marks SLC BBM pages, enables BENAND on-die ECC callbacks when requested and detected, and then installs model-specific timing callbacks; the TC58TEG5DCLTA00 path also enables scrambling and a distance-3 pairing scheme.

State and persistence: no private allocation is used. The file changes ECC callback pointers, ECC geometry, OOB layout, MTD pairing scheme, and NAND options. BENAND ECC status updates MTD ECC stats after reads.

Dependencies and integration points: it uses raw NAND exec_op for BENAND ECC status command `0x7A`, generic raw read/page helpers, `nand_get_large_page_ooblayout()`, ONFI timing fill helpers, `nand_choose_best_sdr_timings()`, and the MTD pairing API.

Risks: BENAND detailed ECC status requires exec_op; otherwise it falls back to coarse status bits and threshold-based correction counts. Raw page operations are disabled for BENAND. Model string matches are exact or prefix based, so new revisions may miss quirks. Custom timing patches rely on manually maintained datasheet values.

Test signals: validate ID decoding for 43/32/24 nm SLC, BENAND on-die ECC read/subpage behavior, ECC stats for correctable and uncorrectable cases, OOB layout exposure, timing selection for listed models, scrambling and pairing setup, and fallback status handling when ECC status read is unsupported.
