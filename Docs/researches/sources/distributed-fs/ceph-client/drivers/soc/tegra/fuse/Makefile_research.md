# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/Makefile

## Purpose

This Makefile builds Tegra fuse, speedo, and APBMISC support objects.

## Important APIs, Types, and Functions

Always-built objects are `fuse-tegra.o`, `fuse-tegra30.o`, and `tegra-apbmisc.o`. Conditional speedo/fuse objects are selected for Tegra20, Tegra30, Tegra114, Tegra124/132, and Tegra210.

## Control Flow

Kbuild includes base fuse/APBMISC support for Tegra, then adds SoC-family-specific calibration/speedo files according to architecture config symbols.

## State and Persistence Behavior

There is no runtime state in the Makefile. The built objects provide runtime fuse/SKU/speedo data used by other Tegra drivers.

## Dependencies and Integration Points

It integrates with Tegra SoC Kconfig and supplies objects consumed indirectly by common SoC code, OPP setup, chip-id helpers, and platform identification.

## Risks and Edge Cases

Tegra132 reuses `speedo-tegra124.o`, so source compatibility must remain intentional. Missing a speedo object can break voltage/OPP decisions. Always-built objects must avoid depending on unavailable SoC-specific symbols.

## Test Signals

Build all supported Tegra family configs and verify fuse/speedo symbols link. Runtime tests should confirm `tegra_sku_info` and chip-id helpers are populated before dependent drivers call them.
