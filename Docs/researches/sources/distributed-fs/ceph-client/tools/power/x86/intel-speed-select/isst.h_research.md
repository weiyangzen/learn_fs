# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst.h

## Purpose
`isst.h` is the shared contract for the Intel Speed Select user-space tool. It collects system includes, local bit macros, mailbox command constants, topology limits, core data structures, the backend ops interface, and cross-file function declarations used by the CLI, core abstraction, backends, display code, daemon, and HFI integration.

## Important APIs, Types, And Functions
The key identity type is `struct isst_id`, which represents a logical CPU plus package, die, and punit power-domain coordinates. Feature data types include `struct isst_clos_config`, `struct isst_pbf_info`, `struct isst_fact_bucket_info`, `struct isst_fact_info`, `struct isst_pkg_ctdp_level_info`, and `struct isst_pkg_ctdp`. `struct isst_platform_ops` is the backend vtable and includes callbacks for frequency units, TRL names, punit validity, PM config, perf-profile levels, TDP details, power data, core masks, TRL ratios/buckets, PBF/FACT get/set, uncore adjustment, and CLOS/core-power operations.

The header declares common APIs from `isst-config.c`, wrapper APIs from `isst-core.c`, rendering APIs from `isst-display.c`, daemon/HFI APIs, backend factory functions, and cgroup helpers.

## Control Flow
At runtime, `isst-config.c` initializes platform state and calls `isst_set_platform_ops()`. `isst-core.c` then uses `struct isst_platform_ops` declarations from this header to delegate to either `mbox_get_platform_ops()` or `tpmi_get_platform_ops()`. Data flows from backend-specific ioctls into header-defined structures, then to display functions and command-specific policy code.

## State And Persistence Behavior
The header itself stores no state, but it defines the structure fields that carry mutable command state. Several structures contain `cpu_set_t *` members and `core_cpumask_size`; ownership is shared by convention, with allocation through `alloc_cpu_set()` and cleanup through `free_cpu_set()` or `isst_get_process_ctdp_complete()`.

## Dependencies And Integration Points
The file depends on Linux and GNU interfaces: `sched.h` CPU sets, `sys/ioctl.h`, `cpuid.h`, `dirent.h`, and `linux/isst_if.h`. Its constants mirror mailbox command encodings and resource limits used by both mailbox and TPMI code. It is the single include that lets separate implementation files share platform predicates, topology helpers, display functions, backend factories, and daemon entry points.

## Risks And Edge Cases
The header mixes public declarations, backend ABI constants, and utility macros, so any change has broad rebuild and behavioral impact. `BIT(x)` uses `1 << x`, which is not safe for large bit positions unless callers use `BIT_ULL()`. Fixed limits such as `MAX_PACKAGE_COUNT`, `MAX_DIE_PER_PACKAGE`, `MAX_PUNIT_PER_DIE`, `ISST_MAX_TDP_LEVELS`, and bucket counts must match hardware/kernel ABI expectations. Several function declarations use raw pointers and ownership conventions without type-level enforcement.

## Test Signals
Compile-time tests should cover all translation units with warnings enabled. ABI-sensitive tests should validate that structure fields are populated consistently by both backends and displayed correctly. Static analysis should watch for mismatched `alloc_cpu_set()`/`free_cpu_set()` use, invalid bit macro widths, and array indexing by package/die/punit values.
