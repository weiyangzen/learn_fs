# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.c

Purpose: defines Digital Devices board metadata and register maps used by ddbridge probe and core initialization. It maps PCI vendor/device/subdevice IDs to `struct ddb_info` descriptors and provides `get_ddb_info()`.

Important APIs/types/functions: static `ddb_regset` and `ddb_regmap` describe Octopus input/output, DMA, DMA buffer, and I2C register windows plus interrupt bases. Numerous `ddb_info` entries encode board type, name, port count, I2C mask, board-control reset bits, LEDs/fans/temp sensors, TS quirks, temp monitor IRQ, MCI port count, and MCI type. `ddb_device_ids[]` is searched by `get_ddb_info()`.

Control flow: `ddbridge-main.c` populates `dev->link[0].info` from PCI IDs. The core uses the resulting descriptor to initialize boards, I2C adapters, ports, DMA register offsets, temp monitoring, and sysfs attributes. Unknown boards fall back to `ddb_none`, which still has the Octopus register map but identifies unsupported hardware.

State and persistence: all data is immutable static metadata. There is no runtime mutation or persistence in this file.

Dependencies/integration: depends on constants from `ddbridge.h` and `ddbridge-hw.h`. It is the hardware database for `ddbridge-main.c`, `ddbridge-core.c`, and `ddbridge-i2c.c`.

Risks and test signals: incorrect metadata can misprobe hardware, use wrong I2C masks, assert wrong reset bits, or attach unsupported frontends. Test by matching `dmesg` board names and hardware/regmap IDs against real cards, verifying port counts and temp/fan attributes, and confirming new PCI IDs do not regress existing subdevice matches.
