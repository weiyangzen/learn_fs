# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_platform.c

## Purpose
`m_can_platform.c` is the platform-device glue for IO-mapped Bosch M_CAN controllers. It maps controller registers and shared Message RAM, obtains clocks and optional transceiver, then registers the common M_CAN class device.

## Important APIs, Types, And Functions
- `struct m_can_plat_priv` embeds `struct m_can_classdev` and stores separate register and Message RAM bases.
- `iomap_read_reg()` and `iomap_write_reg()` access controller registers.
- `iomap_read_fifo()` and `iomap_write_fifo()` access Message RAM using the parsed offsets supplied by the common core.
- `m_can_plat_probe()` allocates the class device, gets clocks, maps named resources `m_can` and `message_ram`, obtains optional IRQ `int0`, optional PHY, fills class fields, enables runtime PM, and registers the class.
- Runtime PM callbacks enable/disable `hclk` and `cclk`; system sleep callbacks forward to the common class suspend/resume helpers.

## Control Flow
Probe begins with `m_can_class_allocate_dev()`, which already parses `bosch,mram-cfg`. The platform wrapper then supplies hardware access resources and clock rate before calling `m_can_class_register()`. If no interrupt properties are present, `net->irq` stays zero and the common driver uses hrtimer polling.

## State And Persistence
The wrapper stores only `base` and `mram_base`; the common class owns netdev, CAN state, NAPI, and PM behavior. Runtime clock state is held by PM runtime. No disk state exists.

## Dependencies And Integration Points
The file depends on platform devices, device properties, named memory resources, clocks from `m_can_class_get_clocks()`, optional PHY, runtime PM, and Open Firmware match string `bosch,m_can`.

## Risks And Edge Cases
- Missing `message_ram` resource is fatal, and bad `bosch,mram-cfg` values can still cause invalid accesses unless the integration ensures the memory range is large enough.
- The IRQ is optional; polling mode should be tested because it is selected by absence of interrupt properties.
- Runtime PM must be enabled before class registration because the common class starts clocks during setup.

## Test Signals
Validate device-tree probing with and without `interrupts`, named resource mapping, clock prepare/unprepare through runtime PM, PHY bitrate max propagation, open/close, suspend/resume, and polling-mode RX/TX.
