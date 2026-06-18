# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umc.c

## Purpose
Registers UMC 386/486-era CPUs with vendor identification and legacy model names.

## Important APIs, Types, And Functions
`umc_cpu_dev` declares vendor string `UMC`, CPUID identifier `UMC UMC UMC`, family 4 model names `U5D` and `U5S`, and vendor enum `X86_VENDOR_UMC`. `cpu_dev_register()` exposes it to generic CPU identification.

## Control Flow
There is no active init hook. Generic CPU detection matches the vendor string and uses the legacy model table for names.

## State, Persistence, And Dependencies
State is limited to static registration data. It depends on x86 CPU vendor infrastructure and legacy model-name lookup.

## Integration Points
Participates in CPU identification paths that populate `/proc/cpuinfo` and `cpuinfo_x86` vendor/model metadata.

## Risks
The file intentionally performs no quirks; if a UMC-compatible CPU needs feature masking or timing fixes, this registration will not supply them.

## Test Signals
Booting a matching UMC CPU or emulator should identify vendor/model without running any special init and without feature side effects.
