<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a5-reset.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a5-reset.h

### Purpose
This header provides Amlogic A5 reset IDs for device-tree reset consumers. It is close to the A4 map but adds A5-specific DSP, NNA, RTC, SPI flash, and UART/I2C slave reset lines.

### Important APIs, Types, And Functions
The exported surface is 51 `RESET_*` macros under `__DTS_AMLOGIC_A5_RESET_H`. Important constants include `RESET_DSPA_DEBUG`, `RESET_DSPA`, `RESET_NNA`, `RESET_ABUS_ARB`, `RESET_SPIFC`, `RESET_RTC`, `RESET_UART_C`, `RESET_I2C_S_A`, and A5-specific bridge resets such as `RESET_BRG_AO_NIC_DSPA` and `RESET_BRG_NIC_NNA`.

### Control Flow
DTS preprocessing expands these macros into integer reset cells. Runtime sequencing is handled by Linux reset consumers and the Amlogic reset controller, not by this header.

### State, Persistence, And Dependencies
There is no stored state. The numbers are ABI-like binding constants and must stay aligned with the A5 reset controller's register/bit layout and DTS includes.

### Integration Points
A5 DTSI files use the constants to wire device nodes to reset-controller lines. The constants integrate with peripheral drivers for USB, DSP/NNA, Ethernet, SD/eMMC, UART, I2C, SPI, watchdog, and bus fabric.

### Risks
A4 and A5 share many macro names but differ in some line assignments and available blocks. Copying a DTS include from the wrong SoC can silently target the wrong reset. The comment around UART offsets has a stale-looking reserved range label, so numeric values, not comments, must be treated as authoritative.

### Test Signals
Build A5 DTBs, validate reset references with `dtbs_check` where bindings are available, and confirm affected peripherals probe cleanly after cold boot, module reload, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a5-reset.h -->
