# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxbf-pmc.c

## Purpose
BlueField performance monitoring counter driver. It builds a hwmon sysfs hierarchy named `bfperf` from ACPI-described PMC blocks and exposes event selection, counter reads, register reads/writes, L3 cache controls, and CR-space counter controls across BF1, BF2, and BF3 event sets.

## Important APIs, Types, And Functions
`struct mlxbf_pmc_context` stores ACPI block names, block metadata, secure-register state, event set, and hwmon groups. `struct mlxbf_pmc_block_info` stores per-block MMIO/physical base, size, counter count, type, and generated attributes. Event tables map names to hardware event numbers for PCIe, SMGEN, TRIO, ECC, MSS, HNF, L3C, LLT, clock, GGA, APT, EMI, PRNF, and MSN blocks. Access helpers are `mlxbf_pmc_read()`, `mlxbf_pmc_write()`, secure SMC variants, and `mlxbf_pmc_valid_range()`. Sysfs handlers implement `counterX`, `eventX`, `event_list`, `enable`, and `count_clock`.

## Control Flow
Probe validates the SiP UUID, optionally enables secure-register SMC access from `sec_reg_block`, selects an event table set from ACPI HID, reads `block_num` and `block_name`, filters unavailable tiles/MSS/EMI/LLT/APT blocks, maps each block from ACPI u64 arrays, generates per-block attribute groups, and registers hwmon. Event writes accept names or numbers, validate against the block event table, then program L3, CR-space, or generic counter layouts.

## State, Dependencies, Integration, Risks, Tests
State is global through the singleton `pmc`, plus hardware counter configuration in MMIO or secure firmware. Dependencies include ACPI properties, Arm SMCCC/PSCI return codes, reg-sized MMIO, hwmon, bitfield helpers, and event-name conventions encoded with `strstr()`. Integration is with platform firmware and user-space performance tooling via sysfs. Risks include global singleton behavior, insufficient locking for concurrent sysfs counter programming, block-name substring ambiguity, event-list output truncation at one page, secure access version mismatches, and register writes that can perturb live counters. Test signals include ACPI permutations for BF1/BF2/BF3, secure and direct MMIO modes, invalid event names, counter bounds, L3 counter enable/reset behavior, CR-space clear/count-clock behavior, and unsupported block warnings.
