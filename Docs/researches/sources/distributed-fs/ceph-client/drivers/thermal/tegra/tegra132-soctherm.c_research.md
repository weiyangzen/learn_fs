# sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra132-soctherm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/tegra132-soctherm.c` provides Tegra132 SOCTHERM descriptor data, including the flag that routes CPU throttling through CCROC. The source was read as a complete 223-line file.

## Important APIs, Types, and Functions

This descriptor-only file defines Tegra132 masks, `tegra132_tsensor_config`, CPU/GPU/PLL/MEM group descriptors, `tegra132_tsensors[]`, `tegra132_soctherm_fuse`, and exported `tegra132_soctherm` with `.use_ccroc = true`.

## Control Flow

The common driver selects this descriptor for `nvidia,tegra132-soctherm`. The `.use_ccroc` flag changes probe resource mapping from `car-reg` to `ccroc-reg` and changes throttle programming to use CCROC CPU-local pulse skipper configuration.

## State and Persistence Behavior

The file stores static tables only. Runtime `tegra_soctherm` state and CCROC/SOCTHERM register programming are derived from the tables and recreated on resume.

## Dependencies and Integration Points

It depends on Tegra124 thermal binding IDs, shared SOCTHERM structures, the pre-Tegra210 fuse layout, and `CONFIG_ARCH_TEGRA_132_SOC`. The common driver uses this file's `.use_ccroc` to decide register resources and throttle paths.

## Risks and Edge Cases

Tegra132 is close to Tegra124 but not identical. Incorrect `.use_ccroc`, CCROC resource availability, or CPU throttle level values can break hardware throttling. The sensor table is mutable rather than `const`, unlike adjacent descriptors, so accidental runtime writes would be possible if introduced.

## Test Signals

Validation should include CCROC resource mapping, CPU/GPU throttle configuration from DT, debugfs output for CCROC path, temperature plausibility for all groups, and suspend/resume trip reprogramming on Tegra132 hardware.
