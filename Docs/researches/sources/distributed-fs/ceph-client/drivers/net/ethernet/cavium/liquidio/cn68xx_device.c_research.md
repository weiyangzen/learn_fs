# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.c

## Purpose
This file adds CN68XX-specific LiquidIO setup on top of the CN6XXX common helpers. It programs DPI FIFO/engine settings, overrides reset and device register setup, configures CN68XX packet pipe counts, applies a PCIe vendor-message filter workaround, detects 210NV versus 410NV card type, and installs the CN68XX function table.

## Important APIs, Types, And Functions
The exported entry point is `lio_setup_cn68xx_octeon_device()`. Internal helpers are `lio_cn68xx_set_dpi_regs()`, `lio_cn68xx_soft_reset()`, `lio_cn68xx_setup_pkt_ctl_regs()`, `lio_cn68xx_setup_device_regs()`, `lio_cn68xx_vendor_message_fix()`, and `lio_is_210nv()`.

## Control Flow
Setup maps BAR0 and BAR1, initializes the shared CN6XXX DROQ interrupt lock, installs mostly CN6XXX function pointers while overriding soft reset and device-register setup, binds register addresses with the common helper, detects card type from `CN6XXX_MIO_QLM4_CFG`, loads the matching config (`LIO_210NV` or `LIO_410NV`), stores coprocessor clock rate, and applies the vendor-message filter mask. Soft reset calls the CN6XXX reset, then programs DPI DMA control, disables DMA engines, sets FIFO sizes, and enables DPI. Device setup configures PCIe MPS default and MRRS 256B, enables errors, programs global input/output registers, writes CN68XX packet pipe count into `CN68XX_SLI_TX_PIPE`, configures backpressure, and sets the window timeout.

## State And Persistence
Runtime state is the shared `struct octeon_cn6xxx` chip state, function table, configuration pointer, BAR mappings, and hardware CSRs. No filesystem state is persisted.

## Dependencies And Integration Points
It depends on `cn66xx_device.c` helpers and `cn66xx_regs.h` for most register programming, plus `cn68xx_regs.h` for CN68XX-specific pipe/PKIND constants. It integrates with LiquidIO core chip detection and config lookup.

## Risks
DPI setup uses fixed FIFO sizes and disables engines before core setup; hardware revisions must match those assumptions. Card-type detection depends on one QLM config field. MPS/MRRS register writes share the common OR-style helpers. Setup failure after BAR mapping must unmap both bars; this path is covered when config lookup fails. Vendor-message workaround writes PCI config filter bits unconditionally for CN68XX.

## Test Signals
Test both 210NV and 410NV card detection, BAR mapping cleanup, DPI register programming after reset, MRRS 256B operation, packet pipe count matching configured OQs, backpressure on/off configs, vendor-message filter behavior, and inherited CN6XXX interrupt/queue operations under traffic.
