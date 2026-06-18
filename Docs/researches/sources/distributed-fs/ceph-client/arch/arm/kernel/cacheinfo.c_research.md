# sources/distributed-fs/ceph-client/arch/arm/kernel/cacheinfo.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/cacheinfo.c` populates generic cacheinfo from
ARM cache type registers and device tree. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 173 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: cache_line_size_cp15(), cache_line_size(), get_cache_type(),
detect_cache_level(), early_cache_level(), init_cache_level(), and populate_cache_leaves().
Visible dependencies include: `linux/bitfield.h`, `linux/cacheinfo.h`, `linux/of.h`,
`asm/cachetype.h`, `asm/cputype.h`, `asm/system_info.h`.
Important macros/constants include: `CLIDR_CTYPE_SHIFT(level)`, `CLIDR_CTYPE_MASK(level)`,
`CLIDR_CTYPE(clidr, level)`, `MAX_CACHE_LEVEL`, `CTR_FORMAT_MASK`, `CTR_FORMAT_ARMV6`,
`CTR_FORMAT_ARMV7`, `CTR_CWG_MASK`, `CTR_DSIZE_LEN_MASK`, `CTR_ISIZE_LEN_MASK`.
C functions detected in this file include: `Copyright()`, `cache_line_size()`, `get_cache_type()`,
`ci_leaf_init()`, `detect_cache_level()`, `early_cache_level()`, `init_cache_level()`,
`populate_cache_leaves()`.

## Control Flow
CTR/CLIDR reads derive levels/leaves, DT can extend external unified cache levels, and generic
cacheinfo leaves are filled per CPU.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: old CPU formats, missing CLIDR, or wrong DT external cache levels can mislead DMA
alignment and sysfs cache reporting. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
