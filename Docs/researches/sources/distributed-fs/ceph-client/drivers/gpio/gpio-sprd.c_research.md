# sources/distributed-fs/ceph-client/drivers/gpio/gpio-sprd.c

## Purpose
This driver supports Spreadtrum GPIO controllers with 16 banks of 16 lines for 256 total GPIOs. It provides GPIO request/direction/value operations and chained parent IRQ demultiplexing.

## Important APIs, Types, and Functions
`struct sprd_gpio` stores the gpio chip, MMIO base, raw spinlock, and parent IRQ. `sprd_gpio_bank_base()` maps a bank number to its register block. `sprd_gpio_update()` performs locked per-bit updates. GPIO callbacks use DMSK, DIR, INEN, and DATA registers. IRQ callbacks manage IE, IC, IS, IBE, and IEV registers and dispatch from MIS.

## Control Flow
Probe obtains the parent IRQ, maps the resource, initializes the lock, fills a 256-line gpio chip, configures a one-parent `gpio_irq_chip`, and registers it. GPIO request sets DMSK and free clears it. Input clears DIR and enables input; output sets DIR, disables input, and writes DATA. The chained IRQ handler scans every bank's masked interrupt status and dispatches set bits.

## State and Persistence
GPIO and IRQ state live in hardware registers. The driver keeps no software trigger shadow and has no suspend/resume hooks.

## Dependencies and Integration Points
It uses platform DT compatible `sprd,sc9860-gpio`, gpiolib, chained IRQ handling, raw spinlocks, and immutable irqchip resource helpers.

## Risks
`sprd_gpio_get()` reads DATA for both input and output; correctness depends on hardware DATA reflecting input state. Direction output programs direction before data, which may produce a transient output level. The handler scans all 16 banks on every interrupt. Wake is skipped by irqchip flags.

## Test Signals
Test all trigger modes, request/free DMSK behavior, direction input/output and INEN transitions, bank boundary offsets, chained IRQ dispatch across all 16 banks, interrupt clear on edge types, and bad parent IRQ/resource paths.
