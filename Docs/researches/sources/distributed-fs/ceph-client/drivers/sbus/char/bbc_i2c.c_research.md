# sources/distributed-fs/ceph-client/drivers/sbus/char/bbc_i2c.c

Purpose: provides a custom low-level I2C controller driver for UltraSPARC-III BBC devices and hosts the BBC environmental-control client code. It exposes blocking byte/buffer operations for child devices and probes OF children on each BBC I2C bus.

Important APIs/types/functions: exported client helpers are `bbc_i2c_getdev()`, `bbc_i2c_attach()`, `bbc_i2c_detach()`, `bbc_i2c_writeb()`, `bbc_i2c_readb()`, `bbc_i2c_write_buf()`, and `bbc_i2c_read_buf()`. Internal helpers include `wait_for_pin()`, `bbc_i2c_interrupt()`, `reset_one_i2c()`, `attach_one_i2c()`, and platform driver probe/remove. `struct bbc_i2c_bus` and `struct bbc_i2c_client` are declared in the header.

Control flow: probe maps the controller registers, optionally maps the bus-select register, requests a shared IRQ, records up to eight OF child platform devices, saves controller owner/clock bytes, resets the controller, and calls `bbc_envctrl_init()`. Client attach reads the child's `reg` property into bus/address and marks the child claimed. Reads and writes select a bus if needed, issue PCF-style START/STOP/control bytes, wait for the PIN interrupt/status transition, and transfer one register byte; buffer helpers loop bytewise.

State and persistence: each bus stores mapped MMIO pointers, original owner/clock settings, waitqueue state, child slots and claimed flags, and environmental-control lists. Hardware state is the I2C controller control/data registers plus optional bus selector. State is volatile and removed on driver detach.

Dependencies and integration: depends on OF platform devices, SPARC BBC/IO helpers, IRQs from `op->archdata.irqs`, exported symbols consumed by `bbc_envctrl.c`, and the platform compatible `SUNW,bbc-i2c`.

Risks and test signals: the driver explicitly does not use the Linux I2C core, so locking and transfer semantics are local. The bus `lock` is initialized but not used around transfers, which is risky if multiple clients issue I2C transactions concurrently. Probe failure and remove paths appear to swap resource indices in some `of_iounmap()` calls when both control and bus-select mappings exist. `wait_for_pin()` can spend many seconds retrying and returns a generic failure. Test probe with one/two resources, IRQ wakeup and timeout paths, concurrent client read/write access, child `reg` parsing, transfer NACK handling, cleanup after `bbc_envctrl_init()` failure, and module unload with active environment clients.
