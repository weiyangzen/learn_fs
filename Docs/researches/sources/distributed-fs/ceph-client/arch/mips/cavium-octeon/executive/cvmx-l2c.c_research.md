# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-l2c.c

## Purpose
Implements Octeon L2 cache partitioning, performance counters, line locking/unlocking, tag inspection, flushing, and geometry queries.

## Important APIs, Types, And Functions
Major APIs include `cvmx_l2c_set_core_way_partition()`, `cvmx_l2c_set_hw_way_partition()`, `cvmx_l2c_config_perf()`, `cvmx_l2c_read_perf()`, `cvmx_l2c_lock_line()`, `cvmx_l2c_flush()`, `cvmx_l2c_unlock_line()`, `cvmx_l2c_get_tag()`, `cvmx_l2c_address_to_index()`, `cvmx_l2c_get_num_sets()`, `cvmx_l2c_get_num_assoc()`, and `cvmx_l2c_flush_line()`.

## Control Flow
Partition APIs validate masks and write CN63XX `WPAR` or older `SPAR` fields. Perf APIs use old global counters or newer TAD counters. Locking uses CN63XX cache instructions or older debug-core lock registers plus fault-in loads. Tag reads enter debug mode with interrupts disabled and convert model-specific tag formats.

## State, Persistence, And Dependencies
State includes partition registers, perf counter configuration, cache lock bits, and cache contents. `cvmx_l2c_spinlock` serializes debug operations only within this kernel/application.

## Integration Points
Low-level diagnostics and drivers use this module for cache control. Packet helper initialization changes L2 arbitration priority nearby.

## Risks
Debug mode makes data loads return tag data; interrupt disabling and serialization are critical. Multi-OS coordination is not handled. Model/fuse-specific geometry is fragile.

## Test Signals
Check geometry by model/fuse, partition validation, perf counter increments, lock-bit verification, no stuck debug mode, and full flush behavior.
