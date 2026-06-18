# sources/distributed-fs/ceph-client/arch/s390/include/asm/lowcore.h

Purpose: This header defines the s390 lowcore layout: the per-CPU architected low-address save area used for interrupt old/new PSWs, machine-check data, timers, stacks, current task, ASCEs, and register save areas.

Important APIs/types/functions: `LC_ORDER`, `LC_PAGES`, `LOWCORE_ALT_ADDRESS`, `struct pgm_tdb`, packed/aligned `struct lowcore`, `get_lowcore()`, `lowcore_ptr[]`, `set_prefix()`, and assembler macros `GET_LC`/`STMG_LC` are central.

Control flow: Exception entry and low-level CPU code read and write fixed lowcore offsets for interruption parameters, old/new PSWs, save areas, stack pointers, per-CPU pointers, timers, current task, kernel/user ASCEs, IPL/OS info pointers, machine-check extended save area, and register save areas. `get_lowcore()` uses alternatives to return either address zero or relocated lowcore.

State and persistence: The lowcore is persistent per CPU and architecturally visible through prefixing. Its offsets are part of the low-level ABI with assembly, dump tools, firmware expectations, and KVM/machine-check paths.

Dependencies and integration points: It depends on machine-feature alternatives, ptrace PSW types, control registers, CPU definitions, and assembly alternative infrastructure.

Risks and test signals: Changing field offsets can break interrupts, dumps, restart, or machine-check recovery. Tests should include boot, interrupt delivery, CPU hotplug/prefix changes, lowcore relocation, crash dumps, machine checks, KMSAN lowcore metadata, and objdump/offset validation.
