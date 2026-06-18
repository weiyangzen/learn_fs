# sources/distributed-fs/ceph-client/arch/x86/mm/pat/Makefile

## Purpose
This Makefile selects the x86 PAT/page-attribute implementation objects for the `arch/x86/mm/pat` subdirectory.

## Important APIs, Types, and Functions
- `obj-y := set_memory.o memtype.o` always builds the core set-memory and memtype logic.
- `obj-$(CONFIG_X86_PAT) += memtype_interval.o` adds the interval-tree reservation backend when PAT is enabled.

## Control Flow and State
There is no runtime control flow. Build-time Kconfig decides whether the interval tracking implementation is compiled. When PAT is disabled, inline stubs from `memtype.h` replace the interval backend.

## Dependencies and Integration Points
The objects are consumed by x86 page-attribute changes, ioremap, pfnmap tracking, and cache-mode conversion. `memtype.c` is always present because it also handles disabled-PAT and MTRR-compatible behavior.

## Risks
Omitting `memtype_interval.o` when `CONFIG_X86_PAT=y` would leave non-stub symbols unresolved. Building it when PAT is disabled would be unnecessary and could conflict with stub expectations.

## Test Signals
Builds should pass with `CONFIG_X86_PAT=y` and `CONFIG_X86_PAT=n`. Runtime PAT debugfs availability depends on the enabled configuration.
