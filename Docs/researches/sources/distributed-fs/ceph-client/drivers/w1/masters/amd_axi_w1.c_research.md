## sources/distributed-fs/ceph-client/drivers/w1/masters/amd_axi_w1.c

Purpose: this platform driver exposes the AMD AXI 1-Wire programmable logic IP core as a Linux 1-Wire bus master.

Important APIs/types/functions: `struct amd_axi_w1_local` stores MMIO base, IRQ, wait queue, atomic IRQ flag, and `struct w1_bus_master`. Bus callbacks are `amd_axi_w1_touch_bit()`, `amd_axi_w1_read_byte()`, `amd_axi_w1_write_byte()`, and `amd_axi_w1_reset_bus()`. Probe/remove are `amd_axi_w1_probe()` and `amd_axi_w1_remove()`, with interrupt handler `amd_axi_w1_irq()`.

Control flow: probe maps registers, obtains IRQ and clock, verifies the IP ID and major version, sets bus callbacks, resets the IP, and registers the w1 master. Each bus operation waits for READY, writes an instruction, asserts GO, waits for DONE via interrupt-enabled waits with timeout, reads data/status as needed, then clears GO. Reset also issues controller reset and checks the presence flag.

State and persistence behavior: runtime state is device-managed except the w1 master registration. The atomic flag records a pending IRQ and is cleared after waiters consume it. Hardware registers hold transient controller state.

Dependencies and integration points: depends on platform device resources, device tree compatible `amd,axi-1wire-host`, clock framework, MMIO, IRQs, and w1 core.

Risks: w1 callbacks cannot report rich errors, so timeout/interruption often returns inactive bus values. Busy loops rely on IRQ wakeups and 100 ms timeout. Version gating only accepts major version 1.

Test signals: probe with correct/incorrect IP ID and version, IRQ timeout paths, byte and bit transactions, reset/presence detection, clock enable failure, and w1 master unregister on remove.
