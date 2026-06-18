# sources/distributed-fs/ceph-client/include/dt-bindings/clock/alphascale,asm9260.h

Purpose: defines Alphascale ASM9260 clock IDs for AHB gates and system dividers.

Important APIs/types/functions: IDs cover AHB ROM/RAM/GPIO/MAC/EMI/USB/DMA/UART/I2S/I2C/SSP/IOCONFIG/WDT/CAN/MPWM/SPI/QEI/QuadSPI/camera/LCD/timers/IRQ/RTC/NAND/ADC/LED/DAC and system CPU/AHB/I2S/UART/SPI/QuadSPI/SSP/NAND/trace/camera/WDT/clkout/MAC/LCD/ADCANA dividers. `MAX_CLKS` is 74.

Control flow: DTS consumers use IDs; the ASM9260 clock driver maps them to gates/dividers.

State and persistence: constants are DT ABI.

Dependencies and integration: standalone clock binding for ASM9260.

Risks and test signals: `CLKID_SYS_UART3` and `CLKID_SYS_UART4` share value 56 in this header, so provider/consumer expectations must match that historical ABI. Test duplicate handling, UART clock lookup, and provider array bounds.
