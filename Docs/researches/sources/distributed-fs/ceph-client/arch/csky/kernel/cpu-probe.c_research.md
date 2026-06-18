# sources/distributed-fs/ceph-client/arch/csky/kernel/cpu-probe.c

## Purpose

detects C-SKY CPU identity and feature flags from processor registers during early CPU setup

## Important APIs, Types, and Functions

Source read size: 79 lines, 1709 bytes. Includes: `linux/of.h`, `linux/init.h`, `linux/seq_file.h`,
`linux/memblock.h`, `abi/reg_ops.h`. Functions: `percpu_print`, `c_show`, `c_stop`. Local structs:
`seq_file`.

## Control Flow and Behavior

the probe reads implementation/configuration registers, derives cache/MMU/FPU/DSP/ISA capabilities,
and publishes the result for feature-dependent arch code

## State and Persistence

persistent state is the probed CPU capability data used after boot

## Dependencies and Integration Points

depends on ABI register accessors, Kconfig CPU feature symbols, and early setup ordering

## Risks and Test Signals

bad detection enables unsupported instructions or cache/MMU paths; boot logs, feature-dependent
selftests, and CPU hotplug paths provide signals
