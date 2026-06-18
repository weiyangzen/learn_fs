# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ibm_iic.c

Purpose: IBM PPC 4xx IIC controller driver. It handles OF platform discovery, interrupt or polling completion, hardware byte transfers in up-to-four-byte chunks, 7/10-bit addressing, software reset/bus recovery, and SMBus Quick emulation through direct-control bit banging.

Important APIs/types/functions: driver-private state comes from `struct ibm_iic_private` in `i2c-ibm_iic.h`. Key functions are `iic_dev_init()`, `iic_dev_reset()`, `iic_smbus_quick()`, `iic_handler()`, `iic_wait_for_tc()`, `iic_xfer_result()`, `iic_abort_xfer()`, `iic_xfer_bytes()`, `iic_address()`, `iic_xfer()`, `iic_clckdiv()`, `iic_request_irq()`, `iic_probe()`, and `iic_remove()`.

Control flow: probe maps OF MMIO, optionally requests IRQ unless forced polling, chooses fast mode from module parameter or OF property, reads OPB clock frequency, computes divider, initializes registers, and registers an HWMON-class adapter. Transfers validate that all messages share the same address and have nonzero length except SMBus Quick, reset a stuck bus, load the target address, then process each message in chunks of up to four bytes. Completion waits on IRQ wakeups or polling, then checks transfer counts and hardware error bits.

State and persistence: persistent state includes mapped register pointer, waitqueue, adapter, IRQ number, fast-mode flag, and clock divider. Hardware state includes local/remote addresses, mode control, interrupt mask, transfer count, direct-control lines, and status registers. Reset toggles `XTCNTLSS_SRST`, tries to regain bus control by toggling SCL, then reinitializes.

Dependencies and integration: depends on OF address/IRQ APIs, PowerPC `in_8/out_8`, Linux I2C core, waitqueues, module parameters, and the register definitions in `i2c-ibm_iic.h`.

Risks: all messages in a transfer must share address mode/address, which limits arbitrary combined transfers. SMBus Quick bypasses the hardware engine and depends on timing tables and direct-control line ownership. IRQ request failure silently falls back to polling. Error recovery may soft-reset the controller, potentially affecting an in-progress bus peer. Clock divider uses compatibility fallback for missing OPB frequency.

Test signals: standard and fast mode probing, IRQ and forced-poll transfers, 7-bit and 10-bit addressing, chunked reads/writes larger than four bytes, SMBus Quick ACK/NACK behavior, stuck bus recovery, interrupted waits, and remove cleanup.
