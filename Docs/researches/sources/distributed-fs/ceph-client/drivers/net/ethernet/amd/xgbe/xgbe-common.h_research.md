# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-common.h

## Purpose

`xgbe-common.h` is the shared register map and bitfield access contract for the AMD XGBE Ethernet driver. It names the Synopsys XGMAC DMA, MAC, MMC, MTL, PCS, SerDes, MAC-control, I2C, descriptor, and MDIO fields used by the implementation files in this directory. The file contains no executable functions, but it is the central ABI between C code and the device's memory-mapped and MDIO-visible hardware blocks.

The header is intentionally source-tree-aligned with the rest of the xgbe driver: `xgbe-dev.c`, `xgbe-drv.c`, `xgbe-desc.c`, `xgbe-debugfs.c`, DCB, PHY, I2C, PTP, and platform/PCI code all depend on these offsets and helper macros to avoid open-coded shifts and register arithmetic.

## Important APIs, Types, and Macros

- DMA global registers: `DMA_MR`, `DMA_SBMR`, `DMA_ISR`, AXI cache registers, descriptor prefetch registers, and channel register blocks starting at `DMA_CH_BASE` with `DMA_CH_INC`.
- MAC registers: transmit/receive control, packet filter, VLAN, flow control, queue mapping, hardware feature registers, MDIO, GPIO, MAC address filters, RSS, timestamp/PPS registers, and interrupt fields.
- MMC counters: transmit and receive counter offsets plus interrupt-enable/status bitfield definitions.
- MTL registers: queue operation mode, queue FIFO sizes, flow-control thresholds, traffic class ETS registers, queue-to-TC mapping, and dynamic queue/channel mapping.
- PCS, SerDes, RxTx, MAC-control, and I2C register definitions: these support XPCS windowed access, SerDes workarounds, platform properties, ECC status, and internal I2C transactions.
- Descriptor and packet bit definitions: `RX_PACKET_ATTRIBUTES`, `RX_PACKET_ERRORS`, `RX_NORMAL_DESC*`, `RX_CONTEXT_DESC*`, `TX_PACKET_ATTRIBUTES`, `TX_CONTEXT_DESC*`, and `TX_NORMAL_DESC*`.
- MDIO/vendor definitions: conditional definitions for PMA/PCS/AN/vendor MMD registers, clause 37/73 masks, KR training bits, CDR tracking, PMA reset/signal/valid/adaptation bits, and PLL control.
- Bitfield helpers: `GET_BITS`, `SET_BITS`, little-endian variants, and wrapper macros such as `XGMAC_GET_BITS`, `XGMAC_SET_BITS_LE`, `XP_GET_BITS`, and `XI2C_SET_BITS`.
- Register access helpers: `XGMAC_IOREAD/IOWRITE`, `XGMAC_MTL_IOREAD/IOWRITE`, `XGMAC_DMA_IOREAD/IOWRITE`, `XPCS{16,32}_IOREAD/IOWRITE`, `XSIR*`, `XRXTX`, `XP`, `XI2C`, and MDIO helpers `XMDIO_READ`, `XMDIO_WRITE`, and masked variants.

## Control Flow and Register Semantics

The file enables a consistent three-step pattern throughout the driver: read a register or descriptor word, extract or modify a named field, then write the value back. For queue/channel-specific hardware blocks, the macros compute offsets from a base plus an index stride, which is how `xgbe-dev.c` configures every DMA channel, MTL queue, and traffic class without duplicating address arithmetic.

Descriptor helpers operate on little-endian descriptor fields because DMA descriptors are shared with hardware. Normal host registers use CPU-endian MMIO values. This distinction is visible in transmit and receive paths: `xgbe-dev.c` writes TX/RX descriptors with `XGMAC_SET_BITS_LE`, while configuration paths write device registers with `XGMAC_IOWRITE_BITS`.

The MDIO helpers are built on `pdata->hw_if.read_mmd_regs` and `write_mmd_regs`, so code using `XMDIO_*` is abstracted from the platform-specific XPCS windowing implementation. The helpers inject `XGBE_ADDR_C45` and encode MMD/register address fields into the expected hardware access format.

## State and Persistence Behavior

This header does not own runtime state. Its macros mutate the state pointed to by `struct xgbe_prv_data`, `struct xgbe_channel`, hardware descriptor memory, or local variables passed by the caller. Persistence is therefore entirely hardware-side or caller-side: register writes survive until reset/power management reconfiguration, descriptor writes persist in DMA-coherent memory until the ring is reinitialized, and bitfield manipulations on local values persist only if the caller writes them back.

## Dependencies and Integration Points

`xgbe-common.h` depends on standard kernel primitives such as `BIT()`, endian conversion helpers, `ioread32/iowrite32`, `ioread16/iowrite16`, and the surrounding xgbe private structures declared in `xgbe.h`. It is included by files that implement the netdev path, descriptor allocator, DCB operations, debugfs register access, PHY/PCS access, I2C, and PTP support. Because it names hardware registers directly, changes here must be evaluated against all driver call sites and the relevant hardware programming manual.

## Risks and Failure Modes

- Incorrect bit index or width definitions can silently program the wrong hardware field, causing data-path hangs, wrong offload behavior, or link failures.
- `SET_BITS` uses `0x1 << width`; definitions with widths at or above the native literal width would be unsafe, so field widths must remain within expected register bit ranges.
- Read-modify-write helpers are not inherently synchronized. Callers must hold the appropriate lock or be in a serialized context when registers can be touched concurrently, especially XPCS window selection and RSS programming.
- The little-endian descriptor helpers must be used only for descriptor words. Mixing descriptor and MMIO helpers would corrupt byte ordering.
- Debugfs uses these macros for raw register access, so malformed offsets selected by users can touch arbitrary mapped registers if higher layers do not constrain them.

## Test Signals

Useful validation includes building the driver with sparse/endian warnings enabled, exercising netdev open/close, TX/RX traffic, VLAN filtering/stripping, RSS, VXLAN, DCB/PFC, PTP timestamping, MDIO/PHY access, and debugfs register reads. Hardware feature decoding in `xgbe_get_all_hw_features()` is a broad smoke test for MAC feature fields. Descriptor-level tests should verify that DMA ownership transitions, checksum/TSON/VLAN/VXLAN bits, and RX status parsing match expected packets under load.
