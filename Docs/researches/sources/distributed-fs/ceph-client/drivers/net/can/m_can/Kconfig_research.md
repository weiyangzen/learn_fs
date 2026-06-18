# sources/distributed-fs/ceph-client/drivers/net/can/m_can/Kconfig

## Purpose
This Kconfig file defines build-time selection for the Bosch M_CAN common framework and its PCI, platform MMIO, and TCAN4x5x SPI integrations.

## Important APIs, Types, And Functions
- `menuconfig CAN_M_CAN` is the parent tristate and selects `CAN_RX_OFFLOAD`.
- `CAN_M_CAN_PCI` depends on `PCI` and enables the generic PCI bus wrapper.
- `CAN_M_CAN_PLATFORM` depends on `HAS_IOMEM` and enables the IO-mapped platform wrapper.
- `CAN_M_CAN_TCAN4X5X` depends on `SPI`, selects `REGMAP_SPI`, and enables the Texas Instruments TCAN4x5x peripheral wrapper.

## Control Flow
When the parent option is disabled, all child drivers are hidden. When enabled, child options determine which bus glue modules are compiled alongside or on top of `m_can.o`.

## State And Persistence
Kconfig state is build configuration only. It controls which modules or built-in objects exist; it has no runtime state.

## Dependencies And Integration Points
The parent option integrates with SocketCAN and specifically selects RX offload because peripheral variants use `can_rx_offload`. The TCAN option pulls in regmap SPI support needed by `tcan4x5x-regmap.c`.

## Risks And Edge Cases
- Selecting only `CAN_M_CAN` builds the common core without a concrete bus device unless another wrapper is enabled.
- `CAN_M_CAN_PLATFORM` relies on device-tree or firmware properties at runtime despite only declaring `HAS_IOMEM` at build time.
- `CAN_M_CAN_TCAN4X5X` requires SPI IRQ, clock, GPIO, regulator, and MRAM properties at runtime beyond the Kconfig dependency.

## Test Signals
Check that each selected symbol produces the expected object/module, that `CAN_RX_OFFLOAD` and `REGMAP_SPI` are selected where needed, and that allyesconfig/allmodconfig builds cover all combinations.
