<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/min_addr.c -->
# sources/distributed-fs/ceph-client/security/min_addr.c

## Purpose

`min_addr.c` owns the global low-address mmap protection floor exposed through `vm.mmap_min_addr`. It combines a DAC-controlled sysctl value with the configured LSM minimum to decide the effective `mmap_min_addr`.

## Important APIs, Types, and Functions

- `mmap_min_addr` is the effective low virtual-address floor used by mmap checks.
- `dac_mmap_min_addr` stores the sysctl-controlled DAC value, initialized from `CONFIG_DEFAULT_MMAP_MIN_ADDR`.
- `update_mmap_min_addr()` sets `mmap_min_addr` to `max(dac_mmap_min_addr, CONFIG_LSM_MMAP_MIN_ADDR)` when an LSM floor exists, otherwise to the DAC value.
- `mmap_min_addr_handler()` enforces `CAP_SYS_RAWIO` for writes, delegates parsing to `proc_doulongvec_minmax()`, and refreshes the effective floor.
- `mmap_min_addr_init()` registers the sysctl and initializes the effective value.

## Control Flow

At pure initcall time, the file registers `/proc/sys/vm/mmap_min_addr` and computes the initial effective floor. Sysctl reads and writes go through `mmap_min_addr_handler()`. Writes without `CAP_SYS_RAWIO` fail before parsing; reads and authorized writes use the generic unsigned-long vector handler. After the generic handler returns, the effective value is recomputed.

## State and Persistence Behavior

`dac_mmap_min_addr` is mutable at runtime via sysctl, but `mmap_min_addr` never drops below `CONFIG_LSM_MMAP_MIN_ADDR` when that option is set. Changes persist only until reboot unless userspace reapplies sysctl settings.

## Dependencies and Integration Points

The file depends on initcall, mm, security, sysctl, capability, and min/max helpers. The effective global is consumed by memory-management security checks that reject low-address mappings or round non-fixed hints.

## Risks and Edge Cases

Calling `update_mmap_min_addr()` even after a failed generic parse preserves consistency but may recompute from the previous value. Systems expecting to lower the floor below the LSM default cannot do so. Capability checks use `CAP_SYS_RAWIO`, reflecting the security sensitivity of mapping low addresses.

## Test Signals

Tests should verify boot initialization from config, sysctl readback, unauthorized write `-EPERM`, authorized write updates, effective floor clamping by `CONFIG_LSM_MMAP_MIN_ADDR`, and mmap behavior for addresses below and above the resulting floor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/min_addr.c -->
