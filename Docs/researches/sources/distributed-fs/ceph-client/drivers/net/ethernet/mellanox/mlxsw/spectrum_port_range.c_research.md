# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_port_range.c

## Purpose
This file manages ACL L4 port-range registers. TC flower range matches consume a small hardware register indexed by a bit in the ACL `l4_port_range` key; this file deduplicates identical ranges, reference-counts them, programs PPRR registers, and exposes devlink occupancy.

## Important APIs, Types, And Functions
Public APIs are `mlxsw_sp_port_range_init()`, `mlxsw_sp_port_range_fini()`, `mlxsw_sp_port_range_reg_get()`, and `mlxsw_sp_port_range_reg_put()`. `struct mlxsw_sp_port_range_reg` stores min/max/source flag/refcount/index. `struct mlxsw_sp_port_range_core` stores an xarray, ID limits, and atomic count. Internal helpers configure PPRR, create/destroy/find range registers, and report occupancy.

## Control Flow
Init validates `ACL_MAX_L4_PORT_RANGE`, warns if the resource exceeds the 16 ACL key bits, initializes an allocating xarray, and registers devlink occupancy. Get searches for an identical range and increments its refcount, or allocates a new xarray index, writes PPRR for IPv4/IPv6 and TCP/UDP source or destination matching, increments occupancy, and returns the index. Put loads by index, decrements refcount, and destroys the register when it reaches zero.

## State And Persistence
Runtime state is the xarray of active range registers, refcounts, and occupancy count. Hardware state is PPRR content by register index. No persistent storage exists.

## Dependencies And Integration Points
It integrates with `spectrum_flower.c` ports-range parsing and devlink resource accounting. It uses xarray allocation, Linux refcounting, and PPRR register packers.

## Risks And Edge Cases
Get/find is a linear scan over active xarray entries; the hardware resource is small, but concurrency assumptions rely on higher-level serialization because there is no local lock around xarray operations. A failed PPRR write erases the allocated xarray slot. `put()` warns and returns if the index is unknown, which helps catch ACL cleanup imbalance. Register bits are limited to a `u16` ACL key element.

## Test Signals
Test duplicate range sharing, source and destination ranges, exhaustion extack, PPRR write failure rollback, refcounted destroy on final put, devlink occupancy, flower rule add/delete cleanup, and WARN-free fini.
