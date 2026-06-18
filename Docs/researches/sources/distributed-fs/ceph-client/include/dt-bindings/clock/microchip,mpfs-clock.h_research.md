<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,mpfs-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,mpfs-clock.h

Purpose: Provides DT clock IDs for Microchip PolarFire SoC (MPFS), covering fabric-visible base clocks, peripheral gates, and Clock Conditioning Circuitry outputs.

Important APIs, types, and functions: Defines `CLK_CPU`, `CLK_AXI`, `CLK_AHB`, peripheral IDs for eNVM, MACs, MMC, timers, MMUART, SPI, I2C, CAN, USB, RTC, QSPI, GPIO, DDRC, FICs, ATHENA, CFM, a reserved MSS PLL hole, and `CLK_CCC_*` PLL/DLL outputs. No C functions are declared.

Control flow: Declarative only. The MPFS clock driver interprets DT IDs to expose common-clock-framework handles.

State and persistence: Numeric values are stable DT ABI. Runtime enable/rate state belongs to the clock provider and hardware.

Dependencies and integration points: Coupled to MPFS DTS, clock binding YAML, and consumers for networking, storage, serial, SPI/I2C, CAN, USB, RTC, FPGA fabric interfaces, and CCC-generated clocks.

Risks and test signals: Risks include the reserved ID 38 being accidentally reused and CCC output index mistakes. Test with DT validation, clock count checks, peripheral probe coverage, CCC output rate checks, and boot on boards using FPGA fabric and MSS peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,mpfs-clock.h -->
