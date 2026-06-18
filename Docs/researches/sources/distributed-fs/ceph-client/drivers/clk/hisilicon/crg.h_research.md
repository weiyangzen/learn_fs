## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg.h

### Purpose
`crg.h` defines small shared data structures for Hisilicon clock-and-reset generator platform drivers.

### Important APIs, Types, And Functions
`struct hisi_crg_funcs` holds controller-specific `register_clks` and `unregister_clks` callbacks. `struct hisi_crg_dev` stores the registered clock data, reset controller, and selected function table.

### Control Flow
There is no executable code. CRG platform drivers fill these structures during probe and use them during remove/error unwinding.

### State, Persistence, And Dependencies
The header declares only pointers to clock and reset controller state. It depends on `struct platform_device` being visible via included users, though the header itself does not include a platform-device declaration.

### Integration Points
Hi3516CV300 and Hi3798CV200 CRG drivers use this as their common private-device shape.

### Risks
The callback contract assumes `register_clks()` returns either a valid `hisi_clock_data *` or `ERR_PTR`. A missing direct declaration for `struct platform_device` relies on include order in users.

### Test Signals
Build all CRG users with sparse/W=1, and test probe/remove error paths that exercise both callbacks.
