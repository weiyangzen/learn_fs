<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max732x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max732x.c

## Purpose
`gpio-max732x.c` supports Maxim MAX7319/MAX7320-7327 I2C port expanders with differing combinations of push-pull outputs, inputs, open-drain I/O, and optional interrupt support.

## Important APIs, types, and functions
`max732x_features[]` encodes per-model port layout and interrupt capability. `struct max732x_chip` stores clients for group A/B I2C addresses, direction masks, output shadows, locks, and optional IRQ state. GPIO callbacks implement get, set, set_multiple, direction input/output. Optional IRQ helpers support mask/unmask, type, wake, pending calculation, and threaded handling.

## Control flow
Probe obtains platform/OF pdata, derives port layout from device ID, creates a dummy I2C client for the second group when needed, initializes output shadows by reading hardware, sets up optional IRQ support if compiled and wired, and registers the gpiochip. Port operations choose group A or B based on masks and update shadow registers before writing. IRQ pending reads two bytes from group A, computes changed bits against configured rising/falling triggers, and handles nested child IRQs.

## State and persistence behavior
`reg_out[2]` shadows output bytes and is the basis for set_multiple and masked updates. Direction capability masks are static per chip model. Optional IRQ masks and trigger bitmaps are cached in software and synced to hardware mask schemes that differ by model.

## Dependencies and integration points
The driver binds to I2C IDs and OF compatibles for MAX7319/MAX7320-7327, uses optional platform data for base, optional threaded parent IRQ, and gpiolib nested IRQ support.

## Risks and edge cases
The OF helper only supplies gpio base, so richer platform settings are unavailable in DT. Some models have no interrupt mask or merged masks, making IRQ behavior model-specific. Address group handling depends on the client's high address bits and can fail if board data uses the wrong address.

## Test signals
Test every model's port count/direction masks, group A/B dummy-client creation, get/set/set_multiple, open-drain input-as-high behavior, IRQ edge type rejection/acceptance, mask sync for independent/merged/no-mask models, and wake propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max732x.c -->
