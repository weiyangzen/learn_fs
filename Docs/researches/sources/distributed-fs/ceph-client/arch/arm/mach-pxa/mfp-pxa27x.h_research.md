<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa27x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa27x.h

Purpose: PXA27x-specific pin multiplexing macro catalog for the PXA2xx MFP framework.

Important definitions: GPIO85-120, clock/timer pins, memory and PC Card signals, I2C, UARTs, FICP, PWM, AC97 including warm-reset workaround GPIO configs, I2S, SSP1-3, MMC, LCD, keypad matrix, USB P2/P3/host, QCI camera, USIM, MSL, Memory Stick, and aggregate LCD macros. Declares `keypad_set_wake()`.

Control flow and integration: SoC and board code pass macros to `pxa2xx_mfp_config()`. `pxa27x_configure_ac97reset()` in `pxa27x.c` specifically uses AC97 reset macros from this header.

State and persistence: macro values become GAFR/GPDR/PGSR/wake register programming. Header itself has no state.

Dependencies: includes `mfp-pxa2xx.h`.

Risks and test signals: PXA27x has bidirectional special-function pins and power-I2C override behavior on GPIO3/4; incorrect configuration can conflict with controllers. Test with UART, AC97 warm reset, keypad wake, LCD, MMC, USB, and suspend/resume pin restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa27x.h -->
