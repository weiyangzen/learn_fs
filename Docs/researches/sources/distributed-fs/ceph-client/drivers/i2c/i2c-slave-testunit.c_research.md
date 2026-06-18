# sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-testunit.c

Purpose: programmable I2C slave-mode test target. It accepts register-like command writes from a remote master, delays execution, then performs adapter actions such as reading bytes from another address, emitting SMBus Host Notify, participating in SMBus Alert, block process-call behavior, and returning the kernel version string over repeated-start reads.

Important APIs/types: command enum values include `TU_CMD_READ_BYTES`, `TU_CMD_SMBUS_HOST_NOTIFY`, `TU_CMD_SMBUS_BLOCK_PROC_CALL`, `TU_CMD_GET_VERSION_WITH_REP_START`, and `TU_CMD_SMBUS_ALERT_REQUEST`. `struct testunit_data` stores flags, four command registers, indices, client, delayed work, optional GPIO, and alert completion.

Control flow: the slave callback gathers up to four bytes, validates command numbers, queues delayed work on STOP when a full command is present, NACKs while busy or after errors until STOP, and serves status/version/proc-call bytes on reads. Worker execution performs regular I2C transfers, writes host-notify frames to address `0x08`, or temporarily unregisters/re-registers the client at alert address `0x0c` while asserting a GPIO.

State and persistence: command registers and busy/NACK flags persist until command completion or STOP. Optional GPIO state is used for SMBALERT tests. No persistent storage beyond the device lifetime.

Dependencies and integration: depends on I2C slave core, normal I2C master transfers on the same adapter, workqueues, completions, optional non-sleeping GPIO, and generated `UTS_RELEASE`.

Risks: it intentionally drives complex bus behavior and can conflict with real devices if misconfigured. SMBALERT mode temporarily changes the client address and registration. GPIOs that can sleep are rejected. Workqueue operations after removal are guarded by `cancel_delayed_work_sync()`.

Test signals: scripted command writes, busy/NACK behavior, host-notify delivery, alert completion timeout, repeated-start version reads, delayed execution, and removal during pending work.
