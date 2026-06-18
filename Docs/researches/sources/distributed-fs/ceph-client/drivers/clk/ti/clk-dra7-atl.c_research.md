# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-dra7-atl.c

Purpose: DRA7 Audio Tracking Logic clock driver. It registers four ATL clock outputs early as CCF clocks and later binds them to the ATL hardware platform device, programming ATL mux/divider registers and runtime PM when clocks are enabled.

Important APIs/types/functions: `of_dra7_atl_clock_setup()` handles `ti,dra7-atl-clock` clock nodes; `of_dra7_atl_clk_probe()` handles the `ti,dra7-atl` platform device. `dra7_atl_desc` stores per-output clock state (`probed`, `valid`, `enabled`, BWS/AWS/divider), and `dra7_atl_clock_info` stores device and MMIO base. `atl_clk_ops` implements enable, disable, is_enabled, recalc, determine_rate, and set_rate.

Control flow: early DT clock setup allocates a descriptor, validates one parent, registers the clock with `CLK_IGNORE_UNUSED`, and provides it to consumers. Platform probe maps MMIO, enables PM, configures PCLKMUX, resolves each `ti,provided-clocks` phandle back to its descriptor, optionally reads child `atl0`..`atl3` BWS/AWS properties, writes mux configuration, marks descriptors probed, and replays enable if a consumer enabled the clock before the hardware driver loaded.

State and persistence: per-clock descriptors persist for the life of the built-in driver. Divider values are cached until enable, and `enabled` is software state used before and after probe. BWS/AWS and SWEN/ATLCR are programmed into hardware registers; runtime PM references are acquired while enabled.

Dependencies/integration: uses OF clock providers, platform bus, runtime PM, raw MMIO, and TI clock registration helpers. Consumers obtain clocks from the early `ti,dra7-atl-clock` nodes while the hardware node provides register access and phandle binding.

Risks: `divider - 1` is written on enable; the default divider is one, but bad rate paths must not leave zero. Probe assumes exactly four `ti,provided-clocks`; missing phandles fail the whole probe. Runtime PM return values are not checked. Unconfigured ATL instances still enable with only a warning.

Test signals: validate DT with four provided clocks and optional `atlN` children, request rates from audio drivers, enable before and after platform probe, inspect ATL registers, and test runtime PM balance across enable/disable.
