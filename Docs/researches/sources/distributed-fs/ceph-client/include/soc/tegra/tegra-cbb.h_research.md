# sources/distributed-fs/ceph-client/include/soc/tegra/tegra-cbb.h

## Purpose

`tegra-cbb.h` declares common support for Tegra CBB interconnect error reporting, including registration, IRQ lookup, debugfs formatting, and error/fault/stall controls.

## Important APIs, Types, and Functions

`struct tegra_cbb_error` maps an error code to source and description. `struct tegra_cbb` stores the device, ops table, and registry list node. `struct tegra_cbb_ops` provides callbacks for debugfs display, interrupt enable, error enable, fault enable, stall enable, error clear, and status read. Public functions include `tegra_cbb_get_irq()`, `tegra_cbb_print_err()`, `tegra_cbb_print_cache()`, `tegra_cbb_print_prot()`, `tegra_cbb_register()`, `tegra_cbb_fault_enable()`, `tegra_cbb_stall_enable()`, `tegra_cbb_error_clear()`, and `tegra_cbb_get_status()`.

## Control Flow

A SoC CBB driver fills a `struct tegra_cbb`, obtains secure/non-secure IRQs, registers the block, enables reporting, and uses common print helpers while decoding faults in debugfs or interrupt paths.

## State and Persistence

State lives in the registered CBB object, the common list node, SoC-specific callback state, and hardware status registers.

## Dependencies and Integration Points

The header includes Linux list support and uses platform device, seq_file, and device types from kernel context. It integrates with platform IRQ resources, debugfs/seq_file output, and SoC-specific CBB decoders.

## Risks

Risks include missing callbacks, IRQ-resource mismatches, stale status after clear, and incomplete cache/protection/error decoding.

## Test Signals

Test registration, IRQ lookup, callback wrappers, simulated CBB faults, error clear/status reads, and debugfs output formatting.
