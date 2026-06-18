# sources/distributed-fs/ceph-client/arch/mips/dec/prom/locore.S

Purpose: provides a tiny early exception handler used while probing PMAX memory.

Important label: `genexcept_early` stores CP0 Status into global `mem_err`, advances EPC by four bytes to skip the faulting instruction, and returns with `rfe`.

Control flow and integration: `memory.c` copies this handler to the exception vector at `CKSEG0 + 0x80` during memory probing, then restores the old handler afterward.

State and risks: modifies `mem_err` as the probe signal. The code is R3000-era exception handling and must remain small enough for the copied vector slot. Test PMAX memory probing and restoration of the original exception vector.
