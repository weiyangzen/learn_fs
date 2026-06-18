# sources/distributed-fs/ceph-client/drivers/firmware/raspberrypi.c

## Purpose
`raspberrypi.c` implements the Raspberry Pi firmware property-channel driver. It provides synchronous mailbox transactions to VPU firmware, exports property-list helpers to other drivers, registers legacy hwmon/clock platform devices, and manages shared firmware handles by reference count.

## Important APIs, Types, And Functions
- `struct rpi_firmware` stores mailbox client/channel, transaction completion, and `kref` consumers.
- Mailbox helpers: `response_callback()` and `rpi_firmware_transaction()`.
- Exported property APIs: `rpi_firmware_property_list()` and `rpi_firmware_property()`.
- Clock helper: `rpi_firmware_clk_get_max_rate()`.
- Handle APIs: `rpi_firmware_find_node()`, `rpi_firmware_get()`, `rpi_firmware_put()`, and `devm_rpi_firmware_get()`.
- Driver lifecycle: `rpi_firmware_probe()`, `rpi_firmware_shutdown()`, and `rpi_firmware_remove()`.

## Control Flow
Probe allocates non-devm firmware state, configures a blocking mailbox client with callback completion, requests channel 0, initializes completion and reference count, stores driver data, prints firmware revision, and registers child hwmon/clock devices if supported/needed. Property calls allocate coherent DMA memory, build the firmware property buffer header and terminator, issue a mailbox transaction on channel 8, enforce memory barriers around firmware access, copy tag data back, validate firmware status, and free the DMA buffer.

Consumers find the firmware DT node, obtain the platform device, get the driver data, increment the kref unless zero, and later release with `rpi_firmware_put()`. Shutdown sends a reboot notification property.

## State And Persistence
Firmware handle state persists until the platform device and all consumers release references. The transaction lock serializes mailbox property access globally. Firmware properties can read and change persistent or hardware state in the VPU firmware, but the driver itself caches only handle/channel state and global child platform-device pointers.

## Dependencies And Integration Points
The driver depends on the BCM2835 mailbox framework, coherent DMA, OF platform devices, Raspberry Pi firmware tag definitions, kref lifetime management, hwmon and clock child drivers, and platform shutdown callbacks.

## Risks
Mailbox transactions have a one-second timeout; stuck firmware yields warnings and failed property calls. The transaction buffer must be 32-bit aligned and below the firmware's practical size limit. `rpi_firmware_property()` copies back tag data even when the underlying call fails, so callers should heed return codes. Global child pointers assume a single firmware device. Passing `NULL` tag data with zero size is valid but must not be dereferenced by callers.

## Test Signals
Probe should log the firmware revision date and create child platform devices when supported. Property reads such as `GET_FIRMWARE_REVISION`, `GET_THROTTLED`, and clock-rate queries validate transactions. Shutdown should send `RPI_FIRMWARE_NOTIFY_REBOOT`. Timeout warnings or firmware status errors identify mailbox or firmware issues.
