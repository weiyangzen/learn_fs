# sources/distributed-fs/ceph-client/arch/parisc/include/asm/delay.h

Purpose: declares PA-RISC busy-wait delay routines and maps generic delay interfaces to architecture implementations.

Important APIs/types/functions: declares `__delay`, `__udelay`, `__cr16_delay`, and delay calibration hooks used by `udelay`/`ndelay` style callers.

Control flow: callers request a short wait; architecture code loops against CPU counters or calibrated cycles until elapsed time has passed.

State and persistence: relies on boot-calibrated CPU timing state outside this header. Dependencies and integration: used by drivers, early boot, firmware wait loops, and generic delay APIs.

Risks and test signals: under-delays break device programming; over-delays slow boot and drivers. Test with timer calibration, driver probe timing, and CPU-frequency/CR16 behavior checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
