# sources/distributed-fs/ceph-client/drivers/ssb/driver_mipscore.c

## Purpose
MIPS core support for SSB SoCs: assigns backplane IRQ routing, initializes serial ports, detects flash, sets external timing, computes CPU clock, and prepares platform flash devices/NVRAM discovery.

## Important APIs, Types, and Functions
Public functions include `ssb_mips_irq`, `ssb_cpu_clock`, and `ssb_mipscore_init`. Key internals are `ssb_irqflag`, `find_device`, `clear_irq`, `set_irq`, `dump_irq`, `ssb_mips_serial_init`, and `ssb_mips_flash_detect`. Defines global `ssb_pflash_dev` and resource/data for physmap flash.

## Control Flow
Init returns if no MIPS core exists. It computes bus clock and nanoseconds, initializes EXTIF or ChipCommon timings, iterates all SSB devices assigning IRQs based on core type and available MIPS interrupt lines, dumps routing, initializes serial ports via EXTIF/ChipCommon, and detects serial or parallel flash. Flash detection uses ChipCommon flash capability if present, otherwise assumes a default 4 MiB parallel flash window; it also seeds BCM47xx NVRAM from detected flash memory.

## State and Persistence
Updates `dev->irq` for each SSB device, `mcore->nr_serial_ports`, serial descriptors, `mcore->sflash`/`pflash`, global flash platform resources, MIPS core IPSFLAG/INTVEC registers, and flash timing registers.

## Dependencies and Integration Points
Used by SSB bus registration before device attach. Integrates with ChipCommon/EXTIF timing and serial helpers, serial core descriptors, MTD physmap, BCM47xx NVRAM, and SSB sflash init.

## Risks
IRQ routing manipulates shared MIPS core registers and may reassign old devices recursively. Some return values encode disabled/unassigned/not-supported IRQs as 5/0/6, which callers must interpret correctly. Flash defaults can be wrong on unusual boards without ChipCommon. Global flash device/resource limits multi-bus scenarios.

## Test Signals
After init, debug IRQ dump should match expected core routing, serial ports should register with correct baud/IRQ, NVRAM should initialize from correct flash window, and MTD platform devices should reflect flash size and bus width.
