# sources/distributed-fs/ceph-client/drivers/spmi/hisi-spmi-controller.c

## Purpose

`hisi-spmi-controller.c` implements the Hisilicon Kirin 970 / Hi3670 SPMI controller driver. It translates SPMI framework read/write opcodes into the controller's APB command, status, write-data, and read-data registers for a configured hardware channel.

## Important APIs, Types, And Functions

`struct spmi_controller_dev` stores the framework controller, parent device, MMIO base, spinlock, and selected channel. Register constants define per-channel and per-slave offsets, command fields, data-register layout, transaction-done and fail bits, timeout, and the maximum transfer size of 16 bytes.

Main functions are `spmi_controller_wait_for_done()`, `spmi_read_cmd()`, `spmi_write_cmd()`, and `spmi_controller_probe()`. Driver registration uses `spmi_controller_init()` at `postcore_initcall()` and `spmi_controller_exit()` at module exit. The OF match table binds `"hisilicon,kirin970-spmi-controller"`.

## Control Flow And State

Probe allocates a devres-managed SPMI controller with private driver data, maps the platform MMIO resource, reads the `hisilicon,spmi-channel` property, initializes the spinlock, installs `read_cmd` and `write_cmd`, and adds the controller through `devm_spmi_controller_add()`. Runtime transfers serialize through `spmi_controller->lock`.

Read commands validate byte count and opcode, map SPMI framework opcodes to controller command types, pack enable/type/length/slave/address into the command register, write it, poll the status register until `SPMI_APB_TRANS_DONE`, check `SPMI_APB_TRANS_FAIL`, then read up to four 32-bit data registers. Data words are converted from big-endian register order before copying into the caller buffer.

Write commands validate byte count and opcode, copy caller bytes into 32-bit chunks, write big-endian data words to write-data registers, issue the packed command, and poll for completion. Both read and write paths hold the spinlock across register programming and polling, so transactions on a controller channel are strictly serialized.

## State And Persistence Behavior

The selected channel and mapped base persist for the platform device lifetime. No state is stored outside driver memory and hardware registers. The hardware status is polled per transaction; there is no IRQ-driven completion path in this driver.

## Dependencies And Integration Points

The driver depends on platform resources, OF properties, MMIO accessors, spinlocks, delay polling, and the SPMI framework callbacks. It uses devres helpers from `spmi-devres.c` for controller lifetime management.

## Risks And Test Signals

Risks include byte-count edge cases because `(bc - 1)` is encoded without an explicit zero-length rejection, endian or partial-word copying mistakes, long spinlock hold time during polling, stale status bits if hardware requires explicit clearing not visible here, and incorrect channel selection from firmware. Useful tests are probing with missing MMIO or channel properties, read/write opcodes for normal/ext/ext-long accesses, 1/4/5/16-byte transfers, invalid SID/opcode/length handling, transaction-fail injection, timeout behavior, concurrent SPMI clients, and endianness checks against known PMIC registers.
