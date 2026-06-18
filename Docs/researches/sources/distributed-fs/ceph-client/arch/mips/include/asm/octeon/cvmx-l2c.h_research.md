# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c.h

## Purpose
`cvmx-l2c.h` declares the public Octeon L2 cache control API. It covers cache geometry, performance counters, core and hardware way partitioning, line and region locking/unlocking, tag inspection, index calculation, and flush operations.

## Important APIs, Types, And Functions
It defines deprecated geometry macros `CVMX_L2_ASSOC`, `CVMX_L2_SET_BITS`, `CVMX_L2_SETS`, index/alias constants, `union cvmx_l2c_tag`, `enum cvmx_l2c_event`, and `enum cvmx_l2c_tad_event`. Public functions include `cvmx_l2c_config_perf`, `cvmx_l2c_read_perf`, partition get/set APIs, `cvmx_l2c_lock_line`, `cvmx_l2c_lock_mem_region`, `cvmx_l2c_unlock_line`, `cvmx_l2c_unlock_mem_region`, `cvmx_l2c_get_tag`, deprecated wrapper `cvmx_get_l2c_tag`, `cvmx_l2c_address_to_index`, `cvmx_l2c_flush`, geometry getters, and `cvmx_l2c_flush_line`.

## Control Flow
The header is declaration-heavy. Implementations configure counter selectors before reads, compute index/alias geometry from model-specific cache shape, use debug registers for tag reads and flushes, and use lock/unlock routines over individual lines or regions. The deprecated wrapper simply calls `cvmx_l2c_get_tag`.

## State And Persistence
Functions mutate hardware cache state: counters, way partitions, locked-line state, tag state, and flush effects. Region locks persist until explicitly unlocked or flushed/reset. No software persistence is declared in the header.

## Dependencies And Integration Points
It includes bitfield helpers and is backed by the L2C/L2D/L2T CSR definitions. It is used by platform initialization, performance tooling, memory management, DMA-sensitive code, and diagnostics.

## Risks
Several functions must only be called by one core at a time because they use L2C debug features. Partition masks can make all ways unavailable if combined badly across cores/hardware. Locking too much memory can severely hurt cache performance. Deprecated macros still execute geometry functions, so they are not compile-time constants.

## Test Signals
Test counter configuration/readback, geometry results on each model, address-to-index calculations, line lock/unlock return values, region lock coverage, full and per-line flush behavior, and multi-core exclusion around debug-register users.
