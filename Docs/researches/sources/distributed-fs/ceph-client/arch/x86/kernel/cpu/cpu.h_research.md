# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpu.h

## Purpose
`cpu.h` is the private header for `arch/x86/kernel/cpu`. It defines the vendor-driver registration contract, declares cross-file CPU detection/cache/mitigation helpers, provides config-dependent stubs, and exposes a small inline helper for Spectre v2 eIBRS mode tests.

## Important APIs, Types, and Functions
`struct cpu_dev` is the key type. It contains vendor display/CPUID identity strings, hooks for early init, BSP init, full init, pre-CPUID identification, TLB detection, vendor enum, and 32-bit legacy cache/model metadata. `cpu_dev_register()` places a `struct cpu_dev` pointer in the `.x86_cpu_dev.init` section consumed by `common.c`.

Declarations cover TSX/Intel helpers, spectral chicken setup, CPU capability/address/cache discovery, scattered CPUID features, Intel/AMD/Hygon cacheinfo init, null segment behavior checks, AMD/Hygon LLC ID helpers, AMD northbridge L3 cache private data, aperf/mperf frequency, mitigation selection, AP mitigation MSR setup, SRBDS/GDS MSR updates, and `spectre_v2_enabled`.

`spectre_v2_in_eibrs_mode()` returns true for `SPECTRE_V2_EIBRS`, `SPECTRE_V2_EIBRS_RETPOLINE`, and `SPECTRE_V2_EIBRS_LFENCE`.

## Control Flow
Vendor implementation files define static `struct cpu_dev` objects and invoke `cpu_dev_register()`. During early boot, `common.c:init_cpu_devs()` scans `__x86_cpu_dev_start..__x86_cpu_dev_end` and stores descriptors for matching in `get_cpu_vendor()` and vendor hook calls. The declared helpers form the private call graph between CPU identification, cacheinfo, and mitigation files.

## State and Persistence
The header itself has no mutable state. It declares external state such as `spectre_v2_enabled` and uses linker-section placement for persistent init-time vendor descriptors.

## Dependencies and Integration Points
It includes `asm/cpu.h`, `asm/topology.h`, and local `topology.h`. It is included by core CPU files and vendor files. Config stubs allow code to call Intel TSX/CPUID leaf unlock helpers even when Intel CPU support is not built.

## Risks
Changing `struct cpu_dev` affects every vendor file and the linker-section registration contract. Adding hooks or declarations requires careful init-section annotations because many descriptors live in init memory. Misusing `spectre_v2_in_eibrs_mode()` outside its intended enum can hide Spectre v2 user/BHI policy bugs.

## Test Signals
Build coverage across `CONFIG_CPU_SUP_INTEL`, 32-bit, 64-bit, `CONFIG_AMD_NB`, and `CONFIG_SYSFS` is the main signal. Runtime signals are successful vendor matching and absence of unresolved symbols or init-section mismatch warnings.
