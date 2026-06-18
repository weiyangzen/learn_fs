# sources/distributed-fs/ceph-client/include/linux/mtd/nand-ecc-mtk.h

## Purpose

Defines the MediaTek NAND ECC engine interface used by NAND controller drivers to encode/decode pages through a shared ECC hardware block.

## Important APIs, Types, and Functions

Key items are `enum mtk_ecc_mode`, `enum mtk_ecc_operation`, `struct mtk_ecc_stats`, `struct mtk_ecc_config`, `struct mtk_ecc`, and exported helpers for getting/releasing the engine, enabling/disabling it, and waiting for completion.

Source-visible symbols include structs: `struct device_node;`, `struct mtk_ecc;`, `struct mtk_ecc_stats`, `struct mtk_ecc_config`, `struct mtk_ecc *of_mtk_ecc_get(struct device_node *);`; enums: `enum mtk_ecc_mode`, `enum mtk_ecc_operation`, `enum mtk_ecc_operation op;`, `enum mtk_ecc_mode mode;`; typedefs: none visible in this header; prototypes: `int mtk_ecc_encode(struct mtk_ecc *, struct mtk_ecc_config *, u8 *, u32);`, `void mtk_ecc_get_stats(struct mtk_ecc *, struct mtk_ecc_stats *, int);`, `int mtk_ecc_wait_done(struct mtk_ecc *, enum mtk_ecc_operation);`, `int mtk_ecc_enable(struct mtk_ecc *, struct mtk_ecc_config *);`, `void mtk_ecc_disable(struct mtk_ecc *);`, `void mtk_ecc_adjust_strength(struct mtk_ecc *ecc, u32 *p);`, `unsigned int mtk_ecc_get_parity_bits(struct mtk_ecc *ecc);`, `void mtk_ecc_release(struct mtk_ecc *);`; representative macros: `__DRIVERS_MTD_NAND_MTK_ECC_H__`.

## Control Flow

A controller builds an ECC config describing mode, operation, strength, sector count, length, and buffer addresses, enables the engine for encode or decode, waits for interrupt/poll completion, consumes stats, then disables/releases it.

## State and Persistence Behavior

Runtime state belongs to the hardware engine and the config/stat objects. Corrected, failed, and max-bitflip counts are transient per operation; no persistent metadata is defined.

## Dependencies and Integration Points

It depends on Linux types, device tree lookup, and the MediaTek ECC driver. It integrates with NAND ECC engine selection and MediaTek NFI host drivers.

Direct includes observed in the source are: `#include <linux/types.h>`.

## Risks and Edge Cases

Mismatched sector size, strength, and DMA/NFI mode can cause silent ECC miscorrection. Completion handling and stats propagation must match MTD bitflip/ECC error semantics.

## Test Signals

Run encode/decode vectors at each supported strength, injected bitflip tests, timeout/error paths, and shared-engine get/release lifecycle tests.

Source read signal: 47 lines, 1213 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
