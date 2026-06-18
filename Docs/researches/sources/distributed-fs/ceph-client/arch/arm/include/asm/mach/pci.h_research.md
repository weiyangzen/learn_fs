# sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/pci.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/pci.h` declares ARM machine PCI host-
controller setup, scan, swizzle, and mapping hooks. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
types: `pci_sys_data`, `pci_ops`, `pci_bus`, `pci_host_bridge`, `device`, `hw_pci`, `list_head`,
`resource`; functions/prototypes: `u8`, `pci_common_init_dev`, `pci_map_io_early`,
`iop3xx_pci_setup`, `iop3xx_pci_preinit`, `iop3xx_pci_preinit_cond`, `dc21285_setup`,
`dc21285_preinit`, `dc21285_postinit`, `iop3xx_ops`, `dc21285_ops`. The file is 86 lines / 2164
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `pci_sys_data`, `pci_ops`, `pci_bus`, `pci_host_bridge`,
`device`, `hw_pci`, `list_head`, `resource`. External state or implementation hooks include
`pci_map_io_early`, `iop3xx_ops`, `iop3xx_pci_setup`, `iop3xx_pci_preinit`,
`iop3xx_pci_preinit_cond`, `dc21285_ops`, `dc21285_setup`, `dc21285_preinit`, and 1 more. There is
no userspace filesystem persistence in this file; persistence is either kernel memory, CPU register
state, hardware register state, or generated ABI values. Direct includes are `linux/ioport.h`. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `pci.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
