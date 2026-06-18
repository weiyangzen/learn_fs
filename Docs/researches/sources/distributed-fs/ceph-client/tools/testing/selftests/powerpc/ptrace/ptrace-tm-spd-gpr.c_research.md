# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-gpr.c

## Purpose
`ptrace-tm-spd-gpr.c` validates ptrace visibility of GPRs in suspended transactional state on POWER transactional-memory systems.

## Important APIs, Types, and Functions
Important functions are `tm_spd_gpr()`, `trace_tm_spd_gpr()`, `ptrace_tm_spd_gpr()`, and `main()`. It uses `tm.h` transaction helpers and GPR validation constants from `ptrace-gpr.h`.

## Control Flow and State
The child enters a transactional-memory sequence, loads known GPR values into transactional or suspended state, records TEXASR/result information, and synchronizes with the parent. The parent uses ptrace to read the relevant register set and validates that expected GPR values are present. State includes shared memory, TM checkpoint/suspended registers, TEXASR, and child stop status.

## Dependencies and Integration Points
It depends on POWER TM hardware/kernel support, ptrace TM register sets, shared memory, and kselftest skip/pass macros.

## Risks and Test Signals
Risks are TM disabled by firmware/kernel, transaction failure modes changing register state, and ptrace register-set ABI drift. A pass means ptrace exposes the correct GPR values for the tested TM state.
