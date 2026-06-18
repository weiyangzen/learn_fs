# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_policer.c

## Purpose
This file implements Spectrum policer allocation, validation, hardware programming, counter query, and devlink resource registration. The implemented family is global single-rate byte policers, used by TC police actions and ACL actions.

## Important APIs, Types, And Functions
Public APIs include `mlxsw_sp_policers_init()`, `mlxsw_sp_policers_fini()`, `mlxsw_sp_policer_add()`, `mlxsw_sp_policer_del()`, `mlxsw_sp_policer_drops_counter_get()`, and `mlxsw_sp_policer_resources_register()`. Core structures are `mlxsw_sp_policer_core`, `mlxsw_sp_policer_family`, and `mlxsw_sp_policer`. Family ops allocate/free indexes with IDR, validate params, initialize QPCR hardware, and register occupancy callbacks. Generation ops set allowable burst-size bit ranges for Spectrum-1 versus Spectrum-2.

## Control Flow
Init allocates the core, runs generation init, and registers each policer family. The single-rate family skips CPU-reserved policer indexes by using `MAX_CPU_POLICERS` as start and `MAX_GLOBAL_POLICERS` as end, registers devlink occupancy, and initializes the IDR. Add validates byte policing, power-of-two burst, burst/rate limits, allocates a policer object/index, writes QPCR with CIR and burst size, clears the counter, and returns the index. Delete removes the index and frees the object. Counter query reads QPCR violate count.

## State And Persistence
State is runtime: per-family IDR, mutex, start/end index, atomic policer count, params, and index. Hardware QPCR state persists until reprogrammed/reset. Devlink resource occupancy is derived from the atomic count.

## Dependencies And Integration Points
It depends on devlink resource APIs, mlxsw core resource discovery, QPCR register definitions, IDR, mutexes, and TC/ACL policer users. `spectrum_flower.c` validates TC police actions before requesting ACL policer action programming.

## Risks And Edge Cases
Only bandwidth policers are supported; packet-rate, average-rate, peak-rate, and overhead modes are rejected elsewhere or here. Burst conversion maps bytes to 512-bit units and depends on power-of-two inputs. Resource registration has two devlink calls without local unwind if the second fails. The checked-out source contains a duplicated family lookup line in `mlxsw_sp_policer_add()`, a review/compile-risk signal.

## Test Signals
Test valid/invalid TC police offloads, burst/rate lower and upper limits, policer exhaustion, QPCR counter reads, add failure rollback, devlink resource occupancy, generation-specific burst limits, and unload warnings for leaked policers.
