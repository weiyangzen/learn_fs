## sources/distributed-fs/ceph-client/arch/arm/tools/syscallnr.sh

### Purpose
Generates an ARM `unistd-nr.h`-style header containing an aligned `__NR_syscalls` value derived from the highest syscall number.

### Important APIs, Types, And Functions
Inputs are the syscall table path and output header path. The script computes a file guard from the output basename and emits `#define __NR_syscalls`.

### Control Flow
It filters numeric syscall rows, sorts them, takes the highest entry, increments the number, grows the alignment from 1 by factors of 4 while crossing 256-aligned ranges, rounds up, and writes the guarded header.

### State, Persistence, And Dependencies
State is local shell variables `in`, `out`, `align`, and `fileguard`. It depends on POSIX shell, `grep`, `sort`, `tail`, `basename`, and `sed`.

### Integration Points
Called by `arch/arm/tools/Makefile` when generating kernel syscall API headers.

### Risks
Assumes syscall numbers sort correctly with `sort -n`; unusual hexadecimal formats must remain accepted by shell arithmetic. If the last row is malformed, syscall count generation becomes wrong.

### Test Signals
Add a high syscall number to a temporary table and confirm the generated count rounds as expected. Run shellcheck-style review and `make ARCH=arm archprepare`.
