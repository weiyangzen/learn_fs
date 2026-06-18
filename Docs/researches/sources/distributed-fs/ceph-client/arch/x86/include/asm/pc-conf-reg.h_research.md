# sources/distributed-fs/ceph-client/arch/x86/include/asm/pc-conf-reg.h

Purpose: defines helpers for the legacy PC indexed configuration register pair at I/O ports `0x22` and `0x23`, used by MP Spec IMCR, Cyrix CPUs, and old chipsets.

Important APIs, types, and functions: constants are `PC_CONF_INDEX`, `PC_CONF_DATA`, and `PC_CONF_MPS_IMCR`. It declares `raw_spinlock_t pc_conf_lock`. Inline helpers `pc_conf_get(u8 reg)` and `pc_conf_set(u8 reg, u8 data)` perform index/data port I/O.

Control flow: `pc_conf_get()` writes the register index to port `0x22` then reads the value from `0x23`. `pc_conf_set()` writes the index then the data byte. Serialization is not performed in the helpers; callers are expected to use `pc_conf_lock` where necessary.

State and persistence: state lives in hardware configuration registers and the external lock. Writes can persist in chipset/CPU register state until reset or later writes.

Dependencies and integration points: depends on `linux/io.h`, raw spinlocks, and low-level users such as Cyrix register access and IMCR/chipset setup code.

Risks: register access order is mandatory. Missing locking can interleave index/data cycles across CPUs or drivers. Touching unknown indexed registers can misconfigure legacy chipsets.

Test signals: Cyrix and MP-table legacy paths should read/write expected registers, lockdep should catch misuse when lock wrappers exist, and I/O tracing or hardware tests should confirm ordered `outb(0x22)` then `inb/outb(0x23)`.
