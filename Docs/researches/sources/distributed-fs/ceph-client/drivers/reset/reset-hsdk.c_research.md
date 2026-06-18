# sources/distributed-fs/ceph-client/drivers/reset/reset-hsdk.c

Purpose: Synopsys HSDK SDP reset driver that selects an IP reset and triggers a software reset operation.

Important APIs/types/functions: `struct hsdk_rst`, `rst_map[]`, `hsdk_reset_config()`, `hsdk_reset_do()`, `hsdk_reset_reset()`, and `hsdk_reset_probe()`.

Control flow: probe maps control and reset resources, initializes a lock, and registers reset lines for entries in `rst_map`. Reset writes the selected IP mask to the control register, sets the reset trigger bit with delay fields, and polls until hardware clears the trigger bit.

State and persistence: no cached reset state; hardware reset controller executes pulses. Spinlock serializes selecting an IP and triggering reset.

Dependencies and integration: built-in platform driver for `snps,hsdk-reset`, MMIO, atomic polling, reset framework.

Risks and test signals: `.deassert` aliases `.reset`, which is unusual for consumers expecting level semantics. Test poll timeout, each `rst_map` entry, and client behavior that uses deassert instead of reset.
