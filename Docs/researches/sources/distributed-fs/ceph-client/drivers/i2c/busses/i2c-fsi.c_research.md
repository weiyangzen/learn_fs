# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-fsi.c

Purpose: FSI-attached IBM/OpenPOWER I2C controller driver. It exposes each hardware port as an `i2c_adapter`, polls the FSI engine status instead of using interrupts, and implements controller reset plus generic SCL/SDA recovery through diagnostic line-control registers.

Important APIs/types/functions: `struct fsi_i2c_ctrl` owns the FSI device, FIFO size, adapter list, and controller mutex. `struct fsi_i2c_port` wraps each adapter and current byte count. Core helpers are `fsi_i2c_dev_init()`, `fsi_i2c_set_port()`, `fsi_i2c_start()`, FIFO read/write helpers, `fsi_i2c_wait()`, `fsi_i2c_abort()`, `fsi_i2c_reset_bus()`, `fsi_i2c_reset_engine()`, and `fsi_i2c_xfer()`. Probe/remove are registered through `module_fsi_driver()`.

Control flow: probe initializes the controller, reads `I2C_STAT_MAX_PORT`, locates per-port OF child nodes, and registers adapters. Transfers serialize on `ctrl->lock`, select the port in `I2C_FSI_MODE`, emit a command with start/address/read/stop/length fields, then poll `I2C_FSI_STAT` until data requests, command completion, or an error. Data movement is chunked into FSI FIFO operations limited to at most four bytes, with three-byte operations reduced to two bytes for FSI alignment.

State and persistence: runtime state is in the controller object, port list, FIFO size, selected hardware port, and per-message `xfrd` byte counter. Hardware state persists in mode, watermark, interrupt mask, status, extended status, and port-busy registers. Reset paths reinitialize the controller and restore the selected port.

Dependencies and integration: depends on the FSI device API, OF child nodes, Linux I2C core, `i2c_bus_recovery_info`, jiffies timeouts, endian conversion, and bitfield helpers. It reports `I2C_FUNC_I2C`, protocol mangling, SMBus emulation, and SMBus block data.

Risks: all transfer completion depends on polling and fixed adapter timeouts. Error handling can reset the engine or the full bus and may issue a final STOP only for selected error classes. FIFO size comes from hardware and is used in watermark math, so bogus extended status would affect thresholds. Timeout subtraction uses adapter timeout minus elapsed jiffies per message. Probe skips unavailable OF ports but continues on adapter registration failures.

Test signals: probe should log the port count and create one adapter per available child node. Useful validation includes read/write across multiple FIFO chunks, repeated-start multi-message transfers, NACK mapping to `-ENXIO`, arbitration loss mapping to `-EAGAIN`, SDA-low recovery, port switching, and remove cleanup of every registered adapter.
