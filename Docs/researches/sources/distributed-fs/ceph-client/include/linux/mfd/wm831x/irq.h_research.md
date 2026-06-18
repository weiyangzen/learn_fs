<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/irq.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/irq.h

## Purpose
`irq.h` defines the WM831x interrupt-controller ABI used by the MFD core and child drivers. It assigns Linux-local interrupt numbers for temperature, GPIO, power path, watchdog, RTC, charger, touch, AUXADC, current-sink, high-current, and regulator undervoltage events, then maps the chip interrupt status and mask registers at `0x4010` through `0x401d`.

## Important APIs, types, and functions
There are no functions or structs. The public API is macro based: `WM831X_IRQ_*` indexes, `WM831X_NUM_IRQS`, root status bits such as `WM831X_PPM_INT`, per-source event bits such as `WM831X_CHG_BATT_HOT_EINT`, GPIO event bits `WM831X_GP1_EINT` through `WM831X_GP16_EINT`, IRQ output configuration bits `WM831X_IRQ_OD` and `WM831X_IM_IRQ`, and matching `WM831X_IM_*` masks.

## Control flow
The runtime IRQ controller code uses the root `System Interrupts` register to identify active interrupt classes, then reads the child status registers and dispatches child IRQ numbers. Mask updates write the parallel mask registers. This header supplies the bit layout needed for that decode/ack/mask flow.

## State and persistence behavior
State is in chip registers: latched event status, output-line mode, and interrupt mask bits. Driver state derived from these macros is volatile and must be reconstructed on probe or resume.

## Dependencies and integration points
The header is consumed by WM831x MFD IRQ setup and by child drivers requesting specific IRQ numbers. It aligns with PMU, RTC, charger, GPIO, touch, AUXADC, OTP, watchdog, current-sink, and regulator headers that define the controlled hardware blocks.

## Risks and test signals
Risks include off-by-one IRQ numbering, missing `WM831X_IRQ_CHG_END` gap handling, masking a root interrupt while leaving child status pending, and confusing status bits with mask bits. Test signals are probe-time IRQ-domain size checks against `WM831X_NUM_IRQS`, per-source interrupt injection, suspend/resume mask restoration, GPIO edge tests, and charger/regulator fault IRQ routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/irq.h -->
