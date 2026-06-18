# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_types.h

## Purpose
Defines small x86-specific KVM type and symbol-export policy constants shared by common KVM code and x86 vendor modules.

## Important APIs, Types, And Functions
`KVM_SUB_MODULES` expands to `kvm-amd`, `kvm-intel`, or both when the respective vendor backends are modules. If neither vendor backend is modular, `EXPORT_SYMBOL_FOR_KVM(symbol)` is suppressed because `kvm.ko` only exists when at least one vendor module is enabled. `KVM_ARCH_NR_OBJS_PER_MEMORY_CACHE` sets the x86 per-cache object target to 40.

## Control Flow
Kbuild and export macro expansion are the only flow. The preprocessor selects module names from `CONFIG_KVM_AMD` and `CONFIG_KVM_INTEL` module states.

## State And Persistence
No runtime state. The constants affect build output and memory-cache sizing in KVM runtime allocations.

## Dependencies And Integration Points
Integrates with Linux KVM symbol exporting, vendor module packaging, and architecture memory-cache helpers included through generic KVM types.

## Risks And Edge Cases
Incorrect module detection can hide symbols required by modular backends or export symbols unnecessarily. Cache sizing changes can affect allocation pressure and latency in MMU hot paths.

## Test Signals
Build matrix coverage for builtin-only, AMD-module-only, Intel-module-only, and both-module KVM configurations is the main signal. Link failures in vendor modules expose export mistakes.
