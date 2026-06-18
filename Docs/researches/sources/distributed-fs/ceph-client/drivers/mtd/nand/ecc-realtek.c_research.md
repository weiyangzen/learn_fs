# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-realtek.c

Purpose: provides a Realtek RTL93xx on-host hardware ECC engine for a vendor-specific BCH OOB layout used by supported 2 KiB-page NAND systems.

Important APIs and types: `rtl_ecc_engine` owns the generic `nand_ecc_engine`, mutex, noncoherent DMA buffer, DMA address, and regmap. `rtl_ecc_ctx` stores the engine pointer, request tweak context, step count, BCH mode, strength, and parity size. Engine hooks are `rtl_ecc_init_ctx()`, `rtl_ecc_cleanup_ctx()`, `rtl_ecc_prepare_io_req()`, and `rtl_ecc_finish_io_req()`.

Control flow: probe maps registers through regmap, allocates a single noncoherent DMA buffer, initializes an external on-host `nand_ecc_engine`, and registers it globally. Context init strictly validates geometry and user ECC config: 2048-byte page, at least 64 OOB bytes, BCH, strength 6, OOB placement, and 512-byte step. It installs an OOB layout with 6 free bytes per step, reserving the first two for bad-block indicators, and parity after all free-byte regions. Prepare tweaks partial requests and, on writes, runs each 512-byte step through the engine to fill parity. Finish restores writes directly; on reads it decodes each step, falls back to `nand_check_erased_ecc_chunk()` for erased chunks that hardware reports badly, updates ECC stats, restores the original request, and returns max bitflips or `-EBADMSG`.

State and persistence: runtime state is the shared DMA staging buffer and per-NAND context. Persistent state is the fixed OOB arrangement containing protected free bytes and parity bytes.

Dependencies and integration points: depends on generic NAND ECC registry, MTD OOB layouts, DMA sync APIs for noncoherent memory, regmap MMIO, platform OF compatible `realtek,rtl9301-ecc`, and erased-page checking from NAND core.

Risks and test signals: risks include the intentionally narrow geometry support, protected bad-block indicator compatibility, noncoherent DMA synchronization, polling timeout, and handling all-ones erased chunks. Tests should cover unsupported geometry/config rejection, OOB layout offsets, encode/decode per step, bitflip stat accumulation, uncorrectable reads, erased-chunk fallback, raw mode no-op, cleanup unregistering the engine, and concurrent requests serialized by the mutex.
