# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra210.c

## Purpose

`speedo-tegra210.c` bins Tegra210 CPU, GPU, and SoC silicon using speedo revision spare bits, raw speedo fuse words, revision/SKU rules, and threshold arrays. It supports multiple speedo fusing revisions with different calibration formulas.

## Important APIs, Types, and Functions

The public hook is `tegra210_init_speedo_data()`. `get_speedo_revision()` reads spare bits 2..4. `rev_sku_to_speedo_ids()` maps chip revision and SKU to CPU/GPU/SoC speedo IDs and threshold index. `get_process_id()` scans threshold arrays. Constants name CPU and SoC speedo fuse offsets plus IDDQ offsets.

## Control Flow

The init hook reads three CPU speedo words and three SoC speedo words, derives speedo revision, and computes final CPU/GPU/SoC speedo values. Revision >= 3 uses raw values; revision 2 applies linear correction formulas; older revisions use defaults for CPU/SoC and GPU as CPU_SPEEDO_2 minus 75. If any resulting value is nonpositive, the function warns and returns. Otherwise it assigns speedo IDs from SKU/revision and computes process IDs with per-domain threshold arrays.

## State and Persistence Behavior

The function mutates `tegra_sku_info` fields for speedo values, speedo IDs, and process IDs. It does not currently store IDDQ values despite defining IDDQ offsets. All source calibration data is immutable fuse state.

## Dependencies and Integration Points

It depends on early fuse reads and the global revision/SKU initialization. `tegra210_fuse_soc` wires this function as its speedo hook. Consumers include Tegra210 OPP, clock, GPU, thermal, and regulator policy.

## Risks and Edge Cases

`gpu_process_speedos` rows contain `UINT_MAX` for both corners, so valid GPU speedo values select process ID 0 with current data. `get_process_id()` can return `-EINVAL` if no threshold is greater, and those negative process IDs are stored directly. Unknown SKUs log errors but retain default speedo IDs and thresholds. Older speedo revisions use hardcoded default CPU/SoC values, so silicon binning accuracy depends on the correctness of revision detection.

## Test Signals

Test speedo revisions 0, 2, and 3+, all known SKUs for A02+ and pre-A02 handling, nonpositive fuse value warning, negative process-ID paths, and downstream OPP/regulator choices. Debug logs should report speedo revision and GPU speedo ID/value.
