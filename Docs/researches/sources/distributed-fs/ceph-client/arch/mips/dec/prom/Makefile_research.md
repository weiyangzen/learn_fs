# sources/distributed-fs/ceph-client/arch/mips/dec/prom/Makefile

Purpose: selects DECstation PROM support library objects.

Important build behavior: always includes init, memory, command-line, identify, and console helpers. Adds `locore.o` only for R3000 CPUs.

Dependencies and integration: these objects run before normal platform setup to establish PROM vectors, memory, machine type, and early console.

Risks and test signals: wrong CPU conditional can omit the early exception handler needed for PMAX memory probing. Build R3000 and R4x00 DEC configs.
