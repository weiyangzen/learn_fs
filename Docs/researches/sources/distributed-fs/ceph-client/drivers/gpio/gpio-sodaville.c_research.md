# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sodaville.c

## Purpose
This built-in PCI driver supports Intel Sodaville public GPIOs. It exposes 12 GPIOs through `gpio_generic_chip` and provides level interrupt support with a legacy IRQ domain and generic irqchip.

## Important APIs, Types, and Functions
`struct sdv_gpio_chip_data` stores the MMIO base, legacy IRQ base, IRQ domain, generic IRQ chip, and generic GPIO chip. `sdv_gpio_pub_set_type()` programs level high/low in GPIT registers. `sdv_gpio_pub_irq_handler()` masks status with interrupt-enable bits and dispatches domain IRQs. `sdv_register_irqsupport()` allocates descriptors, requests the shared PCI IRQ, initializes a generic irqchip, and creates the legacy domain.

## Control Flow
PCI probe enables the device, maps BAR0, optionally writes `intel,muxctl`, initializes the generic chip with input, output, and output-enable registers, registers the gpio chip, then registers IRQ support. IRQ setup masks and acknowledges all sources, requests the PCI IRQ, configures fast-EOI handling with mask/eoi registers, and maps 12 legacy IRQs.

## State and Persistence
GPIO state is hardware-backed. IRQ controller state is held in generic irqchip mask cache and hardware registers. There is no suspend/resume handling in this file.

## Dependencies and Integration Points
The driver is a built-in PCI driver for Intel device ID `0x2e67`, uses managed PCI resource mapping, gpiolib generic helpers, OF property parsing on PCI device nodes, and irqdomain/generic-chip APIs.

## Risks
Only level-high and level-low IRQs are supported. The hardware latches level IRQs, so the comment notes that unmask/ACK ordering matters; fast-EOI handling is chosen accordingly. GPIO registration occurs before IRQ support; if IRQ setup fails, probe fails and managed cleanup unwinds. Legacy IRQ domains and descriptor allocation are older patterns.

## Test Signals
Test PCI enable/BAR mapping, optional mux control write, GPIO direction/value operations, level-high/low type setup for lines below/above 8, IRQ status masking, EOI behavior while level remains active, and failure paths in descriptor allocation/request_irq/domain creation.
