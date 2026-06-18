<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/uncached.c -->
# sources/distributed-fs/ceph-client/arch/sh/mm/uncached.c

## Purpose
This file tracks the SH cached-to-uncached virtual alias window. It exposes the uncached range used by legacy 29-bit mappings, no-MMU builds, or PMB-managed 32-bit MMU systems.

## Important APIs, Types, and Functions
Global state includes `cached_to_uncached`, `uncached_size`, `uncached_start`, and `uncached_end`; `uncached_start` and `uncached_end` are exported. `virt_addr_uncached()` tests whether a kernel address lies in the uncached range. `uncached_init()` initializes the range from `P2SEG` for 29-bit/no-MMU systems or from `memory_end` otherwise. `uncached_resize()` changes the tracked size.

## Control Flow
Early architecture setup calls `uncached_init()` after memory sizing is available. Platform/PMB code may later call `uncached_resize()` when it needs a different uncached window. Runtime callers use `virt_addr_uncached()` as a pure range check.

## State and Persistence Behavior
The range variables are global kernel state and persist after boot. There is no allocation or persistent storage; changing `uncached_size` recomputes `uncached_end` but does not itself create mappings.

## Dependencies and Integration Points
It depends on SH address-space constants, `memory_end`, `CONFIG_29BIT`, and `CONFIG_MMU`. It integrates with low-level cache-alias handling, DMA/cache maintenance, and code that converts between cached and uncached aliases.

## Risks
The default 512 MiB offset is only valid for legacy 29-bit layout until PMB code updates it. Incorrect start/end values can classify cached memory as uncached or the reverse, causing coherency bugs or invalid accesses. `uncached_resize()` assumes `uncached_start` was already initialized.

## Test Signals
Boot SH 29-bit, 32-bit PMB, and no-MMU configurations; verify exported range symbols, uncached alias conversions, DMA buffers, and `virt_addr_uncached()` around boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/mm/uncached.c -->
