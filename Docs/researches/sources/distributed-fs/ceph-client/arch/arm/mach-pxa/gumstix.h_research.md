<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.h

Purpose: Gumstix board GPIO and IRQ definition header.

Important definitions: GPIOs for Bluetooth reset, USB VBUS/pullup, SD/MMC write-protect and detect, SMC Ethernet reset/IRQ, CompactFlash status/reset lines, and carrier hook prototypes `am200_init()` and `am300_init()`.

Control flow and integration: included by Gumstix board and carrier files to translate fixed board wiring into PXA GPIO numbers and IRQs via `PXA_GPIO_TO_IRQ()`.

State and persistence: header only; no state.

Dependencies: includes `irqs.h` for GPIO-to-IRQ mapping and relies on legacy GPIO direction flag macros.

Risks and test signals: incorrect GPIO constants break board IO and carrier operation. Test through Gumstix peripherals: USB cable detect, MMC detect, Ethernet IRQs, CF lines, and Bluetooth reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.h -->
