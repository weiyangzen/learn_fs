# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.h

## Purpose
Provides register offsets, bit masks, and bitfield helper macros for the Synopsys HDMI receiver driver and Rockchip-specific integration registers.

## Important APIs, Types, And Functions
The header exports `UPDATE()` and `HIWORD_UPDATE()` helpers plus hundreds of defines for SYS_GRF, VO1_GRF, HDMI PHY, controller, SCDC, packet decoder, CEC, DMA, interrupt, HDCP, audio, video, and monitor registers. These names form the internal register API used by `snps_hdmirx.c` and `snps_hdmirx_cec.c`.

## Control Flow
There is no executable control flow. The constants drive all MMIO programming paths: PHY init, SCDC setup, HDCP disable/switch override, timing detection, DMA format/addressing, EDID SRAM access, interrupt masking/clearing, CEC TX/RX, and infoframe parsing.

## State And Persistence
No state is stored in the header. The defined addresses and masks describe mutable hardware state in the HDMI RX and Rockchip GRF blocks.

## Dependencies And Integration Points
Depends on Linux `bitfield`, `bitops`, and `hw_bitfield` helpers. It is tightly integrated with Synopsys HDMIRX IP register layout and Rockchip RK3588 syscon bits.

## Risks
Incorrect offsets or masks can corrupt unrelated hardware state. Some register names encode downstream documentation assumptions, and comments note errata or undocumented behavior in the C source. Duplicate `OPMODE_STS_MASK` definition is harmless but signals manual register-table maintenance. The header exposes no type safety around register groups, so C code must avoid mixing GRF, controller, CEC, and DMA offsets.

## Test Signals
Compile coverage catches missing macros only. Real validation comes from probing hardware, successful PHY register reads/writes, interrupt behavior, EDID access, CEC traffic, and DMA capture.
