# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/speedo-tegra20.c

## Purpose

`speedo-tegra20.c` derives Tegra20 CPU and SoC process bins from spare fuse bits. It handles redundant speedo bit storage, revision/SKU-based speedo ID selection, and threshold lookup for early boot SKU state.

## Important APIs, Types, and Functions

The public hook is `tegra20_init_speedo_data()`. Macros define CPU and SoC speedo bit ranges, redundant bit offsets, a `SPEEDO_MULT` of 4, and SKU/revision speedo-ID selection rules. Static threshold arrays map three speedo IDs to four process corners for CPU and SoC.

## Control Flow

The hook chooses `soc_speedo_id` from revision and SKU: older revisions get ID 0, most SKUs get ID 1, and a small SKU set gets ID 2. It then reads CPU speedo bits from MSB to LSB, ORing primary and redundant spare bits, multiplies the accumulated value by four, logs it, and scans the CPU threshold row to assign `cpu_process_id`. It repeats the same pattern for SoC speedo bits and `soc_process_id`.

## State and Persistence Behavior

The function mutates the boot-lifetime `tegra_sku_info` fields for SoC speedo ID, CPU process ID, and SoC process ID. It reads immutable spare fuse bits only.

## Dependencies and Integration Points

It depends on `tegra_fuse_read_spare()` and the revision/SKU fields initialized by fuse/APBMISC code. It is selected by `tegra20_fuse_soc.speedo_init` and indirectly used by Tegra20 voltage and frequency policy.

## Risks and Edge Cases

Redundant bits are ORed with primary bits, so any blown redundant bit can force a one. The code sets only `soc_speedo_id`; CPU thresholds also index by that same value, which is intentional for this SoC but easy to misread. SKU selection macros encode historical SKU exceptions and need hardware validation before updates.

## Test Signals

Validate speedo extraction from spare bits including redundant-bit cases, process IDs for all three speedo ID rows, SKU exception handling for 20/23/24/27/28, and downstream Tegra20 regulator nominal voltage selection.
