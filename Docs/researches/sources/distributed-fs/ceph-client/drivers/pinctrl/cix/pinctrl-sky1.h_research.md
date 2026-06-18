# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.h

Purpose: Provides the private data model for the CIX Sky1 pinctrl implementation. It describes per-pin function lists, SoC-level pin tables, and the controller runtime state passed between the SoC table file and the shared base probe.

Important APIs and types: `struct sky1_pinctrl_group` names one pin group and its config; `struct sky1_pin_desc` wraps a `pinctrl_pin_desc` plus a function-name array; `struct sky1_pinctrl_soc_info` points at the SoC pin table; `struct sky1_pinctrl` stores device, `pinctrl_dev`, MMIO base, SoC info, generated groups, and group names. `SKY_PINFUNCTION()` is the table-construction macro. `sky1_base_pinctrl_probe()` is the exported probe boundary.

Control flow: No executable code runs in this header. Its types define the flow used by `pinctrl-sky1.c`: static pin descriptions are passed to `sky1_base_pinctrl_probe()`, which is expected to allocate groups and register a pinctrl device.

State and persistence: The header defines state containers but owns no state itself. `struct sky1_pinctrl` fields persist for the device lifetime under devres or platform-driver ownership; register state persists in MMIO hardware.

Dependencies and integration points: Requires Linux pinctrl and platform-device types from includers. It is tightly coupled to the shared Sky1 base driver and the SoC data file.

Risks: The macro assumes every `_func` has a matching `_func_group` array in scope. If `nfunc` and group names do not match hardware mux values used by the base driver, pin selections can silently program the wrong mode. Header changes affect both Sky1 domains.

Test signals: Compile coverage, probe of both Sky1 compatibles, debugfs group/function counts matching table sizes, and DT state selection through the base driver validate this contract.
