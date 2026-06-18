# sources/distributed-fs/ceph-client/kernel/liveupdate/Makefile

## Purpose
`Makefile` maps liveupdate/KHO configuration symbols to object files and groups the LUO implementation into a composite `luo.o`.

## Important APIs, Types, and Functions
`luo-y` contains `luo_core.o`, `luo_file.o`, `luo_flb.o`, and `luo_session.o`. `obj-$(CONFIG_KEXEC_HANDOVER)` builds `kexec_handover.o`; debug and debugfs objects are conditional; `obj-$(CONFIG_LIVEUPDATE)` builds `luo.o`.

## Control Flow
The build system compiles KHO core independently when enabled and links LUO as a multi-object unit only when liveupdate is configured. Optional debug functionality is split so production builds can omit checks and debugfs.

## State and Persistence Behavior
No runtime state. The object grouping determines which initcalls and exported symbols enter the kernel image.

## Dependencies and Integration Points
It is driven by the Kconfig symbols in the same directory and kernel kbuild composite object rules.

## Risks and Test Signals
Missing an object from `luo-y` would silently remove an initcall or exported registration function. Build tests should cover KHO-only, KHO+debug, KHO+debugfs, and full LIVEUPDATE configurations.
