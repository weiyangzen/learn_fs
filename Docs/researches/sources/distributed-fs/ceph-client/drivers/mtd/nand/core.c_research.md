# sources/distributed-fs/ceph-client/drivers/mtd/nand/core.c

Purpose: implements the generic NAND device framework: erased-page checking, bad/reserved block handling, generic erase helpers, ECC engine setup, and core NAND device initialization.

Important APIs and types: exported functions include `nand_check_erased_ecc_chunk()`, `nanddev_isbad()`, `nanddev_markbad()`, `nanddev_isreserved()`, `nanddev_mtd_erase()`, `nanddev_mtd_max_bad_blocks()`, `nanddev_ecc_engine_init()`, `nanddev_ecc_engine_cleanup()`, `nanddev_init()`, and `nanddev_cleanup()`. It consumes `struct nand_device`, `nand_ops`, `nand_memory_organization`, `nand_pos`, BBT helpers, and ECC helper APIs.

Control flow: erased-buffer checking counts zero bits against a threshold across data, ECC bytes, and optional protected OOB, restoring buffers to `0xff` on tolerated bitflips. Bad-block checks use expert-analysis bypass, then the BBT with lazy low-level `isbad()` lookup, or direct ops when no BBT exists. Markbad calls the low-level hook, updates BBT status to worn, persists through `nanddev_bbt_update()`, and increments `mtd->ecc_stats.badblocks`. Generic erase walks eraseblocks in a requested range and refuses bad/reserved blocks. ECC init reads device-tree user config, selects none/software/on-die/on-host engine, initializes its context, and warns if it is weaker than datasheet requirements. Device init validates ops and memory geometry, derives row conversion shifts, fills MTD geometry, and allocates the BBT.

State and persistence: persistent state is only through low-level erase/markbad hooks and any engine-managed ECC metadata. The generic BBT is in-memory. MTD geometry and ECC context live for the device lifetime.

Dependencies and integration points: integrates MTD core, NAND controller drivers, generic ECC engine selection in `ecc.c`, BBT in `bbt.c`, device tree ECC properties, and chip requirements/defaults supplied by identification layers.

Risks and test signals: risks include lazy BBT cache staleness, mismatched memory geometry shifts, erase range off-by-one handling, and weak ECC accepted with only a warning. Tests should cover invalid ops/geometry, erased chunk thresholds, expert-analysis mode, BBT unknown-to-good/factory-bad transitions, markbad failure and stats, multi-block erase fail address, max-bad-blocks per LUN, all ECC engine types including probe defer, and cleanup after partial ECC init failure.
