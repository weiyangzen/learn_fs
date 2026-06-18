# sources/distributed-fs/ceph-client/arch/sparc/kernel/power.c

## Purpose
Simple OF platform power-button/control-register driver. Maps a `power` node control register and requests a button IRQ that triggers orderly shutdown when the node advertises one.

## Important APIs, Types, and Functions
`power_probe()` maps the first resource, logs the control register address, and conditionally registers the IRQ handler. `has_button_interrupt()` requires a valid IRQ and `button` property. `power_handler()` calls `orderly_poweroff(true)`. `power_driver` matches OF node name `power`.

## Control Flow
Built-in platform registration probes matching nodes. Probe maps four bytes and reads `op->archdata.irqs[0]`; if valid and marked as a button, it installs the handler. Button interrupts request an orderly userspace-assisted poweroff.

## State and Persistence
Static `power_reg` stores the mapped register but is not otherwise used. Shutdown is delegated to the reboot/poweroff subsystem. No persistence.

## Dependencies and Integration Points
Uses OF/platform resources, SPARC I/O mapping, interrupt APIs, and Linux orderly poweroff.

## Risks and Test Signals
Probe does not check map failure and assumes an IRQ entry exists. Handler does not inspect hardware status, so every interrupt is treated as a button. Test via boot register log, successful IRQ request, and power button causing `orderly_poweroff(true)`.
