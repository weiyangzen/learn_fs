# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_cs.h

**Purpose:** Declares chip-select configuration helpers for BCM63xx external memory/peripheral interfaces.

**Important APIs/types/functions:** Exports `bcm63xx_set_cs_base(cs, base, size)`, `bcm63xx_set_cs_timing(cs, wait, setup, hold)`, `bcm63xx_set_cs_param(cs, flags)`, and `bcm63xx_set_cs_status(cs, enable)`.

**Control flow:** Board or flash/PCMCIA setup code programs the chip-select base window, timing, bus parameters, then enables/disables the CS line.

**State and persistence behavior:** No local state. Implementations mutate external bus controller registers that persist until reset or reconfiguration.

**Dependencies and integration points:** Integrated by flash, PCMCIA, board setup, and memory controller code. Uses `u32` through include context, so callers generally include CPU/IO types first.

**Risks:** Wrong base/size/timing can make flash or PCMCIA unreadable or corrupt accesses. No constraints are visible in the prototype for valid chip-select numbers or timing ranges.

**Test signals:** Probe flash/PCMCIA devices, verify CS windows with resource maps, stress reads/writes at configured timings, and test disable/enable transitions.
