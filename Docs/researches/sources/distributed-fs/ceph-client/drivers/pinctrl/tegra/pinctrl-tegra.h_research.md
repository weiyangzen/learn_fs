<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.h

## Purpose
Defines the shared data model and public interface for Tegra pinctrl SoC table drivers and the common implementation in `pinctrl-tegra.c`.

## Important APIs, Types, And Functions
Key types are `struct tegra_pmx`, `struct tegra_pingroup_config`, `struct tegra_function`, `struct tegra_pingroup`, and `struct tegra_pinctrl_soc_data`. Enumerations define Tegra-specific pinconf parameters and legal pull/tristate values. Macros `TEGRA_PINCONF_PACK`, `TEGRA_PINCONF_UNPACK_PARAM`, and `TEGRA_PINCONF_UNPACK_ARG` encode configs. The public symbols are `tegra_pinctrl_probe` and `tegra_pinctrl_pm`.

## Control Flow
The header itself has no execution. SoC files fill arrays of `pinctrl_pin_desc`, function names, and `tegra_pingroup` entries, then pass a `tegra_pinctrl_soc_data` instance to `tegra_pinctrl_probe`. The common implementation interprets per-group register offsets, banks, bit positions, and widths from this metadata.

## State And Persistence Behavior
`struct tegra_pmx` is mutable per-controller state: device, pinctrl device, SoC data, generated functions, group pin names, GPIO range, mapped register banks, suspend backup registers, and counted pingroup config cache. SoC data and pingroup arrays are static descriptors that encode hardware register layout.

## Dependencies And Integration Points
Integrates with platform devices, pinctrl descriptors, GPIO ranges, MMIO resources, and noirq PM. The SoC files depend on the documented meanings of negative `*_reg` and `*_bit` fields to mark unsupported features.

## Risks And Edge Cases
The bitfield widths in `struct tegra_pingroup` constrain register banks, bits, and widths; out-of-range metadata would truncate at compile/runtime. `funcs[4]` hardcodes four mux slots per group. Descriptor comments are part of the ABI between generated SoC tables and common code; changes must be coordinated across every Tegra table.

## Test Signals
Compile all Tegra SoC table files, validate pinconf packing/unpacking, exercise groups with unsupported fields, verify SoC data flags for `hsm_in_mux`, `schmitt_in_mux`, `drvtype_in_mux`, and `sfsel_in_mux`, and run suspend/resume with multiple MMIO banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.h -->
