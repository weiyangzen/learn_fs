# sources/distributed-fs/ceph-client/scripts/syscallnr.sh

Purpose: `syscallnr.sh` generates a small header containing only the number of syscalls for selected ABIs.

Important APIs, types, and functions: options are `--abis` and `--prefix`. It filters matching rows, sorts them numerically, tracks the last syscall number, and emits `#define __NR_${prefix}syscalls $((max + 1))` inside a generated include guard.

Control flow: the script validates two positional arguments, computes the guard, streams filtered/sorted rows through a while loop, and writes the header to the output file.

State and persistence: writes one generated header.

Dependencies and integration points: used by architecture syscall generation where the full number header is not wanted or is split. Depends on sort, grep, sed, and shell arithmetic.

Risks: sorting with `sort -n` and arithmetic assumes numeric syscall identifiers; hexadecimal rows may not behave as expected despite the grep accepting them. ABI regex is caller-controlled.

Test signals: syscall tables with gaps, ABI filters, prefixes, and highest-number edge cases.
