# sources/distributed-fs/ceph-client/include/dt-bindings/clock/am3.h

Purpose: defines TI AM3 clock-control register offsets as DT clock IDs for the clkctrl provider.

Important APIs/types/functions: base/index macros include `AM3_CLKCTRL_INDEX()` and per-domain variants for L4LS, L3S, L3, L4HS, PRUSS OCP, LCDC, 24MHz, L3 AON, and L4 WKUP AON. Constants identify UART, MMC, ELM, I2C, SPI, timers, RNG, GPIO, CAN, EPWMSS, spinlock, mailbox, OCPWP, USB OTG, GPMC, McASP, EMIF, AES, SHAM, TPCC/TPTC, PRUSS, CPSW, LCDC, control, ADC/TSC, SmartReflex, watchdog, debug, WKUP M3, MPU, RTC, GFX, and CEFUSE clkctrl offsets.

Control flow: DTS uses offset-derived IDs; TI clock drivers translate IDs back to register offsets relative to clkctrl blocks.

State and persistence: IDs are DT ABI and encode hardware register layout.

Dependencies and integration: standalone TI clock binding for AM33xx/AM3 SoCs.

Risks and test signals: wrong offset bases break register programming. Test clockctrl lookup, module enable/idle for each domain, suspend/resume, and DTS references against TRM offsets.
