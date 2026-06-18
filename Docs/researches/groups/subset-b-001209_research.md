# sources/distributed-fs/ceph-client/drivers/cpufreq subset-b-001209 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/intel_pstate.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/intel_pstate.c

## Purpose

`intel_pstate.c` is Intel's native CPU frequency scaling driver for modern x86 processors. It supports two cpufreq operating modes: the active `intel_pstate` driver, which owns policy selection through scheduler utilization callbacks and direct P-state/HWP programming, and the passive `intel_cpufreq` driver, which exposes Intel hardware to ordinary cpufreq governors. It handles legacy PERF_CTL P-states, Hardware P-states (HWP), HWP Energy Performance Preference (EPP), turbo limits, ACPI limits, hybrid CPU capacity scaling, and runtime sysfs mode changes.

The file is intentionally self-contained because it coordinates CPU model identification, MSR programming, scheduler hooks, cpufreq policy callbacks, HWP notifications, Energy Model registration for hybrid systems, and global `/sys/devices/system/cpu/intel_pstate/` controls.

## Important APIs, types, and functions

- `struct cpudata` is per-CPU persistent driver state: policy, scheduler update hook, P-state limits, APERF/MPERF samples, EPP cache, HWP request/capability cache, HWP boost state, ACPI `_PSS` data, hybrid capacity data, and HWP notification work.
- `struct pstate_data`, `struct vid_data`, `struct sample`, `struct global_params`, and `struct pstate_funcs` separate hardware limits, Atom VID encoding, utilization samples, global sysfs limits, and CPU-model-specific callbacks.
- `intel_pstate` and `intel_cpufreq` are the two `struct cpufreq_driver` instances. Active mode uses `.setpolicy`; passive mode uses `.target`, `.fast_switch`, and HWP `.adjust_perf`.
- `intel_pstate_init()` is the `device_initcall()` entry point. It rejects unsupported/vendor-managed platforms, selects HWP or PERF_CTL operation, applies early-parameter choices, allocates `all_cpu_data`, exposes sysfs, and registers the selected cpufreq driver.
- `intel_pstate_setup()` parses `intel_pstate=` early parameters: `disable`, `active`, `passive`, `no_hwp`, `no_cas`, `force`, `hwp_only`, `per_cpu_perf_limits`, and ACPI `_PPC` support when enabled.
- `intel_pstate_set_policy()`, `intel_pstate_update_util()`, `intel_pstate_adjust_pstate()`, and `intel_pstate_set_pstate()` implement active PERF_CTL control.
- `intel_pstate_hwp_set()`, `intel_cpufreq_hwp_update()`, `intel_cpufreq_adjust_perf()`, and HWP interrupt helpers program `MSR_HWP_REQUEST`, track `MSR_HWP_CAPABILITIES`, and react to firmware-reported performance changes.
- Sysfs handlers manage `status`, `no_turbo`, `min_perf_pct`, `max_perf_pct`, `hwp_dynamic_boost`, `energy_efficiency`, and per-policy HWP EPP attributes.

## Control flow and integration

Initialization first checks for Intel vendor, platform out-of-band power management, HWP support, and CPU model tables. With HWP, the file can use HWP on any Intel CPU advertising the feature, subject to EPP or DEC safety checks. Without HWP, it falls back to explicit model matches and validates the P-state MSRs. It then registers either active `intel_pstate` or passive `intel_cpufreq`, while sysfs `status` can switch between active/passive or turn the non-HWP driver off.

CPU policy init allocates or reuses `struct cpudata`, enables HWP if active, reads MSR-derived min/max/turbo limits, initializes ACPI performance limits, and sets cpufreq policy bounds. Active mode installs a scheduler utilization hook unless HWP active mode does not need dynamic boost. The hook samples APERF/MPERF/TSC at `INTEL_PSTATE_SAMPLING_INTERVAL`, accounts for IO-wait boost, computes a target P-state from busy fraction and previous average performance, clamps it through policy/global limits, and writes `MSR_IA32_PERF_CTL`.

Passive mode lets the cpufreq governor choose target frequencies. Normal target calls wrap transitions with `cpufreq_freq_transition_begin/end`; fast-switch and adjust-perf paths write local MSRs directly when allowed. With HWP, passive mode updates min/max/desired performance fields in `MSR_HWP_REQUEST`; without HWP, it writes PERF_CTL target ratios.

HWP notification interrupts queue delayed work to refresh HWP capabilities, policy maximums, and hybrid capacity scaling. Hybrid systems use CPPC or model scaling factors to translate performance levels to frequency, register lightweight Energy Model perf domains, and set architecture CPU capacity for scheduler asymmetry. If HWP is disabled on a hybrid CPU, the driver warns because that setup is known to be problematic.

## State and persistence behavior

Global mutable state includes `all_cpu_data`, selected `intel_pstate_driver`, `global` performance percentages, HWP mode flags, EPP defaults, hybrid scaling state, and sysfs kobjects. Per-CPU state persists across policy life and CPU hotplug until driver cleanup; offline CPUs have HWP min/max forced to the lowest performance to avoid constraining siblings. Suspend marks CPUs suspended, disables HWP interrupts, and resume re-enables HWP/request state when online callbacks did not already do so.

Hardware state persists in MSRs: `MSR_PM_ENABLE`, `MSR_HWP_REQUEST`, `MSR_HWP_INTERRUPT`, `MSR_HWP_STATUS`, `MSR_IA32_PERF_CTL`, `MSR_IA32_POWER_CTL`, APERF/MPERF, platform info, turbo ratio, Atom ratio/VID, and config TDP registers. The driver caches selected HWP request/capability values because scheduler callbacks and sysfs writes can race with direct MSR updates. Locks used for serialization include `intel_pstate_driver_lock`, `intel_pstate_limits_lock`, `hybrid_capacity_lock`, and `hwp_notify_lock`.

## Dependencies

The driver depends on x86 MSR and CPU model infrastructure, cpufreq core, scheduler cpufreq hooks, tracing, frequency QoS, ACPI processor/CPPC when configured, thermal HWP interrupt integration, Energy Model support for hybrid systems, and CPU topology/cache metadata. Correct behavior also depends on firmware not retaining exclusive P-state control unless `force` is used, valid HWP capability MSRs, correct ACPI `_PSS`/`_PPC`/PCCH data on systems that expose platform limits, and sane BIOS turbo/HWP defaults.

## Risks and edge cases

- Mode switching through sysfs unregisters and re-registers cpufreq drivers; cleanup must remove scheduler hooks and per-CPU allocations without racing hotplug.
- HWP request updates are shared between scheduler boost, sysfs EPP writes, passive governor paths, and suspend/offline paths. Stale cached request bits can leak undesired desired/min/max values.
- ACPI platform detection intentionally avoids systems with firmware-owned P-state control. `force` can bypass parts of this protection and may conflict with SMM/firmware.
- Hybrid scaling is subtle: wrong scaling factors or CPPC values can produce incorrect capacity, Energy Model cost, or frequency reporting.
- APERF/MPERF sampling skips unchanged counters and assumes local callbacks. Remote execution or NOHZ behavior can reduce responsiveness.
- Turbo and global percentage limits are coupled to `turbo_pstate`; invalid MSR data can make percentage math and sysfs limits misleading.
- HWP-notify work updates policy limits asynchronously; missed interrupt masking or work cancellation on offline/suspend can leave stale limits until the next policy refresh.

## Test signals

Build coverage should include HWP and non-HWP x86 configurations, ACPI/CPPC variants, and Energy Model enabled/disabled. Runtime signals include successful driver selection, correct `status` transitions, sysfs limit clamping, EPP attribute behavior, CPU hotplug, suspend/resume with HWP enabled, HWP notify interrupt handling, turbo disable/enable behavior, and cpufreq trace samples. Performance validation should compare active versus passive modes, fast-switch versus normal target paths, IO-wait boost response, and hybrid scheduler capacity on systems with P/E cores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/intel_pstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/kirkwood-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/kirkwood-cpufreq.c

## Purpose

`kirkwood-cpufreq.c` is a Marvell Kirkwood cpufreq driver that switches the CPU between two pre-existing clock parents: the normal CPU clock and the DDR clock. It does not synthesize arbitrary rates; it exposes a two-entry cpufreq table populated from device-tree clocks during probe.

## Important APIs, types, and functions

- The file-global `priv` stores the CPU, DDR, and powersave clocks, mapped control register base, and device pointer.
- `kirkwood_freq_table` has two states, `STATE_CPU_FREQ` and `STATE_DDR_FREQ`, whose frequencies are filled from `clk_get_rate()`.
- `kirkwood_cpufreq_target()` blocks CPU software interrupts with `CPU_SW_INT_BLK`, reparents the powersave clock, enters `cpu_do_idle()` so hardware completes the transition, and then restores interrupts.
- `kirkwood_cpufreq_cpu_init()` calls `cpufreq_generic_init()` with a 5000 ns transition latency.
- `kirkwood_cpufreq_probe()` maps the platform resource, fetches CPU node clocks by name, enables them, fills the table, and registers `kirkwood_cpufreq_driver`.

## Control flow

The platform driver probes a `"kirkwood-cpufreq"` device. It obtains CPU0's device-tree node, looks up `cpu_clk`, `ddrclk`, and `powersave`, enables all three clocks, then registers a cpufreq driver. Policy init uses the static table. A target transition selects the table row, disables local IRQs, writes the interrupt block bit in the mapped register, switches the `powersave` parent to CPU or DDR clock, idles the CPU to trigger the hardware transition, clears the block bit, and re-enables IRQs.

## State and persistence behavior

Runtime state is a single global `priv` and a globally mutated two-entry frequency table. Clock parent selection persists in the hardware clock tree until another cpufreq transition. Probe enables all referenced clocks for the driver's lifetime; remove unregisters cpufreq and disables the clocks. There is no suspend/resume-specific state handling.

## Dependencies

The driver depends on a platform device with one MMIO resource, CPU0 device-tree clocks named exactly `cpu_clk`, `ddrclk`, and `powersave`, common clock framework parent switching, ARM `cpu_do_idle()`, and cpufreq generic table helpers.

## Risks and edge cases

- The driver is global and assumes one Kirkwood CPU clock domain; multiple instances would overwrite `priv`.
- `clk_set_parent()` return values are ignored, so a failed reparent is reported as a successful frequency change.
- The transition masks local interrupts and blocks CPU software interrupts; incorrect register mapping or hardware behavior can hang the CPU in idle.
- Frequency table contents are populated at probe only, so later parent clock rate changes are not reflected.

## Test signals

Boot should show successful cpufreq registration and two available frequencies matching CPU and DDR clocks. Runtime tests should switch both states repeatedly, verify `scaling_cur_freq` follows `clk_get_rate(powersave)`, check there are no IRQ stalls, and unload/remove the platform device without leaked prepared clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/kirkwood-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.c

## Purpose

`longhaul.c` implements the VIA/Centaur C3 LongHaul and PowerSaver cpufreq driver for legacy x86 family 6 processors. It supports LongHaul v1 through `MSR_VIA_BCR2`, LongHaul v2 through `MSR_VIA_LONGHAUL`, and PowerSaver through the same LongHaul MSR with optional voltage scaling. The driver is deliberately opt-in through the `enable` module parameter because unsafe motherboard/interrupt/APIC combinations can freeze the machine.

## Important APIs, types, and functions

- `longhaul_get_cpu_mult()`, `calc_speed()`, and `guess_fsb()` translate hardware multiplier encodings and guessed FSB values into kHz.
- `do_longhaul1()` programs BCR2 software clock multiplier changes and invokes halt.
- `do_powersaver()` programs bus ratio and optional VID changes through `MSR_VIA_LONGHAUL`, using either halt or ACPI C3 I/O reads to trigger transitions.
- `longhaul_setstate()` is the core transition path. It masks PIC interrupts, waits for PCI bus master idle, disables bus arbitration through ACPI or VIA northbridge support, performs the MSR transition, restores arbitration/interrupt masks, verifies the multiplier, and retries with errata fallbacks.
- `longhaul_get_ranges()` builds the cpufreq table from model-specific multiplier tables.
- `longhaul_setup_voltagescaling()` reads VID bounds, selects VRM 8.5 or Mobile VRM tables, annotates table rows with VID data, and enables staged voltage scaling.
- `longhaul_cpu_init()` detects CPU model/stepping, selects multiplier tables from `longhaul.h`, discovers ACPI C3/northbridge support, builds the table, and installs policy data.

## Control flow

`late_initcall(longhaul_init)` first requires a Centaur family 6 CPU, the `enable` parameter, UP operation, and no APIC configuration known to be broken. CPU init maps model and stepping to Samuel, Samuel2, Ezra, Ezra-T, or Nehemiah behavior, copies the right multiplier/EBLCR tables, validates LongHaul v2 availability, initializes southbridge and ACPI data, and refuses systems without a safe bus-master/arbitration mechanism.

On target changes, the cpufreq core passes a table index. If voltage scaling is disabled, the driver calls `longhaul_setstate()` once. If voltage scaling is enabled, it walks intermediate table entries one VID step at a time with sleeps between steps, because large voltage jumps were observed to power off boards. `longhaul_setstate()` decides whether voltage must rise before frequency, performs low-level transition, then verifies the actual multiplier. If verification fails, it may enable the revision-key erratum workaround, disable ACPI C3, or downgrade v2 to v1 before retrying.

## State and persistence behavior

Global state tracks CPU model, LongHaul version, FSB, speed bounds, current table index, voltage-scaling tables, ACPI processor/C3 data, ACPI register address, and safety flags. `longhaul_table` is dynamically allocated during CPU init and freed on module exit. Exit attempts to return to the maximum multiplier before unregistering. Hardware state persists in LongHaul/BCR2 MSRs, chipset arbitration registers, and possibly voltage regulator state.

## Dependencies

The driver depends on x86 MSR access, ACPI processor C-state and bus-master control, PCI discovery of VIA northbridge/southbridge IDs, legacy PIC I/O ports, VIA-specific FADT timer behavior, and multiplier/VID tables from `longhaul.h`. It also depends on accurate boot `cpu_khz` for FSB guessing and on running on a single CPU without IO-APIC.

## Risks and edge cases

- The driver can hang hardware, which is why `enable` is required and SMP/APIC are rejected.
- FSB detection is heuristic for most models; wrong guesses produce invalid frequency tables or unsafe target speeds.
- `bm_timeout` is initialized once before the retry loop, so repeated retry paths inherit decremented timeout state.
- ACPI C3 may claim to work but fail to trigger frequency changes; the driver has fallback retries, but transition failure can still leave hardware at an unexpected rate.
- Voltage scaling relies on VID tables and CPU-reported min/max values; bogus values disable it, but incorrect-but-plausible firmware data remains risky.
- Transition code manipulates PIC masks, ACPI arbiter bits, and northbridge ports directly; interrupts and bus masters are highly sensitive here.

## Test signals

Useful signals are mostly hardware-based: module load should require `enable=1`, build a sorted table with more than one entry, and log selected ACPI/northbridge safety method. Repeated transitions across all table entries should verify actual multiplier after each change, avoid PCI bus timeout warnings, and survive module exit returning to max multiplier. Voltage-scaling validation needs board power stability and temperature/power observation across stepped VID transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.h

## Purpose

`longhaul.h` is the VIA-specific data contract used by `longhaul.c`. It defines the MSR bitfield layouts for LongHaul/BCR2 control and provides static multiplier, EBLCR decode, and voltage ID lookup tables for multiple VIA C3 generations and VRM schemes.

## Important APIs, types, and functions

- `union msr_bcr2` describes the BCR2 software bus-frequency fields used by LongHaul v1, especially `ESOFTBF` and `CLOCKMUL`.
- `union msr_longhaul` describes LongHaul/PowerSaver MSR fields for revision key, soft bus ratio, soft VID, FSB select, max/min ratio, and voltage limits.
- `samuel1_mults`, `samuel1_eblcr`, `samuel2_eblcr`, `ezra_mults`, `ezra_eblcr`, `ezrat_mults`, `ezrat_eblcr`, `nehemiah_mults`, and `nehemiah_eblcr` map 4-bit or 5-bit hardware encodings to multipliers expressed as ratio times 10.
- `struct mV_pos`, `vrm85_mV`, `mV_vrm85`, `mobilevrm_mV`, and `mV_mobilevrm` map voltage IDs to millivolts and reverse VID encodings.

## Control flow and integration

The header has no runtime control flow. `longhaul_cpu_init()` copies the appropriate multiplier and EBLCR arrays into mutable driver arrays after identifying CPU model and stepping. `longhaul_get_cpu_mult()` decodes the current EBLCR value through the copied `eblcr` table. `longhaul_get_ranges()` builds the cpufreq table from the copied `mults` table. `longhaul_setup_voltagescaling()` uses the VRM tables to convert CPU-reported VID fields into voltage steps and to embed VID values into cpufreq `driver_data`.

## State and persistence behavior

The arrays are static constant source data and do not mutate. Persistent runtime state lives in `longhaul.c`, which copies the selected arrays so it can use one transition path for all CPU variants. The union definitions mirror MSR persistence but do not own state themselves.

## Dependencies

The header depends on compiler bitfield layout matching the driver's intended x86 little-endian MSR interpretation and on `longhaul.c` selecting the correct table for CPU model/stepping. It is tightly coupled to VIA C3 hardware documentation and to cpufreq table construction in `longhaul.c`.

## Risks and edge cases

- Table values marked `-1` represent reserved encodings; missing checks in callers would allow invalid multiplier programming.
- Some table comments document hardware quirks and alternate meanings; changing one table can affect both decode and write paths differently.
- The MSR bitfield names include reserved fields and a spelling typo in `Reseved`; this is harmless but underscores that the layout must not be casually reordered.
- Voltage reverse maps must remain consistent with `struct mV_pos` entries or staged voltage scaling will write the wrong VID.

## Test signals

Static validation should compare all multiplier and VID tables against VIA datasheets. Runtime signals come from `longhaul.c`: correct table selection for each CPU stepping, no reserved current multiplier, sorted frequency table generation, and safe voltage logs showing expected VID per frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/longhaul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/longrun.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/longrun.c

## Purpose

`longrun.c` implements CPUFreq support for Transmeta Crusoe and Efficeon LongRun processors. Unlike table-based drivers, LongRun exposes a firmware/microcode policy range: the driver converts cpufreq kHz limits into performance percentages and programs Transmeta MSRs that bound the processor's internal dynamic scaling.

## Important APIs, types, and functions

- `longrun_low_freq` and `longrun_high_freq` cache the discovered frequency range used for percent/kHz conversion.
- `longrun_get_policy()` reads `MSR_TMTA_LONGRUN_FLAGS` and `MSR_TMTA_LONGRUN_CTRL` to report current powersave/performance policy and min/max bounds.
- `longrun_set_policy()` writes policy mode and lower/upper LongRun percentages back to the same MSRs.
- `longrun_verify_policy()` clamps policy requests to CPU limits.
- `longrun_get()` uses Transmeta CPUID leaf `0x80860007` to report current MHz as kHz.
- `longrun_determine_freqs()` discovers low/high frequency using the LongRun Table Interface when available, or by manipulating LongRun bounds and deriving low frequency from CPUID percentage data.
- `longrun_cpu_init()` supports CPU0 only, discovers limits, and seeds the cpufreq policy.

## Control flow

`module_init(longrun_init)` matches a Transmeta CPU with `X86_FEATURE_LONGRUN` and registers the cpufreq driver. Policy init rejects nonzero CPUs, discovers the low/high range, fills `policy->cpuinfo`, then reads current LongRun policy from MSRs. Future policy changes call `.setpolicy`, which converts cpufreq min/max into 0-100 percentages, clamps them, writes performance/economy mode, and writes the lower/upper percentage fields.

When the LongRun Table Interface is present, discovery reads table levels from `MSR_TMTA_LRTI_*`. Otherwise it uses boot `cpu_khz` as high frequency, temporarily lowers the upper performance percentage in 10% steps if needed, reads current MHz and percentage from CPUID, restores original MSR limits, and solves for low frequency.

## State and persistence behavior

The driver has only two global frequency-bound variables and relies on hardware MSRs for persistent policy. It registers and unregisters the cpufreq driver at module init/exit. LongRun microcode continues controlling actual frequency within programmed bounds; the kernel does not own a discrete OPP table.

## Dependencies

Dependencies include Transmeta CPUID leaves, Transmeta LongRun MSRs, optional `X86_FEATURE_LRTI`, boot-calibrated `cpu_khz`, cpufreq policy interfaces, and x86 CPU matching. It assumes single-CPU control and returns zero frequency for CPUs other than CPU0.

## Risks and edge cases

- Degenerate low/high tables are handled by collapsing min and max, but percentage math depends on `(high - low) / 100`; very narrow ranges can lose precision.
- The fallback discovery method temporarily changes LongRun bounds. Failures restore saved values in the main loop, but unusual firmware responses can produce `-EIO`.
- Policy conversion truncates integer percentages, so exact requested kHz limits may not be represented.
- The `.setpolicy` path does not reject unknown `policy->policy` values beyond ignoring them after clearing the performance bit.

## Test signals

Tests should verify module load only on LongRun-capable Transmeta CPUs, correct min/max discovery through both LRTI and fallback paths, policy toggling between powersave and performance, and current frequency reporting from CPUID. Regression signals include preserved MSR bounds after discovery, valid cpufreq limits, and no divide-by-zero behavior on degenerate firmware tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/longrun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/loongson2_cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/loongson2_cpufreq.c

## Purpose

`loongson2_cpufreq.c` is the Loongson-2F CPUFreq driver. It builds a clock-modulation table from the platform's CPU clock, programs Loongson rate changes through platform helpers, and optionally replaces the architecture `cpu_wait` hook with a Loongson-specific wait sequence.

## Important APIs, types, and functions

- `loongson2_cpufreq_cpu_init()` computes table frequencies from `cpu_clock_freq` and `loongson2_clockmod_table`, sets the initial full rate, and calls `cpufreq_generic_init()`.
- `loongson2_cpufreq_target()` converts a selected table row into a kHz target by multiplying the base clock by the row's divisor data over 8, then calls `loongson2_cpu_set_rate()`.
- `loongson2_cpu_freq_notifier()` updates `current_cpu_data.udelay_val` after cpufreq transitions.
- `loongson2_cpu_wait()` saves `LOONGSON_CHIPCFG`, clears low clock bits to enter wait mode, restores the saved value, and re-enables local IRQs.
- The `nowait` module parameter disables replacement of `cpu_wait`.

## Control flow

Module init registers a platform driver ID table, registers the transition notifier, then registers the cpufreq driver. On success, unless `nowait` is set, it saves the existing `cpu_wait` pointer and installs `loongson2_cpu_wait`. Policy init populates table entries from index 2 upward, because the shared clockmod table encodes fractional eighths, and sets the CPU to full boot rate. Target changes call the board-specific rate setter directly.

## State and persistence behavior

Global state includes `nowait`, `saved_cpu_wait`, the notifier block, and the architecture-global `cpu_wait` pointer. Frequency state persists in Loongson chip configuration registers managed by `loongson2_cpu_set_rate()`. Module exit restores `cpu_wait`, unregisters the cpufreq driver and notifier, and unregisters the platform driver.

## Dependencies

The driver depends on Loongson2EF platform headers for `cpu_clock_freq`, `loongson2_clockmod_table`, `loongson2_cpu_set_rate()`, and `LOONGSON_CHIPCFG`, plus MIPS idle hooks and cpufreq generic helpers. It assumes the platform device name `loongson2_cpufreq`.

## Risks and edge cases

- The file comment says Loongson 2E does not support this feature; platform registration must ensure only supported 2F hardware binds.
- `loongson2_cpu_wait()` calls `local_irq_enable()` after restoring state, so callers must match the expected idle/IRQ context.
- The notifier is registered before cpufreq driver registration and is not unwound if `cpufreq_register_driver()` fails.
- Target changes do not wrap transition notifications locally, relying on cpufreq core behavior around `.target_index`.

## Test signals

Boot should log the Loongson-2F driver, expose the expected fractional table, and keep delay calibration correct after transitions. Runtime tests should switch every table row, verify chip configuration restoration from wait, test `nowait=1`, and unload the module while confirming `cpu_wait` is restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/loongson2_cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/loongson3_cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/loongson3_cpufreq.c

## Purpose

`loongson3_cpufreq.c` is a LoongArch Loongson-3 cpufreq driver that delegates DVFS control to platform firmware through an IOCSR SMC mailbox. It discovers firmware-provided frequency levels per CPU/core, marks boost levels, and exposes them as cpufreq tables shared across topology siblings.

## Important APIs, types, and functions

- `union smc_message` defines the packed mailbox protocol fields: ID, info, value, command, extra flag, and completion bit.
- Command macros cover feature negotiation, sensor/fan commands, and DVFS commands such as `CMD_GET_FREQ_LEVEL_NUM`, `CMD_GET_FREQ_LEVEL_INFO`, and `CMD_SET_FREQ_INFO`.
- `struct loongson3_freq_data` stores the default frequency level and a flexible cpufreq table.
- `do_service_request()` serializes per-package mailbox access, writes `LOONGARCH_IOCSR_SMCMBX`, raises the soft interrupt bit, polls for completion, checks `CMD_OK`, and returns `msg.val`.
- `configure_freq_table()` queries level count, first boost level, and per-level frequencies, then allocates and caches per-CPU frequency data.
- `loongson3_cpufreq_target()` sets a frequency level for the target CPU core via firmware.

## Control flow

The platform driver matches `loongson3_cpufreq`. Probe initializes one mutex per package, validates firmware version, enables DVFS and boost features, stores the platform device in driver data, and registers cpufreq. CPU init lazily builds the table for the policy CPU, sets transition latency to 10 us, sets `suspend_freq` to the default non-boost level, and copies sibling CPUs into the same policy mask while sharing the same `freq_data` pointer.

Targets are level indexes, not raw frequencies. The driver sends `CMD_SET_FREQ_INFO` with `FREQ_INFO_TYPE_LEVEL` and the requested table index. `.get` asks firmware for current frequency and converts MHz-like values to kHz with `KILO`. Exit restores the default level.

## State and persistence behavior

State is split between firmware mailbox state, per-package mutexes, and per-CPU cached `loongson3_freq_data` allocations managed by device-managed memory. Sibling CPUs share the same table pointer. The driver does not free per-CPU pointers on policy exit because allocations are tied to platform device lifetime. Hardware DVFS enable/boost settings persist in firmware after probe until platform reset or firmware changes.

## Dependencies

Dependencies include LoongArch IOCSR accessors, `LOONGARCH_IOCSR_SMCMBX`, `LOONGARCH_IOCSR_MISC_FUNC`, CPU package/core topology in `cpu_data`, `MAX_PACKAGES`, cpufreq boost helpers, platform device binding, and firmware support for the documented SMC command set.

## Risks and edge cases

- `do_service_request()` uses `raw_smp_processor_id()` for package locking, while callers may request data for another CPU ID; mailbox affinity assumptions must match firmware routing.
- Completion polling waits up to 10000 short sleeps and collapses all timeout/non-OK statuses to `-EPERM`, reducing diagnosability.
- `def_freq_level = boost_level - 1` assumes firmware reports boost level greater than zero.
- Tables are capped at `FREQ_MAX_LEVEL`; firmware levels beyond 16 are ignored.
- `.get` returns `ret * KILO` even if `ret` is negative, so firmware errors can appear as large unsigned values.

## Test signals

Probe should successfully read interface version, enable DVFS/boost, and build cpufreq tables with boost flags at and above the firmware boost level. Runtime tests should switch every level, confirm current frequency from firmware, verify sibling policy masks, test suspend frequency selection, and exercise multi-package concurrent transitions for mailbox serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/loongson3_cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq-hw.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq-hw.c

## Purpose

`mediatek-cpufreq-hw.c` is a MediaTek hardware-managed cpufreq driver. Instead of using OPP/regulator/PLL sequencing in software, it reads firmware-populated LUTs from MMIO performance domains and switches performance states by writing hardware registers or, on hybrid DVFS variants such as MT8196, per-CPU FDVFS registers.

## Important APIs, types, and functions

- `struct mtk_cpufreq_variant` holds register offsets, an optional variant init hook, and an `is_hybrid_dvfs` flag.
- `struct mtk_cpufreq_priv` stores the device, variant, and optional FDVFS mapping.
- `struct mtk_cpufreq_domain` stores one cpufreq domain's table, register bases, requested resource, mapping, and OPP count.
- `mtk_cpu_create_freq_table()` reads up to 32 LUT rows, extracts `LUT_FREQ`, stops at a repeated frequency, and terminates the cpufreq table.
- `mtk_cpu_resources_init()` maps the domain selected by `performance-domains`, with an index adjustment for hybrid DVFS.
- `mtk_cpufreq_hw_target_index()`, `mtk_cpufreq_hw_fast_switch()`, and `mtk_cpufreq_hw_get()` implement cpufreq callbacks.
- `mtk_cpufreq_register_em()` registers an Energy Model using power data read from `REG_EM_POWER_TBL`.

## Control flow

Probe first checks that every present CPU has a `"cpu"` regulator available, preventing cpufreq registration before supplies exist. It selects variant data from device-tree compatible strings, performs variant init if needed, stores private data, and registers the cpufreq driver. Policy init maps the correct MMIO domain through `of_perf_domain_get_sharing_cpumask()`, builds a table from the LUT, sets transition latency from hardware, enables the cpufreq hardware block, and polls for CPUFreq/SVS hardware readiness.

Target changes either write the table index to `REG_FREQ_PERF_STATE` or, with FDVFS, convert target kHz to the 26 kHz divider units expected by the FDVFS register and write one register per real CPU in the policy. Fast switch uses the same writes after selecting the closest table index. Energy Model registration exposes firmware-provided power rows for scheduler/thermal use.

## State and persistence behavior

Per-policy domain mappings are explicitly requested and mapped at init, then unmapped and released at exit. The cpufreq table is device-managed but tied to the domain data. Hardware state persists in performance-state, enable, and FDVFS registers. The driver enables the hardware block during policy lifetime and writes zero to pause it on exit. There is no dedicated suspend/resume callback.

## Dependencies

The driver depends on device-tree `performance-domains`, ordered MMIO resources matching domain indexes, variant-compatible register layouts, firmware-populated LUT/status/power/latency registers, CPU regulators, cpufreq fast-switch support, and Energy Model APIs.

## Risks and edge cases

- In `mtk_cpu_resources_init()`, errors after `ioremap()` during table creation return without unmapping/releasing the region, so probe-failure cleanup is incomplete on that path.
- LUT parsing stops on the first repeated frequency; malformed LUTs can truncate valid states or produce zero OPPs.
- FDVFS fast-switch writes `target_freq` rather than the selected table frequency, so callers must pass a value acceptable to hardware rounding.
- `mtk_cpufreq_get_cpu_power()` decrements `i` after the loop; requests below the first table frequency can underflow.
- Poll timeout distinguishes missing CPUFreq hardware from missing SVS only through current status bits; SVS timeout is logged but not fatal.

## Test signals

Validation should include probe deferral until CPU regulators exist, correct domain mapping for each `performance-domains` entry, table contents matching hardware LUTs, successful hardware enable/status polling, fast-switch operation, FDVFS writes on MT8196, Energy Model power readings, and clean region release on policy exit. Thermal cooling registration should also observe `CPUFREQ_IS_COOLING_DEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq.c

## Purpose

`mediatek-cpufreq.c` is MediaTek's software DVFS cpufreq driver. It uses CPU OPP tables, CPU/intermediate clocks, and one or two regulators per cluster to change CPU frequency safely. It supports SoC-specific voltage constraints, optional SRAM voltage tracking, and optional CCI frequency coordination.

## Important APIs, types, and functions

- `struct mtk_cpufreq_platform_data` provides voltage shift limits, max voltages, SRAM bounds, and CCI support per SoC.
- `struct mtk_cpu_dvfs_info` stores a cluster's CPU mask, CPU/CCI devices, regulators, CPU and intermediate clocks, OPP notifier, current voltage/frequency, and tracking parameters.
- `mtk_cpufreq_voltage_tracking()` enforces `Vsram - Vproc` shift constraints while stepping voltage up or down.
- `mtk_cpufreq_set_target()` is the main transition sequence: raise voltage if needed, reparent CPU to intermediate clock, change ARM PLL rate, reparent back, then lower voltage if allowed.
- `mtk_cpufreq_opp_notifier()` reacts to OPP voltage adjustments and disabled current OPPs.
- `mtk_cpu_dvfs_info_init()` acquires devices, clocks, regulators, OPP tables, intermediate voltage, and notifier state for one sharing domain.
- `mtk_cpufreq_driver_init()` matches machine compatibles, registers an internal platform driver, then creates a `"mtk-cpufreq"` platform device carrying SoC data.

## Control flow

Module init matches the machine compatible table and creates a platform device because cpufreq drivers historically lacked direct DT binding. Probe iterates present CPUs, skips CPUs already covered by a sharing mask, allocates `mtk_cpu_dvfs_info`, initializes hardware resources, and appends each domain to `dvfs_info_list`. It then registers the cpufreq driver. Policy init looks up the domain for the policy CPU, converts OPPs into a cpufreq table, copies the sharing mask, and stores `policy->clk` and `driver_data`.

During a target transition, the driver locks `reg_lock`, resolves the target OPP voltage, optionally raises it to at least boot voltage until the CCI driver is bound, scales voltage up to the maximum of intermediate and target voltage, switches the CPU clock to a stable intermediate parent, changes the original PLL rate, switches back, and scales voltage down to the final target when safe. Error paths try to restore previous voltage or clock parent/rate.

## State and persistence behavior

Each DVFS domain persists in `dvfs_info_list` for platform device lifetime. Regulator and clock handles are explicitly enabled during init and disabled/put only on probe failure; the platform driver has no remove callback, so normal operation assumes built-in lifetime. `pre_vproc` caches the last set voltage for faster transitions, while `current_freq` is used by OPP notifiers. Device links track CCI readiness and are auto-removed on consumer cleanup.

## Dependencies

Dependencies include CPU device-tree OPP v2 tables with sharing data, CPU clocks named `"cpu"` and `"intermediate"`, optional `"proc"` and `"sram"` regulators, optional `mediatek,cci` phandle, regulator voltage constraints, common clock reparenting/rate APIs, OPP notifier infrastructure, and SoC-compatible platform data.

## Risks and edge cases

- `dev_err_probe(cpu_dev, ...)` is used when `cpu_dev` may be NULL, which is questionable because there is no device to log against.
- Voltage tracking has many rollback paths; regulator failures can leave Vproc/Vsram at intermediate values if the rollback itself fails.
- CCI readiness raises CPU voltage to boot voltage as a crash-prevention workaround, but may reduce power efficiency until supplier binding completes.
- OPP disable notification calls back into `cpufreq_driver_target()` while OPP lists are changing; locking and notifier ordering are important.
- The driver registers a platform device in module init and has no platform-driver remove path for releasing `dvfs_info_list` on normal unload beyond module exit unregistering the device/driver.

## Test signals

Tests should cover all compatible SoC voltage constraints, OPP table parsing, regulator enable/disable failure paths, SRAM tracking up/down steps, intermediate-clock parent switching, CCI unavailable-to-bound transitions, OPP voltage adjustment, current OPP disable fallback, thermal cooling registration, and repeated frequency sweeps under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/mediatek-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/mvebu-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/mvebu-cpufreq.c

## Purpose

`mvebu-cpufreq.c` is a small Armada XP compatibility initializer. It adds nominal and half-rate OPPs for each present CPU and registers the generic `cpufreq-dt` platform device when the device tree has the newer Armada XP CPU clock binding that exposes PMU DFS registers.

## Important APIs, types, and functions

- `armada_xp_pmsu_cpufreq_init()` is the only function and runs as a `device_initcall()`.
- It uses `of_machine_is_compatible()`, `of_find_compatible_node()`, and `of_address_to_resource()` to validate the CPU clock binding.
- It uses `clk_get()`, `clk_get_rate()`, `dev_pm_opp_add()`, and `dev_pm_opp_set_sharing_cpus()` to register per-CPU OPPs.
- It ends by creating `platform_device_register_simple("cpufreq-dt", ...)`.

## Control flow

On Armada XP only, the initializer finds the `"marvell,armada-xp-cpu-clock"` node and requires resource index 1 to exist. That resource check filters out old device trees whose CPU clock binding lacks PMU DFS registers. It then iterates present CPUs, gets each CPU clock, adds the full clock rate and half clock rate as OPPs, marks OPP sharing as per-CPU, releases the clock, and finally instantiates `cpufreq-dt`.

## State and persistence behavior

The file owns no private runtime state. OPPs are added to CPU device OPP tables and persist for the kernel lifetime. The created `cpufreq-dt` platform device persists; there is no removal path because this is built as an init helper.

## Dependencies

Dependencies include Armada XP machine compatibility, a CPU clock provider with PMU DFS register resource, CPU devices, common clock framework, OPP library, and the generic `cpufreq-dt` driver. It relies on another clock notifier path to perform the PMSU hardware portion of transitions.

## Risks and edge cases

- On old device trees the driver quietly returns after a firmware warning, so cpufreq is unavailable.
- If adding the second OPP fails, it removes the first OPP for that CPU but leaves OPPs already added for earlier CPUs.
- `dev_pm_opp_set_sharing_cpus()` errors are logged but not fatal.
- Only nominal and half-rate states are exposed; hardware or board-specific additional states are not represented.

## Test signals

Boot on Armada XP should register two OPPs per CPU and create a `cpufreq-dt` device only when the CPU clock binding has the PMU DFS resource. Runtime validation should switch between full and half rates, confirm PMSU notifier execution, and test old-DT fallback logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/mvebu-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/p4-clockmod.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/p4-clockmod.c

## Purpose

`p4-clockmod.c` exposes Pentium 4/Xeon and related Intel ACPI clock-modulation duty cycles as cpufreq states. It is a throttling driver, not true voltage/frequency scaling, and it intentionally avoids module autoloading because platform-specific SpeedStep or ACPI cpufreq drivers are usually better.

## Important APIs, types, and functions

- Duty-cycle enum values map to IA32 thermal-control modulation states, with `DC_DISABLE` representing full speed.
- `cpufreq_p4_setdc()` writes `MSR_IA32_THERM_CONTROL`, checks thermal status, applies N44/O17 errata by avoiding 12.5% and 25% duty cycles, and enables/disables modulation.
- `p4clockmod_table` contains duty-cycle cpufreq entries from 12.5% through 100%, with reserved/invalid rows.
- `cpufreq_p4_get_frequency()` detects stock frequency through `speedstep-lib` helpers and marks constant loops where TSC is invariant under throttling.
- `cpufreq_p4_cpu_init()` sets sibling policy masks, detects errata steppings, may recalibrate on early desktop P4, fills the table from `stock_freq`, and sets high transition latency.

## Control flow

`late_initcall(cpufreq_p4_init)` requires Intel `X86_FEATURE_ACC` and ACPI capability, then registers cpufreq. Policy init fills a global table from the detected stock frequency and invalidates low duty cycles on errata CPUs. Target changes iterate all logical CPUs in the policy sibling mask and write the selected duty-cycle control bits to each CPU's thermal-control MSR. `.get` reads the current modulation bits and returns stock frequency scaled by duty cycle or full stock frequency when disabled.

## State and persistence behavior

Global state includes `has_N44_O17_errata[]`, `stock_freq`, and the mutated frequency table. Duty-cycle settings persist per logical CPU in `MSR_IA32_THERM_CONTROL` until another target or external thermal control changes them. There is no suspend/resume state handling. The driver sets `CPUFREQ_CONST_LOOPS` for processors where loop calibration should not scale with clock modulation.

## Dependencies

The driver depends on x86 MSR access, Intel ACPI clock modulation feature detection, SpeedStep frequency helpers, topology sibling masks, and cpufreq generic table verification. It intentionally has no `MODULE_DEVICE_TABLE`.

## Risks and edge cases

- Clock modulation reduces duty cycle without lowering voltage; it can hurt performance/power efficiency and should not be confused with real DVFS.
- `stock_freq` and `p4clockmod_table` are global, so heterogeneous systems are not represented.
- Thermal throttling can already be active; the driver only logs it and still writes modulation.
- Errata invalidation is per policy CPU, but the table is global and may affect all policies after one errata CPU initializes.

## Test signals

Validation should confirm the driver does not autoload, warns when better EST/SpeedStep drivers exist, exposes valid duty-cycle states, avoids errata low states, writes all SMT siblings, and reports current frequency from thermal-control MSR bits. Thermal stress should ensure hardware throttling interactions do not corrupt cpufreq state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/p4-clockmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pasemi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pasemi-cpufreq.c

## Purpose

`pasemi-cpufreq.c` implements CPUFreq support for PA Semi PWRficient systems. It exposes five A-states, reads their frequencies from SDCPWR configuration registers, and switches all online CPUs by writing SDC ASR registers.

## Important APIs, types, and functions

- `pas_freqs` contains A0-A4 table rows; turbo A5/A6 are intentionally excluded.
- `get_astate_freq()`, `get_cur_astate()`, and `get_gizmo_latency()` read SDCPWR registers to determine table frequencies, current state, and transition latency.
- `set_astate()` writes a CPU's ASR register with IRQs disabled.
- `check_astate()` and `restore_astate()` are exported helper-style functions used by platform idle/power paths to observe or restore the current A-state.
- `pas_cpufreq_cpu_init()` maps SDC/Gizmo resources from device tree, fills the table, initializes current frequency, and calls `cpufreq_generic_init()`.
- `pas_cpufreq_target()` updates `current_astate`, writes every online CPU, and updates `ppc_proc_freq`.

## Control flow

Module init only registers the driver on `PA6T-1682M` or `pasemi,pwrficient` machines. CPU init reads CPU `clock-frequency`, maps the SDC ASR window and Gizmo power registers, fills the frequency table by reading each A-state's configuration register, reads the current A-state for the policy CPU, updates PowerPC global processor frequency, and initializes cpufreq. Target changes are global: the selected A-state is written for every online CPU.

## State and persistence behavior

State is global MMIO mappings plus `current_astate`. The driver deliberately does not unmap resources after the system reaches running state because CPU hotplug is not supported. Hardware A-state persists in SDCPWR/SDCASR registers, and `restore_astate()` uses cached `current_astate` when returning from power savings. `ppc_proc_freq` is updated on init and target changes.

## Dependencies

The driver depends on PA Semi device-tree compatibles (`1682m-sdc`, `pasemi,pwrficient-sdc`, `1682m-gizmo`, `pasemi,pwrficient-gizmo`), PowerPC MMIO helpers, hard SMP processor IDs, `ppc_proc_freq`, and platform power-management code using `check_astate()`/`restore_astate()`.

## Risks and edge cases

- Only one set of global mappings exists; multiple policies or hotplug are not supported.
- `pas_cpufreq_cpu_init()` can be invoked per policy, but mapping globals are not protected against repeated initialization.
- Frequencies are derived from register low bits times 100 MHz, which assumes hardware encoding remains stable.
- Target changes update all online CPUs regardless of policy CPU mask.

## Test signals

Tests should verify table rows match SDCPWR A-state configuration, current state reads correctly, target writes affect all online CPUs, `ppc_proc_freq` tracks selected state, idle restore paths call `restore_astate()`, and module unload before `SYSTEM_RUNNING` unmaps resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pasemi-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pcc-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pcc-cpufreq.c

## Purpose

`pcc-cpufreq.c` implements the ACPI Processor Clocking Control interface. It communicates with firmware through a shared PCCH memory region and a doorbell register, exposing firmware-defined percentage-of-nominal frequency control as a cpufreq driver.

## Important APIs, types, and functions

- `struct pcc_header` maps the shared PCCH header containing command/status, latency, nominal, throttled, and minimum frequencies.
- `struct pcc_register_resource` and `struct pcc_memory_resource` parse ACPI resource buffers from the `PCCH` package.
- `struct pcc_cpu` stores per-CPU input and output offsets obtained from each processor's `PCCP` object.
- `pcc_cpufreq_evaluate()` finds `\_SB.PCCH`, optionally negotiates `_OSC`, maps the shared memory, parses doorbell preserve/write masks, allocates per-CPU data, and logs limits.
- `pcc_get_offset()` evaluates `PCCP` for a CPU and clears its buffers.
- `pcc_cmd()` rings the ACPI doorbell and polls `pcch_hdr->status` for `CMD_COMPLETE`.
- `pcc_get_freq()` issues `CMD_GET_FREQ`; `pcc_cpufreq_target()` issues `CMD_SET_FREQ`.

## Control flow

`late_initcall(pcc_cpufreq_init)` uses `platform_driver_probe()` so probe runs once. Probe refuses to initialize if another cpufreq driver is active or ACPI is disabled. It evaluates PCCH, disables dynamic switching on systems with more than four CPUs, and registers cpufreq. CPU init evaluates `PCCP` offsets and sets policy min/max from PCCH minimum/nominal frequencies. Target changes translate target kHz to a percentage of nominal, write the CPU input buffer, set command, ring the doorbell, clear the input buffer, and end the cpufreq transition based on completion status.

## State and persistence behavior

Global state includes the PCCH mapping, header pointer, doorbell GAS, preserve/write masks, spinlock, and per-CPU offset storage. All firmware commands are serialized by `pcc_lock`. Mapped shared memory persists until platform remove, which unregisters cpufreq, unmaps PCCH, and frees per-CPU data. Firmware owns the actual processor clock state.

## Dependencies

The driver depends on ACPI `PCCH`, processor `PCCP`, optional `_OSC` negotiation, ACPI generic address read/write helpers, shared memory resources, cpufreq core, and per-CPU ACPI processor objects. It also depends on firmware respecting the command/status protocol and percentage encodings.

## Risks and edge cases

- `pcc_cmd()` busy-polls without delay or timeout error reporting beyond status not complete after 300 loops.
- Shared memory resource lengths and offset bounds are trusted after basic type checks; malformed firmware could point offsets outside the mapping.
- More than four CPUs causes `CPUFREQ_NO_AUTO_DYNAMIC_SWITCHING`, reflecting protocol scalability concerns.
- `pcc_cpufreq_target()` uses the target frequency directly rather than selecting a validated table, so firmware percentage rounding determines the actual result.
- ACPI `_OSC` failure is nonfatal by design, so systems with ambiguous control ownership may still proceed.

## Test signals

Validation should include ACPI table parsing, successful PCCH mapping, correct per-CPU PCCP offsets, get/set command completion, min/max policy bounds matching firmware, dynamic switching disabled on large systems, and cleanup on remove. Firmware error injection should verify incomplete commands return safe failures and clear status/input buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pcc-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pmac32-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pmac32-cpufreq.c

## Purpose

`pmac32-cpufreq.c` provides 32-bit PowerMac CPUFreq support for older Apple PowerBook/iBook/MacRISC3 systems. It exposes two firmware-defined speeds, high and low, and selects one of several machine-specific mechanisms: PMU command plus sleep transition, GPIO bus slewing, 7447A DFS, or 750FX PLL control.

## Important APIs, types, and functions

- Global frequency state includes `low_freq`, `hi_freq`, `cur_freq`, `sleep_freq`, and `transition_latency`.
- `set_speed_proc` and `get_speed_proc` point to the selected hardware implementation.
- `cpu_750fx_cpu_speed()`, `dfs_set_cpu_speed()`, `gpios_set_cpu_speed()`, and `pmu_set_cpu_speed()` implement the four transition mechanisms.
- `do_set_cpu_speed()` wraps transitions and temporarily disables/restores L3 cache around low-speed changes.
- `pmac_cpufreq_suspend()` and `pmac_cpufreq_resume()` force safe speed/voltage handling across sleep.
- `pmac_cpufreq_init_MacRISC3()`, `pmac_cpufreq_init_7447A()`, and `pmac_cpufreq_init_750FX()` detect machine-specific data from device tree.
- `pmac_cpufreq_setup()` is module init and registers the cpufreq driver after selecting a transition implementation.

## Control flow

Setup exits early if the boot command line contains `nocpufreq`. It reads CPU0 `clock-frequency`, then checks machine compatibles and CPU PVR to pick a backend. MacRISC3 systems may use voltage/frequency/slew GPIOs derived from KeyLargo-style device-tree nodes, or PMU-based min/max clock properties. 7447A systems use dynamic power step and DFS with voltage GPIO. 750FX systems use reduced-clock-frequency and HID/PLL control.

The cpufreq table has only high and low entries. A target call passes the selected table index to `do_set_cpu_speed()`, which calls the selected backend and updates `cur_freq` and `ppc_proc_freq`. PMU-based transitions are the most invasive: they suspend PMU operations, raise MPIC priority, suppress decrementer interrupts, disable interrupts, save cache control registers, issue a PMU speed command, enter low-level sleep handling, restore northbridge/cache/MMU context, and resume PMU.

## State and persistence behavior

The driver uses global state because supported systems have one CPU frequency domain. Hardware speed persists in GPIOs, HID/DFS/PLL bits, or PMU-selected PLL configuration. Suspend stores `sleep_freq`, forces high speed for non-PMU low-speed sleep, and resume restores the previous high/low choice after re-reading speed when possible. `no_schedule` switches delays from sleepable `msleep()` to `mdelay()` during suspend.

## Dependencies

Dependencies include PowerMac feature calls, PMU/ADB infrastructure, Open Firmware properties, KeyLargo GPIO addressing, Book3S low-level assembly helpers (`low_choose_7447a_dfs`, `low_choose_750fx_pll`, `low_sleep_handler`), MPIC, PowerPC cache/MMU helpers, and `ppc_proc_freq`.

## Risks and edge cases

- The file itself notes it needs cleanup; many machine detections and transition styles share one global driver.
- Device-tree frequency data is known to be wrong on some machines, so the code contains model-specific corrections.
- PMU transitions run with interrupts suppressed and manipulate cache/MMU/decrementer state; failures can be catastrophic.
- GPIO address extraction is described as hackish and assumes KeyLargo register layout.
- The driver does not provide module exit/unregister in this file, so it is effectively init/lifetime bound.

## Test signals

Validation requires real supported PowerMac hardware. Signals include correct high/low table values, successful backend detection, repeated high/low transitions, voltage GPIO sequencing before up and after down transitions, DFS/PLL state reads matching `get_speed_proc`, suspend/resume restoring prior speed, and no clock/decrementer/cache corruption after PMU sleep transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pmac32-cpufreq.c -->
