# sources/distributed-fs/ceph-client/kernel/module/procfs.c

## Purpose
Implements `/proc/modules`, the traditional userspace listing of loaded modules.

## Important APIs, Types, And Functions
Defines seq-file callbacks `m_start`, `m_next`, `m_stop`, and `m_show`, plus `modules_open`, `proc_modules_init`, `module_total_size`, and unload-specific `print_unload_info`.

## Control Flow
Opening `/proc/modules` creates a seq file and stores whether module text addresses may be shown based on `kallsyms_show_value`. Iteration holds `module_mutex`, walks `modules`, skips unformed modules, prints name, total size, unload/refcount/dependency fields, state, text address or hidden pointer, and taint flags.

## State And Persistence
No persistent state beyond registering the proc entry at module init. Output reflects current module list state.

## Dependencies And Integration Points
Depends on procfs, seq_file, kallsyms pointer visibility policy, `module_mutex`, module use lists, and optional `CONFIG_MODULE_UNLOAD`.

## Risks And Edge Cases
The output format is userspace ABI-like and must remain compatible with `lsmod` consumers. Pointer hiding must match kallsyms policy. Holding `module_mutex` while formatting avoids list mutation but means slow readers interact with module load/unload.

## Test Signals
Check `/proc/modules` formatting, address hiding for restricted credentials, dependency and permanent-module fields, taint display, and behavior during concurrent module load/unload.
