# Research: subset-b-005396 Greybus staging drivers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/camera.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/camera.c

## Purpose
Implements the Greybus camera management driver for camera-class bundles. It exposes module camera operations through `gb_camera_module`, translates host camera requests into Greybus camera protocol messages, and manages a separate offloaded camera data CPort and AP CSI transmitter when streams are configured.

## Important APIs, Types, And Functions
Key state is `struct gb_camera`, holding management and data `gb_connection` objects, the module bundle, data CPort ID, a mutex, configured/unconfigured state, debugfs buffers, and registered `gb_camera_module`. Format translation is table-driven by `gb_camera_fmt_info`. Main protocol helpers are `gb_camera_capabilities()`, `gb_camera_configure_streams()`, `gb_camera_capture()`, and `gb_camera_flush()`. `gb_cam_ops` adapts those helpers to the host-facing camera-module API. `gb_camera_setup_data_connection()` creates the offloaded CSI data path and configures AP CSI output through `gb_hd_output()`.

## Control Flow
`gb_camera_probe()` requires exactly two CPorts, one camera management and one camera data, creates the management connection with `gb_camera_request_handler()`, initializes debugfs, registers the camera module, and drops the runtime-PM reference. Configuration sends `GB_CAMERA_TYPE_CONFIGURE_STREAMS`, validates returned padding and stream count, tears down any prior data connection, and either returns adjusted/test-only results or creates the data connection, switches UniPro links to high speed, programs CSI, and marks the device configured. Disconnect unregisters the module and destroys both connections.

## State And Persistence
State is in-memory only. The configured state pins runtime PM with an extra no-resume reference until streams are unconfigured. Debugfs keeps last operation outputs in per-operation page-sized buffers. CSI clock, lane count, data connection state, and power mode are reconstructed each configuration cycle.

## Dependencies And Integration Points
Depends on Greybus core, AP bridge output requests, Greybus SVC power-mode control, V4L2 media-bus pixel codes, debugfs, and the external camera-module registry declared in `gb-camera.h`. It integrates with runtime PM at the Greybus bundle level.

## Risks
Hard-coded ES2/AP CSI assumptions and fixed four-lane CSI setup limit portability. Response copy in `gb_camera_operation_sync_flags()` trusts the allocated response buffer sizing discipline. Debugfs operations can drive real protocol state and should stay restricted to debugging. Correct runtime-PM balance is critical around configured streams and error unwinds.

## Test Signals
Probe should reject malformed CPort layouts. Exercise capabilities, test-only configure, adjusted configure, real configure/unconfigure, capture, flush, metadata events, suspend/resume with and without a data connection, and all data-connection error unwind paths. Debugfs read/write operations provide manual smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/camera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/firmware.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/firmware.h

## Purpose
Shared private header for the Greybus firmware bundle implementation. It centralizes firmware naming constants and cross-file entry points for firmware management, firmware download, component authentication, and optional SPI support through the core firmware bundle driver.

## Important APIs, Types, And Functions
Defines `FW_NAME_PREFIX` and `FW_NAME_SIZE`, used by firmware download to construct deterministic firmware filenames. Declares `fw_mgmt_init()/fw_mgmt_exit()`, `gb_fw_mgmt_request_handler()`, `gb_fw_mgmt_connection_init()/exit()`, `gb_fw_download_request_handler()`, `gb_fw_download_connection_init()/exit()`, and CAP equivalents. `to_fw_mgmt_connection()` exposes the management connection from a device.

## Control Flow
This header has no runtime control flow, but it defines the contract used by `fw-core.c` to initialize per-protocol connections after parsing bundle CPorts. Request handlers declared here are passed into `gb_connection_create()` for management and download protocols.

## State And Persistence
No state is stored here. The constants shape persistent user-visible firmware lookup names, using interface and product identifiers plus a short tag.

## Dependencies And Integration Points
Includes `<linux/greybus.h>` because all declared connection and operation types are Greybus core structures. It is included by `fw-core.c`, `fw-download.c`, and `fw-management.c`.

## Risks
`FW_NAME_SIZE` must remain synchronized with the formatting string in `fw-download.c`; an undersized constant would truncate firmware names. The header is an internal coupling point, so changing prototypes affects multiple protocol modules.

## Test Signals
Build coverage is the main signal. Firmware download tests should verify generated names fit exactly within `FW_NAME_SIZE`; firmware core tests should catch missing declarations or mismatched prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-core.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-core.c

## Purpose
Core Greybus firmware bundle driver. It binds firmware-management class bundles, parses their protocol CPorts, creates per-protocol connections, initializes optional firmware download, SPI, and authentication paths, and makes firmware management mandatory.

## Important APIs, Types, And Functions
`struct gb_fw_core` stores the download, management, SPI, and CAP connections. `to_fw_mgmt_connection()` returns the management connection from device driver data. `gb_fw_core_probe()` and `gb_fw_core_disconnect()` are the Greybus driver lifecycle hooks. SPI setup is isolated in `gb_fw_spi_connection_init()` and `gb_fw_spi_connection_exit()`. Module init calls `fw_mgmt_init()`, `cap_init()`, and `greybus_register()`.

## Control Flow
Probe allocates `gb_fw_core`, walks all CPorts, rejects duplicate mandatory or optional protocol CPorts, creates connections for known protocols, and rejects unknown protocols. Firmware management must exist; download, SPI, and CAP are optional and are disabled if their init fails. Management init runs last; if it fails, the initialized optional connections are exited and every connection is destroyed.

## State And Persistence
State is per bundle and stored with `greybus_set_drvdata()`. No persistent data is written. Runtime PM is released on successful probe except for interfaces marked `GB_INTERFACE_QUIRK_NO_PM`, preserving compatibility with older S2 loader behavior.

## Dependencies And Integration Points
Integrates Greybus core with firmware management/download submodules, CAP authentication support, and `gb_spilib_master_init()` for SPI. Uses Greybus class matching through `GREYBUS_CLASS_FW_MANAGEMENT`.

## Risks
Optional connection failures are intentionally tolerated, so partial functionality is normal and callers must handle missing download/SPI/CAP paths. The duplicate CPort checks are important because connection pointers are singletons. Runtime-PM quirk behavior should not be removed until all loaders support PM.

## Test Signals
Probe matrices should cover missing management CPort, duplicate CPorts, unknown protocol IDs, optional init failures, management init failure after optional success, disconnect after partial setup, and `GB_INTERFACE_QUIRK_NO_PM` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-download.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-download.c

## Purpose
Implements the Greybus firmware download protocol. It lets a module ask the AP to find a firmware blob by tag, fetch byte ranges by firmware ID, and release the firmware when done.

## Important APIs, Types, And Functions
`struct fw_download` owns the connection, parent device, firmware request list, ID allocator, and mutex. `struct fw_request` tracks one firmware blob, firmware ID, name, `struct firmware`, timeout work, release deadline, kref, and timeout/disabled flags. Handlers are `fw_download_find_firmware()`, `fw_download_fetch_firmware()`, `fw_download_release_firmware()`, dispatched by `gb_fw_download_request_handler()`. Connection lifecycle is `gb_fw_download_connection_init()/exit()`.

## Control Flow
Find validates request size and tag termination, allocates ID 1-255, builds a `gmp_...tag.tftf` name from interface identifiers, calls `request_firmware()`, lists the request, computes a release deadline, starts delayed timeout work, and returns firmware ID and size. Fetch looks up the ID with a kref, cancels current timeout work, verifies not disabled and within total timeout, bounds-checks offset and size, allocates a response, copies bytes, and refreshes the short timeout. Release cancels timeout work, removes the request, drops references, and releases the firmware.

## State And Persistence
Firmware contents are held by Linux firmware loader references until released or timed out. IDs are reused only when a request completes normally; timed-out IDs are deliberately leaked from the allocator to avoid stale module requests referring to a later request.

## Dependencies And Integration Points
Uses Linux firmware loading, IDA, delayed work, kref, jiffies, and Greybus request/response allocation. It depends on `firmware.h` naming constants and is initialized by `fw-core.c`.

## Risks
After 255 timed-out requests no more IDs can be allocated by design. Timeout races are managed by list mutex plus krefs, so changes must preserve that model. Fetch response sizes are module-controlled and must remain bounded by firmware size and operation allocation limits.

## Test Signals
Test valid find/fetch/release, unterminated tags, missing firmware, bad offsets/sizes, fetch after timeout, release after timeout, connection exit with pending requests, ID reuse after normal release, and exhausted IDs after repeated timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-download.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-management.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-management.c

## Purpose
Firmware management protocol driver. It exposes a character-device ioctl API for userspace to query interface/backend firmware versions, load and validate interface firmware, update backend firmware, set operation timeout, and request interface mode switch.

## Important APIs, Types, And Functions
`struct fw_mgmt` holds the management connection, kref/list entry, request ID allocator, ioctl mutex, completion, char device, timeout, disabled/mode-switch flags, and pending/result fields for interface and backend firmware operations. Main operations include `fw_mgmt_interface_fw_version_operation()`, `fw_mgmt_load_and_validate_operation()`, `fw_mgmt_backend_fw_version_operation()`, and `fw_mgmt_backend_fw_update_operation()`. Unsolicited completions are handled by `fw_mgmt_interface_fw_loaded_operation()` and `fw_mgmt_backend_fw_updated_operation()`.

## Control Flow
Connection init allocates `fw_mgmt`, adds it to a global list, enables the Greybus connection, allocates a minor, registers a cdev, and creates a class device. Open finds the object by cdev under `list_mutex` and takes a kref. Ioctls are serialized by `fw_mgmt->mutex`, protected by runtime PM, and reject new operations when disabled or after mode switch starts. Load/update operations allocate request IDs, send Greybus commands, wait for completion, and copy results to userspace.

## State And Persistence
State is per management connection and lifetime-managed by kref. Pending request IDs and result fields persist across the request/completion wait. `mode_switch_started` permanently blocks further ioctls until disconnect. No on-disk state is written.

## Dependencies And Integration Points
Uses Greybus firmware management protocol messages, Linux cdev/class APIs, ioctl copy helpers, completions, IDA, krefs, runtime PM, and the user ABI in `greybus_firmware.h`. Mode switching calls `gb_interface_request_mode_switch()`.

## Risks
Completion reuse requires serialized ioctls; parallel operations would corrupt result fields. On timeout, request IDs are not explicitly reclaimed in this function, so subsequent completions and ID allocator behavior are sensitive areas. Disconnect must block new users, wait out active ioctls, disable the connection, and drop krefs in order.

## Test Signals
Cover every ioctl, invalid load methods, oversized/truncated firmware tags, timeout changes including zero rejection, unsolicited completion with wrong/no request ID, disconnect with open file descriptors, mode switch success/failure, and runtime-PM get failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-management.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gb-camera.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/gb-camera.h

## Purpose
Host-facing Greybus camera module API. It describes camera streams and CSI parameters and defines the operation callbacks used by the Greybus camera protocol driver to expose camera capabilities to another host camera component.

## Important APIs, Types, And Functions
Defines input/output flags `GB_CAMERA_IN_FLAG_TEST` and `GB_CAMERA_OUT_FLAG_ADJUSTED`. `struct gb_camera_stream` stores width, height, V4L2 media-bus pixel code, CSI virtual channel, data types, and frame size. `struct gb_camera_csi_params` stores lane count and clock frequency. `struct gb_camera_ops` declares capabilities, configure_streams, capture, and flush callbacks. `struct gb_camera_module` wraps private data, ops, interface ID, kref, release hook, and global list node. `gb_camera_call()` safely invokes callbacks.

## Control Flow
The header has no implementation flow. The expected lifecycle is that `camera.c` fills a `gb_camera_module`, registers it with `gb_camera_register()`, services callbacks through `gb_cam_ops`, and unregisters on disconnect.

## State And Persistence
No direct state. The struct layout defines in-memory registration and refcounting state for camera modules.

## Dependencies And Integration Points
Depends on `<linux/v4l2-mediabus.h>` for pixel codes and on Linux kref/list types through included kernel context. It bridges Greybus camera management to a host camera stack that consumes `gb_camera_module`.

## Risks
`gb_camera_call()` returns `-ENODEV` for a missing module and `-ENOIOCTLCMD` for a missing operation; callers must distinguish those. The API assumes callback implementers honor stream array bounds and update `nstreams`/flags consistently.

## Test Signals
Build users against callback signature changes. Exercise register/unregister lifetime, missing operation dispatch through `gb_camera_call()`, test-only stream configuration, adjusted stream outputs, and kref release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gb-camera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.c

## Purpose
Implements the Greybus Bridged-PHY bus. It converts a bridged-PHY Greybus bundle into one Linux child `gbphy_device` per CPort and lets protocol-specific `gbphy_driver` instances bind by CPort protocol ID.

## Important APIs, Types, And Functions
`struct gbphy_host` stores the parent bundle and child-device list. The global `gbphy_bus_type` provides match, probe, remove, and uevent callbacks. Exported APIs are `gb_gbphy_register_driver()` and `gb_gbphy_deregister_driver()`. Child creation and teardown are handled by `gb_gbphy_create_dev()`, `gb_gbphy_probe()`, and `gb_gbphy_disconnect()`.

## Control Flow
Module init registers the `gbphy` bus, then the Greybus bridged-PHY bundle driver. Bundle probe allocates a host object, saves it as bundle driver data, creates/registers a `gbphy_device` for each CPort, and drops runtime PM. Bus matching compares the CPort protocol ID against the driver's ID table. Bus probe resumes the parent bundle, enables runtime PM/autosuspend on the child, calls the child driver's probe, and unwinds PM if probe fails. Disconnect resumes the bundle, unregisters all child devices, and frees the host.

## State And Persistence
State is only in kernel device objects and the IDA-allocated gbphy IDs. Each child has a sysfs `protocol_id` attribute and uevent metadata describing bus, module, interface, bundle, and protocol.

## Dependencies And Integration Points
Integrates Greybus bundle discovery with Linux driver core bus/device mechanics and runtime PM. Child drivers in this subset include GPIO, I2C, and PWM. It depends on `gbphy.h` for public structs/macros.

## Risks
Parent/child runtime-PM balance is subtle: child drivers that support PM are expected to put their initial reference before returning from probe. Device registration failures must use `put_device()` so release frees the ID and object. Uevent field changes can affect module autoloading/userspace matching.

## Test Signals
Probe with zero and multiple CPorts, child registration failure mid-loop, driver match/no-match, child probe failure, disconnect while children are bound, sysfs protocol ID, uevent contents, and runtime-PM autosuspend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.h

## Purpose
Public interface for Greybus Bridged-PHY child drivers. It defines child-device and child-driver structures, registration helpers, and runtime-PM wrappers used by protocol drivers bound through the `gbphy` bus.

## Important APIs, Types, And Functions
`struct gbphy_device` stores ID, CPort descriptor, parent bundle, list node, and embedded `struct device`. `struct gbphy_device_id` matches by protocol ID. `struct gbphy_driver` provides name, probe/remove callbacks, ID table, and embedded `device_driver`. Macros include `GBPHY_PROTOCOL()`, `to_gbphy_dev()`, `to_gbphy_driver()`, and `module_gbphy_driver()`. PM wrappers are `gbphy_runtime_get_sync()`, `gbphy_runtime_put_autosuspend()`, `gbphy_runtime_get_noresume()`, and `gbphy_runtime_put_noidle()`.

## Control Flow
No standalone runtime flow. Child protocol modules declare a `gbphy_driver` and use `module_gbphy_driver()` to register it through `gb_gbphy_register_driver()`/`gb_gbphy_deregister_driver()`.

## State And Persistence
The header defines in-memory state only. Driver-private state is attached through `gb_gbphy_set_data()` and read by `gb_gbphy_get_data()`.

## Dependencies And Integration Points
Requires Greybus bundle/descriptor types from the including context and Linux device/runtime-PM APIs. Used by GPIO, I2C, PWM, and other bridged PHY protocol drivers.

## Risks
The PM wrappers compile to no-ops without `CONFIG_PM`, so drivers must not rely on them for non-PM synchronization. `gbphy_runtime_get_sync()` handles negative return by `pm_runtime_put_noidle()`; callers should not double-put on failure.

## Test Signals
Build both `CONFIG_PM=y` and `CONFIG_PM=n`. Exercise module registration macros, driver data helpers, PM wrapper failure paths, and protocol ID table matching through `gbphy.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gbphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/gpio.c

## Purpose
Greybus GPIO bridged-PHY child driver. It presents remote Greybus GPIO lines as a Linux `gpio_chip` with optional IRQ support.

## Important APIs, Types, And Functions
`struct gb_gpio_controller` holds the `gbphy_device`, connection, line count, line state array, `gpio_chip`, `irq_chip`, and IRQ mutex. `struct gb_gpio_line` caches active, direction, value, debounce, IRQ type, and pending mask/type changes. Greybus operation helpers cover line count, activate/deactivate, get/set direction, get/set value, debounce, IRQ mask/unmask/type. Linux callbacks include `gb_gpio_request()`, `gb_gpio_free()`, `gb_gpio_get_direction()`, `gb_gpio_direction_input/output()`, `gb_gpio_get/set()`, and `gb_gpio_set_config()`.

## Control Flow
Probe creates a connection with `gb_gpio_request_handler()`, enables TX only, queries line count, initializes irqchip/gpiochip callbacks, enables full RX/TX, registers the gpiochip, and releases the initial gbphy PM reference. Unsolicited `GB_GPIO_TYPE_IRQ_EVENT` requests validate payload and line number, find the mapped Linux IRQ, and call `generic_handle_irq_safe()`.

## State And Persistence
Line state is cached per line but authoritative state lives on the module. IRQ mask/type changes are staged in `gb_gpio_irq_mask()`, `gb_gpio_irq_unmask()`, and `gb_gpio_irq_set_type()`, then sent under `irq_lock` from `gb_gpio_irq_bus_sync_unlock()`. No persistent storage exists.

## Dependencies And Integration Points
Uses `gbphy` runtime PM, Greybus GPIO protocol, Linux GPIO/IRQ domain APIs, `gpiochip_add_data()`, and generic IRQ handling.

## Risks
Line indexes are cast to `u8`; correctness depends on remote line count fitting protocol limits. IRQ staging must remain synchronized with the irqchip bus lock/unlock contract. Remove disables RX before `gpiochip_remove()` to prevent events racing with teardown.

## Test Signals
Test line-count discovery, each GPIO operation, debounce bounds, IRQ type mapping for all Linux IRQ types, unsolicited bad payloads and invalid lines, remove during active IRQs, PM get failures, and gpiochip registration failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_authentication.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_authentication.h

## Purpose
User ABI header for Greybus Component Authentication Protocol ioctls. It defines certificate/authentication constants and packed ioctl payloads exchanged with the CAP character-device implementation.

## Important APIs, Types, And Functions
Defines certificate and signature maximum sizes, IMS certificate class constants, IMS certificate result codes, authentication type constants, and authentication result codes. User structs are `cap_ioc_get_endpoint_uid`, `cap_ioc_get_ims_certificate`, and `cap_ioc_authenticate`. Ioctls are `CAP_IOC_GET_ENDPOINT_UID`, `CAP_IOC_GET_IMS_CERTIFICATE`, and `CAP_IOC_AUTHENTICATE`.

## Control Flow
No executable flow. Userspace fills the packed structures and submits ioctls; the CAP driver is expected to populate result codes, certificate data, response data, and signatures.

## State And Persistence
No kernel state. This file freezes ABI sizes and field order, including fixed-size certificate and signature arrays embedded in ioctl payloads.

## Dependencies And Integration Points
Includes Linux ioctl and fixed-width type headers. It is part of the user/kernel ABI for the firmware authentication side of Greybus firmware support.

## Risks
Packed ABI structs cannot be changed without breaking userspace. Large embedded arrays make ioctl copies relatively heavy and require strict bounds checking in the implementation. Endianness expectations are implicit in fixed-width integer fields.

## Test Signals
ABI tests should validate ioctl numbers, struct sizes/offsets, max certificate/signature handling, invalid certificate/auth types, result-code propagation, and 32-bit/64-bit userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_authentication.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_firmware.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_firmware.h

## Purpose
User ABI header for Greybus firmware management ioctls. It defines userspace-visible firmware tag size, load methods, status codes, version status codes, packed ioctl payloads, and ioctl command numbers.

## Important APIs, Types, And Functions
Defines `GB_FIRMWARE_U_TAG_MAX_SIZE`, public load method constants, interface load status constants, backend firmware update status constants, and backend version status constants. Payload structs are `fw_mgmt_ioc_get_intf_version`, `fw_mgmt_ioc_get_backend_version`, `fw_mgmt_ioc_intf_load_and_validate`, and `fw_mgmt_ioc_backend_fw_update`. Ioctls include get interface firmware, get backend firmware, interface load/validate, backend update, set timeout, and mode switch.

## Control Flow
No executable flow. `fw-management.c` consumes these ioctl structs in its character-device unlocked ioctl path and maps them to Greybus management operations.

## State And Persistence
No runtime state. The packed struct layout is a persistent kernel/userspace ABI and must remain stable.

## Dependencies And Integration Points
Includes Linux ioctl and fixed-width type headers. It integrates directly with the `gb_fw_mgmt` class device created by firmware management connection init.

## Risks
Tag size is only 10 bytes and operations use padded copies; truncation must be rejected by implementation. ABI constants mirror Greybus protocol statuses but are user-facing, so renumbering is not safe.

## Test Signals
Check ioctl numbers and struct sizes, timeout ioctl with zero and nonzero values, tag truncation behavior, mode switch gating, backend status propagation, and compatibility builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/hid.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/hid.c

## Purpose
Greybus HID class driver. It binds HID-class Greybus bundles and presents the remote HID device through the Linux HID low-level driver interface.

## Important APIs, Types, And Functions
`struct gb_hid` stores bundle, connection, Linux `hid_device`, Greybus HID descriptor, flags, and input buffer. Protocol helpers fetch HID descriptor/report descriptor, set power, get report, and set report. `gb_hid_ll_driver` supplies HID callbacks: parse, start, stop, open, close, power, and raw_request. `gb_hid_request_handler()` receives input report IRQ events.

## Control Flow
Probe requires exactly one HID CPort, creates/enables the connection, allocates a HID device, reads the Greybus HID descriptor, initializes HID identity and low-level callbacks, adds the HID device, and drops runtime PM. HID parse fetches and parses the report descriptor. Start allocates a maximum report buffer and initializes reports unless quirked. Open powers on and marks started; close clears started and powers off. IRQ events feed input reports only while started.

## State And Persistence
State is in-memory: descriptor cache, started flag, buffer size/input buffer, and Linux HID device state. Power state is requested over Greybus and not persisted locally beyond flags.

## Dependencies And Integration Points
Uses Greybus HID protocol, Greybus runtime PM, Linux HID core, HID report parsing, and bundle class matching through `GREYBUS_CLASS_HID`.

## Risks
`gb_hid_request_handler()` assumes payload contains an input report and does not explicitly size-check beyond operation payload. `__gb_hid_output_raw_report()` currently returns `0` after set-report instead of the adjusted transfer length, which is a behavioral concern. Runtime PM wraps descriptor/report/power operations.

## Test Signals
Test descriptor size bounds, report descriptor parsing failure, report get/set paths, numbered and unnumbered reports, IRQ event before/after open, power transitions, disconnect while open, and raw_request return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/i2c.c

## Purpose
Greybus I2C bridged-PHY child driver. It exposes a remote Greybus I2C controller as a Linux `i2c_adapter`.

## Important APIs, Types, And Functions
`struct gb_i2c_device` holds the connection, gbphy device, functionality bits, and adapter. `gb_i2c_device_setup()` queries remote functionality. `gb_i2c_operation_create()` converts Linux `i2c_msg` arrays into one Greybus transfer operation with descriptors followed by outbound data. `gb_i2c_decode_response()` copies inbound data back to read messages. Adapter callbacks are `gb_i2c_master_xfer()` and `gb_i2c_functionality()`.

## Control Flow
Probe creates/enables the CPort connection, queries functionality, initializes adapter metadata and algorithm, registers the adapter, and releases the gbphy runtime-PM reference. Transfers allocate a Greybus operation sized for all message descriptors, write data, and read response data; runtime PM is held while the operation is sent. Expected transfer errors `-EAGAIN` and `-ENODEV` are not logged as hard errors.

## State And Persistence
Only functionality bits and adapter registration persist while the device is bound. Transfers are transient and do not cache remote bus state.

## Dependencies And Integration Points
Uses `gbphy`, Greybus I2C protocol, Linux I2C core, and runtime PM. The adapter is parented to the `gbphy_device`.

## Risks
Request/response sizes are derived from Linux message lengths; overflow and operation-size limits are important to preserve. The flag/functionality mapping currently assumes Greybus and Linux bit values match. Adapter removal must happen before disabling/destroying the connection.

## Test Signals
Test functionality query, mixed read/write transfers, zero-message and large-message boundaries, `msg_count > U16_MAX`, expected and unexpected transfer errors, adapter registration failure, and PM failure during transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/light.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/light.c

## Purpose
Greybus Lights protocol driver. It discovers remote lights/channels, registers Linux LED class devices, flash LED devices, and optional V4L2 flash subdevices, and applies brightness, blink, color, fade, flash intensity, strobe, timeout, and fault operations through Greybus.

## Important APIs, Types, And Functions
`struct gb_lights` owns the connection, light count, light array, and lock. `struct gb_light` tracks one light, channels, flash/V4L2 state, and readiness. `struct gb_channel` stores channel descriptors, LED/flash classdevs, attributes, settings, active/releasing state, and a mutex. Key paths include `gb_lights_create_all()`, `gb_lights_light_config()`, `gb_lights_channel_config()`, `gb_lights_register_all()`, brightness/blink/flash ops, and `gb_lights_request_handler()`.

## Control Flow
Probe validates a single lights CPort, enables TX only, queries light count and each light/channel descriptor, enables RX, registers LED devices, and drops runtime PM. Channel configuration builds LED names, sysfs attribute groups for color/fade, operation callbacks, and flash constraints. Flash channels may attach torch channels and register V4L2 flash devices. Unsolicited config events release, reconfigure, and re-register the affected light under `lights_lock`.

## State And Persistence
Remote configuration is mirrored in allocated light/channel objects. Active LED state affects runtime-PM references: brightness/blink paths retain a PM reference while a channel becomes active and release it when inactive. Attribute values such as color/fade and flash settings are cached in memory.

## Dependencies And Integration Points
Uses Greybus Lights protocol, Linux LED class, LED flash class, optional V4L2 flash LED class, sysfs device attributes, runtime PM, and Greybus bundle lifecycle.

## Risks
Registration is multi-stage and error unwinds must avoid double-freeing channel names, attributes, and classdevs. Runtime-PM reference handling around active lights is subtle. Dynamic reconfiguration events race with user LED operations unless `releasing`, LED locks, and `lights_lock` are respected.

## Test Signals
Test descriptor validation, zero lights/channels, normal LED channels, multicolor/fader attrs, blink, flash/torch/indicator combinations, V4L2 enabled/disabled builds, config events, disconnect during active LED, and all partial registration failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/light.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/log.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/log.c

## Purpose
Greybus Log protocol driver. It receives log strings from a module and emits them through dynamic debug on the bundle device.

## Important APIs, Types, And Functions
`struct gb_log` stores the connection. `gb_log_request_handler()` validates unsolicited `GB_LOG_TYPE_SEND_LOG` requests, checks length fields, bounds against `GB_LOG_MAX_LEN`, forces NUL termination, and logs with `dev_dbg()`. Probe/disconnect manage one connection.

## Control Flow
Probe requires one LOG CPort, allocates state, creates a connection with the request handler, enables it, and saves driver data. Incoming send-log requests are validated and printed. Disconnect disables and destroys the connection and frees state.

## State And Persistence
No persistent state beyond connection lifetime. Received log messages are not stored by the driver.

## Dependencies And Integration Points
Uses Greybus Log protocol, Greybus bundle matching by `GREYBUS_CLASS_LOG`, and Linux dynamic debug via `dev_dbg()`.

## Risks
The handler writes a terminator into the received payload buffer. Logs are intentionally debug-level to limit denial-of-service potential, but high-volume modules can still consume Greybus and CPU resources.

## Test Signals
Test probe CPort validation, wrong request type, too-small payload, mismatched length, zero length, oversized length, missing terminator, dynamic-debug enablement, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/loopback.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/loopback.c

## Purpose
Greybus loopback test/load driver. It exposes sysfs controls and debugfs latency output for generating ping, transfer, and sink loopback traffic synchronously or asynchronously over a Greybus connection.

## Important APIs, Types, And Functions
`struct gb_loopback` stores the connection, class device, debugfs file, latency FIFO, mutex, worker thread, wait queues, outstanding async count, statistics, test parameters, counters, timeouts, and latency tags. `gb_loopback_operation_sync()` and `gb_loopback_async_operation()` send operations. Type-specific helpers handle ping/transfer/sink. `gb_loopback_fn()` is the traffic-generating kthread. `gb_loopback_request_handler()` responds to loopback requests from the peer.

## Control Flow
Module init creates a debugfs root, class, and Greybus driver. Probe validates one loopback CPort, creates/enables the connection, creates a class device with sysfs attributes, allocates the latency FIFO, starts the worker thread, increments global device count, enables latency tags, and drops runtime PM. Writing sysfs attributes resets counters and wakes the worker when type is valid. The worker holds PM while active, sends configured operations until iteration limits, updates stats, and sleeps between sends if requested.

## State And Persistence
State is per connection and visible through sysfs: type, size, wait, iteration counts, async flag, timeout, outstanding max, errors, and computed min/max/avg stats. Debugfs exposes raw latency samples consumed from a FIFO. No on-disk state persists.

## Dependencies And Integration Points
Uses Greybus loopback protocol, operation latency tags, Linux kthreads, wait queues, atomics, kfifo, debugfs, sysfs class devices, runtime PM, and IDA.

## Risks
Complex async lifetime: callbacks own operation references and decrement outstanding counts while disconnect disables the connection and stops the thread. Sysfs parsing uses broad integer scans and clamps only some fields. Latency/stat arithmetic must guard divide-by-zero and wraparound.

## Test Signals
Exercise sync/async ping, transfer data verification, sink, iteration completion, infinite mode, outstanding throttling, timeout accounting, debugfs FIFO reads, sysfs clamping, remote loopback request handling, disconnect with in-flight async operations, and registration failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/loopback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/power_supply.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/power_supply.c

## Purpose
Greybus Power Supply protocol driver. It discovers remote power supplies, maps Greybus properties to Linux `power_supply` properties, registers power_supply devices, polls/caches property values, handles update events, and forwards writable property changes.

## Important APIs, Types, And Functions
`struct gb_power_supplies` owns the connection, supply count, supply array, and lock. `struct gb_power_supply` contains descriptor, registered `power_supply`, name, remote strings/type, property arrays, cache state, delayed work, PM-acquired flag, and lock. `struct gb_power_supply_prop` maps Linux and Greybus property IDs and caches values. Key functions include `get_psp_from_gb_prop()`, description/descriptor fetchers, property update/get/set paths, delayed work polling, registration/setup helpers, and `gb_supplies_request_handler()`.

## Control Flow
Probe validates one power-supply CPort, creates a connection with events, enables TX only, queries supply count and descriptors, enables RX, registers all power supplies, schedules immediate delayed work, and drops runtime PM. `get_property()` refreshes cached values if expired, then returns cached integer or string data. Events invalidate cache and force status update. Polling backs off from `update_interval_init` to `update_interval_max` unless a change resets the interval.

## State And Persistence
Properties are cached in memory for `cache_time` milliseconds unless invalidated. Manufacturer/model/serial strings are fetched once from descriptions. Charging status may hold a runtime-PM reference via `pm_acquired` to keep the module awake while charging.

## Dependencies And Integration Points
Uses Greybus Power Supply protocol, Linux power_supply core, delayed work, runtime PM, mutexes, and bundle class matching.

## Risks
Property mapping drops unsupported kernel properties and compacts arrays; allocation and count adjustments must stay consistent. `_gb_power_supply_property_get()` logs errors but returns 0, which can hide missing properties. Delayed work and event handling must stop cleanly during unregister via `update_interval = 0` and `cancel_delayed_work_sync()`.

## Test Signals
Test supply count zero, descriptor/property mapping including unsupported props, string properties, cache hit/expiry/invalidation, writable property set, polling backoff, change notification thresholds, charging PM reference balance, events during unregister, and partial setup/register failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/power_supply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/pwm.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/pwm.c

## Purpose
Greybus PWM bridged-PHY child driver. It exposes remote Greybus PWM channels as a Linux `pwm_chip`.

## Important APIs, Types, And Functions
`struct gb_pwm_chip` embeds the Linux `pwm_chip` private data and connection. Protocol helpers implement count, activate/deactivate, config, polarity, enable, and disable operations. Linux PWM callbacks are `gb_pwm_request()`, `gb_pwm_free()`, and `gb_pwm_apply()`, collected in `gb_pwm_ops`.

## Control Flow
Probe creates/enables the connection, queries the highest PWM ID and converts it to count, allocates a `pwm_chip`, stores it as gbphy data, registers it, and releases the gbphy PM reference. Request activates a PWM. Apply changes polarity with disable-if-needed, clamps 64-bit period/duty to Greybus 32-bit fields, configures duty/period, and enables if requested. Disable releases the runtime-PM reference held since enable.

## State And Persistence
Linux PWM core owns desired state; the driver does not maintain a separate channel cache. Runtime PM is held while a PWM is enabled and released on disable/deactivate.

## Dependencies And Integration Points
Uses `gbphy`, Greybus PWM protocol, Linux PWM core, and runtime PM. The chip parent is the `gbphy_device`.

## Risks
PM balance depends on `gb_pwm_enable_operation()` retaining a reference on success and `gb_pwm_disable_operation()` always putting it. If free occurs while enabled, the driver warns but deactivates. Period/duty truncation to `U32_MAX` may change requested waveform semantics.

## Test Signals
Test count query, request/free, apply disabled/enabled states, polarity change while enabled, period/duty clamping, duty greater than period, enable failure PM balance, remove with active PWM, and registration failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/pwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/raw.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/raw.c

## Purpose
Greybus Raw protocol driver. It exposes a character device for userspace to send raw Greybus payloads to a module and read raw payloads received from the module.

## Important APIs, Types, And Functions
`struct gb_raw` stores the connection, receive list, byte count, list mutex, disconnect rwsem, disconnected flag, cdev, and device. `struct raw_data` stores one queued received message. `receive_data()` validates and queues inbound messages. `gb_raw_request_handler()` receives `GB_RAW_TYPE_SEND` requests. Character operations are `raw_open()`, `raw_write()`, and `raw_read()`.

## Control Flow
Module init registers class and char major, then the Greybus driver. Probe validates one RAW CPort, allocates a minor and device, creates/enables a connection, initializes queues/locks, and publishes the cdev+device. Incoming Greybus sends are validated and appended to the receive list. Userspace writes copy one message into a Greybus send request under a disconnect read lock. Reads return exactly one queued message or `-ENOSPC` if the user buffer is too small.

## State And Persistence
Queued inbound messages live in memory until read or disconnect. Total queued data is capped by `MAX_DATA_SIZE`; individual messages by `MAX_PACKET_SIZE`. `disconnected` persists after disconnect begins so open file descriptors stop sending.

## Dependencies And Integration Points
Uses Greybus Raw protocol, Linux cdev/device class APIs, IDA minors, user copy helpers, mutexes, and rwsem disconnect coordination.

## Risks
Reads are nonblocking-empty by returning 0 when no message is queued, so userspace must poll externally or retry. Queue overflow drops new inbound messages. Disconnect does not prevent reads of already freed queue after teardown unless userspace operations are serialized by object/device lifetime; write is explicitly protected by `disconnect_lock`.

## Test Signals
Test probe validation, minor exhaustion, send size zero/too large, inbound malformed sizes, queue overflow, read with exact/small/large buffers, writes during disconnect, open fd after disconnect, and class/chrdev cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/raw.c -->
