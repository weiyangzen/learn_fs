## sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/syscallnr.sh

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/syscallnr.sh` generates a guarded header defining the number of Linux syscalls for one MIPS ABI table subset.

### Important APIs, Types, And Functions
The script consumes positional arguments `in`, `out`, ABI selector list, and prefix. It builds `my_abis` from comma-separated ABI names, creates a C header guard from the output basename, filters the syscall table with `grep -E`, sorts numerically, reads rows as `nr abi name entry compat`, and emits `#define __NR_${prefix}_Linux_syscalls`.

### Control Flow
The script filters rows matching the requested ABIs, sorts by syscall number, iterates through all rows while updating `nxt` to `nr + 1`, and writes a header containing only the guard and final syscall count macro. If there are no rows, `nxt` remains zero.

### State, Persistence, And Dependencies
Output is the generated header file. Dependencies are POSIX shell, `basename`, `sed`, `tr`, `grep`, and `sort`. The stable behavior is tied to syscall table column order and numeric sorting.

### Integration Points
The Makefile invokes this script for `unistd_nr_n32.h`, `unistd_nr_n64.h`, and `unistd_nr_o32.h`. The generated syscall count is used by architecture syscall table declarations and validation.

### Risks
Filtering relies on ABI field regexes and table formatting. Numeric sort with hexadecimal-looking patterns can be fragile if table numbers are not accepted by the shell arithmetic used in `nxt=$((nr+1))`. Header guard generation must remain collision-resistant enough for generated filenames.

### Test Signals
Run the script on each MIPS syscall table with ABI filters, verify final count equals last syscall number plus one, test comma-separated ABI lists, and check generated guard and macro names for n32/n64/o32.
