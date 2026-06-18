# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.h

Purpose: declares shared STM32 I2C definitions used by STM32 controller drivers, especially speed identifiers and the DMA helper contract implemented in `i2c-stm32.c`.

Important APIs/types/functions: `enum stm32_i2c_speed` defines standard, fast, fast-plus, and sentinel speed classes. `struct stm32_i2c_dma` carries TX/RX DMA channels, the active channel, DMA address, length, transfer direction, mapping direction, and completion. Function prototypes expose `stm32_i2c_dma_request()`, `stm32_i2c_dma_free()`, and `stm32_i2c_prep_dma_xfer()` to controller-specific drivers.

Control flow: this header has no executable flow. It defines the data and function signatures used by STM32F4/F7-era drivers to share DMA setup and preparation logic. Callers request DMA once at probe time, prepare per-message DMA transfers during master/SMBus transfers, and free channels during remove or probe error unwind.

State and persistence: `struct stm32_i2c_dma` is the persistent shared state object. Its channel pointers persist across the adapter lifetime; per-transfer fields are overwritten for each DMA operation. The completion object allows controller drivers to wait for DMA completion before issuing STOP or moving to the next message.

Dependencies and integration: includes `linux/dma-direction.h`, `linux/dmaengine.h`, and `linux/dma-mapping.h`. It integrates with STM32 controller source files by abstracting DMA channel names and register offsets while leaving controller-specific IRQ and transfer sequencing outside the helper.

Risks: the `rd_wr` argument in `stm32_i2c_prep_dma_xfer()` is a boolean direction selector, so callers must pass the same read/write sense expected by the helper. The structure has no ownership flag; callers must avoid freeing channels twice and must clear or stop active DMA before removal.

Test signals: compile coverage across STM32 controller drivers, static checks that prototypes match implementation, and runtime validation of DMA setup/free plus per-transfer completion in the STM32F7 driver.
