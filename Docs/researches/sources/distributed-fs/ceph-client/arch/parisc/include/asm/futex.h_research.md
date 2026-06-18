# sources/distributed-fs/ceph-client/arch/parisc/include/asm/futex.h

Purpose: implements PA-RISC futex atomic operations used by the userspace locking ABI.

Important APIs/types/functions: defines architecture futex operations such as atomic op-in-user and compare-exchange-in-atomic helpers, wired into generic futex code.

Control flow: futex code performs user-memory atomic reads/modifies under fault handling, returns old values or comparison results, and falls back through exception tables on bad user addresses.

State and persistence: modifies userspace futex words and may observe task wait queues managed by generic futex code. Dependencies and integration: depends on uaccess, exception tables, cmpxchg/atomic primitives, and syscall ABI.

Risks and test signals: user-access fault recovery and endian/width handling are critical for pthreads. Test with futex selftests, robust futexes, PI futexes where supported, and fault-injection on invalid addresses.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
