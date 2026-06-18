# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/tsc.c

Purpose: provides x86 TSC reading and frequency discovery for perf utilities.

Important APIs/types/functions: `rdtsc()` emits the `rdtsc` instruction and returns a 64-bit cycle value. `arch_get_tsc_freq()` is the exported frequency helper. `cpuinfo_tsc_freq()` parses `/proc/cpuinfo` for `cpu MHz`.

Control flow: `arch_get_tsc_freq()` first uses CPUID leaf 0x15 denominator/numerator/crystal frequency to compute TSC frequency. If unavailable or incomplete, it falls back to `/proc/cpuinfo`, parsing MHz into kHz/Hz scale. It returns zero on failure.

State and persistence: no cached state and no persistent writes. Reads CPUID and `/proc/cpuinfo` at call time.

Dependencies and integration: depends on x86 inline asm, `cpuid()` helper, libc stdio/string parsing, and perf's `u64` type. Used by AUX trace timestamp/reference paths and other perf timing code.

Risks: CPUID 0x15 is not universally populated. `/proc/cpuinfo` parsing is locale/string-format sensitive and uses integer/fraction handling limited by the expected `cpu MHz` line. Virtualized systems may expose unstable or synthetic values.

Test signals: unit or manual checks on systems with CPUID 0x15, systems requiring cpuinfo fallback, and comparison against kernel-reported TSC conversion in AUX trace metadata.
