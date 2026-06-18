# sources/distributed-fs/ceph-client/scripts/syscallhdr.sh

Purpose: `syscallhdr.sh` generates a UAPI syscall number header from an architecture syscall table.

Important APIs, types, and functions: options include `--abis`, `--emit-nr`, `--offset`, and `--prefix`. It computes a header guard from the output basename, filters table rows with `grep -E`, emits `#define __NR_${prefix}${name} ${nr}`, optionally applies an offset expression, and optionally emits `__NR_${prefix}syscalls` under `__KERNEL__`.

Control flow: after option parsing and two-argument validation, a pipeline writes the entire header atomically through shell redirection to the output path. `max` tracks the last processed number for syscall count.

State and persistence: writes the output header file.

Dependencies and integration points: used by architecture builds to derive generated syscall headers from `.tbl` files. Depends on table rows formatted as documented in the file header.

Risks: ABI regex is built directly from the option string and should be supplied by trusted build logic. Hex syscall numbers pass the grep but shell arithmetic for `emit_nr` may not handle all forms consistently. Input ordering matters for `max`.

Test signals: generate headers for all ABIs, selected ABI lists, offsets, prefixes, and `--emit-nr`; compare against expected generated headers.
