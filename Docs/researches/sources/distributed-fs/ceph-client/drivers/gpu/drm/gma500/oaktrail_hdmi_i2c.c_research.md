# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi_i2c.c

## Purpose
This file provides the Oaktrail HDMI controller’s hardware I2C/DDC adapter. It configures GPIO muxing for HDMI I2C, registers fixed-number adapter 3, drives EDID read transactions through HDMI registers, and services controller interrupts for read-buffer-full and transaction-done events.

## Important APIs, Types, and Functions
The exported APIs are `oaktrail_hdmi_i2c_init()` and `oaktrail_hdmi_i2c_exit()`. `struct hdmi_i2c_dev` stores the adapter pointer, mutex, completion, status, active message, and buffer offset. Transfer logic is in `oaktrail_hdmi_i2c_access()`, `xfer_read()`, `xfer_write()`, `hdmi_i2c_read()`, `hdmi_i2c_transaction_done()`, and `oaktrail_hdmi_i2c_handler()`.

## Control Flow
Init allocates `hdmi_i2c_dev`, binds a static `i2c_adapter` to the HDMI device, configures GPIO pins 52/53 to alternate function 2, requests the HDMI IRQ, and registers adapter number 3. Transfers take a mutex, enable the I2C unit and IRQs, run each message as read or no-op write, then disable IRQs. Reads program `HDMI_HI2CHCR`; the interrupt handler copies 64-byte chunks from read buffer registers and clears/continues transactions until done.

## State and Persistence Behavior
State persists in `hdmi_dev->i2c_dev` and the static numbered adapter. Each transfer stores the current `i2c_msg`, buffer offset, and status until completion. The driver uses completions for IRQ wakeup but does not keep EDID data after the caller’s buffer is filled. Exit deletes the adapter, frees state, and releases the shared IRQ.

## Dependencies and Integration Points
This integrates with `oaktrail_hdmi_setup()` and the HDMI connector’s EDID path. It depends on PCI driver data pointing to `oaktrail_hdmi_dev`, Linux I2C core, IRQ handling, HDMI MMIO registers, and hardcoded GPIO controller MMIO for pin muxing.

## Risks
`xfer_read()` waits in a loop without checking the timeout return or signal interruption, so a failed interrupt can spin in repeated timed waits. `hdmi_i2c_read()` always copies 64 bytes per full interrupt and can overrun a short message buffer if hardware delivers more than requested. Writes are stubbed out. The static adapter with fixed `.nr = 3` can conflict if another adapter already owns that number.

## Test Signals
Signals include successful GPIO mux write, IRQ request, numbered adapter registration, EDID reads without buffer corruption, interrupt status clearing for FULL/DONE/HPD, clean adapter/IRQ removal, and no hangs when a display is disconnected or the HDMI controller fails to signal completion.
