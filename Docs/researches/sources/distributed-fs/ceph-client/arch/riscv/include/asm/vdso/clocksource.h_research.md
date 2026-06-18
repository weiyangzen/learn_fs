<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/clocksource.h

Purpose: Selects the RISC-V vDSO clocksource interface.

Important APIs/types/functions: Includes generic vDSO clocksource definitions with RISC-V cycle counter support.

Control flow: vDSO reads the time CSR/cycle source through generic helper paths.

State and persistence: No standalone state; uses vvar clock data.

Dependencies and integration points: Timekeeping, timex counter access, and generic vDSO clock mode code.

Risks: Wrong clock mode exposes non-monotonic vDSO time.

Test signals: vDSO clock_gettime selftests and counter virtualization tests.

Source read size: 8 lines, 169 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/clocksource.h -->
