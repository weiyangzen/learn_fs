
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-powermac.c

Purpose: this driver bridges Apple PowerMac low-level I2C buses (`pmac_i2c_bus`) into Linux `i2c_adapter` instances. It supports legacy Apple Keywest, PMU, and SMU bus types, implements SMBus and single-message I2C transfers through `pmac_i2c_*` firmware/platform calls, and performs custom child-device registration for Apple device-tree quirks.

Important APIs, types, and functions: `i2c_powermac_smbus_xfer()` maps SMBus quick, byte, byte-data, word-data, block-data, and I2C-block-data operations to `pmac_i2c_open()`, `pmac_i2c_setmode()`, and `pmac_i2c_xfer()`. `i2c_powermac_xfer()` handles only one generic I2C message, enforced by `i2c_powermac_quirks.max_num_msgs = 1`. `i2c_powermac_get_addr()`, `i2c_powermac_get_type()`, `i2c_powermac_register_devices()`, and `i2c_powermac_add_missing()` translate Apple OF child nodes into `i2c_board_info` and instantiate clients with `MAC,`-prefixed modaliases.

Control flow: probe receives a `pmac_i2c_bus` as platform data, gets the preallocated adapter from the low-level bus layer, names it according to bus type/channel, assigns algorithm and quirks, clears `of_node` to avoid standard child auto-registration, adds the adapter, restores the OF node, then manually registers children. Transfers open the low-level bus, set mode (`std`, `stdsub`, or `combined`), execute the transfer, log errors with NACKs at debug level, and always close the bus.

State and persistence: adapter storage is owned by the pmac low-level layer and is zeroed on remove after `i2c_del_adapter()`. Per-transfer state is local. Device registration intentionally keeps interrupt mappings allocated because other consumers may have used direct DT lookup.

Dependencies and integration points: it depends on PowerMac-specific `<asm/pmac_low_i2c.h>`, OF node parsing, OF IRQ mapping, platform devices, and I2C core client creation. It deliberately avoids generic I2C driver modaliases for Apple thermal/audio devices unless those drivers are MAC-aware.

Risks: SMBus block read semantics are noted as broken relative to the expected SMBus API because returned length handling is not standard. Generic I2C supports only a single message, so repeated-start I2C users must use SMBus-like paths or fail. Child registration contains Apple-specific address/type workarounds and may miss unknown nodes. Remove zeroes shared adapter memory, which assumes no users remain after adapter deletion.

Test signals: PowerMac boot enumeration, child client creation for DT nodes, Onyx audio fallback probing, single-message I2C read/write, SMBus word endian behavior, block operation consumers, and refusal of ten-bit or multi-message generic I2C transfers.
