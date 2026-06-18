# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.c

Purpose: `cyttsp_core.c` is the shared core for older Cypress TrueTouch Standard Product Gen3 controllers, used by the I2C and SPI transport drivers. It handles bootloader exit, operational/sysinfo mode setup, optional handshake flow control, input reporting, open/close power state, and PM.

Important APIs, types, and functions: the exported entry point is `cyttsp_probe(const struct cyttsp_bus_ops *bus_ops, struct device *dev, int irq, size_t xfer_buf_size)`. Low-level access is abstracted by `ttsp_read_block_data()` and `ttsp_write_block_data()`, which retry through bus ops up to `CY_NUM_RETRY`. Boot and mode helpers include `cyttsp_hard_reset()`, `cyttsp_soft_reset()`, `cyttsp_load_bl_regs()`, `cyttsp_exit_bl_mode()`, `cyttsp_set_sysinfo_mode()`, `cyttsp_set_sysinfo_regs()`, and `cyttsp_set_operational_mode()`. `cyttsp_irq()` reads touch packets and handles bootloader-ready completion. `cyttsp_report_tchdata()` maps up to four contacts into 16 MT slots.

Control flow: bus glue calls `cyttsp_probe()` with transport ops and buffer size. The core enables `vcpin` and `vdd`, gets optional reset GPIO, parses required `bootloader-key` plus optional timing/handshake properties, initializes input and MT slots, requests an initially disabled threaded IRQ, hard-resets the chip, powers it on through bootloader/sysinfo/operate sequencing, and registers input. Input open wakes the controller by reading registers and then enables IRQ. Close sends low-power mode and disables IRQ. Suspend/resume mirror open/close while holding the input mutex.

State and persistence: `struct cyttsp` stores bootloader data, sysinfo data, the latest XY data, BL completion, state enum, suspend flag, GPIO, handshake and timing properties, bootloader keys, and a transport-aligned transfer buffer. There is no persistence beyond device registers programmed during startup.

Dependencies and integration points: the core depends on the transport contract in `cyttsp_core.h`, regulators, optional reset GPIO, device properties, input MT, and `touchscreen_parse_properties()`. It exports `cyttsp_pm_ops` and `cyttsp_probe()` for I2C/SPI modules.

Risks: `bootloader-key` is required; missing firmware properties fail probe. IRQ is disabled/enabled manually and must remain balanced across soft reset/open/close/suspend paths. The touch report uses firmware-provided tracking IDs directly as MT slots, so malformed IDs over 15 could exceed the initialized bitmap/slot assumption. Recovering from unexpected bootloader mode during IRQ may leave the device idle if exit fails.

Test signals: verify I2C and SPI bus ops both reach `cyttsp_probe()`, required property handling, soft reset completion through IRQ, bootloader exit, sysinfo and interval programming, large-area/bad-packet release behavior, open/close IRQ balancing, and suspend/resume with an enabled input device.
