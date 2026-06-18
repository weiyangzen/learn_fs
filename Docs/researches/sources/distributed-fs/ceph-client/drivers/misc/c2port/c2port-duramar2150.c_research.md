# sources/distributed-fs/ceph-client/drivers/misc/c2port/c2port-duramar2150.c

## Purpose
`c2port-duramar2150.c` is the board-specific Silicon Labs C2 backend for the Eurotech Duramar 2150. It bit-bangs C2D and C2CK through legacy I/O ports and registers one C2 device with the generic core.

## Important APIs, Types, and Functions
The backend implements `struct c2port_ops`: `duramar2150_c2port_access()`, `duramar2150_c2port_c2d_dir()`, `duramar2150_c2port_c2d_get()`, `duramar2150_c2port_c2d_set()`, and `duramar2150_c2port_c2ck_set()`. Module entry/exit are `duramar2150_c2port_init()` and `duramar2150_c2port_exit()`. The board advertises 30 flash blocks of 512 bytes.

## Control Flow
Module init reserves I/O ports `0x325..0x326`, then calls `c2port_device_register("uc", &duramar2150_c2port_ops, NULL)`. Core sysfs operations later call the ops while bit-banging C2 transactions. Exit sets both lines to input/high impedance through `access(..., 0)`, unregisters the device, and releases the I/O region.

## State and Persistence
Global state is `duramar2150_c2port_dev` and `update_lock`, which serializes read-modify-write updates to the data and direction ports. Hardware line state persists on the board until changed, but the driver tries to leave lines as inputs on unload.

## Dependencies and Integration Points
The file depends on x86-style `inb()`/`outb()`, `request_region()`, `linux/c2port.h`, and the C2 core exported registration API. It integrates directly with fixed board I/O-port wiring.

## Risks and Edge Cases
The fixed I/O port addresses are board-specific and unsafe on the wrong platform. `c2d_get()` reads without `update_lock`, so concurrent line updates can race with reads. Init failure after registration is handled, but no hardware identity is verified before exposing flash programming sysfs.

## Test Signals
Tests should verify region conflict returns `-EBUSY`, registration failure releases the region, unload leaves direction bits as input, and C2 core read/write/reset sysfs operations produce expected C2D/C2CK transitions on the board.
