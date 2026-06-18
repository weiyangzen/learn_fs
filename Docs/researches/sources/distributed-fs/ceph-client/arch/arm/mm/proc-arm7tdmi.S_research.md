# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm7tdmi.S

## Purpose
This file supports ARM7TDMI and several compatible no-MMU SoCs by providing minimal processor hooks and proc-info records.

## Important APIs, Types, and Functions
The `cpu_arm7tdmi_*` init, idle, dcache clean, switch-mm, finish, reset, and setup routines are no-ops or direct returns. `define_processor_functions arm7tdmi` is marked `nommu=1` with `v4t_late_abort` and `legacy_pabort`. The `arm7tdmi_proc_info` macro emits records for ARM7TDMI, Triscend-A7x, Atmel AT91M40xxx, Samsung S3C variants, and NETARM-style IDs, with optional THUMB hwcaps.

## Control Flow
CPU identification selects one proc-info record, but setup and runtime hooks intentionally do almost nothing because there is no MMU/cache maintenance surface in this file.

## State and Persistence Behavior
Only static proc-info and function-table metadata is stored. No CPU memory-management state is programmed.

## Dependencies and Integration Points
It integrates with ARM no-MMU boot, CPU probe, legacy abort handlers, and generic cache function tables (`v4_cache_fns`) where appropriate.

## Risks
The proc-info list spans vendor-specific IDs; mask mistakes can misidentify a CPU. Hwcaps such as THUMB differ by variant. Because hooks are no-op, selecting this path for a CPU with caches or protection hardware needing setup would break coherency or access control.

## Test Signals
Build no-MMU ARM7TDMI board configurations and verify CPU identification, userspace startup, exception handling, and reset. Confirm THUMB-capable variants advertise THUMB only when specified.
