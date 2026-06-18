<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.c

## Purpose
`smscoreapi.c` implements the shared Siano MDTV core used by bus-specific transports and higher-level clients such as `smsdvb-main.c`. It owns core device registration, hotplug notification, firmware and mode management, common DMA/buffer pools, client message routing, board setup hooks, IR startup, GPIO control, and module-global device/mode registries.

## Important APIs, Types, and Functions
The file defines private `smscore_device_notifyee_t`, `smscore_idlist_t`, `smscore_client_t`, and `smscore_registry_entry_t` objects around the public types from `smscoreapi.h`. Exported entry points include `smscore_register_device()`, `smscore_unregister_device()`, `smscore_start_device()`, `smscore_register_hotplug()`, `smscore_unregister_hotplug()`, `smscore_register_client()`, `smscore_unregister_client()`, `smsclient_sendrequest()`, `smscore_onresponse()`, `smscore_getbuffer()`, `smscore_putbuffer()`, `smscore_set_device_mode()`, `smscore_get_device_mode()`, `smscore_registry_getmode()`, board-id helpers, LED state, and old/new GPIO helpers.

Message support is centered on `smscore_translate_msg()`, the large `siano_msgs[]` table, `SMS_INIT_MSG()`, and completions embedded in `struct smscore_device_t`. Firmware mode lookup uses `smscore_fw_lkup`, `smscore_get_fw_filename()`, `smscore_load_firmware_from_file()`, and `smscore_load_firmware_family2()`.

## Control Flow
Transport drivers call `smscore_register_device()` with `smsdevice_params_t`; this allocates a `smscore_device_t`, initializes lists, locks, completions, and waitqueues, allocates either `kzalloc()` USB buffers or DMA-coherent buffers, wraps them in `smscore_buffer_t`, stores transport callbacks, records the devpath/type in the registry, and puts the device on `g_smscore_devices`.

`smscore_start_device()` chooses the persisted/default mode, calls `smscore_set_device_mode()`, applies board MTU/crystal configuration, notifies registered hotplug callbacks under `g_smscore_deviceslock`, and initializes IR if the board advertises an IR port. DVB registration is reached through this hotplug path.

Mode setting detects the current firmware mode with `MSG_SMS_GET_VERSION_EX_REQ`, optionally loads firmware with request-firmware and download chunks, initializes the device with `MSG_SMS_INIT_DEVICE_REQ`, updates `coredev->mode`, and clears `SMS_DEVICE_NOT_READY`. Family 2 firmware download sends reload/data/validity/trigger or reload-exec messages and waits on completions handled by `smscore_onresponse()`.

Incoming transport data arrives as a `smscore_buffer_t` in `smscore_onresponse()`. The header at `cb->p + cb->offset` is used to find a registered client by message type and destination id. If no client handles the buffer, core control responses complete the relevant core completion, IR sample indications are forwarded to `sms_ir_event()`, known harmless indications are ignored, and the buffer is returned to the pool.

## State and Persistence Behavior
Global state includes hotplug notifyees, live devices, and a registry keyed by `devpath`. The registry persists selected mode and type across re-registration within the module lifetime. Per-device state includes current mode, supported mode bitmask, firmware version, board id, LED state, IR state, common buffer pool, waitqueue, and completion objects.

Buffers are pooled in `coredev->buffers`; `smscore_getbuffer()` waits until a descriptor is available, while `smscore_putbuffer()` wakes the waitqueue and returns it to the list. Client routing state is a per-client id/type list protected by `clientslock`.

## Dependencies and Integration Points
The code depends on Linux firmware loading, DMA mapping, completions, waitqueues, list/mutex/spinlock primitives, media-controller conditionals, `sms-cards` board helpers, and `smsir`. It is the central integration layer between bus transports, board database, IR rc-core setup, DVB clients, firmware files declared by `MODULE_FIRMWARE()`, and Siano firmware protocol message ids.

## Risks and Test Signals
High-risk paths are firmware download sequencing, timeout handling, and response routing. `smscore_gpio_get_level()` stores the response in a single `coredev->gpio_get_res`, and the source comment explicitly notes a race between concurrent callers. `smscore_putbuffer()` wakes before adding the buffer back to the list, which is unusual but protected by the wait condition. `sms_ir_exit()` is called during unregister even if IR may not have initialized, so rc-core null handling and config stubs matter.

Useful test signals include successful firmware request and mode transition logs, hotplug callback registration/removal under module load/unload, DVB adapter creation after `smscore_start_device()`, completion of version/init/download requests within `SMS_PROTOCOL_MAX_RAOUNDTRIP_MS`, balanced buffer counts during unregister, and no duplicate client id/type registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.c -->
