# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tigerlake.c

Purpose: Supplies Intel Tiger Lake-LP and Tiger Lake-H PCH pinctrl/GPIO topology to the shared Intel pinctrl core. It maps ACPI IDs to SoC data containing pin descriptors and GPIO community/pad-group layouts.

Important APIs/types/functions: Main objects are `tgllp_pins`, `tgllp_communities`, `tgllp_soc_data`, `tglh_pins`, `tglh_communities`, and `tglh_soc_data`. `TGL_LP_COMMUNITY()` and `TGL_H_COMMUNITY()` bind per-generation register offsets for pad ownership, pad config locks, host/software ownership, GPI status, and GPI enable. The platform driver is registered via `module_platform_driver(tgl_pinctrl_driver)`.

Control flow: ACPI IDs `INT34C5` and `INTC1055` select Tiger Lake-LP data; `INT34C6` selects Tiger Lake-H data. Probe is delegated to `intel_pinctrl_probe_by_hid`, which uses the selected community definitions to register pinctrl, GPIO, interrupt, and PM behavior.

State and persistence: The file is static data only. Hardware state is managed by the shared Intel core: pad mux/config, GPIO ownership, interrupt masks/status, and wake state. The HVCMOS, JTAG, and SPI pad groups with `INTEL_GPIO_BASE_NOMAP` are intentionally not exported as normal GPIO ranges.

Dependencies and integration points: Depends on Linux module/platform/PM/pinctrl APIs and `pinctrl-intel.h`. Integrates with ACPI-enumerated Intel PCH devices and imports `PINCTRL_INTEL`.

Risks: This file has no active logic, so correctness depends on exact pin numbering and pad-group GPIO bases. LP and H variants have different group ordering and community splits; an off-by-one range or wrong GPIO base can break interrupt routing or expose non-GPIO pads. Virtual GPIO and non-mapped pad groups need careful validation because the shared core treats them differently.

Test signals: Kernel build, ACPI probe for all listed IDs, `debugfs` pinctrl pin/group listings, GPIO line count and names, GPIO interrupt and wake tests, suspend/resume state preservation, and real board validation for LP and H pin banks including non-mapped HVCMOS/JTAG/SPI groups.
