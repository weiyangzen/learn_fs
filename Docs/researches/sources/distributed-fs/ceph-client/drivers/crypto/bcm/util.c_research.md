# sources/distributed-fs/ceph-client/drivers/crypto/bcm/util.c

Purpose: utility implementation for the Broadcom SPU crypto driver. It provides scatterlist slicing/copy helpers, counter arithmetic, software hash fallback/helper execution, debugfs statistics, algorithm-name formatting, and CCM integer formatting.

Important APIs and functions: `spu_sg_at_offset()`, `sg_copy_part_to_buf()`, `sg_copy_part_from_buf()`, `spu_sg_count()`, and `spu_msg_sg_add()` manage scatterlist offsets and fragments; `add_to_ctr()` increments a 128-bit big-endian counter; `do_shash()` runs synchronous kernel shash with optional key; `__dump_sg()` is DEBUG-only packet dumping; `spu_alg_name()` maps common SPU enum pairs to Crypto API names; `spu_setup_debugfs()` and `spu_free_debugfs()` manage a debugfs stats file; `format_value_ccm()` writes a 32-bit value into a variable-length CCM field.

Control flow: request-building code calls SG helpers while assembling DMA messages. Hash setup can call `do_shash()` for software precomputation. Debugfs read walks `iproc_priv` counters and, for SPU-M, reads per-SPU FIFO high-water registers.

State and persistence: persistent state is external in `iproc_priv`, atomic counters, debugfs dentries, and mapped hardware registers. This file allocates transient buffers for debugfs reads and shash descriptors.

Dependencies and integration points: uses Linux scatterlist, Crypto API shash, debugfs, ioread32, `cipher.h`, `spu.h`, and `util.h`. It is shared by SPU-M/SPU2 code and higher-level Broadcom crypto paths.

Risks: `spu_msg_sg_add()` updates caller SG pointers and skip state and is sensitive to partial-entry math; `do_shash()` currently calls update with `data1` unconditionally, so callers must pass a valid pointer when `data1_len` is nonzero; debugfs stats are bounded by a fixed 2048-byte buffer and can truncate; `format_value_ccm()` only represents up to 32-bit values even if `len` is larger.

Test signals: SG split/copy tests across offsets and zero lengths, counter carry tests, shash known-answer tests, debugfs read under active counters, and CCM value formatting for 2/3/4-byte lengths.
