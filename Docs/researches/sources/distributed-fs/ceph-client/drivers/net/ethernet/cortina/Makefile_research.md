# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/Makefile

## Purpose
`cortina/Makefile` maps the Gemini Ethernet Kconfig symbol to its object file.

## Important APIs, types, and functions
- `obj-$(CONFIG_GEMINI_ETHERNET) += gemini.o` builds the Gemini driver when selected.

## Control flow and state
Kbuild expands the object list based on `CONFIG_GEMINI_ETHERNET`. No runtime state exists.

## Dependencies and integration points
It integrates the Cortina vendor directory with the kernel build system and the `GEMINI_ETHERNET` Kconfig option.

## Risks and test signals
The main risk is object name drift if the source file is renamed. Test with `CONFIG_GEMINI_ETHERNET=y` and `m` builds.
