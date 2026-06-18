# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/transmeta.c

## Purpose
Registers Transmeta CPUs and applies Transmeta-specific CPUID/MSR initialization, cache detection, revision reporting, and capability unmasking.

## Important APIs, Types, And Functions
`early_init_transmeta()` reads Transmeta CPUID leaf `0x80860001` capabilities. `init_transmeta()` reports CPU/CMS revisions, product string, cache sizes, unmasks hidden CPUID bits through MSR `0x80860004`, sets `CONSTANT_TSC`, and disables VA randomization under `CONFIG_SYSCTL`. `transmeta_cpu_dev` registers vendor strings.

## Control Flow
Early init caches extended Transmeta flags if available. Full init calls early init, detects cache sizes, prints revision leaves, assembles a 64-byte CPU information string from leaves `0x80860003` to `0x80860006`, temporarily unmasks CPUID capabilities via MSR, then restores the mask.

## State, Persistence, And Dependencies
State changes are CPU capability bits, `cpuinfo_x86.x86_capability`, printk diagnostics, and optionally global `randomize_va_space`. It depends on Transmeta CPUID leaves, MSRs, scheduler clock headers, and generic CPU vendor registration.

## Integration Points
Participates in x86 CPU vendor selection through `cpu_dev_register()`. Capabilities it exposes influence later feature setup and userspace CPUID visibility.

## Risks
MSR writes assume Transmeta behavior and must not run on misidentified CPUs. Disabling ASLR is a broad policy side effect. Product/revision leaves are legacy and may be absent or partially populated.

## Test Signals
Transmeta boot should print expected revisions, preserve restored capability-mask MSR, expose hidden standard CPUID capabilities correctly, and mark TSC constant.
