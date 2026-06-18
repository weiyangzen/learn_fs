# sources/distributed-fs/ceph-client/kernel/ksysfs.c

## Purpose
`ksysfs.c` creates `/sys/kernel` and populates generic kernel-level sysfs attributes not owned by another subsystem.

## Important APIs, Types, And Functions
The file exports `struct kobject *kernel_kobj`. `ksysfs_init()` creates the kobject, installs `kernel_attr_group`, and optionally publishes a binary `notes` file from linker symbols. Attributes include `uevent_seqnum`, `cpu_byteorder`, `address_bits`, optional `uevent_helper`, `profiling`, `vmcoreinfo`, `fscaps`, `rcu_expedited`, and `rcu_normal`.

## Control Flow
Each show/store function formats or parses a simple value using sysfs helpers. `profiling_store()` serializes initialization so profiling buffers and proc entries are only allocated once. `ksysfs_init()` unwinds sysfs group/kobject creation on failure and logs an initialization error.

## State And Persistence
`kernel_kobj` persists for the kernel lifetime and anchors many other features, including kexec and kheaders. Mutable attributes write global state such as `uevent_helper`, `prof_on`, `rcu_expedited`, and `rcu_normal`; most other attributes report read-only build/runtime facts.

## Dependencies And Integration Points
The file integrates with kobject/sysfs, uevent, profiling, vmcoreinfo, file capabilities, RCU policy, linker notes, and architecture byte order definitions. Other files depend on `kernel_kobj` for their own sysfs files.

## Risks And Edge Cases
Store handlers must validate input length and parse errors. `uevent_helper` mutability is security-sensitive when enabled. `profiling_store()` must not reinitialize after profiling is active. Notes size derives from linker symbols and must only create a bin file when positive.

## Test Signals
Signals include `/sys/kernel` creation, expected attributes under config combinations, read/write behavior for RCU and profiling controls, notes bin-file size/content, and dependent sysfs users such as `/sys/kernel/kexec` and `/sys/kernel/kheaders.tar.xz`.
