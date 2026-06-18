# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra-cbb.c

## Purpose

`tegra-cbb.c` is the common helper layer for Tegra Control Backbone error drivers. It centralizes diagnostic printing, debugfs registration, IRQ lookup, and calls through `struct tegra_cbb_ops`.

## Important APIs, Types, and Functions

Exported helper-style functions include `tegra_cbb_print_err()`, `tegra_cbb_print_cache()`, `tegra_cbb_print_prot()`, `tegra_cbb_stall_enable()`, `tegra_cbb_fault_enable()`, `tegra_cbb_error_clear()`, `tegra_cbb_get_status()`, `tegra_cbb_get_irq()`, and `tegra_cbb_register()`. `tegra_cbb_err_show()` delegates debugfs reads to SoC-specific `debugfs_show`. `tegra_cbb_err_debugfs_init()` creates a single `tegra_cbb_err` debugfs file.

## Control Flow

SoC-specific probe code fills a `struct tegra_cbb` with ops and calls `tegra_cbb_register()`. Registration optionally initializes debugfs, asks the SoC driver to request interrupts, enables errors through SoC ops, and issues a full-system barrier. At runtime, SoC ISRs and debugfs show callbacks use the common print helpers for consistent console/seq_file output.

## State and Persistence Behavior

Common state is limited to a static debugfs root/file guard. Hardware state is manipulated through SoC callbacks. The debugfs file stores the `cbb` pointer from the first registration as private data, while SoC debugfs callbacks may iterate their own global lists.

## Dependencies and Integration Points

It depends on debugfs, platform IRQ APIs, seq_file, printk, and the CBB public header. It integrates Tegra194 and CBB2 drivers through the ops table.

## Risks and Edge Cases

`tegra_cbb_get_irq()` accepts one or two IRQs and treats one IRQ as secure; callers passing a NULL `nonsec_irq` are safe only when platform IRQ count is one. The debugfs creation helper uses `debugfs_create_file()` once and does not create a directory. If ops are missing, wrapper functions silently no-op or return zero, which can hide incomplete SoC implementations.

## Test Signals

Test one-IRQ and two-IRQ platform devices, debugfs read paths with and without pending errors, and ops tables with all required callbacks. Verify printed cache/protection decoding matches AXI attributes.
