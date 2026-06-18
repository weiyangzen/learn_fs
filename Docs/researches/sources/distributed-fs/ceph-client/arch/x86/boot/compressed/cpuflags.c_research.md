## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/cpuflags.c

### Purpose
`compressed/cpuflags.c` exposes early CPU feature detection to compressed boot code by reusing the setup CPU flag implementation.

### Important APIs, Types, And Functions
It includes `../cpuflags.c` and exports `has_cpuflag(int flag)`.

### Control Flow
`has_cpuflag()` calls `get_cpuflags()` to populate the shared early `cpu.flags` bitmap and then returns `test_bit(flag, cpu.flags)`.

### State, Persistence, And Dependencies
State is the included CPU flag cache from setup code. Dependencies include early CPUID support, boot bitops, and the compressed build environment.

### Integration Points
Compressed boot users such as KASLR entropy, CPU capability checks, and early platform handling can test feature bits without entering the full kernel CPU initialization path.

### Risks
Feature detection this early must avoid facilities not set up yet, especially under encrypted guests where CPUID may trap. SEV/TDX code arranges exception or paravirtual handling before sensitive CPUID users.

### Test Signals
Boot on CPUs and guests with different CPUID leaves, SEV-ES/SNP/TDX guests, and configurations that call `has_cpuflag()` before and after decompressor setup.
