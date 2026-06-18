# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm740.S

## Purpose
This file provides no-MMU/MPU-oriented low-level support for ARM740T.

## Important APIs, Types, and Functions
The `cpu_arm740_*` hooks are mostly no-op except `proc_fin()` and `reset()`, which disable caches. `__arm740_setup()` programs protection areas for default 4 GB, RAM, and flash, cacheability/write-buffer registers, access permissions, and control bits. `define_processor_functions arm740` is marked `nommu=1`, so no `set_pte_ext` hook is installed. `__arm740_proc_info` matches `0x41807400`.

## Control Flow
The CPU probe invokes setup, which disables unused areas, computes area register values from `CONFIG_DRAM_BASE`, `CONFIG_DRAM_SIZE`, `CONFIG_FLASH_MEM_BASE`, and `CONFIG_FLASH_SIZE`, configures cache/write-buffer permissions, and returns the control value to early boot code.

## State and Persistence Behavior
The file persists MPU/protection area and cache-control state in CP15 registers. No page-table state exists for this CPU path.

## Dependencies and Integration Points
It depends on no-MMU ARM boot, `proc-macros.S` protection-region macros, compile-time DRAM/flash layout options, `legacy_pabort`, and `v4t_late_abort`.

## Risks
DRAM and flash sizes must be powers/encodings suitable for the protection area calculation. Wrong base/size options can leave RAM uncached or inaccessible. Marking it `nommu=1` means page-table callbacks are absent; generic MMU-only code must not reach this path.

## Test Signals
Boot ARM740T no-MMU configurations with realistic DRAM/flash settings. Verify memory access, flash execution, cache behavior, exceptions, and reset. Build-time tests should cover zero flash size and write-through/write-buffer variants.
