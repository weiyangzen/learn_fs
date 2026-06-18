<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/Makefile

## Purpose
This Makefile includes CE4100 platform setup code when the Intel CE platform is configured.

## Important APIs, types, and functions
It contains `obj-$(CONFIG_X86_INTEL_CE) += ce4100.o`.

## Control flow
No runtime control flow. Kbuild includes `ce4100.o` only for `CONFIG_X86_INTEL_CE`.

## State and persistence behavior
No runtime state. The build output determines whether CE4100 early setup hooks are available.

## Dependencies and integration points
It is included by the parent x86 platform Makefile and depends on the x86 Intel CE Kconfig symbol.

## Risks and edge cases
Wrong gating would either omit CE4100 platform boot support or compile CE4100-only hooks into unrelated builds.

## Test signals
Build with `CONFIG_X86_INTEL_CE=y` and confirm `ce4100.o` is linked; build without it and confirm omission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ce4100/Makefile -->
