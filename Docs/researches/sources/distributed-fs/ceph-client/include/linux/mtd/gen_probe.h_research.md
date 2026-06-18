# sources/distributed-fs/ceph-client/include/linux/mtd/gen_probe.h

## Purpose

Defines the generic map-chip probe shim used to connect CFI/JEDEC probe implementations with the MTD map infrastructure.

## Important APIs, Types, and Functions

Important interfaces are `struct chip_probe` with a `probe_chip()` callback and `mtd_do_chip_probe()` returning an `mtd_info` for a `map_info`.

Source-visible symbols include structs: `struct chip_probe`, `struct mtd_info *mtd_do_chip_probe(struct map_info *map, struct chip_probe *cp);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_GEN_PROBE_H__`.

## Control Flow

The generic probe walks candidate map bases, records chip presence in a chip bitmap, fills CFI private data, then hands the recognized map to a chip driver.

## State and Persistence Behavior

Probe state is transient and held in caller-provided `chip_map` and `cfi_private` data. No persistent state is introduced.

## Dependencies and Integration Points

It includes `flashchip.h`, `map.h`, `cfi.h`, and bit operations; integration is with `do_map_probe()` and CFI/JEDEC probe modules.

Direct includes observed in the source are: `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/map.h>`, `#include <linux/mtd/cfi.h>`, `#include <linux/bitops.h>`.

## Risks and Edge Cases

Incorrect base/chip-map accounting can double-detect interleaved chips or miss aliases. Probes must honor bus width and map access ordering.

## Test Signals

Probe mocked maps with no chip, one chip, interleaved chips, and aliasing behavior; assert returned `mtd_info` and chip bitmap contents.

Source read signal: 23 lines, 615 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
