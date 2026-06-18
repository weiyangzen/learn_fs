<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pxa.c

## Purpose
GPIO driver for Intel/Marvell PXA and MMP SoCs. It manages banked GPIO registers, pinctrl handoff, direct GPIO0/GPIO1 IRQs, muxed IRQ demuxing, wake forwarding, DT/legacy init, and syscore suspend/resume.

## Important APIs, types, and functions
`struct pxa_gpio_chip` stores device, chip, banks, irqdomain, direct IRQs, and wake callback. `struct pxa_gpio_bank` stores register base, IRQ mask/edge masks, and PM saved registers. Key paths are chip init, direction/get/set, IRQ type, mux/direct handlers, ack/mask/unmask, probe, and syscore PM.

## Control flow
Probe derives SoC type/count, creates a legacy irqdomain, validates IRQ resources, maps registers, enables clock, registers the chip, clears edge detects/status, optionally unmasks MMP AP-side detection, requests direct and mux IRQs, and stores the singleton. Direction output writes level first, then pinctrl, then GPDR.

## State and persistence behavior
Global state tracks last GPIO, IRQ base, chip, and type. Per-bank state tracks IRQ masks and edge selections. Syscore suspend saves GPLR/GPDR/GRER/GFER and clears GEDR; resume restores output levels through GPSR/GPCR, then edge and direction registers.

## Dependencies and integration points
Uses platform/OF data, clocks, pinctrl direction helpers, legacy irqdomain mapping, gpiolib, and syscore PM. DT and non-DT registration use separate initcalls.

## Risks and edge cases
Singleton globals, PXA26x inverted GPIO86-89 semantics, alternate-function occupancy checks, MMP edge mask handling, and syscore register-width assumptions are subtle. Probe rejects partial IRQ descriptions.

## Test signals
SoC counts, DT/legacy paths, inverted GPIOs, pinctrl handoff, direct and mux IRQs, edge type changes, wake callback, MMP mask writes, and syscore resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pxa.c -->
