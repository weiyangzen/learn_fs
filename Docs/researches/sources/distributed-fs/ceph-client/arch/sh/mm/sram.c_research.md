# sources/distributed-fs/ceph-client/arch/sh/mm/sram.c

Purpose: initializes the architecture SRAM allocation pool when available.

Important function: `sram_pool_init`.

Control flow: called during init, validates configured SRAM pool metadata, and registers the pool with generic/arch SRAM support.

State and persistence: establishes allocator state for on-chip SRAM regions.

Dependencies and integration: depends on `asm/sram.h` and init/error handling; used by platform code needing fast SRAM allocations.

Risks: wrong SRAM bounds can overlap normal memory or device registers.

Test signals: boot with `CONFIG_HAVE_SRAM_POOL`, SRAM allocation/free tests, and platform driver SRAM users.
