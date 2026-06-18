# sources/distributed-fs/ceph-client/drivers/bus/da8xx-mstpri.c

## Purpose
Programs TI DA8xx master peripheral priority registers for boards that need fixed bus-priority tuning. The current table targets DA850 LCDK to avoid LCD controller FIFO underflow by adjusting LCDC and EDMA priorities.

## Important APIs, Types, And Functions
`struct da8xx_mstpri_descr` maps each master to register offset, shift, and mask. `struct da8xx_mstpri_priority` stores the desired priority value, and `struct da8xx_mstpri_board_priorities` ties a board compatible string to a priority list. `da8xx_mstpri_get_board_prio()` selects the board table using `of_machine_is_compatible()`, and `da8xx_mstpri_probe()` maps registers and applies each masked update.

## Control Flow
Probe maps the MSTPRI resource, locates a board-specific priority list, then for each requested change validates the register offset against resource size, reads the register, clears the target field, inserts the new priority value, and writes the register back.

## State And Persistence
The driver keeps no private runtime state. Its only lasting effect is programming SoC priority registers during probe; values persist until hardware reset or later firmware/kernel writes.

## Dependencies And Integration Points
It depends on platform/OF probing, DA8xx memory-mapped priority registers, and machine compatible strings such as `ti,da850-lcdk`. It indirectly integrates with display and DMA drivers by shaping bus arbitration.

## Risks And Test Signals
Risks include hard-coded policy becoming stale, missing board table entries, incorrect bitfield definitions, and changing arbitration in ways that harm other peripherals. Test signals include clean probe on supported boards, no out-of-range warnings, stable LCD output under DMA load, and absence of tilcdc FIFO-underflow warnings.
