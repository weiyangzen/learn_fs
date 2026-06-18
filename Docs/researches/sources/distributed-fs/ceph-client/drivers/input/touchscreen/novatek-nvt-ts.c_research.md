<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/novatek-nvt-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/novatek-nvt-ts.c

Purpose: I2C driver for Novatek NT11205 and NT36672A touchscreen controllers. It powers and resets the chip, reads a parameter block to discover size/touch count/IRQ type/chip ID, and reports multitouch slots from six-byte contact records.

Important APIs/types/functions: `struct nvt_ts_i2c_chip_data` holds expected chip ID; `struct nvt_ts_data` stores client, input, reset GPIO, regulators, touchscreen properties, max touches, and receive buffer. `nvt_ts_read_data()` performs register-addressed I2C reads. Runtime functions are `nvt_ts_irq()`, `nvt_ts_start()`, `nvt_ts_stop()`, PM suspend/resume, and `nvt_ts_probe()`.

Control flow: probe requires an IRQ, gets match data, obtains `vcc` and `iovcc`, powers the chip, gets reset GPIO, waits 100 ms, reads parameters at `0x78`, puts the chip back into reset and disables regulators, validates width/height/max touches/IRQ type/chip ID, creates input with parsed touchscreen properties, initializes MT slots, requests a no-auto-enable threaded IRQ with device-specified trigger type, and registers input. Open enables regulators, enables IRQ, and releases reset; close disables IRQ, asserts reset, and disables regulators. IRQ reads all touch records, validates slot and state, reports active/release state and transformed coordinates, then syncs.

State and persistence: state is volatile and power-gated; the chip is reset and regulators are off while the input device is closed. No persistent configuration is written.

Dependencies/integration: depends on I2C, regulator bulk API, reset GPIO, OF/I2C match data for `novatek,nt11205-ts` and `novatek,nt36672a-ts`, input MT core, touchscreen properties, and PM mutexing.

Risks and test signals: start enables IRQ before reset release, so interrupt timing around power-up should be tested. Validate parameter rejection paths, chip ID mismatch, unsupported buttons warning, max touch zero/out of range, IRQ trigger mapping, slot numbers starting at one, release records still carrying coordinates, regulator disable on probe errors, and suspend/resume while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/novatek-nvt-ts.c -->
