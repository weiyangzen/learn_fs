# sources/distributed-fs/ceph-client/include/dt-bindings/clock/am4.h

Purpose: defines TI AM4 clock-control register offset IDs for DT clkctrl consumers.

Important APIs/types/functions: macros derive IDs from offsets for global, L3S TSC, L4 WKUP AON, L4 WKUP, L3S, PRUSS OCP, L4LS, EMIF, DSS, and CPSW 125MHz domains. Constants cover ADC/TSC, WKUP M3, counter, timers, watchdog, I2C, UART, SmartReflex, control, GPIO, MPU, GFX, RTC, AES/DES/SHAM/TPCC/TPTC/L4HS, VPFE, GPMC, McASP, MMC, QSPI, USB OTG SS, PRUSS, CAN, EPWMSS, ELM, HDQ1W, mailbox, RNG, SPI, spinlock, UART, OCP2SCP, EMIF, DSS, and CPSW.

Control flow: clock-controller code uses the numeric IDs from DTS to select clkctrl registers and manage module clocks.

State and persistence: IDs encode stable hardware register offsets and are DT ABI.

Dependencies and integration: standalone AM4 clock binding.

Risks and test signals: offset arithmetic must match clock-driver base blocks. Test clkctrl registration, peripheral probe, low-power transitions, and schema references for every AM4 clock cell.
