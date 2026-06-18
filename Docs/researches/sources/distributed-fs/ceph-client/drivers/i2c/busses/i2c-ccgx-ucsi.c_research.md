# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ccgx-ucsi.c

## Purpose
Small helper module that instantiates a Cypress CCGx UCSI Type-C controller as an I2C client on an existing adapter. It centralizes board-info construction for consumers that discover the controller indirectly.

## APIs, Control Flow, and State
The exported API is `i2c_new_ccgx_ucsi(struct i2c_adapter *adapter, int irq, const struct software_node *swnode)`. It creates a local `struct i2c_board_info`, sets `type` to `ccgx-ucsi`, address to `0x08`, propagates IRQ and software node, and calls `i2c_new_client_device()`. There is no persistent module-owned state beyond the created client owned by the I2C core/consumer.

## Dependencies and Integration
Depends on the I2C core, exported GPL symbol use, and the matching `i2c-ccgx-ucsi.h` declaration. Downstream integration is with the `ccgx-ucsi` client driver and platform-specific code that supplies an adapter, IRQ, and software node.

## Risks and Test Signals
Risks are fixed address/type drift, caller lifetime of `swnode`, duplicate client creation on the same adapter, and IRQ propagation mistakes. Test helper callers by confirming the `ccgx-ucsi` device probes at `0x08`, interrupt delivery works, software-node properties are visible, and duplicate/failed adapter cases unwind at the caller.
