# sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/scoop.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/scoop.h` declares Sharp SCOOP
GPIO/controller register data and platform helper APIs. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `SCOOP_MCR`, `SCOOP_CDR`, `SCOOP_CSR`, `SCOOP_CPR`, `SCOOP_CCR`, `SCOOP_IRR`, `SCOOP_IRM`,
`SCOOP_IMR`, `SCOOP_ISR`, `SCOOP_GPCR`, `SCOOP_GPWR`, `SCOOP_GPRR`, `SCOOP_CPR_OUT`,
`SCOOP_CPR_SD_3V`, `SCOOP_CPR_CF_XV`, `SCOOP_CPR_CF_3V`, `SCOOP_GPCR_PA22`, `SCOOP_GPCR_PA21`, and
10 more; types: `scoop_config`, `scoop_pcmcia_dev`, `device`, `scoop_pcmcia_config`;
functions/prototypes: `reset_scoop`, `read_scoop_reg`, `write_scoop_reg`, `platform_scoop_config`.
The file is 67 lines / 1822 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `scoop_config`, `scoop_pcmcia_dev`, `device`,
`scoop_pcmcia_config`. External state or implementation hooks include `platform_scoop_config`. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit.
Interrupt-related declarations integrate with generic irqchip, exception entry, and per-CPU irq
accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `scoop.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
