<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/Makefile

## Purpose
Builds legacy i386 cpupower debugging helpers: `centrino-decode`, `dump_psb`, `intel_gsic`, and `powernow-k8-decode`. It supports `O=` output, clean, and install into `bindir`.

## Important APIs, Types, And Functions
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Control Flow
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## State And Persistence
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Dependencies And Integration Points
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Risks And Edge Cases
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.

## Test Signals
Control flow is direct one-command compile rules per utility; `intel_gsic` links `-llrmi`. State is produced helper binaries and installed copies. Dependencies are a C compiler, `/dev/mem`/MSR-capable runtime systems for tools, and liblrmi for `intel_gsic`. Risks include architecture-specific assumptions, no dependency tracking, liblrmi absence, and installing low-level debug tools by default if invoked. Test signals are builds with/without liblrmi, clean, staged install, and helper `--help`/error paths where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/Makefile -->
