# sources/distributed-fs/ceph-client/net/6lowpan/Makefile

## Purpose
`net/6lowpan/Makefile` maps the 6LoWPAN Kconfig symbols to kernel objects and determines which sources become the core `6lowpan` module versus separate compression modules.

## Important build rules
`obj-$(CONFIG_6LOWPAN) += 6lowpan.o` builds the core aggregate. `6lowpan-y` includes `core.o`, `iphc.o`, `nhc.o`, and `ndisc.o`; `debugfs.o` is conditionally added for `CONFIG_6LOWPAN_DEBUGFS`. RFC6282 NHC modules and RFC7400 GHC modules are emitted as separate objects controlled by their individual config symbols.

## Control flow
There is no runtime flow. Build-time object composition determines which module init/exit functions and compression descriptors are present.

## State and persistence
No runtime state is held here. The persistent result is the kernel build artifact layout.

## Dependencies and integration points
The Makefile ties Kconfig symbols to the core module and helper modules consumed by `core.c` autoload requests and `iphc.c` calls into the NHC registry.

## Risks and invariants
Core IPHC code assumes `nhc.o` is part of `6lowpan.o`; missing that object would break next-header compression dispatch. Optional modules must keep names aligned with `request_module_nowait()` and `module_lowpan_nhc()` registrations.

## Test signals
Check generated objects/modules for representative configs and verify `modprobe 6lowpan` can autoload common `nhc_*` modules when available.
