# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra30.c

## Purpose

`speedo-tegra30.c` implements Tegra30 speedo calibration and binning. It decodes CPU/G and LP speedo values from fuse calibration words and spare bits, maps revision/SKU/package combinations to speedo IDs and threshold rows, and assigns CPU/SoC process IDs.

## Important APIs, Types, and Functions

The public hook is `tegra30_init_speedo_data()`. `fuse_speedo_calib()` reads `FUSE_SPEEDO_CALIB_0`, `FUSE_TEST_PROG_VER`, and correction spare bits to produce CPU/G and LP speedo values. `rev_sku_to_speedo_ids()` handles revision, SKU, and package ID mapping. Threshold arrays cover 12 threshold indices with CPU and SoC process corners.

## Control Flow

The init hook validates threshold table dimensions, maps revision/SKU/package into CPU speedo ID, SoC speedo ID, and `threshold_index`, reads calibrated speedo values, logs them, scans CPU thresholds to set `cpu_process_id`, and scans SoC thresholds to set `soc_process_id`. If either scan underflows to -1, it warns and forces process ID 0 and speedo ID 1 for that domain.

`fuse_speedo_calib()` multiplies two 16-bit fields by four, then either appends low correction bits from spare fuses for ATE program version >= 26 or forces both low bits to one for older test program versions.

## State and Persistence Behavior

The file mutates `tegra_sku_info` speedo IDs and process IDs. `threshold_index` is static `__initdata`, used only during boot. No persistent storage is written.

## Dependencies and Integration Points

It depends on early fuse reads, spare fuse reads, package info, test program version, and revision/SKU data from common fuse init. The Tegra30 SoC descriptor selects it through `speedo_init`.

## Risks and Edge Cases

The mapping table is complex and SKU/package-specific. Unknown package IDs log errors but may leave speedo IDs and threshold index at whatever was previously assigned in that switch path. CPU/SOC process assignment intentionally stores `i - 1`, making underflow possible and handled afterward. The help string has no direct effect, but binning mistakes can propagate into voltage/frequency policy.

## Test Signals

Validate all documented SKU/package combinations, ATE version below and above 26, spare-bit correction paths, unknown SKU/package warnings, underflow handling, and resulting Tegra30 regulator nominal voltage and OPP choices.
