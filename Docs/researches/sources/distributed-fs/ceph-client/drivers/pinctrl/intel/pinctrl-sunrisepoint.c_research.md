# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-sunrisepoint.c

Purpose: Provides the Intel Sunrisepoint PCH pinctrl/GPIO SoC descriptions for Sunrisepoint-LP and Sunrisepoint-H. The file is mostly immutable platform data consumed by the shared Intel pinctrl core, with ACPI IDs selecting the correct SoC table at probe.

Important APIs/types/functions: The main data objects are `sptlp_pins`, `sptlp_groups`, `sptlp_functions`, `sptlp_communities`, `sptlp_soc_data`, and the corresponding `spth_*` tables. `SPT_H_COMMUNITY()` and `SPT_LP_COMMUNITY()` wrap Intel community macros with Sunrisepoint register offsets for ownership, pad locks, host/software ownership, interrupt status, and interrupt enable. The platform driver uses `intel_pinctrl_probe_by_hid`, `intel_pinctrl_pm_ops`, `subsys_initcall(spt_pinctrl_init)`, and `module_exit`.

Control flow: ACPI matches `INT344B` to LP data and `INT3451`/`INT345D` to H data. Probe is delegated entirely to the shared Intel driver, which interprets the pin descriptors, groups, functions, and communities to register pinctrl/GPIO/IRQ services. Runtime muxing and GPIO access happen in `pinctrl-intel.c`, not here.

State and persistence: This file owns no mutable runtime state. Register offsets and pin/community topology become persistent hardware state only when the shared Intel core programs pad configuration, ownership, interrupt, or wake registers. Suspend/resume state handling is delegated through `intel_pinctrl_pm_ops`.

Dependencies and integration points: Depends on Linux platform, ACPI match, PM, and pinctrl APIs plus local `pinctrl-intel.h`. It integrates with ACPI-enumerated PCH devices and the Intel pinctrl namespace imported as `PINCTRL_INTEL`.

Risks: Most defects are table defects: wrong pin numbers, group membership, mux mode values, GPIO base mapping, or community pad ranges silently misroute GPIOs or interrupts. There are suspicious copied group mappings where `sptlp_spi1_groups` and `spth_spi1_groups` point at `"spi0_grp"`, and UART2 pin arrays repeat pin 71 instead of including pin 70; those may be inherited quirks but are test-worthy. Community ranges must match hardware register layout because the core derives MMIO offsets from them.

Test signals: Build with Sunrisepoint support, ACPI probe on LP and H systems, `debugfs` pinctrl enumeration, GPIO line naming/counts, SPI/I2C/UART/eMMC/SD mux selection, GPIO interrupt delivery, wake from suspend, and suspend/resume register restoration through the shared Intel PM ops.
