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
