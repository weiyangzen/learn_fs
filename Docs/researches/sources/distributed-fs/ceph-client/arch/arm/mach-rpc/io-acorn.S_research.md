# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/io-acorn.S

Purpose: assembly I/O access routines for Acorn/RiscPC legacy port space.

Important APIs/types/functions: provides low-level byte/word/long I/O primitives used by the ARM port I/O layer for this machine.

Control flow: callers enter small assembly routines that translate legacy I/O port operations to the RiscPC I/O windows and perform the access.

State and persistence: mutates only target hardware registers.

Dependencies and integration points: paired with `mach/io.h` and `hardware.h`; used by drivers that expect traditional port I/O.

Risks: assembly address translation must match the machine map; bad ordering/width handling can break legacy devices.

Test signals: podule/ISA-style device access, IDE/serial/parallel operations, and build/link coverage for I/O symbols.
