# sources/distributed-fs/ceph-client/arch/sparc/kernel/pmc.c

## Purpose
Power Management Controller driver for SPARCstation Voyager. Maps the PMC register block and installs a Swift idle callback that signals hardware idle state.

## Important APIs, Types, and Functions
`pmc_probe()` maps the `SUNW,pmc` OF resource and assigns `sparc_idle`. `pmc_swift_idle()` sets `PMC_IDLE_ON` in `PMC_IDLE_REG`, optionally toggling an AUXIO LED under debug. `pmc_readb()` / `pmc_writeb()` wrap SBus access. `pmc_driver` matches `SUNW,pmc`.

## Control Flow
`pmc_init()` registers after SBus initialization. Probe maps registers and, unless disabled by compile-time macro, replaces the architecture idle function. Each idle entry writes the PMC idle bit.

## State and Persistence
Static `regs` stores the mapped I/O base. Runtime state includes the global `sparc_idle` function pointer and PMC register bit. No persistence.

## Dependencies and Integration Points
Uses OF platform probing, SBus I/O helpers, AUXIO debug support, and SPARC idle hooks.

## Risks and Test Signals
No remove/unmap path. Replacing global idle assumes no competing provider. Test via boot log `pmc: power management initialized` and idle register writes on Voyager hardware.
