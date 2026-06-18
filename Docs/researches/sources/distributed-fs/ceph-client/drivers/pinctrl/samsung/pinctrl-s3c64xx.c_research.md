# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-s3c64xx.c

## Purpose
This file provides S3C64xx-specific data and interrupt logic for the shared Samsung pinctrl driver. It handles legacy S3C64xx GPIO EINT groups and EINT0 wakeup interrupts, then exports `s3c64xx_of_data` for the common Samsung platform driver.

## Important APIs, Types, and Functions
The file defines several S3C64xx bank layouts: 4-bit, 4-bit-alive, 4-bit with alternate register spacing, 2-bit, and 2-bit-alive types. Bank macros such as `PIN_BANK_4BIT_EINTG`, `PIN_BANK_4BIT_EINTW`, `PIN_BANK_2BIT_EINTG`, and `PIN_BANK_2BIT_EINTW` set the bank type, EINT function number, EINT mask, and EINT offset.

Interrupt-specific data structures are `struct s3c64xx_eint0_data`, `struct s3c64xx_eint0_domain_data`, and `struct s3c64xx_eint_gpio_data`. Key functions include `s3c64xx_irq_get_trigger()`, `s3c64xx_irq_set_function()`, GPIO EINT mask/ack/type handlers, `s3c64xx_eint_gpio_init()`, EINT0 wakeup mask/ack/type handlers, `s3c64xx_irq_demux_eint()`, and `s3c64xx_eint_eint0_init()`.

## Control Flow
The common Samsung probe calls `s3c64xx_eint_gpio_init()` for GPIO EINT setup and `s3c64xx_eint_eint0_init()` for wakeup setup. GPIO EINT setup creates one IRQ domain per GPIO EINT bank, stores them in group order, and installs a chained parent handler. The handler repeatedly reads the service register, decodes group and pin, handles the special group-1 split between two banks, and dispatches the pin through the relevant IRQ domain.

Wakeup setup locates a `samsung,s3c64xx-wakeup-eint` child node, maps four parent IRQs for EINT0 ranges 0-3, 4-11, 12-19, and 20-27, then creates per-bank domains for wakeup banks. The demux handlers read EINT0 pending and mask registers, filter by range, and dispatch active bits using a global mapping from EINT number to bank domain and pin.

## State and Persistence
Runtime state is stored in devm-managed EINT data structures, per-bank IRQ domains, the common bank structures, and the hardware registers. This file does not implement suspend/resume retention callbacks. It initializes `drvdata->pud_val` with S3C64xx-specific pull encoding through `s3c64xx_pud_value_init()`.

## Dependencies and Integration Points
It integrates with the common Samsung pinctrl/gpiolib driver through `s3c64xx_pin_ctrl`, with irqdomain and chained IRQ APIs, and with device tree child nodes for wakeup EINT parent interrupts. It depends on `drvdata->virt_base`, a legacy single base mapping retained by the common driver specifically for platforms like S3C64xx.

## Risks
The service-register domain indexing assumes GPIO EINT bank domains are stored in group order and that group 1 is split exactly as coded. `BUG_ON(ret)` in interrupt dispatch can panic if a pending unmasked interrupt lacks a domain mapping. Some mask arrays use `fls(mask)` to size domains, so sparse masks must have `ddata->eints` and domain translations consistent with pin indexes. Clock gating is not explicit in this file, relying on legacy access assumptions through `virt_base`.

## Test Signals
Tests should cover GPIO EINT group dispatch, group-1 split behavior, EINT0 range demux, all trigger types, invalid trigger rejection, bank function switching to EINT, sparse wakeup masks, and DT failure paths for missing wakeup parent IRQs. GPIO pull configuration should be checked for S3C-specific pull disable/down/up encodings.
