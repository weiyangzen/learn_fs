# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Kconfig

## Purpose
Defines the TPO HVGA panel driver option for the MMP display subsystem.

## Important APIs, Types, and Functions
- `config MMP_PANEL_TPOHVGA` is a bool depending on `SPI_MASTER`.

## Control Flow
Kconfig exposes support for the TPO TJ032MD01BW panel when SPI master support is available.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Controls compilation of the SPI panel driver that registers an MMP panel and uses SPI writes for power/init.

## Risks
The option depends only on `SPI_MASTER`; it assumes the enclosing MMP display menu and platform data provide a compatible SPI device and path.

## Test Signals
Build with SPI master enabled and verify the panel object is selectable and compiled.
