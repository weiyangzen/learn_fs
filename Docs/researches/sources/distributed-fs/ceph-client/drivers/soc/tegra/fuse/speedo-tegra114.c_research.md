# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra114.c

## Purpose

`speedo-tegra114.c` converts Tegra114 SKU, revision, and speedo fuse values into CPU and SoC speedo IDs and process IDs stored in `struct tegra_sku_info`. These bins are consumed by later voltage, clock, and SoC policy code.

## Important APIs, Types, and Functions

The exported init hook is `tegra114_init_speedo_data()`. Internal logic is `rev_sku_to_speedo_ids()`, which maps SKU IDs to CPU/SoC speedo IDs and threshold table index. Static threshold arrays `cpu_process_speedos` and `soc_process_speedos` define two process corners per threshold index.

## Control Flow

The common fuse init path calls `tegra114_init_speedo_data()` after revision/SKU data is known. The function checks threshold-table sizes at build time, derives speedo IDs from SKU, applies an A01-specific fuse override for CPU speedo ID, reads CPU speedo from fuse 0x12c plus 1024 and SoC speedo from fuse 0x134, then scans the threshold arrays to assign process IDs.

## State and Persistence Behavior

The only mutable state is the caller-provided `tegra_sku_info`: CPU speedo ID, SoC speedo ID, CPU process ID, and SoC process ID. Fuse values are read-only and threshold tables are immutable.

## Dependencies and Integration Points

It depends on early fuse reads and the revision/SKU values already populated by APBMISC/fuse core. It integrates through `tegra114_fuse_soc.speedo_init` in `fuse-tegra30.c`.

## Risks and Edge Cases

Unknown SKUs log an error and fall back to speedo IDs 0/0 and threshold index 0, which may be conservative but can mis-bin unusual silicon. The A01 override reads two raw fuse offsets and sets CPU speedo ID to 0 if both are zero. Threshold arrays include a zero row for one index, so any positive speedo value selects process ID 1 for that SKU class.

## Test Signals

Validate known Tegra114 SKUs 0x00, 0x10, 0x05, 0x06, 0x03, and 0x04, A01 override behavior, unknown SKU logging, and resulting regulator/clock OPP selection derived from `tegra_sku_info`.
