<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.c

Purpose: Implements the memory-mapped I2C master controller support for five Cobalt I2C buses, registering Linux `i2c_adapter` instances used by ADV HDMI subdevices.

Important APIs/functions: `cobalt_i2c_init()` resets/enables each controller, sets the 400 kHz prescaler from `ALT_CPU_FREQ`, fills adapter metadata, and calls `i2c_add_adapter()`. `cobalt_i2c_exit()` deletes adapters. `cobalt_xfer()` implements I2C master transfers over one or more `i2c_msg`s. Low-level helpers `cobalt_tx_bytes()`, `cobalt_rx_bytes()`, and `cobalt_stop()` program the core command/status registers and poll TIP, ACK, and arbitration bits.

Control flow: For each message, `cobalt_xfer()` optionally sends the address with START, then reads or writes payload bytes with STOP only on the last message. Address write retries use `adap->retries`; transfer timeouts use `adap->timeout`. On failure it emits a synthetic stop sequence.

State/persistence: Per-bus state is `struct cobalt_i2c_data` with parent card and register base; adapter fields store retries, parent, algo, and name. Hardware state includes prescaler, control, command/status, and bus busy/transfer bits.

Dependencies/integration: Used by Cobalt probe to instantiate ADV7604/ADV7842/ADV7511 subdevices. Depends on Linux I2C core and Cobalt BAR1 register layout.

Risks: Poll loops rely on `adap->timeout`; the template does not set an explicit timeout, so I2C core defaults matter. `cobalt_i2c_exit()` deletes all adapters even if `cobalt_ignore_err` caused a later adapter to have `dev.parent = NULL`, which needs caution. The custom stop workaround is hardware-specific. A bus timeout during init with `ignore_err` returns success early and skips remaining adapters.

Test signals: I2C scan/subdevice probe on all five buses, repeated combined read/write transactions, NACK and arbitration-loss handling, timeout behavior, ignore-error path, and adapter cleanup on partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-i2c.c -->
