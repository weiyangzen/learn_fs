# subset-b-001089 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-npcm8xx.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-npcm8xx.c

### Purpose
`clk-npcm8xx.c` implements the common clock framework provider for Nuvoton NPCM8xx BMC SoC clocks. The bootloader programs the clock generator; this driver mostly exposes the existing PLL, mux, fixed-factor, and divider topology to Linux as read-only or limited-operation clocks.

### Important APIs, Types, And Functions
Important types are `struct npcm8xx_clk_pll`, `struct npcm8xx_clk_pll_data`, `struct npcm8xx_clk_div_data`, and `struct npcm8xx_clk_mux_data`. The main operations are `npcm8xx_clk_pll_recalc_rate()`, `npcm8xx_clk_register_pll()`, and `npcm8xx_clk_probe()`. Registration uses `devm_clk_hw_register()`, `devm_clk_hw_register_fixed_factor()`, `devm_clk_hw_register_mux_parent_data_table()`, `devm_clk_hw_register_divider_parent_hw()`, and `devm_of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe runs as an auxiliary driver named `reset_npcm.clk-npcm8xx`, receives the MMIO base through `struct npcm_clock_adev`, allocates a `clk_hw_onecell_data`, initializes all slots to `-EPROBE_DEFER`, then registers PLLs, fixed dividers, muxes, pre-dividers, and exported dividers in dependency order. PLL rates are computed directly from PLLCON fields using parent rate, feedback divider, input divider, and output dividers. Global state includes the MMIO `clk_base`, static template arrays updated with registered `clk_hw` copies, and `npcm8xx_clk_lock` shared by mux/divider helpers.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the NPCM reset/clock auxiliary device, `dt-bindings/clock/nuvoton,npcm845-clk.h`, `soc/nuvoton/clock-npcm8xx.h`, MMIO register layout, and OF onecell consumers. Risks include divide-by-zero if hardware PLL fields are unexpectedly zero, copied `clk_hw` template state being used as parent handles, incorrect onecell IDs, and races around writable mux/divider helpers if future code removes read-only assumptions. Test signals include boot probe on NPCM8xx, `/sys/kernel/debug/clk/clk_summary` rates matching hardware, OF consumers resolving all exported IDs, critical CPU/AHB clocks staying enabled, and deferred consumers unblocking after provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-npcm8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-nspire.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-nspire.c

### Purpose
`clk-nspire.c` is an early OF clock provider for TI-Nspire calculator SoCs. It reads a hardware clock configuration register and exposes either the base clock or an AHB divider as simple fixed-rate/fixed-factor clocks.

### Important APIs, Types, And Functions
`struct nspire_clk_info` carries decoded `base_clock`, `base_cpu_ratio`, and `base_ahb_ratio`. `nspire_clkinfo_cx()` and `nspire_clkinfo_classic()` decode model-specific bit fields. `nspire_clk_setup()` registers fixed-rate base clocks, while `nspire_ahbdiv_setup()` registers fixed-factor AHB dividers. Four `CLK_OF_DECLARE()` entries bind CX and classic compatible strings for base clocks and AHB dividers.

### Control Flow, State, And Persistence
The init callback maps the node register with `of_iomap()`, reads one 32-bit value, unmaps immediately, decodes rates, optionally overrides the clock name from `clock-output-names`, and registers a clock provider on that node. No runtime mutable state is retained beyond the registered CCF objects. The base clock path also logs base, CPU, and AHB MHz values.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are early devicetree clock init, MMIO access, `clock-output-names`, and parent lookup for AHB divider nodes. Risks include invalid register fields producing zero divisors, no cleanup for failed legacy early registrations, integer assumptions around MHz units, and silent no-op when mapping fails. Test signals include boot logs on CX/classic hardware, `clk_summary` showing expected base/AHB rates, consumers obtaining parented AHB clocks, and DT coverage for all four compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-nspire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-palmas.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-palmas.c

### Purpose
`clk-palmas.c` exposes the Palmas PMIC 32 kHz clock outputs `clk32kg` and `clk32kgaudio` through the common clock framework. It supports direct software enablement and optional external sleep-control pins.

### Important APIs, Types, And Functions
`struct palmas_clk32k_desc` describes control register, active/sleep masks, external requestor ID, and stabilization delay. `struct palmas_clock_info` stores the parent MFD handle, descriptor, `clk_hw`, and selected external-control pin. Clock ops are `palmas_clks_prepare()`, `palmas_clks_unprepare()`, `palmas_clks_is_prepared()`, and `palmas_clks_recalc_rate()`. Probe uses `palmas_clks_get_clk_data()`, `palmas_clks_init_configure()`, `devm_clk_hw_register()`, and `of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe selects descriptor data from OF match, reads optional `ti,external-sleep-control`, registers one fixed 32768 Hz clock, clears sleep mode, and, when externally controlled, prepares the clock and configures `palmas_ext_control_req_config()`. Prepare sets the active bit and delays when requested; unprepare avoids clearing the bit when external control owns disable behavior. Remove only deletes the OF provider; allocations are devm-managed.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on the Palmas MFD core, `palmas_read()`, `palmas_update_bits()`, external requestor programming, OF child nodes, and consumers of 32 kHz PMIC clocks. Risks include leaked prepared state for externally controlled clocks on remove, invalid DT external-control values falling back to software mode, register update failures during clock ops, and fixed `CLK_IGNORE_UNUSED` keeping outputs on. Test signals include toggling both clock outputs, external ENABLE1/ENABLE2/NSLEEP control behavior, sleep-mask clearing, DT property validation, and consumers receiving 32768 Hz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-palmas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-plldig.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-plldig.c

### Purpose
`clk-plldig.c` drives the NXP LS1028A display PLLDIG block used for display output pixel clocks. It exposes a single `dpclk` clock with rate calculation and programming around a fixed or DT-specified VCO frequency.

### Important APIs, Types, And Functions
`struct clk_plldig` stores `clk_hw`, MMIO base, and VCO frequency. Clock ops include `plldig_enable()`, `plldig_disable()`, `plldig_is_enabled()`, `plldig_recalc_rate()`, `plldig_determine_rate()`, and `plldig_set_rate()`. `plldig_init()` programs multiplier and optional fractional divider from parent rate and `fsl,vco-hz`; `plldig_clk_probe()` maps resources and registers the OF provider.

### Control Flow, State, And Persistence
Probe registers `dpclk`, adds the provider, validates optional VCO range, then initializes PLLDV and PLLFD. Enable sets SSCG bypass mode; disable clears it. Rate changes clamp the requested PHI1 output range, choose an RFDPHI1 divider from VCO to target, update the divider field, wait briefly, and poll PLL lock. Persistent state is hardware registers plus cached `vco_freq`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform MMIO resources, one parent clock, `readl_poll_timeout_atomic()`, and DT compatible `fsl,ls1028a-plldig`. Risks include provider being registered before `plldig_init()` failure, confusing bypass-bit checks across PLLFM versus PLLDV fields, parent-rate zero assumptions, and lock polling in atomic timeout context. Test signals include VCO property boundary tests, successful lock after `set_rate`, rate clamping to 27-600 MHz, display pipeline pixel-clock requests, and failure injection for missing parent/MMIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-plldig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-pwm.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-pwm.c

### Purpose
`clk-pwm.c` wraps a PWM output as a fixed-rate clock provider. It is for hardware where a PWM controller can emit a 50 percent duty-cycle signal usable as a clock.

### Important APIs, Types, And Functions
`struct clk_pwm` stores `clk_hw`, the `pwm_device`, desired `pwm_state`, and fixed rate. Atomic and sleepable operation tables select between `pwm_apply_atomic()` and `pwm_apply_might_sleep()` based on `pwm_might_sleep()`. Important functions are `clk_pwm_probe()`, `clk_pwm_enable()`, `clk_pwm_prepare()`, `clk_pwm_disable()`, `clk_pwm_unprepare()`, `clk_pwm_recalc_rate()`, and `clk_pwm_get_duty_cycle()`.

### Control Flow, State, And Persistence
Probe acquires the PWM, validates the PWM period, derives or checks `clock-frequency`, initializes the PWM state to enabled with a 1/2 duty cycle, chooses the clock name, registers the clock, and adds an OF provider. Enable/prepare applies the stored enabled state; disable/unprepare turns the PWM off. The fixed rate is persistent driver state, while the hardware PWM state is read for duty-cycle queries.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the PWM subsystem, DT `pwm-clock` binding, `clock-frequency`, `clock-output-names`, and OF consumers. Risks include mismatched PWM period/rate rejecting valid rounded configurations, atomic ops being selected for a provider whose low-level driver later sleeps, ignoring errors from disable paths, and no provider removal through devm for `of_clk_add_hw_provider()` until explicit remove. Test signals include 50 percent duty output on a scope, period-derived and explicit frequency cases, atomic versus might-sleep PWM drivers, invalid period/frequency rejection, and CCF duty-cycle reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-pwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-qoriq.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-qoriq.c

### Purpose
`clk-qoriq.c` is the early clock provider for Freescale/NXP QorIQ and Layerscape clock generator blocks. It builds a SoC-specific tree of sysclk/coreclk inputs, PLL divider outputs, core muxes, hardware accelerator muxes, FMAN clocks, legacy providers, and a `qoriq-cpufreq` platform device.

### Important APIs, Types, And Functions
Key data models are `struct clockgen_chipinfo`, `struct clockgen`, `struct clockgen_pll`, `struct clockgen_muxinfo`, `struct clockgen_sourceinfo`, and `struct mux_hwclock`. Major functions include `_clockgen_init()`, `create_sysclk()`, `create_coreclk()`, `create_plls()`, `create_one_pll()`, `create_muxes()`, `create_mux_common()`, `clockgen_clk_get()`, legacy `sysclk_init()`, `core_pll_init()`, `core_mux_init()`, and `clockgen_cpufreq_init()`. CCF integration uses `clk_register_fixed_rate()`, `clk_register_fixed_factor()`, custom `clk_ops` for muxes, `clk_register_clkdev()`, and `of_clk_add_provider()`.

### Control Flow, State, And Persistence
`CLK_OF_DECLARE()` invokes `_clockgen_init()` early, maps the clockgen registers, matches a chipinfo table entry, optionally maps GUTS registers, applies erratum A-4510 policy, creates inputs, PLL divider clocks, cmux/hwaccel muxes, SoC-specific peripheral clocks, and registers a phandle provider. Legacy subnodes lazily initialize the parent clockgen and expose older onecell/simple providers. State is global and effectively singleton: `clockgen`, mapped MMIO pointers, registered clocks, chipinfo copy, and `add_cpufreq_dev` for a later `device_initcall()`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include early OF init, QorIQ DT bindings, endian-specific MMIO, GUTS RCW fields, PPC SVR erratum checks, clkdev lookup, and cpufreq. Risks include singleton behavior on systems with multiple clockgen nodes, early allocations without devm cleanup, old LS1021A physical-address fallback, bad mux source tables filtering all parents, endian flag mistakes, and legacy/new DT mixtures. Test signals include boot on every compatible entry, phandle lookups for `QORIQ_CLK_*`, core mux parent switching within allowed rate limits, FMAN source selection from RCW bits, `qoriq-cpufreq` creation only for non-legacy clockgen blocks, and clkdev names for PLL dividers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-qoriq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-renesas-pcie.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-renesas-pcie.c

### Purpose
`clk-renesas-pcie.c` supports Renesas/IDT 9-series PCIe clock generators, currently 9FGV0241, 9FGV0441, and 9FGV0841. It registers each DIF output as a fixed-factor clock and programs optional output amplitude, spread-spectrum, and slew-rate settings.

### Important APIs, Types, And Functions
`struct rs9_chip_info` describes output count, output-enable bit shift, and expected device ID. `struct rs9_driver_data` holds I2C client, regmap, per-DIF `clk_hw`, and DT-derived settings. Important functions are custom `rs9_regmap_i2c_read()/write()`, `rs9_get_common_config()`, `rs9_get_output_config()`, `rs9_update_config()`, `rs9_of_clk_get()`, `rs9_probe()`, `rs9_suspend()`, and `rs9_resume()`.

### Control Flow, State, And Persistence
Probe loads match data, parses top-level and per-child DT configuration, initializes a custom flat regmap, programs BCP for one-byte reads, verifies VID/DID, registers `DIF0..DIFn` fixed-factor clocks with parent index 0 and multiplier 4, adds an OF provider, then writes non-default configuration. Suspend switches regmap to cache-only and marks it dirty; resume syncs cached register state back to hardware.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C transfers with device-specific framing, regmap cache, OF children named `DIF%d`, Renesas DT properties, and PCIe clock consumers. Risks include no bounds check in `rs9_of_clk_get()`, relying on BCP before all reads, partial configuration if `regmap_update_bits()` errors are ignored in update, DT child naming sensitivity, and regcache sync failures after suspend. Test signals include VID/DID mismatch rejection, valid/invalid amplitude and spread-spectrum values, per-DIF slew-rate programming, phandle access for all outputs, suspend/resume retention, and measured 100 MHz-class PCIe outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-renesas-pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rk808.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-rk808.c

### Purpose
`clk-rk808.c` exposes two 32.768 kHz clock outputs from Rockchip RK805/RK808/RK809/RK817/RK818 PMIC families. CLKOUT1 is fixed always-on behavior from the clock framework perspective; CLKOUT2 can be enabled and disabled through PMIC registers.

### Important APIs, Types, And Functions
`struct rk808_clkout` stores the parent PMIC regmap and two `clk_hw` objects. Common helpers include `rk808_clkout_recalc_rate()`, `of_clk_rk808_get()`, `rk808_clkout_probe()`, and variant dispatch through `rkpmic_get_ops()`. RK808-style and RK817-style CLKOUT2 ops use different register and bit definitions from the RK808 MFD header.

### Control Flow, State, And Persistence
Probe inherits the parent OF node, allocates state, obtains the parent regmap, registers `rk808-clkout1` and `rk808-clkout2` with optional `clock-output-names`, and publishes a two-entry OF provider. CLKOUT2 prepare/unprepare updates the relevant enable bit; `is_prepared` reads it back. Persistent state is the PMIC register bit and devm-managed clock objects.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the RK808 MFD platform device, parent regmap, PMIC variant ID, OF clock cells, and 32 kHz consumers such as RTC, WiFi, or Bluetooth. Risks include variant misclassification selecting the wrong register, CLKOUT1 lacking enable-state control, RK817 `is_prepared()` returning 0 instead of an error on failed reads, and invalid phandle indexes. Test signals include both output names, phandle index 0/1 behavior, CLKOUT2 bit toggling on each supported PMIC variant, consumer enable counts, and measured 32768 Hz output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rk808.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rp1.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-rp1.c

### Purpose
`clk-rp1.c` implements the Raspberry Pi RP1 PCIe multifunction chip clock controller. It exposes PLL cores, primary PLL outputs, phase outputs, secondary dividers, peripheral clocks, general-purpose outputs, video clocks, and variable external sources through a single onecell provider.

### Important APIs, Types, And Functions
Core types are `struct rp1_clockman`, `struct rp1_clk_desc`, `struct rp1_pll_core_data`, `struct rp1_pll_data`, `struct rp1_pll_ph_data`, `struct rp1_pll_divider_data`, and `struct rp1_clock_data`. Operation groups are `rp1_pll_core_ops`, `rp1_pll_ops`, `rp1_pll_ph_ops`, `rp1_pll_divider_ops`, `rp1_clk_ops`, and `rp1_varsrc_ops`. Registration helpers are `rp1_register_pll()`, `rp1_register_pll_divider()`, `rp1_register_clock()`, descriptor macros, `clk_desc_array`, and `rp1_clk_probe()`.

### Control Flow, State, And Persistence
Probe allocates `rp1_clockman`, maps MMIO, creates a lockless regmap guarded externally by `regs_lock`, iterates `clk_desc_array`, registers each descriptor, caches special audio/I2S/xosc pointers, and adds a onecell OF provider. PLL core ops program feedback dividers and poll lock; PLL output ops choose primary dividers; phase and secondary-divider ops enable/reset and divide PLL outputs. Peripheral clock ops choose parent selectors, integer/fractional dividers, and GPCLK output-enable bits. `cached_rate` stores audio coordination rates and varsrc rates for externally managed MIPI DSI byte clocks.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `dt-bindings/clock/raspberrypi,rp1-clocks.h`, platform MMIO, regmap, CCF parent propagation, and downstream RP1 Ethernet, UART, PWM, audio, SDIO, ADC, MIPI, DPI, VEC, and GPCLK consumers. Risks include descriptor/table drift against binding IDs, lockless regmap requiring every write sequence to hold `regs_lock`, complex audio/I2S cached-rate coupling, parent selector gaps using AUX source conventions, no explicit unwind for failed individual descriptor registration, and rate calculations near hardware max limits. Test signals include every binding ID present in `clk_summary`, PLL lock timeout coverage, parent switching with `CLK_SET_RATE_NO_REPARENT` clocks, GPCLK OE bit toggles, audio/I2S exact-rate requests, varsrc updates from display drivers, and probe failure on bad MMIO/regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rpmi.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-rpmi.c

### Purpose
`clk-rpmi.c` is a RISC-V RPMI mailbox-backed clock provider. It discovers clocks from firmware, retrieves supported rate formats, and translates CCF rate and enable operations into RPMI clock service messages.

### Important APIs, Types, And Functions
Important types include `struct rpmi_clk_context`, `struct rpmi_clk`, `union rpmi_clk_rates`, and the packed TX/RX message structs for get attributes, supported rates, get/set rate, and set config. Major functions are `rpmi_clk_get_num_clocks()`, `rpmi_clk_get_attrs()`, `rpmi_clk_get_supported_rates()`, `rpmi_clk_recalc_rate()`, `rpmi_clk_determine_rate()`, `rpmi_clk_set_rate()`, `rpmi_clk_enable()`, `rpmi_clk_disable()`, `rpmi_clk_enumerate()`, and `rpmi_clk_probe()`.

### Control Flow, State, And Persistence
Probe configures a blocking mailbox client, requests channel 0, registers devm cleanup, validates RPMI message and clock service versions, obtains maximum message data size, asks firmware for clock count, enumerates every clock, and adds a onecell provider. Enumeration reads attributes, allocates rate storage, receives discrete or linear supported-rate data, registers a no-parent clock with `CLK_GET_RATE_NOCACHE`, and sets the allowed CCF rate range. Runtime operations send mailbox messages for get rate, set rate, enable, and disable; local state caches only metadata and supported ranges.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include RISC-V RPMI mailbox transport, `rpmi_mbox_*` helpers, `rpmi_to_linux_error()`, OF compatible `riscv,rpmi-clock`, and firmware correctness. Risks include `num_rates` exceeding the fixed 16-entry discrete array, subtle pagination bugs in supported-rate retrieval, returning negative errors through unsigned `recalc_rate`, ignoring disable message failures, and no parent or state query support. Test signals include version/service mismatch rejection, multi-message discrete rate enumeration, linear rate rounding, firmware error translation, CCF rate range enforcement, enable/disable message tracing, and all discovered clocks appearing in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rpmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-s2mps11.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-s2mps11.c

### Purpose
`clk-s2mps11.c` exposes 32.768 kHz PMIC clocks for Samsung S2MPG10, S2MPS11, S2MPS13, S2MPS14, and S5M8767 devices. It registers AP, CP, and BT clocks where present and controls enable bits in the PMIC RTC/control register.

### Important APIs, Types, And Functions
`struct s2mps11_clk` stores PMIC device pointer, clocks child node, `clk_hw`, legacy `clk`, clkdev lookup, mask, and register. Clock ops are `s2mps11_clk_prepare()`, `s2mps11_clk_unprepare()`, `s2mps11_clk_is_prepared()`, and `s2mps11_clk_recalc_rate()`. Probe uses `s2mps11_clk_parse_dt()`, device ID based register selection, `devm_clk_register()`, `clkdev_hw_create()`, and `of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe allocates three clock slots and onecell data, selects the PMIC register for the matched platform ID, finds the parent MFD `clocks` child node, applies optional `clock-output-names`, registers each supported clock, creates clkdev lookups, fills onecell hardware pointers, and publishes the provider. S2MPS14 skips the CP clock. Remove deletes the provider, releases the child-node reference, and drops clkdev lookups. Hardware state persists as PMIC enable bits.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include Samsung MFD core, per-device PMIC register headers, platform device IDs from the parent MFD, OF child node `clocks`, and clkdev users. Risks include global mutation of the static `s2mps11_clks_init` names across devices, `of_clk_add_hw_provider()` return value ignored, unprepare writing `~mask` as value relying on regmap masking semantics, and missing hardware variants. Test signals include all PMIC ID probes, S2MPS14 CP omission, OF and clkdev lookups, prepare/unprepare bit transitions, custom clock names, and provider cleanup on remove/error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-s2mps11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scmi.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-scmi.c

### Purpose
`clk-scmi.c` maps ARM SCMI clock protocol objects into CCF clocks. It dynamically selects operation sets per firmware-reported clock capabilities, including state, rate, parent, atomic transport, and optional OEM duty-cycle configuration.

### Important APIs, Types, And Functions
`struct scmi_clk` stores SCMI ID, device, `clk_hw`, firmware `scmi_clock_info`, protocol handle, and parent data. Key functions are `scmi_clk_recalc_rate()`, `scmi_clk_determine_rate()`, `scmi_clk_set_rate()`, parent get/set helpers, atomic and non-atomic enable/disable helpers, duty-cycle get/set helpers, `scmi_clk_ops_alloc()`, `scmi_clk_ops_select()`, `scmi_clk_ops_init()`, and `scmi_clocks_probe()`.

### Control Flow, State, And Persistence
Probe obtains the SCMI clock protocol, gets the firmware clock count, allocates onecell data and `struct scmi_clk` array, asks the transport whether atomic commands are supported, then iterates every clock. For each valid firmware clock, it chooses or reuses a `clk_ops` combination based on forbidden controls, enable latency, parent support, and duty-cycle probing, builds parent data from firmware parent IDs, registers the clock with `CLK_GET_RATE_NOCACHE`, and sets rate range from discrete list or linear range. State remains firmware-owned; the driver caches metadata and parent arrays.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the SCMI bus, clock protocol ops, OF onecell consumers, transport atomicity, firmware-provided parent topology, and optional OEM duty-cycle config. Risks include global `scmi_proto_clk_ops` shared across instances, parent indices referring to skipped or invalid clocks, duty-cycle integer truncation, unsupported firmware features only discovered at operation time, and per-instance devm `clk_ops` reuse constrained to probe stack database. Test signals include atomic and non-atomic transports, clocks with forbidden state/rate/parent controls, discrete and range rates, parent changes, duty-cycle get/set success and failure, invalid clock info holes, and suspend/resume firmware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scpi.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-scpi.c

### Purpose
`clk-scpi.c` exposes ARM SCPI firmware clocks. It supports variable clocks controlled by direct rate get/set calls and DVFS clocks controlled by firmware OPP indexes, and creates a virtual `scpi-cpufreq` device when DVFS clocks are present.

### Important APIs, Types, And Functions
`struct scpi_clk` stores clock ID, `clk_hw`, optional DVFS info, and `scpi_ops`. Operation tables are `scpi_clk_ops` for variable clocks and `scpi_dvfs_ops` for OPP-index clocks. Key functions include `scpi_clk_ops_init()`, `scpi_clk_add()`, `scpi_of_clk_src_get()`, `scpi_clocks_probe()`, `scpi_clocks_remove()`, `__scpi_dvfs_round_rate()`, and `scpi_dvfs_set_rate()`.

### Control Flow, State, And Persistence
Probe requires `get_scpi_ops()`, scans child nodes under `arm,scpi-clocks`, matches `arm,scpi-dvfs-clocks` or `arm,scpi-variable-clocks`, and registers each named/indexed clock. Variable clocks query firmware min/max ranges; DVFS clocks query OPP tables and convert requested rates to exact OPP indexes. Provider lookup searches the registered array by SCPI clock ID rather than array position. A module-global `cpufreq_dev` is registered once for DVFS provider presence and unregistered during remove.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include legacy ARM SCPI firmware ops, DT child properties `clock-output-names` and `clock-indices`, OF provider registration, and cpufreq integration. Risks include global `cpufreq_dev` across possible instances, remove deleting the wrong provider node in the child loop, no parent support, firmware OPP ordering assumptions, and direct `get_scpi_ops()` lifetime. Test signals include variable clock range enforcement, DVFS OPP rounding and exact set, invalid child property failures, provider phandle lookup by ID, cpufreq platform-device creation/removal, and firmware error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si514.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-si514.c

### Purpose
`clk-si514.c` drives the Silicon Labs Si514 programmable oscillator over I2C. It exposes one programmable output clock with enable control and frequency programming from 100 kHz to 250 MHz.

### Important APIs, Types, And Functions
`struct clk_si514` holds `clk_hw`, regmap, and I2C client. `struct clk_si514_muldiv` holds fractional multiplier, integer multiplier, low-speed divider bits, and high-speed divider. Important functions are `si514_get_muldiv()`, `si514_set_muldiv()`, `si514_calc_muldiv()`, `si514_calc_rate()`, `si514_recalc_rate()`, `si514_determine_rate()`, `si514_set_rate()`, `si514_enable_output()`, and `si514_probe()`.

### Control Flow, State, And Persistence
Probe sets the clock name from `clock-output-names` or node name, initializes an I2C regmap, registers the clock, and adds an OF provider. Rate calculation reads seven hardware registers, reconstructs the multiplier/divider tuple, and computes output from the fixed 31.98 MHz crystal. Setting a rate disables output, writes divider registers in an order that triggers the change last, starts calibration, waits 10-12 ms, and restores output if it was previously enabled. Persistent state is entirely in oscillator registers and regmap cache.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C, regmap with volatile/writeable callbacks, OF compatible `silabs,si514`, and CCF rate consumers. Risks include no parent clock modeling for the crystal, `determine_rate()` placing an errno in `req->rate`, output left disabled after failed programming, integer overflow risk in low-frequency calculations, and large-rate changes only despite hardware fine-adjust support. Test signals include recalc from known register images, min/max rate rejection, output-enable prepare/unprepare, calibration wait after set-rate, regmap access restrictions, and measured oscillator frequency after programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si514.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si521xx.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-si521xx.c

### Purpose
`clk-si521xx.c` supports Skyworks Si52144/Si52146/Si52147 PCIe clock generators. It registers each differential output as a CCF clock, controls output-enable bits, and optionally configures output amplitude.

### Important APIs, Types, And Functions
`struct si521xx` holds client, regmap, up to nine `struct si_clk`, chip info bit map, and amplitude setting. `struct si_clk` stores the per-output `clk_hw`, backpointer, OE register, and OE bit. Important functions include custom I2C regmap read/write helpers, `si521xx_diff_recalc_rate()`, `si521xx_diff_determine_rate()`, `si521xx_diff_prepare()`, `si521xx_diff_unprepare()`, `si521xx_get_common_config()`, `si521xx_update_config()`, `si521xx_diff_idx_to_reg_bit()`, `si521xx_probe()`, `si521xx_suspend()`, and `si521xx_resume()`.

### Control Flow, State, And Persistence
Probe decodes model match data into an OE bit map, parses optional `skyworks,out-amplitude-microvolt`, initializes a flat custom regmap, programs BCP for one-byte reads, registers one `DIFF%d` clock for every populated OE bit, maps logical output indexes to OE registers using bit reversal, publishes an OF provider, and writes non-default amplitude. Prepare/unprepare sets or clears the mapped OE bit. Suspend switches regmap to cache-only and marks dirty; resume syncs settings.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C, regmap cache, parent clock index 0, Skyworks DT compatibles, and PCIe reference-clock consumers. Risks include no phandle bounds check, OF match data for `skyworks,si52147` differing from I2C ID data, ignored regmap errors in prepare/unprepare, no hardware ID verification, and rate modeling as parent multiplied by four. Test signals include output count per model, OE bit mapping for all DIFF outputs, amplitude validation from 300000 to 1000000 uV in 100000 uV steps, suspend/resume cache restore, parent-rate propagation, and measured differential outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si521xx.c -->
