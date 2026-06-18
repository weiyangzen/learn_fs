<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tpic2810.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tpic2810.c

Purpose: exposes the TI TPIC2810 8-bit LED driver as an output-only GPIO expander over I2C.

Important APIs, types, and functions: `struct tpic2810` stores the gpiochip, I2C client, cached output byte, and mutex. GPIO callbacks are output-only get_direction, direction_output, set, and set_multiple. `tpic2810_set_mask_bits()` performs the cached read-modify-write and SMBus write using command `TPIC2810_WS_COMMAND`.

Control flow: I2C probe allocates state, copies a template 8-line output gpiochip, sets the parent and client, initializes the mutex, and registers the gpiochip. Single and multiple set paths update the cached byte under lock and write the whole output register; cache is updated only after a successful transfer.

State and persistence behavior: `buffer` is the driver's shadow of the output latch. It starts at zero, so the driver assumes initial low/off state until users set lines. Hardware output state may differ if boot firmware programmed it before probe.

Dependencies and integration points: depends on I2C SMBus byte-data writes, OF and I2C ID matching, gpiolib, and sleeping GPIO semantics.

Risks and test signals: there is no hardware readback and set returns success even if `tpic2810_set_mask_bits()` logs no error to caller, because it is void. Initial cache may clobber firmware output state on first write. Test single/multiple updates, I2C write failures preserving cache, output-only direction behavior, and probe via OF and I2C IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tpic2810.c -->
