# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cs.c

Purpose: BCM63xx chip-select control helpers for external memory/peripheral windows.

Important APIs and functions: `bcm63xx_set_cs_base()` validates chip-select number and power-of-two size, writes base/size encoding, and is exported. `bcm63xx_set_cs_param()` updates timing/parameter registers. `bcm63xx_set_cs_status()` enables or disables a CS line. A spinlock serializes register updates.

Control flow: board/device code calls these helpers before using external devices such as PCMCIA or flash windows. Each helper validates CS range and writes CPU-specific MPI registers.

State and persistence: mutates chip-select hardware registers for the current boot only.

Dependencies and integration points: depends on BCM63xx CPU helpers, MPI register definitions, `ilog2`, and external bus consumers.

Risks and test signals: invalid base/size encodings can alias memory windows or hang the bus. Test with flash/PCMCIA access, register dumps, and error paths for unsupported CS indexes.
