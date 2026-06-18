# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-i2c.c

Purpose: implements the I2C transport and interrupt handling for Si470x FM radio receivers, wiring the common Si470x V4L2 logic to raw I2C register transfers and GPIO reset.

Important APIs and functions: I2C lifecycle is `si470x_i2c_probe`, `si470x_i2c_remove`, and optional PM suspend/resume. Register callbacks are `si470x_get_register`, `si470x_set_register`, and `si470x_get_all_registers`. File callbacks are `si470x_fops_open` and `si470x_fops_release`. Interrupt processing is `si470x_i2c_interrupt`.

Control flow: probe allocates managed state, initializes callbacks, registers V4L2 and controls, copies the common video template, optionally asserts reset GPIO, powers up the chip, reads all registers and firmware version, sets an initial 87.5 MHz frequency, allocates an RDS buffer, requests a threaded falling-edge IRQ, registers the video device, and stores client data. Opening the first handle starts the common radio path and enables RDS/STC interrupt bits/GPIO2 interrupt output. The IRQ reads `STATUSRSSI`, completes tune/seek waiters on STC, checks RDS enable and readiness, reads the RDS register window, converts four RDS blocks to 3-byte V4L2 block records with error flags, updates the circular buffer, and wakes readers.

State and persistence: uses `struct si470x_device` with I2C client, reset GPIO, register cache, buffer indices, completion, mutex, and V4L2 objects. Device state is volatile; reset GPIO is driven low on remove.

Dependencies and integration points: depends on I2C block transfers, GPIO descriptor API, threaded IRQs, V4L2 core/controls, and exported common Si470x helpers. Device-tree matching supports `silabs,si470x`.

Risks: `devm_request_threaded_irq` is called even if `client->irq` is zero, which depends on board data providing a valid interrupt. `si470x_set_register` writes the full writable register window even when one register changes. Buffer producer updates are not locked against read-side consumers. Suspend only sets DISABLE and resume only ENABLEs without fully restoring common start configuration.

Test signals: probe with and without reset GPIO, firmware warning, valid/invalid IRQ board data, RDS interrupt block decoding and overflow, tune/seek completion via STC, suspend/resume retaining usability, remove lowering reset GPIO, and `v4l2-compliance`.
