## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_fw_if.h

### Purpose
`goya_fw_if.h` defines small but critical Goya firmware interface constants: the MSI-X event queue index, CPU boot address, firmware image offsets, and low PLL frequency.

### Important APIs, Types, And Functions
The macros are `GOYA_EVENT_QUEUE_MSIX_IDX`, `CPU_BOOT_ADDR`, `UBOOT_FW_OFFSET`, `LINUX_FW_OFFSET`, and `GOYA_PLL_FREQ_LOW`. They describe firmware placement in SRAM/DDR and the low clock used during boot or safe configuration.

### Control Flow
There is no code flow. Boot and interrupt setup code consumes these constants while programming firmware load addresses, CPU reset vectors, and event queue interrupt routing.

### State, Persistence, And Dependencies
State lives in hardware registers and firmware memory regions programmed by callers. The header depends on matching Goya firmware layout assumptions: U-Boot starts at 1 MiB in SRAM and Linux firmware starts at 8 MiB in DDR.

### Integration Points
It integrates with Goya firmware loading, CPU bring-up, event queue setup, and PLL configuration paths in the HabanaLabs driver.

### Risks
Incorrect offsets or boot address values can make firmware boot fail or overwrite reserved memory. Changing the MSI-X queue index without matching device/firmware changes can break event delivery.

### Test Signals
Boot logs should show firmware copied to expected offsets, firmware ready events arriving on MSI-X index 5, and low-frequency PLL programming succeeding before normal device bring-up.
