# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cpu.c

Purpose: detects BCM63xx CPU identity, revision, clock frequency, memory size, and CPU-specific register layout used by the rest of the platform.

Important APIs and functions: `bcm63xx_get_cpu_rev()`, `bcm63xx_get_cpu_freq()`, and `bcm63xx_get_memory_size()` expose detected state. `detect_cpu_clock()` decodes PLL and strap registers for supported SoCs. `detect_memory_size()` reads memory controller registers. `bcm63xx_cpu_init()` matches PRID/chip ID, sets `bcm63xx_cpu_id`, revision, frequency, memory size, and exported register/IRQ tables.

Control flow: early platform code calls `bcm63xx_cpu_init()` before device registration. The function handles supported CPU families with compile-time conditionals, then logs or panics for unsupported combinations.

State and persistence: stores CPU ID, revision, frequency, memory size, and register table pointers in globals for this boot. No persistent writes.

Dependencies and integration points: used by nearly every BCM63xx file through `BCMCPU_IS_*` predicates and base/IRQ lookup helpers. Depends on MIPS CP0 PRID and BCM63xx memory-mapped registers.

Risks and test signals: incorrect detection cascades into wrong MMIO bases, IRQs, clocks, and resets. Test via boot logs, `/proc/cpuinfo`, memory size, platform-device resources, and peripheral operation on each enabled SoC.
