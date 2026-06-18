# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/Makefile

## Purpose
This Makefile defines the VHE hyp object set and compiler/assembler defines for ARM64 KVM when the host kernel runs with Virtualization Host Extensions.

## Important APIs, Types, and Functions
It sets `asflags-y` and `ccflags-y` to `-D__KVM_VHE_HYPERVISOR__`, suppresses override-initializer warnings for `switch.o`, and builds `timer-sr.o`, `sysreg-sr.o`, `debug-sr.o`, `switch.o`, `tlb.o`, plus shared hyp objects from the parent directory such as VGIC, entry, FPSIMD, hyp entry, exception, and GICv5 support.

## Control Flow
There is no runtime control flow. The build flow marks these objects as VHE hyp code and links a mixture of VHE-specific source files and common hyp code into the KVM hyp object set.

## State and Persistence
The file persists build configuration only. Its `__KVM_VHE_HYPERVISOR__` define changes conditional compilation in included hyp headers and source code.

## Dependencies and Integration Points
It integrates with the ARM64 KVM build system and determines that VHE uses common `../vgic-v3-sr.o`, `../vgic-v2-cpuif-proxy.o`, `../entry.o`, `../fpsimd.o`, `../hyp-entry.o`, `../exception.o`, and `../vgic-v5-sr.o`.

## Risks and Edge Cases
Missing an object here can silently remove a hyp entry point required by VHE world switch. Wrong flags can compile code with nVHE assumptions or expose incompatible symbols. The warning override for `switch.o` is deliberate because the exit-handler array uses range initialization.

## Test Signals
Build tests should cover VHE-enabled ARM64 configurations, nested virtualization options, VGICv5 options, and warning-clean builds with W=1 where practical. Runtime smoke tests should confirm VHE guest entry, timer, sysreg, debug, and TLB paths resolve symbols from this object set.
