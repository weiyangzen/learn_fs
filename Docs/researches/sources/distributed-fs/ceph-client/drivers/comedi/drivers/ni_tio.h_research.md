## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_tio.h

### Purpose
`ni_tio.h` is the public header for the NI general-purpose counter support layer. It defines the register namespace, hardware variant enum, core counter/device state structures, and exported APIs consumed by NI Comedi board drivers.

### Important APIs, Types, And Functions
Important definitions are `enum ni_gpct_register`, `enum ni_gpct_variant`, `struct ni_gpct`, and `struct ni_gpct_device`. `struct ni_gpct_device` holds board callback hooks `write` and `read`, the variant, counter array, register cache, `regs_lock`, and route tables. Public functions include constructor/destructor helpers, counter initialization, Comedi instruction callbacks, command/cancel/interrupt helpers, MITE channel binding, interrupt acknowledge, and route get/set/unset helpers.

### Control Flow, State, And Persistence
The header does not execute logic, but it defines the persistent shape used by `ni_tio.c` and `ni_tiocmd.c`. The software register cache is stored as `[num_chips][NITIO_NUM_REGS]` and protected by `regs_lock`; each counter stores its MITE DMA channel pointer under its own lock. Callers create a `ni_gpct_device`, initialize counters, attach individual `struct ni_gpct` instances to Comedi subdevices, and then reuse the function table for synchronous instructions or asynchronous commands.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `linux/comedi/comedidev.h` and forward declarations from NI routing/MITE users. Integration is through exported symbols in `ni_tio.c` and `ni_tiocmd.c`. Risks are ABI-style coupling: register enum ordering is assumed by cache arrays and register-index macros, and callback users must honor the locking/cache model. Test signals include building all NI counter consumers, constructing devices with different counter counts/chip groupings, and verifying command-capable drivers can bind `mite_channel` without including private internals.
