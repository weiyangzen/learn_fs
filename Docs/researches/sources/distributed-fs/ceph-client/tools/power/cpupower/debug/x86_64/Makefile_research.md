<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/x86_64/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/x86_64/Makefile

## Purpose
Builds x86_64 variants of selected debug helpers by reusing the i386 source files for `centrino-decode` and `powernow-k8-decode`. It supports `O=`, clean, and install.

## Important APIs, Types, And Functions
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Control Flow
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## State And Persistence
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Dependencies And Integration Points
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Risks And Edge Cases
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.

## Test Signals
Control flow is direct compile rules pointing at `../i386/*.c`; no `dump_psb` or `intel_gsic` targets are built for x86_64. State is produced helper binaries and installed copies. Dependencies are a C compiler, x86 MSR runtime support, and inherited source compatibility. Risks include duplicated build logic from i386, no dependency tracking, and legacy CPU assumptions on modern 64-bit systems. Test signals are build, clean, staged install, and helper behavior against missing/present `/dev/cpu/N/msr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/x86_64/Makefile -->
