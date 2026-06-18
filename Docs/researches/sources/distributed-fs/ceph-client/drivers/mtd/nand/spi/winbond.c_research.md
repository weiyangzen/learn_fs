<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/winbond.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/winbond.c

Purpose: Winbond SPI NAND support for W25/W35 families, including high-speed configuration, volatile configuration register writes, OOB layout variants, ECC status decoding, and multi-die target selection.

Important APIs/types/functions: Defines Winbond select-target op template/fill helper, OOB layout callbacks for W25M02GV, W25N01KV/W25N02KV, W25N01JW/W35N01JW, `w25m02gv_select_target()`, `w25n02kv_ecc_get_status()`, `w25n0xjw_hs_cfg()`, `w35n0xjw_write_vcr()`, `w35n0xjw_vcr_cfg()`, the `winbond_spinand_table`, `winbond_spinand_init()`, and `winbond_spinand_manufacturer`.

Control flow: Core matches device IDs, selects family-specific layouts and optional configure hooks. Multi-die W25M02GV target selection sends a vendor die-select operation. High-speed JW/JW-like parts configure feature/VCR registers during chip setup. Init iterates targets where needed to apply configuration.

State and persistence: Runtime state is mostly core `cur_target` plus chip configuration state. Persistent/semi-persistent state includes die-select register, volatile configuration registers, high-speed mode bits, block locks, and OOB metadata.

Dependencies/integration: Uses SPI-MEM custom ops beyond standard core templates, SPI NAND exported helpers, `SPINAND_SELECT_TARGET`, and optional `configure_chip` table hooks.

Risks: VCR/high-speed setup is bus-interface sensitive; bad configuration can make subsequent operations unreliable. Multi-die target selection must be applied before any per-target register or media operation. Several OOB layouts and ECC decoders mean table-to-part mapping must remain precise.

Test signals: Probe every listed family cluster, target-switch read/write/erase on W25M02GV, high-speed config on JW/W35 parts, ECC status mapping including W25N04KV 5-8 corrected range, OOB layout verification, and fallback on controllers that cannot support faster variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/winbond.c -->
