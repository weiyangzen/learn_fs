<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa25x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa25x.h

Purpose: PXA25x-specific multi-function pin configuration macros built on the PXA2xx MFP encoding.

Important definitions: GPIO aliases for pins 2-8, reset input, clock outputs, chip selects, DMA request lines, bus-master pins, PC Card pins, FFUART/BTUART/STUART/HWUART, FICP, PWM, AC97, I2S, SSP1/SSP2, MMC, and LCD data/control pins. Provides aggregate LCD macros `GPIOxx_LCD_16BPP`, `GPIOxx_LCD_DSTN_16BPP`, and `GPIOxx_LCD_TFT_16BPP`.

Control flow and integration: board files pass these macros to `pxa2xx_mfp_config()` to program GAFR, GPDR, PGSR, and wake-related registers.

State and persistence: header only; macro values encode run-mode function, direction, and low-power state that become persistent register state after configuration.

Dependencies: includes `mfp-pxa2xx.h` for `MFP_CFG_IN()` and `MFP_CFG_OUT()`.

Risks and test signals: wrong AF or direction can drive board lines incorrectly, especially memory bus and LCD outputs. Test with Gumstix pin setup, serial ports, MMC, LCD/EPD carriers, and suspend pin levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa25x.h -->
