# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_i2c.c

## Purpose

`rmi_i2c.c` implements the I2C transport adapter for RMI4 devices. It maps RMI 16-bit register reads/writes onto I2C transfers using the RMI page-select register, handles regulators and startup delay, and registers an `rmi_transport_dev` with the RMI core.

## Important APIs, Types, and Functions

`struct rmi_i2c_xport` stores the transport, I2C client, page mutex/current page, reusable transmit buffer, regulators, and startup delay. `rmi_set_page()` writes the page-select register. `rmi_i2c_write_block()` and `rmi_i2c_read_block()` implement `rmi_transport_ops`. `rmi_i2c_probe()` powers and registers the transport, while suspend/resume hooks coordinate RMI driver suspend/resume with regulator disable/enable.

## Control Flow

Probe allocates transport state, copies platform data when present, checks I2C functionality, gets/enables `vdd` and `vio`, registers a cleanup action, reads optional `syna,startup-delay-ms`, initializes the page mutex and transport ops, forces page zero, and calls `rmi_register_transport_device()`. Reads and writes lock the page mutex, switch pages when needed, then issue native I2C transfers. System and runtime suspend call into the RMI driver then disable regulators; resume enables regulators, waits startup delay, and resumes the RMI driver.

## State and Persistence Behavior

The transport persists the current RMI page and a growable devm-managed TX buffer. Regulator enablement is runtime power state. The registered `rmi_transport_dev` persists until devm cleanup unregisters it.

## Dependencies and Integration Points

The file depends on I2C core, regulator framework, OF matching, RMI core transport registration, and PM helper macros. It supplies the `read_block` and `write_block` backend used by all RMI functions over I2C.

## Risks and Edge Cases

Every read/write depends on correct page tracking under `page_mutex`. Large writes reallocate the TX buffer and use devm allocation/free during runtime operations. Suspend warning messages say "resume" in some error paths. Runtime suspend returns zero even if `rmi_driver_suspend()` fails, after disabling regulators. Devices without both regulators must rely on regulator framework dummy supplies or fail probe.

## Test Signals

Tests should include page-crossing reads/writes, large write buffer growth, regulator failure and cleanup, startup delay behavior, system and runtime PM, OF and platform-data probe paths, I2C short transfer error handling, and full RMI enumeration over I2C.
