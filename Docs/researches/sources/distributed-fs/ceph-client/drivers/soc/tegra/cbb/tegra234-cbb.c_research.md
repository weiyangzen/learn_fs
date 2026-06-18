# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/tegra234-cbb.c

## Purpose

`tegra234-cbb.c` implements Control Backbone 2.0 error reporting for Tegra234-derived and newer NVIDIA SoCs. It decodes fabric notifier/monitor registers, supports DT and ACPI matching, maps target ids to fabric target blocks, reports transaction attributes, masks SError for selected fabrics, and warns on CCPLEX in-band errors.

## Important APIs, Types, and Functions

Key types are `tegra234_target_lookup`, `tegra234_fabric_lookup`, `tegra234_cbb_fabric`, and `tegra234_cbb`. Register helpers include `tegra234_cbb_fault_enable()`, `tegra234_cbb_error_clear()`, `tegra234_cbb_get_status()`, and `tegra234_cbb_mask_serror()`. Decode/print paths include `tegra234_cbb_print_error()`, `print_errlog_err()`, `print_errmonX_info()`, and `print_err_notifier()`. Timeout helpers include `tegra234_sw_lookup_target_timeout()`, `tegra234_hw_lookup_target_timeout()`, and `tegra234_cbb_lookup_apbslv()`. The file contains fabric/error/initiator/target tables for Tegra234, Tegra238, Tegra241, Tegra264, and T254 ACPI UID variants.

## Control Flow

Probe selects fabric data from OF match data or ACPI HID/UID, allocates an instance, maps fabric registers, obtains the secure IRQ, checks firewall write access, adds the instance to the global list, optionally masks SError through the ERD mask offset, and registers with the common CBB layer. Error enable writes the fabric notifier interrupt-enable mask. On IRQ, the driver scans registered fabrics, reads notifier status, maps each active error monitor address through notifier address-index registers, reads monitor status/overflow and logged address/attributes/user bits, decodes error type and initiator, optionally performs software or hardware target timeout lookup, clears monitor status, and emits a warning for CCPLEX errors on fabrics with ERD masking.

## State and Persistence Behavior

Each instance stores immutable fabric metadata, mapped MMIO, resource base, IRQ, current monitor pointer, current error type/mask, decoded access address and attribute registers. A global spinlocked `cbb_list` tracks active fabrics. Hardware notifier and monitor status persists until `tegra234_cbb_error_clear()` writes force/status-clear registers. Resume noirq reapplies SError masking and fault enable.

## Dependencies and Integration Points

It depends on platform resources, OF and ACPI matching, common Tegra CBB helpers, NUMA helpers, MMIO accessors, IRQ APIs, debugfs, and SoC-specific firewall/notifier register layouts. It integrates with CBB2 fabrics for multiple SoC generations via data tables rather than separate drivers.

## Risks and Edge Cases

Table correctness is critical across many SoCs; out-of-range fabric ids can index `fab_list` before validation in some print paths. `sprintf()` into fixed 64-byte stack buffers relies on target names staying short. The ISR holds a spinlock while printing large diagnostics. If firewall write access is blocked, probe returns success without adding the instance or enabling errors, which can look like a silent no-op. NUMA filtering suppresses some remote-socket errors. ACPI support depends on exact UID strings.

## Test Signals

Test DT matching for all listed compatibles and ACPI `NVDA1070` UIDs, firewall-allowed and firewall-blocked probes, single secure IRQ handling, debugfs dumping, suspend/resume re-enable, timeout lookups for AXI and AXI2APB targets, NUMA filtering, and injected error types including overflow bits.
