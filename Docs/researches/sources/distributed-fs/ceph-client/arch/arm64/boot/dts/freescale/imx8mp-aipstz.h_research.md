<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-aipstz.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-aipstz.h

### Purpose
This header defines i.MX8M Plus AIPSTZ consumer types, permission flags, and master IDs for DTS access-protection configuration.

### Important APIs, Types, And Functions
It exports 17 macros under `__IMX8MP_AIPSTZ_H`: consumer types `IMX8MP_AIPSTZ_MASTER` and `IMX8MP_AIPSTZ_PERIPH`, master flags `MPL/MTW/MTR/MBW`, peripheral flags `TP/WP/SP/BW`, and master IDs for EDMA, Cortex-A53, SDMA2, SDMA3, HIFI4, and Cortex-M7. `SDMA2` and `SDMA3` intentionally both use ID 3 in this file.

### Control Flow
DTS preprocessing emits numeric cells for an AIPSTZ provider/consumer binding. Runtime enforcement is performed by the relevant i.MX platform or bus-protection driver that programs access-control registers.

### State, Persistence, And Dependencies
The header has no runtime state. The values define a binding contract with i.MX8MP AIPSTZ hardware and its driver/firmware expectations.

### Integration Points
i.MX8MP DTS files can include the header to describe access permissions for bus masters and peripherals, affecting DMA engines, CPU cluster, DSP, and Cortex-M7 interactions with protected regions.

### Risks
Permission bits are security-sensitive; overly broad flags can expose protected peripherals, while restrictive or wrong master IDs can break DMA, DSP, or M7 operation. The duplicate SDMA2/SDMA3 ID deserves careful validation against hardware documentation.

### Test Signals
Build i.MX8MP DTBs, run binding checks, and validate DMA, audio DSP, M7 remoteproc, and protected peripheral access. Security/regression tests should cover denied and allowed access paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-aipstz.h -->
