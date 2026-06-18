<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa300.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa300.h

Purpose: PXA300/PXA310 pin-function macro catalog for the PXA3xx MFP framework.

Important definitions: GPIO overrides, chip selects, AC97, I2C with pull-high low-power state, camera, keypad, LCD/mini-LCD, MMC1/MMC2/MMC3, SSP1-4, UART1-3, USB host/P2/P3/UTMI/ULPI, PWM, CIR, one-wire, data-flash ready, clocks, smart-card/USIM, and PXA310-only additions.

Control flow and integration: board or platform code uses these macros with `pxa3xx_mfp_config()`/`mfp_config()`. `pxa300.c` installs the address map that makes these logical pins resolve to MFPR offsets.

State and persistence: macros encode AF, drive strength, and low-power settings; runtime state exists only after applying them to MFPR registers.

Dependencies: includes `mfp-pxa3xx.h`; some sections are guarded by `CONFIG_CPU_PXA300` or `CONFIG_CPU_PXA310`.

Risks and test signals: PXA300/PXA310 pin address maps differ, so using macros before `mfp_init_addr()` or with wrong CPU config misprograms pins. Test pinmux users for camera, MMC, USB, UART, and keypad on both PXA300 and PXA310.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa300.h -->
