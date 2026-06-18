# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-alderlake.c

## Purpose
Describes Alder Lake-family PCH GPIO/pinctrl hardware for the shared Intel pinctrl core. It covers Alder Lake-N, Alder Lake-S class data reused for Raptor Lake and Twin Lake ACPI IDs, including pad names, GPP groups, communities, register offsets, and ACPI matching.

## Important APIs, Types, and Functions
Register offset macros define PAD_OWN, PADCFGLOCK, HOSTSW_OWN, GPI_IS, and GPI_IE locations for ADL-N and ADL-S layouts. `ADL_N_COMMUNITY()` and `ADL_S_COMMUNITY()` expand to `INTEL_COMMUNITY_GPPS()`. Static data includes `adln_pins[]`, `adln_community*_gpps[]`, `adln_communities[]`, `adln_soc_data`, plus corresponding `adls_*` arrays. `adl_pinctrl_acpi_match[]` maps `INTC1056`, `INTC1057`, and `INTC1085` to the right SoC data. The platform driver probes through `intel_pinctrl_probe_by_hid`.

## Control Flow
Module/platform registration exposes `alderlake-pinctrl`. ACPI matching supplies a `struct intel_pinctrl_soc_data` pointer as match data. The shared Intel core maps resources, registers pinctrl/GPIO/IRQ support, interprets communities, and applies power-management callbacks via `intel_pinctrl_pm_ops`.

## State and Persistence Behavior
This file contains immutable descriptor tables only. Runtime state such as pad ownership, locks, GPIO line state, interrupt enables/status, and saved sleep context is managed by `pinctrl-intel.c` and hardware registers.

## Dependencies and Integration Points
Depends on ACPI platform enumeration, `pinctrl-intel.h`, generic pinctrl descriptors, and PM sleep hooks. It integrates with board firmware using Intel ACPI HIDs and with consumers requesting GPIOs or pin states from the shared Intel core.

## Risks
Pin numbering, GPIO base values, and community boundaries are hardware ABI. Errors can mis-map interrupts, expose non-GPIO pads as GPIOs, or hide valid pads. The same data supports multiple product names, so ACPI ID mapping must stay aligned with platform variants.

## Test Signals
Probe on Alder/Raptor/Twin Lake ACPI IDs, pin count and names in debugfs, GPIO ranges matching GPP bases, IRQ delivery through GPI_IS/GPI_IE, suspend/resume save-restore through the shared PM ops, and build coverage with `PINCTRL_ALDERLAKE` are useful signals.
