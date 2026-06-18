# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_core.c

## Purpose

`mtu3_core.c` is the hardware access and gadget-device initialization layer for MTU3. It powers and resets the device IP, initializes FIFOs, endpoints, QMU, interrupts, speed/link behavior, and exposes `ssusb_gadget_init/exit/suspend/resume()` to platform and dual-role code.

## Important APIs, Types, and Functions

Important functions include FIFO alloc/free (`ep_fifo_alloc()`, `ep_fifo_free()`), device power and port control (`mtu3_device_enable()`, `mtu3_device_disable()`, `mtu3_dev_power_on()`, `mtu3_dev_power_down()`), interrupt control (`mtu3_intr_enable()`, `mtu3_intr_disable()`), endpoint setup (`mtu3_config_ep()`, `mtu3_deconfig_ep()`, `mtu3_ep_stall_set()`), device lifecycle (`mtu3_start()`, `mtu3_stop()`), memory setup (`mtu3_mem_alloc()`), ISR dispatch (`mtu3_irq()`), and public gadget glue (`ssusb_gadget_init()`, `ssusb_gadget_suspend()`, `ssusb_gadget_resume()`).

## Control Flow

Gadget init allocates `struct mtu3`, obtains the device IRQ and MAC MMIO, links it to `ssusb_mtk`, initializes hardware, sets the DMA mask, registers a threaded IRQ, stops the device for power saving, registers the UDC, and initializes debugfs. Hardware init reads IP version and capabilities, clamps max speed, resets and enables device mode, allocates endpoint arrays and QMU resources, and initializes registers. Runtime interrupts read level-1 status under `mtu->lock` and dispatch link speed changes, U2 common events, U3 LTSSM events, EP0, and QMU interrupts. Start powers on, configures CSR/speed, enables interrupts, and applies pending softconnect; stop reverses this.

## State and Persistence Behavior

State is held in `struct mtu3`: endpoint arrays, FIFO bitmaps, QMU pool, speed, active flags, connection status, hardware version, Gen2 compatibility, and wake/suspend flags. Hardware register state is reinitialized after reset and start. There is no nonvolatile persistence.

## Dependencies and Integration Points

The file depends on platform resources, DMA mask APIs, runtime PM, IRQ registration, QMU helpers, gadget core setup/cleanup, debugfs helpers, tracepoints, and IPPC/MAC register definitions. It is called from `mtu3_plat.c` and cooperates with `mtu3_gadget.c`, `mtu3_gadget_ep0.c`, `mtu3_qmu.c`, and `mtu3_dr.c`.

## Risks and Test Signals

Risks include FIFO bitmap exhaustion, hardware clock polling failures, incorrect max-speed downgrade when U3 port0 is disabled, IRQ handling while stopped, runtime PM imbalance on connect/disconnect speed changes, and error unwinding after IRQ or UDC registration failures. Test signals include probe on U2-only and U3-capable IP, speed-change interrupts for FS/HS/SS/SSP, endpoint config for bulk/int/isoc, QMU error interrupt handling, gadget suspend rejection while connected, and clean remove after partial init failures.
