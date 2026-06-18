## sources/distributed-fs/ceph-client/drivers/input/keyboard/pinephone-keyboard.c

Purpose: Pine64 PinePhone keyboard I2C driver. It reports a 6x12 matrix plus FN layer, validates scan CRCs, controls keyboard scanning for power, and optionally exposes the keyboard accessory's tunneled SMBus adapter.

Important APIs/types/functions: `struct pinephone_keyboard` stores optional `i2c_adapter`, input, double scan buffers, CRC table, FN state per column, buffer selector, and current FN press state. `ppkb_update()` reads scan data and reports diffs. `ppkb_adap_smbus_xfer()` proxies SMBus byte-data operations through keyboard firmware registers. `ppkb_open()`/`close()` enable or disable scanning.

Control flow: probe enables `vbat`, reads and validates device ID/firmware/matrix size, disables scanning by default, optionally registers a child I2C adapter from an `i2c` child node, builds the CRC table, allocates input, builds static normal/FN keymap, registers input, and requests a threaded IRQ. IRQ calls `ppkb_update()`, which reads CRC+columns, verifies CRC8, swaps buffers, reports changed normal or FN-layer scancodes, tracks FN key state, and syncs.

State/dependencies/integration: state includes scan buffers, FN state used to report releases against the layer active at press time, firmware scan-enable bit, regulator state, child I2C adapter, and input keymap. Dependencies are I2C SMBus block reads/writes, regulator, OF, CRC8, input matrix helpers, and threaded IRQ.

Risks and test signals: FN state tracking is subtle; release scancode must match the layer selected when pressed, not current FN state. CRC failures intentionally drop whole scans. Test bad CRC, scan enable/disable on open/close, FN press/hold/release combinations, child SMBus read/write proxy status handling, unexpected firmware matrix size, and IRQ before input open.
