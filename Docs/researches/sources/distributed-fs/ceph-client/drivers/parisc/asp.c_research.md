<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/asp.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/asp.c

## Purpose
`asp.c` initializes the ASP/Cutoff GSC ASIC on older PA-RISC systems. It claims the hardwired GSC interrupt, installs the common GSC ASIC interrupt handler, programs the VIPER interrupt word, assigns local IRQs to known ASP child devices, and optionally registers old-style chassis LED support.

## Important APIs, Types, And Functions
The static `struct gsc_asic asp` holds ASP state. `asp_choose_irq()` maps child `sversion` values to local IRQ lines and optional auxiliary IRQs. `asp_init_chip()` probes the ASIC, claims/request IRQs, initializes the GSC common layer, fixes child IRQs, and registers LEDs. The `parisc_driver` matches `HPHW_BA` with sversion `0x00070`.

## Control Flow
At `arch_initcall`, `asp_init()` registers the PA-RISC driver. Probe reads the ASP version from `dev->hpa.start + ASP_VER_OFFSET`, names it `"Asp"` or `"Cutoff"`, uses the separate interrupt register base `ASP_INTERRUPT_ADDR`, claims hardcoded GSC IRQ 3, constructs `asp.eim`, and requests `gsc_asic_intr`. It then writes VIPER so ASP interrupts arrive on that line, calls `gsc_common_setup()`, and walks both ASP children and a sibling Mongoose device through `gsc_fixup_irqs()`.

## State And Persistence
Runtime state is in the single static `asp` object and assigned IRQ fields in `parisc_device` children. Hardware state includes VIPER interrupt programming and LED registration at fixed legacy addresses. There is no remove path; this is boot-time platform setup.

## Dependencies And Integration Points
The driver depends on PA-RISC inventory/probing, GSC interrupt helpers, raw GSC I/O access, parent device traversal, and optional `CONFIG_CHASSIS_LCD_LED` LED registration.

## Risks
IRQ routing is hardcoded by historical sversion tables and hardware path checks. Unknown child devices are left untouched. ASP has two register windows, but firmware reports only the special-register base, so incorrect use of `hpa` versus `ASP_INTERRUPT_ADDR` would break interrupt handling. Error paths after `request_irq()` do not visibly undo earlier allocation.

## Test Signals
Boot tests should confirm ASP/Cutoff detection, GSC IRQ claim, child SCSI/LAN/HIL/parallel/serial/EISA/graphics/audio/FDDI IRQ assignment, aux IRQ assignment for HIL and EISA, Mongoose sibling fixups, VIPER interrupt delivery, and LED operation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/asp.c -->
