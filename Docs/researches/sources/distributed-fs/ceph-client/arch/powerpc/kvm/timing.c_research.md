
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.c

## Purpose
Implements optional per-vCPU exit timing statistics for PowerPC KVM when `CONFIG_KVM_EXIT_TIMING` is enabled. It records time spent in host exit handling and guest execution by exit type and exposes a resettable debugfs file.

## Important APIs, Types, And Functions
Public functions are `kvmppc_init_timing_stats()`, `kvmppc_update_timing_stats()`, and `kvmppc_create_vcpu_debugfs_e500()`. Internals include `add_exit_timing()`, `kvmppc_exit_timing_show()`, `kvmppc_exit_timing_write()`, `kvmppc_exit_timing_open()`, the `kvmppc_exit_timing_fops` file operations, and `kvm_exit_names[]`.

## Control Flow
Initialization clears counters, sum, squared sum, min, max, and timestamp fields under `exit_timing_lock`. Each update shifts the last exit timestamp, skips incomplete cycles, adds the duration from prior exit to guest enter to the recorded exit type, and adds guest runtime to the `TIMEINGUEST` bucket. Debugfs `show` converts timebase ticks to microseconds and prints a table; writing a single `c` clears stats.

## State And Persistence
All counters live in `vcpu->arch`: last exit type, count per type, min/max/sum/squared-sum durations, last exit, exit timestamp, and last enter timestamp. The debugfs file persists for the vCPU lifetime.

## Dependencies And Integration Points
Depends on `timing.h`, KVM vCPU arch fields, PowerPC timebase conversion, debugfs, seq_file, and Linux file operations. e500mc exposes it through the backend `create_vcpu_debugfs` hook.

## Risks
Squared duration accumulation can overflow; the code logs wrap detection but continues. Min values initialize to `0xffffffff`, which may be awkward if durations exceed that before first update. Debugfs write validation only accepts one byte, so newline-containing writes may fail. Locking protects stats but debugfs readers still report live, changing counters.

## Test Signals
Runtime signals are presence of `timing` debugfs files, readable tables with named exit buckets, and successful clear via `c`. Stress tests should exercise frequent exits and confirm counters grow without lockdep warnings or crashes.
