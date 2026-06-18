<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int0002_vgpio.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int0002_vgpio.c

## Purpose
Models the Bay Trail/Cherry Trail `INT0002` ACPI PME event as a virtual GPIO controller so gpiolib-acpi can invoke firmware `_L02`/`_E02` handlers and clear PME bus 0 status to avoid IRQ storms.

## Important APIs, Types, And Functions
`struct int0002_data` embeds a `gpio_chip`, parent IRQ, and wake-enable count. Dummy GPIO get/set/direction methods reflect that this is not real GPIO hardware. The irqchip ack/mask/unmask functions manipulate I/O ports `GPE0A_STS_PORT` and `GPE0A_EN_PORT`. `int0002_irq()` checks the GPE status bit, handles the virtual GPIO IRQ, and emits a hard wake event.

## Control Flow
Probe is limited to Bay Trail or Cherry Trail SoCs, requests the shared parent IRQ directly, configures a GPIO irqchip with only pin 2 valid, registers the gpiochip, registers an ACPI wake handler, and enables device wakeup. Suspend applies parent IRQ wake only for non-firmware suspend and only if consumers requested wake.

## State And Persistence
State includes GPE enable/status bits, wake enable count, and gpiochip IRQ domain. No real GPIO value state exists.

## Dependencies And Integration Points
Depends on ACPI, gpiolib, shared IRQ handling, x86 I/O port access, platform SoC detection, suspend core, and AML event methods referencing the virtual GPIO.

## Risks And Test Signals
Risks include direct fixed-port assumptions, wake-enable count imbalance, shared IRQ side effects, and incorrect valid-mask setup. Test on BYT/CHT systems for no IRQ9 storm, ACPI event handler execution, PME wake from s2idle, and non-binding on Menlow/other SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int0002_vgpio.c -->
