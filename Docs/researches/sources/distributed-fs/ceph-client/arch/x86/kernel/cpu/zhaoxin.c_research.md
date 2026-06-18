# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/zhaoxin.c

## Purpose
Registers Zhaoxin CPUs and applies vendor-specific capability setup for TSC behavior, cache/perf features, crypto/RNG units, and IA32 feature control.

## Important APIs, Types, And Functions
`early_init_zhaoxin()` sets constant/nonstop TSC capabilities. `init_zhaoxin_cap()` enables ACE crypto and RNG units via `MSR_ZHAOXIN_FCR57` when CPUID reports present-but-disabled units, stores extended capability flags, and sets `REP_GOOD`. `init_zhaoxin()` initializes cache info, architectural perfmon, LFENCE/RDTSC on 64-bit, and feature control.

## Control Flow
Early init handles TSC caps. Full init repeats early init, initializes Intel-like cache info, checks CPUID leaf 10 for usable perf counters, then enables Zhaoxin extended units and feature caps for family 6+. Vendor registration matches CPUID identifier `"  Shanghai  "`.

## State, Persistence, And Dependencies
State is CPU capability bits, CPUID capability arrays, and MSR-enabled ACE/RNG units. It depends on CPUID extended leaf `0xC0000001`, Zhaoxin MSR `0x1257`, Intel-style cache/perf helpers, and feature-control initialization.

## Integration Points
Participates in x86 CPU vendor init and affects crypto/RNG feature visibility, perf events, TSC clocksource trust, and virtualization feature control.

## Risks
MSR bit definitions are vendor-specific. Enabling units based on CPUID must match hardware behavior. Treating Zhaoxin like Intel for cache/perf helpers can miss vendor deviations.

## Test Signals
Boot should enable ACE/RNG only when present and disabled, set constant/nonstop TSC where advertised, expose arch perfmon when leaf 10 is valid, and avoid MSR faults.
