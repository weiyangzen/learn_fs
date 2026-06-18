# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_hpc.c

## Purpose
Implements the hardware access layer for Standard Hot Plug Controllers. It maps SHPC working registers, serializes and issues SHPC commands, handles interrupts or polling, reads slot status, controls LEDs/power/bus speed, and initializes/releases controller resources.

## Important APIs, Types, and Functions
Public hardware APIs include `shpc_init()`, `shpchp_release_ctlr()`, `shpchp_power_on_slot()`, `shpchp_slot_enable()`, `shpchp_slot_disable()`, `shpchp_set_bus_speed_mode()`, `shpchp_get_*_status()`, `shpchp_get_adapter_speed()`, `shpchp_query_power_fault()`, LED helpers, and `shpchp_check_cmd_status()`. Internal helpers include MMIO accessors, indirect SHPC config reads, `shpc_write_cmd()`, `shpc_wait_cmd()`, `shpc_isr()`, and polling timer helpers.

## Control Flow
Initialization locates SHPC MMIO either through AMD special handling or SHPC capability indirect registers, enables the PCI device, reserves and maps MMIO, initializes locks/wait queues, reads slot configuration, masks controller and per-slot events, installs a polling timer or MSI/INTx IRQ, computes max/current bus speed, and unmasks slot events. Commands wait for controller not busy, write the command register, wait for command completion via IRQ waitqueue or polling, and decode command errors. ISR masks global interrupts, wakes command waiters, dispatches per-slot event bits to `shpchp_ctrl.c`, clears slot events, and unmasks global interrupts.

## State and Persistence Behavior
Controller state includes MMIO base/size/mapping, capability offset, slot counts/offsets, speed fields stored in the subordinate bus, polling timer, IRQ allocation, and cached AMD errata register values. Hardware state includes SHPC logical slot registers, SERR/interrupt enable register, command/status register, and secondary bus speed mode.

## Dependencies and Integration Points
Depends on PCI config/MMIO APIs, MSI/IRQ APIs, timers, wait queues, SHPC constants from the spec, `shpchp_ctrl.c` event handlers, and `shpchp_core.c` lifecycle management.

## Risks
Resource failure paths in `shpc_init()` can leak memory regions if future changes add exits after `request_mem_region()`. Command completion waits are limited to one second and can return interrupted by signals. MMIO register masks must preserve reserved-zero bits. Polling and IRQ paths share `shpc_isr()`, so assumptions about IRQ numbers must remain minimal. Bus speed encoding depends on programming interface version.

## Test Signals
Probe with capability and AMD Golam paths, MMIO reservation/map failure injection, MSI success/fallback to INTx, polling mode, command timeout/interruption, every slot event bit, LED/power commands, bus speed set/get across PI 1 and 2, release masking, and controller remove during pending work.
