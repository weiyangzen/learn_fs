<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/amlogic,meson-g12a-gpio-intc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/amlogic,meson-g12a-gpio-intc.h

## Purpose
This header assigns GPIO interrupt IDs for the Amlogic Meson G12A GPIO interrupt controller binding. It maps GPIO banks to a contiguous IRQID space from GPIOAO through GPIOE.

## Important APIs, types, and functions
The exported API is `IRQID_*` macros: `IRQID_GPIOAO_0..11`, `IRQID_GPIOZ_0..15`, `IRQID_GPIOH_0..8`, `IRQID_BOOT_0..15`, `IRQID_GPIOC_0..7`, `IRQID_GPIOA_0..15`, `IRQID_GPIOX_0..19`, and `IRQID_GPIOE_0..2`.

## Control flow
DTS interrupt specifiers use these IDs instead of raw integers. The preprocessed DTB carries the numbers to the Meson GPIO interrupt controller driver, which maps the bank/line ID to hardware interrupt routing.

## State and persistence
There is no in-kernel state in this file. The IDs are stable DT binding values and persist in compiled board DTBs.

## Dependencies and integration points
It integrates with Amlogic pinctrl/GPIO interrupt-controller nodes and any peripheral DTS node that sources interrupts from Meson GPIO lines. It depends on the driver's hardware bank ordering matching this macro ordering.

## Risks and test signals
Risks include bank-order mismatch, off-by-one numbering around bank boundaries, and using G12A IDs on incompatible Meson variants. Test signals include GPIO interrupt smoke tests for each bank, `dtbs_check`, and edge/level interrupt validation through the Meson GPIO IRQ driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/amlogic,meson-g12a-gpio-intc.h -->
