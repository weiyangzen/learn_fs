# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/Makefile

Purpose: Builds early position-independent RISC-V code used before the main kernel relocation environment is fully available.

Important APIs/types/functions: Lists PI objects such as early FDT parsing, command-line parsing, and early random/KASLR seed support, with flags suitable for freestanding early execution.

Control flow: Kbuild compiles these objects for early boot use and links them into the kernel image so assembly boot code can call them before normal subsystems initialize.

State and persistence: Produces build artifacts only; runtime state is owned by the individual PI C files.

Dependencies and integration points: Integrates with `head.S`, early FDT, KASLR, SATP mode selection, and architecture build flags.

Risks and test signals: Incorrect flags can introduce relocations or instrumentation unsafe for early boot. Test early boot with KASLR, no-MMU/MMU modes, and objdump checks for unsupported relocations.
