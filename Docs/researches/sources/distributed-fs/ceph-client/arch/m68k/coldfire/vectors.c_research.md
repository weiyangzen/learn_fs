# sources/distributed-fs/ceph-client/arch/m68k/coldfire/vectors.c

Purpose: high-level trap vector table setup for ColdFire after early startup has established `_ramvec`.

Important APIs and functions: optional `dbginterrupt_c()` under `TRAP_DBG_INTERRUPT`, assembler declarations `buserr`, `trap`, `system_call`, `inthandler`, and `trap_init()`.

Control flow and state: `trap_init()` fills vector entries 3-23 and 33-63 with `trap`, vectors 24-31 and 64-254 with `inthandler`, clears vector 255, installs `buserr` at vector 2 and `system_call` at vector 32, and optionally routes vector 12 to a debug interrupt handler. State is the RAM vector table pointed to by `_ramvec`.

Dependencies and integration: `head.S` sets VBR and `_ramvec`; `entry.S` implements system call and interrupt entry; generic m68k trap code supplies `trap` and `buserr`.

Risks and test signals: wrong vector ranges can route CPU exceptions as IRQs or vice versa. Debug handler halts the CPU after dumping. Test system calls, bus errors, illegal instruction traps, external interrupts, and vector table contents after boot.
