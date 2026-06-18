<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/lp.c -->
# sources/distributed-fs/ceph-client/drivers/char/lp.c

## Purpose
Implements the generic parallel printer character driver. It binds `/dev/lpN` devices to parport devices, supports write and optional IEEE-1284 readback, exposes legacy printer ioctls and timeout controls, optionally registers an lp console, and handles module/boot-time port selection.

## Important APIs, Types, and Functions
- Global `lp_table[LP_NO]` stores per-printer `struct lp_struct`; `port_num[]` tracks bindings.
- `lp_write()` claims the parport, negotiates ECP or compatibility mode, writes user data in `LP_BUFFER_SIZE` chunks, handles status errors, and yields on preemption.
- `lp_read()` under `CONFIG_PARPORT_1284` negotiates nibble mode and reads peripheral data.
- `lp_open()` validates device existence/busy state, handles abort-open status checks, allocates a buffer, and detects best mode.
- `lp_do_ioctl()`, `lp_ioctl()`, and `lp_compat_ioctl()` implement legacy ioctls and 32/64-bit timeout conversion.
- `lp_attach()`/`lp_detach()` bind/unbind parport devices; `lp_init()` registers char major, class, and parport driver.

## Control Flow
Module parameters or `lp=` boot arguments configure port binding. Initialization clears tables, registers major `LP_MAJOR`, class `printer`, and the parport driver. Parport attach selects a free or requested `lpN`, registers a parport device with preemption callback, optionally resets the printer, creates `/dev/lpN`, and maybe registers console. File I/O claims the parport lazily, negotiates mode, performs transfer, releases on preemption or close, and reports printer status.

## State and Persistence
Persistent driver state includes `lp_table`, flags such as `LP_EXIST`, `LP_BUSY`, `LP_ABORT`, `LP_ABORTOPEN`, `LP_CAREFUL`, current/best IEEE-1284 modes, waitqueues, timeout values, per-open buffer, and parport claimed/preempt bits. `lp_mutex` protects global open/ioctl state; each device has `port_mutex` for transfer and status operations.

## Dependencies and Integration Points
Depends on the parport subsystem, character device major `LP_MAJOR`, device class creation, legacy `linux/lp.h` ioctls, optional compat ioctl support, optional IEEE-1284 readback, and optional console support.

## Risks
This is legacy hardware code with unusual semantics: `O_NONBLOCK` is commandeered for `LP_ABORTOPEN`, status bits can stall writes unless abort flags are set, console output can block depending on `CONSOLE_LP_STRICT`, and detach notes that richer cleanup is deferred. Timeout conversion must guard overflow and compat ABI differences.

## Test Signals
Test port selection modes (`auto`, `none`, explicit), open busy/existence/error paths, ECP fallback to compatibility, write partial/error/nonblock/signal paths, IEEE-1284 readback when enabled, all ioctls including timeout old/new and compat forms, parport preemption release, detach cleanup, and optional console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/lp.c -->
