# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4780_bch.c

Purpose: this is the Ingenic JZ4780 BCH hardware ECC provider for the common Ingenic ECC API. It supports configurable BCH strength, parity byte count, a fixed 200 MHz ECC clock target, and hardware-reported bitmask/index corrections.

Important APIs, types, and functions: provider operations are `jz4780_bch_disable()`, `jz4780_calculate()`, and `jz4780_correct()`. Helpers include `jz4780_bch_reset()`, `jz4780_bch_write_data()`, `jz4780_bch_read_parity()`, `jz4780_bch_wait_complete()`, and probe wrapper `jz4780_bch_probe()`.

Control flow: probe calls `ingenic_ecc_probe()` then sets the ECC clock to `BCH_CLK_RATE`. Calculate locks the ECC mutex, resets for encoding with size/parity/strength fields, writes data to `BCH_BHDR`, polls for `BCH_BHINT_ENCF`, reads parity bytes, disables the block, and unlocks. Correct locks, resets for decode, writes data and stored ECC, polls `BCH_BHINT_DECF`, handles uncorrectable status, and for correctable errors reads each `BCH_BHERR` entry, using its 16-bit mask and index to XOR two data bytes per reported location.

State and persistence: persistent state is inherited from `struct ingenic_ecc`. Operation state is in BCH count, control, interrupt, parity, and error registers. The mutex serializes all encode/decode use. The provider leaves the clock rate request in effect after probe.

Dependencies and integration points: the file registers a platform driver for `ingenic,jz4780-bch`, uses `clk_set_rate()`, `readl_poll_timeout()`, and feeds the shared `ingenic_ecc_ops` contract consumed by `ingenic_nand_drv.c`.

Risks: reset writes `params->strength` directly into the BSEL field without local range validation. Correct uses hardware indexes to XOR `buf[(index * 2)]` and the next byte, so bad hardware status or mismatched step size can corrupt memory. `clk_set_rate()` return value is ignored. Timeout is fixed at 100 ms and interrupts are polled rather than used.

Test signals: validate probe clock programming, ECC generation for expected JZ4780 NAND strengths, corrected bit-count returns, uncorrectable `-EBADMSG`, timeout paths, erased-page reads, and concurrent access serialization through the shared mutex.
