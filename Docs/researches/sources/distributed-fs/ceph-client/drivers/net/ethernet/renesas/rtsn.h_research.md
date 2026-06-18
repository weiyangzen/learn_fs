# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.h

## Purpose
`rtsn.h` is the private hardware contract for the Renesas Ethernet-TSN driver. It defines register offsets for AXIBMI, TSNMHD, RMSO, and RMRO blocks; bitfields used by `rtsn.c`; descriptor layouts; chain sizes; timeout constants; and operation-mode/descriptors enums.

## Important APIs, Types, And Constants
The central enum is `enum rtsn_reg`, which maps symbolic names such as `TATLS0`, `RATLS0`, `OCR`, `OSR`, `TGC1`, `CFCR0`, `MPSM`, `MPIC`, `MRMAC0`, and `MLVC` onto block-relative offsets. `enum rtsn_mode` defines DISABLE, CONFIG, and OPERATION values written to `OCR`. Descriptor status and type values are in `enum DIE_DT`, with `DT_FEMPTY`, `DT_FSINGLE`, `DT_LINK`, `DT_EOS`, `DT_MASK`, and interrupt-enable `D_DIE`. DMA-visible layouts are `struct rtsn_desc`, `struct rtsn_ts_desc`, `struct rtsn_ext_desc`, and `struct rtsn_ext_ts_desc`, all packed. Chain constants select one TX and one RX chain, both size 1024. `PKT_BUF_SZ` and `RTSN_ALIGN` define RX buffer allocation.

## Control Flow Role
This header has no executable control flow, but it controls how `rtsn.c` sequences hardware. AXIBMI constants drive descriptor BAT setup and interrupt enable/disable. TSNMHD constants define mode polling and TX/RX filter setup. RMAC constants encode PHY interface, link speed, MII management operations, MAC address registers, and link verification. Descriptor type constants are used by the TX path to hand descriptors to hardware and by RX/NAPI to detect completed packets and refill empties.

## State And Persistence
The structures in this file define DMA-persistent state shared between CPU and device while the interface is open. Endianness annotations (`__le16`, `__le32`, `__le64`) document hardware little-endian fields. `info_ds` carries packet length and flags, `die_dt` carries ownership/type, `dptr` carries 32-bit DMA pointers, `info1` carries extended metadata, and timestamp descriptors append nanosecond/second fields.

## Dependencies And Integration Points
The header depends only on Linux types but is tightly integrated with `rtsn.c`. Register and descriptor definitions must match the R-Car Gen4 TSN hardware manual and the DMA mask used by probe. It also mirrors some concepts used by `rswitch` descriptors, but it is private to the standalone TSN driver.

## Risks
Any offset or bitfield error can cause silent hardware misconfiguration. The 32-bit `dptr` fields constrain DMA addressability. Packed descriptor layout and endianness must remain stable; compiler padding changes would break DMA. Chain-size constants influence memory pressure, latency, and wrap logic. Some enum values represent currently unused TSN features, so future expansion must confirm offsets rather than assuming naming implies support.

## Test Signals
Compile coverage catches symbol drift. Runtime coverage comes from successful descriptor BAT programming, mode transitions, RX/TX interrupt enable/disable, PHY interface/speed programming, MDIO reads/writes, and correct interpretation of RX/TX descriptors under ring wrap and timestamp traffic.
