<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-novalake-events.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-novalake-events.c

## Purpose
Intel Nova Lake ACPI GPE event driver that exposes GPE status/enable bits as GPIO IRQs. It switches firmware toward exposed GPIO interrupt mode through an ACPI `_DSM`; it is not a general output GPIO controller.

## Important APIs, types, and functions
`struct nvl_gpio` stores the chip, mapped I/O-port base, raw spinlock, and GPE block size. GPIO read is `nvl_gpio_get()`. IRQ functions are `nvl_gpio_irq_set_type()`, `nvl_gpio_irq_mask_unmask()`, mask/unmask, ack, and parent `nvl_gpio_irq()`. `nvl_acpi_enable_gpe_mode()` evaluates the DSM GUID.

## Control flow
Probe validates an even nonzero I/O resource up to 0x20 bytes, maps it, requests the IRQ, registers a GPIO chip with pin count equal to the status half in bits, installs the IRQ chip, then calls `_DSM`. Parent IRQ handling scans status bytes, intersects with enable bytes, and dispatches enabled pending bits.

## State and persistence behavior
Hardware owns status and enable state; ack writes the status bit. The driver stores only the mapping and block size. The firmware mode request happens every boot and takes effect on a later boot per the source comment.

## Dependencies and integration points
Binds to ACPI HID `INTC1114`, uses ACPI I/O resources, platform IRQs, gpiolib IRQ domains, raw spinlocks, and ACPI DSM calls.

## Risks and edge cases
Uninstalling while exposed mode is active can leave GPEs unhandled until firmware falls back after two reboots. IRQ type selection only changes Linux flow handlers; hardware polarity is not programmed. The parent scan uses block-size arithmetic that should be checked for status/enable half boundaries.

## Test signals
Bad block-size rejection, successful DSM, correct `ngpio`, enable-byte mask/unmask, status-byte ack, and child IRQ delivery only for enabled pending bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-novalake-events.c -->
