# sources/distributed-fs/ceph-client/arch/xtensa/kernel/setup.c

Purpose: Performs early Xtensa architecture setup: boot parameter parsing, device-tree early scan, MMU/KASAN/platform initialization, memory reservation, topology registration, reset/power paths, and `/proc/cpuinfo` reporting.

Important APIs, types, and functions: `init_arch()`, `setup_arch()`, `early_init_devtree()`, `parse_bootparam()`, tag parsers for memory/initrd/FDT/cmdline, `cpu_reset()`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, and `cpuinfo_op`. It exports `xtensa_kio_paddr` when OF-driven KIO remapping is needed.

Control flow: `init_arch()` sets trap support for KASAN/load-store configurations, initializes the MMU and early KASAN shadow, parses boot tags, scans the flattened device tree, applies configured command line fallback, and calls `platform_init()`. `setup_arch()` publishes the command line, lets the platform adjust it, reserves initrd/kernel/vector/XIP/secondary reset memory, parses early params, initializes boot memory/KASAN/DT/SMP/paging/zones, and selects console behavior. `cpu_reset()` disables interrupts, flushes/rebuilds TLB state, resets debug/timer/loop registers, then jumps to `XCHAL_RESET_VECTOR_VADDR`.

State and persistence: Mutates global boot command buffers, memblock reservations, CPU registration state, DT-derived KIO physical base, initrd bounds, and per-CPU `struct cpu` descriptors. `/proc/cpuinfo` state is derived from hardware config macros, `ccount_freq`, and `loops_per_jiffy`.

Dependencies and integration: Depends on `asm/bootparam.h`, `asm/platform.h`, `asm/sysmem.h`, MMU/KASAN/trap helpers, OF flat-tree helpers, memblock, SMP setup, and linker-provided vector section symbols. Platform hooks (`platform_init`, `platform_setup`) are the key board/simulator integration points.

Risks: Boot tag size walking and command-line copying must remain bounded; KIO remapping assumes a simple-bus `ranges` layout; `cpu_reset()` contains delicate MMUv2/MMUv3 assembly and temporary mappings where wrong addresses can cause multihit or unrecoverable reset failures. Memory reservations must match linker sections or vectors/XIP text may be reused.

Test signals: Boot on OF and bootparam paths, verify memblock map/initrd reservation, `/proc/cpuinfo`, restart/poweroff behavior, SMP possible CPU detection, vector reservation, KASAN boot, and mismatched hardware config ID logging.
