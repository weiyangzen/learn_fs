<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa320.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa320.h

Purpose: PXA320-specific pin-function macro catalog for PXA3xx MFP users.

Important definitions: PXA320 GPIO overrides, chip selects, AC97, I2C, camera/QCI, CIR/ICP/timer clocks, keypad matrix, LCD and mini-LCD, MMC1/MMC2, one-wire, SSP1-4, UART1-3, USB 2.0 UTMI, USB host/P2/P3, PC Card-style signals, and PWM outputs.

Control flow and integration: used by board code through `pxa3xx_mfp_config()`. `pxa320.c` registers the PXA320 MFPR address map used by these pin IDs.

State and persistence: header only; macro values become MFPR register contents when configured.

Dependencies: includes `mfp-pxa3xx.h`.

Risks and test signals: many pins offer multiple aliases; wrong macro can silently select the wrong alternate function. Test with PXA320 board peripherals, especially wake-related keypad/MMC/USB pins and LCD signal integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa320.h -->
