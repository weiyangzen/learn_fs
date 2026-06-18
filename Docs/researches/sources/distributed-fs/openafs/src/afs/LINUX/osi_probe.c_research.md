# sources/distributed-fs/openafs/src/afs/LINUX/osi_probe.c

## Purpose
This file locates Linux syscall tables when direct exported symbols or configured addresses are unavailable. It supports OpenAFS syscall and setgroups hooking on older Linux kernels by using weak symbols, module parameters, optional kallsyms lookups, and pattern scans across kernel memory.

## Important APIs, types, and functions
- Module parameters `sys_call_table_addr`, `probe_carefully`, `probe_ignore_syscalls`, and debug-only probe controls.
- Weak symbol references for `sys_call_table`, 32-bit syscall tables, syscall functions, and optional kallsyms functions.
- `tryctl` describes syscall-number/function combinations to match.
- `probectl` describes one target table, including symbol names, offsets, scan ranges, zapped/unique syscall lists, and verification syscall.
- `main_probe`, plus platform variants `ia32_probe`, `sct32_probe`, and `emu_probe`, define architecture-specific probing.
- `check_table` rejects candidate tables containing invalid text pointers.
- `try` scans for direct syscall function pointer combinations.
- `check_harder` validates candidates through unimplemented syscall equivalence, unique syscall distinctness, and verification pointer.
- `try_harder` performs pattern-only scanning and optionally rejects multiple matches.
- `scan_for_syscall_table` runs all `try` patterns and fallback hard scans.
- `do_find_syscall_table` tries weak symbol, kallsyms, module parameter, compiled-in address, primary scan, and alternate scan.
- `check_access` and `check_table_readable` validate page table readability/writability on i386/amd64.
- `osi_find_syscall_table(which)` is the public entry point.

## Control flow and behavior
For each requested probe index, `osi_find_syscall_table` selects a `probectl`, injects any module-parameter address, and calls `do_find_syscall_table`. Discovery first accepts an exported weak symbol, then optional `kallsyms_symbol_to_address`, then explicit module parameter and compiled-in addresses. If none work, it constructs a scan base/length from configured defaults or kallsyms section bounds and calls `scan_for_syscall_table`; an alternate scan range based around `scsi_command_size` is tried afterward.

Scanning first tests exact syscall function pointer combinations such as close/wait4 or close/ioctl where symbols are available. Candidate bases are range-checked against kernel text/data bounds and `check_table` skips unreadable or obviously invalid tables. If exact combinations fail, `try_harder` looks for tables where known unimplemented syscalls share one handler, unique syscalls do not duplicate other entries, and a verification syscall matches its weak function pointer. S390 variants scan even/odd alignments. On i386/amd64, the final result must be writable or hooks are not installed.

If syscall probing is disabled at compile time, `osi_find_syscall_table` returns `0`.

## State and persistence
There is no long-term state beyond module parameters and debug settings. The function returns raw kernel addresses to the syscall hook layer, which may later mutate the table. No disk state exists.

## Dependencies and integration points
This code depends on Linux architecture macros, syscall-number headers, kernel memory layout symbols such as `init_mm`, optional kallsyms, page table APIs on x86, and weak syscall function exports. It feeds `osi_syscall.c`/setgroups hook setup and is referenced in `osi_prototypes.h`.

## Risks
This is highly version- and architecture-sensitive kernel memory probing. Pattern scans can produce false positives or miss tables on changed layouts; `probe_carefully` mitigates duplicate matches but cannot make scanning inherently safe. Writability checks only exist on i386/amd64. Weak references and function descriptors differ by architecture. Hooking syscall tables is incompatible with many modern kernel hardening policies and may be blocked when tables are read-only or hidden. Incorrect `sys_call_table_addr` parameters can point at arbitrary memory.

## Test signals
Build across supported architectures and configurations with probing enabled/disabled, kallsyms available/unavailable, exported/unexported tables, and 32-bit compatibility tables. Runtime tests should verify table discovery method logs, invalid index handling, explicit module parameter addresses, read-only table rejection on x86, duplicate-match behavior with `probe_carefully`, and successful downstream syscall hook installation only when safe.
