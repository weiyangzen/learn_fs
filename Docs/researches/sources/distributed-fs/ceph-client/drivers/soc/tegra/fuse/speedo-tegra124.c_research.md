# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra124.c

## Purpose

`speedo-tegra124.c` bins Tegra124/Tegra132 silicon by reading CPU, GPU, SoC speedo and IDDQ fuses and mapping SKU IDs into CPU/GPU/SoC speedo IDs plus process IDs.

## Important APIs, Types, and Functions

The public hook is `tegra124_init_speedo_data()`. `rev_sku_to_speedo_ids()` maps SKU values to speedo IDs and threshold index. Constants name fuse offsets for CPU speedo words, SoC speedo words, CPU/SOC/GPU IDDQ, and FT revision. Threshold arrays cover CPU, GPU, and SoC process corners.

## Control Flow

The hook verifies threshold array dimensions, reads `FUSE_CPU_SPEEDO_0`, and returns early with a warning if it is zero. It reads GPU speedo from `FUSE_CPU_SPEEDO_2`, SoC speedo from `FUSE_SOC_SPEEDO_0`, derives speedo IDs from SKU, stores CPU IDDQ, and scans GPU, CPU, and SoC threshold arrays to assign process IDs. It logs GPU speedo ID/value at debug level.

## State and Persistence Behavior

The function mutates `tegra_sku_info` fields for CPU/GPU/SOC speedo IDs, speedo values, process IDs, and CPU IDDQ. It does not persist anything outside the boot-lifetime SKU cache.

## Dependencies and Integration Points

It depends on early fuse reads and is selected by the Tegra124/132 fuse descriptor. Downstream consumers include OPP, voltage, thermal, and GPU/CPU policy code that consults the global SKU information.

## Risks and Edge Cases

A missing CPU speedo fuse causes an early return after `WARN_ON(1)`, leaving many fields at previous/default values. Unknown SKUs log an error and use default speedo IDs/thresholds. Some named fuse offsets such as `FUSE_FT_REV`, `FUSE_CPU_SPEEDO_1`, `FUSE_SOC_SPEEDO_1/2`, `FUSE_SOC_IDDQ`, and `FUSE_GPU_IDDQ` are defined but unused, so future changes should avoid assuming all available calibration words are incorporated.

## Test Signals

Exercise known SKU cases 0x00, 0x0f, 0x23, 0x83, 0x1f, 0x87, 0x27, 0x81, 0x21, 0x07, 0x49, 0x4a, and 0x48. Validate zero CPU speedo behavior, assigned GPU process IDs, CPU IDDQ capture, and OPP/regulator behavior for Tegra124 and Tegra132 boards.
