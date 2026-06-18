<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-t7-reset.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-t7-reset.h

### Purpose
This header defines the larger Amlogic T7 reset ID namespace for DTS reset cells. It spans RESET0 through RESET6 and covers display, video, GPU, DSP, PCIe, camera, bus bridge, and peripheral reset lines.

### Important APIs, Types, And Functions
The API is 163 `RESET_*` macros under `__DTS_AMLOGIC_T7_RESET_H`. Notable groups include USB/U2/U3 resets, HDMI/eDP/MIPI/VDAC/VIU/VENC display resets, MALI/DOS/DSP/ANAKIN compute blocks, PCIe resets, Ethernet, SPI/SmartCard/RSA, UART/I2C/SD-eMMC, NoC/NIC bridges, and RESET6 pipeline/AMPIPE/AXI bridge lines up to ID 223.

### Control Flow
The header is compile-time data only. DTS files include it, C preprocessor emits integer cells, and the reset controller performs runtime assertions/deassertions when drivers request them.

### State, Persistence, And Dependencies
The constants encode hardware register bit positions and have no persistence beyond generated DTBs. Correctness depends on the T7 reset-controller binding, the SoC DTSI reset provider, and the reset controller driver using the same numbering scheme.

### Integration Points
T7 board DTBs in the Amlogic Makefile, including `amlogic-t7-a311d2-*`, can reference these constants. Driver integration is broad because display, video codec, GPU, PCIe, Ethernet, SPI, UART, I2C, SD/eMMC, watchdog, and fabric resets are all represented.

### Risks
The namespace is dense and hardware-facing; an off-by-one macro can reset the wrong display, PCIe, memory, or bridge path. Some macros represent fabric or pipeline resets, where incorrect use can affect multiple consumers rather than one leaf device.

### Test Signals
Build T7 DTBs, run `dtbs_check`, then validate boot logs for reset-controller probe and peripheral resets. Display/video, PCIe, network, storage, and suspend/resume tests give the strongest coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-t7-reset.h -->
