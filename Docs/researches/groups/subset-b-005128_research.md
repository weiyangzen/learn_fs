# Research: subset-b-005128 Raspberry Pi MMAL VCHIQ and Surface Aggregator files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg.h

## Purpose

This header defines the wire-level message ABI used by the BCM2835 V4L2 MMAL client to communicate with the VideoCore firmware over VCHIQ. It gives fixed-size C layouts for control messages, component lifecycle requests, port information, port actions, buffer hand-off, port parameters, and asynchronous events. The file is intentionally protocol-facing rather than algorithmic.

## Important APIs, Types, And Functions

Important definitions are `VC_MMAL_VER`, `VC_MMAL_MIN_VER`, `MMAL_MSG_MAX_SIZE`, `MMAL_MSG_MAX_PAYLOAD`, `enum mmal_msg_type`, `enum mmal_msg_port_action_type`, `struct mmal_msg_header`, and the top-level `struct mmal_msg` union. Payload structures include `mmal_msg_component_create`, `mmal_msg_component_create_reply`, `mmal_msg_port_info_get_reply`, `mmal_msg_port_info_set`, `mmal_msg_port_action_port`, `mmal_msg_port_action_handle`, `mmal_msg_buffer_from_host`, `mmal_msg_port_parameter_set`, `mmal_msg_port_parameter_get_reply`, and `mmal_msg_event_to_host`. Buffer flags such as `MMAL_BUFFER_HEADER_FLAG_EOS`, `FRAME_START`, `FRAME_END`, `KEYFRAME`, `CONFIG`, and `CORRUPTED` are consumed by `mmal-vchiq.c`.

## Control Flow

The header itself has no runtime control flow. `mmal-vchiq.c` constructs `struct mmal_msg` instances, fills `h.type`, `h.magic`, and `h.context`, queues them through VCHIQ, and dispatches replies by `h.type`. Synchronous operations use the header context to match replies, while buffer messages use `mmal_driver_buffer.client_context` to recover a reusable buffer context.

## State And Persistence

There is no mutable state in this file. Its structures define transient in-memory serialization formats that must match the firmware ABI. State represented by these messages exists in VideoCore components, MMAL ports, queued host buffers, and client-side context maps.

## Dependencies And Integration Points

The file depends on `mmal-msg-common.h`, `mmal-msg-format.h`, `mmal-msg-port.h`, and `mmal-vchiq.h`. It is integrated by `mmal-vchiq.c` and indirectly by the BCM2835 camera/video stack using the exported MMAL VCHIQ API.

## Risks

The file explicitly warns that the protocol assumes 32-bit pointer fields and no unexpected structure padding. Any layout drift breaks firmware communication, so compile-time size checks in `vchiq_mmal_init()` are key. Several payload sizes are bounded by fixed arrays (`MMAL_VC_SHORT_DATA`, `MMAL_WORKER_PORT_PARAMETER_SPACE`, `MMAL_WORKER_EVENT_SPACE`); callers must validate lengths before copying. Status is represented both in the common header and in some payload replies, which increases interpretation risk.

## Test Signals

Useful signals are successful `BUILD_BUG_ON()` layout checks, successful MMAL service open, component create/destroy round trips, port info get/set round trips, short-payload and bulk buffer completion tests, port-parameter set/get tests with boundary sizes, and firmware compatibility checks against version 15/minimum 10.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-parameters.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-parameters.h

## Purpose

This header defines MMAL parameter IDs and parameter payload structures for the Raspberry Pi VideoCore multimedia stack. It groups common, camera, video, audio, clock, and Miracast parameter namespaces and provides the camera/video/display enums and structs needed by host drivers when calling MMAL port parameter get/set operations.

## Important APIs, Types, And Functions

The important constants are `MMAL_PARAMETER_GROUP_COMMON`, `CAMERA`, `VIDEO`, `AUDIO`, `CLOCK`, and `MIRACAST`. Major enums include `mmal_parameter_common_type`, `mmal_parameter_camera_type`, `mmal_parameter_camera_config_timestamp_mode`, `mmal_parameter_exposuremode`, `mmal_parameter_exposuremeteringmode`, `mmal_parameter_awbmode`, `mmal_parameter_imagefx`, `MMAL_PARAM_FLICKERAVOID`, `mmal_parameter_rate_control_mode`, `mmal_video_profile`, `mmal_video_level`, `mmal_parameter_video_type`, `mmal_parameter_mirror`, `mmal_parameter_displaytransform`, `mmal_parameter_displaymode`, and `mmal_parameter_displayset`. Important payloads are `mmal_parameter_fps_range`, `mmal_parameter_camera_config`, `mmal_parameter_awbgains`, `mmal_parameter_video_profile`, `vchiq_mmal_rect`, `mmal_parameter_displayregion`, `mmal_parameter_imagefx_parameters`, and `mmal_parameter_camera_info`.

## Control Flow

This file provides data contracts only. Runtime flows are through `vchiq_mmal_port_parameter_set()` and `vchiq_mmal_port_parameter_get()` in `mmal-vchiq.c`: callers pass a parameter ID from this header and a matching payload, which is copied into or out of MMAL worker messages.

## State And Persistence

The header owns no mutable state. Its values describe requested or reported VideoCore state: camera configuration, exposure, AWB, image effects, encoder rate control, display layout, and camera inventory. Persistence is firmware/component state and lasts only until changed, component destruction, firmware reset, or device power state changes.

## Dependencies And Integration Points

The file includes `<linux/math.h>` for fractional numeric types. It integrates with MMAL port-parameter message structs in `mmal-msg.h`, with local format/common MMAL headers, and with camera/V4L2 code that translates user-visible controls into MMAL parameter IDs and payloads.

## Risks

Parameter IDs are ABI values; changing order or group arithmetic would silently alter firmware commands. Many enum comments refer to MMAL types not defined in this header, so caller-side payload matching is convention-based. `mmal_parameter_camera_info` uses fixed maxima for camera, flash, and string counts; firmware responses exceeding those assumptions must be bounded by `mmal-vchiq.c` caller buffers. `mmal_parameter_imagefx_parameters` is capped at five values.

## Test Signals

Good tests include setting and reading camera controls, display regions, H.264 encoder parameters, AWB gains, exposure modes, FPS ranges, image effects, and camera info. Boundary tests should exercise parameter get responses larger than the supplied buffer and parameter set payloads near the MMAL worker parameter-space limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-parameters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.c -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.c

## Purpose

This source implements the BCM2835 MMAL client transport over Raspberry Pi VCHIQ. It opens the VideoCore `mmal` service, serializes synchronous MMAL control messages, receives asynchronous buffer completions, manages component and port state, and exports the in-kernel API used by the V4L2 camera driver.

## Important APIs, Types, And Functions

Key private types are `struct mmal_msg_context` and `struct vchiq_mmal_instance`. `mmal_msg_context` is either a synchronous reply waiter or a bulk-buffer context. The instance stores the VCHIQ service handle, serialization mutex, IDR context map, component array, ordered bulk workqueue, and VCHIQ instance pointer.

Important helpers include `get_msg_context()`, `lookup_msg_context()`, `release_msg_context()`, `send_synchronous_mmal_msg()`, `mmal_service_callback()`, `buffer_from_host()`, `buffer_to_host_cb()`, `bulk_receive()`, `inline_receive()`, `port_info_get()`, `port_info_set()`, `port_action_port()`, `port_action_handle()`, and `port_parameter_get/set()`. Exported APIs include `vchiq_mmal_init()`, `vchiq_mmal_finalise()`, component init/finalise/enable/disable, port enable/disable/set-format/connect-tunnel, parameter set/get, `vchiq_mmal_submit_buffer()`, and buffer context init/cleanup.

## Control Flow

Initialization obtains the parent VCHIQ management state, initializes/connects a VCHIQ instance, allocates the MMAL instance, creates an ordered workqueue, and opens the `mmal` service with `mmal_service_callback()`. Synchronous calls allocate a context ID, queue a message, wait up to `SYNC_MSG_TIMEOUT`, return the reply pointer, and release the VCHIQ message after decoding. Buffer flow is different: each `mmal_buffer` owns a persistent message context, `BUFFER_FROM_HOST` advertises its buffer, firmware responds with inline data or a bulk transfer request, and callback work fills buffer metadata and invokes the port callback outside the VCHIQ callback thread. Component creation queries control/input/output/clock ports and caches VideoCore handles.

## State And Persistence

Mutable state is in the instance context IDR, component slots, cached port fields, buffer queues, atomic `buffers_with_vpu`, and VideoCore handles. Software state is per-driver-instance and destroyed by `vchiq_mmal_finalise()`. Firmware-side component/port state persists until explicit MMAL disable/destroy, service close, or VideoCore reset.

## Dependencies And Integration Points

The file depends on Linux VCHIQ APIs, `videobuf2-vmalloc`, MMAL protocol headers, workqueues, completions, mutexes, spinlocks, atomics, and IDR. It exports symbols for other BCM2835 multimedia drivers and relies on `mmal-msg.h` layout checks to keep the firmware ABI valid.

## Risks

Late replies after a synchronous timeout can arrive after the context has been released, which the source comments call out. Buffer lifecycle is delicate: buffer contexts are reused, callbacks are deferred, and callers must clean up contexts only after firmware no longer owns them. Port array bounds rely on firmware-reported input/output/clock counts fitting `MAX_PORT_COUNT`. `port_parameter_set()` copies caller data into a fixed worker space without an explicit local `value_size` check beyond the global message-size check. `vchiq_mmal_submit_buffer()` returns zero even after queueing on disabled ports. Wake/shutdown paths must drain pending bulk work before buffers disappear.

## Test Signals

Signals include module load/unload, MMAL version query, component create/destroy for camera/encoder/render components, port info get/set readback, parameter boundary tests, tunnel connect/disconnect tests, buffer streaming with inline and bulk payloads, EOS/empty buffer callbacks, disable while buffers are queued, timeout injection, VCHIQ service close handling, and leak checks for IDR contexts and workqueue callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.h

## Purpose

This header exposes the MMAL-over-VCHIQ client API and the client-visible component/port data structures used by the BCM2835 V4L2 driver. It abstracts the VideoCore MMAL service behind component, port, parameter, format, tunnel, and buffer operations.

## Important APIs, Types, And Functions

Important constants are `MAX_PORT_COUNT` and `MMAL_FORMAT_EXTRADATA_MAX_SIZE`. `enum vchiq_mmal_es_type` classifies elementary streams. `struct vchiq_mmal_port_buffer` describes buffer count/size/alignment. `struct vchiq_mmal_port` caches firmware port handle, type/index, component backpointer, tunnel peer, buffer requirements, current format, ES-specific format, queued buffers, spinlock, VPU buffer count, and completion callback. `struct vchiq_mmal_component` tracks lifecycle flags, firmware handle, port counts, control port, fixed arrays of input/output/clock ports, and a client component ID.

The exported API covers instance lifetime, component lifetime, component enable/disable, port enable/disable, parameter set/get, format set, tunnel connection, firmware version query, buffer submission, and MMAL buffer-context allocation/freeing.

## Control Flow

Callers initialize a `vchiq_mmal_instance`, create components by name, configure port format and parameters, enable components/ports, submit buffers or connect tunnels, then disable/finalise in reverse. Buffer callbacks run when `mmal-vchiq.c` receives a VideoCore buffer completion or bulk transfer completion.

## State And Persistence

The header declares the client-visible state containers but owns no storage. `enabled`, `connected`, cached handles, buffer queues, and format fields are runtime state populated by `mmal-vchiq.c`. There is no persistence beyond the active driver instance and VideoCore service session.

## Dependencies And Integration Points

It depends on `mmal-common.h` and `mmal-msg-format.h` for MMAL buffers and format types. It is included by `mmal-msg.h`, implemented by `mmal-vchiq.c`, and consumed by Raspberry Pi camera/video drivers.

## Risks

The fixed `MAX_PORT_COUNT` arrays must be large enough for every firmware component used by callers. Callers can mutate exposed port format and buffer fields, so `vchiq_mmal_port_set_format()` and enable paths rely on disciplined API use. Buffer callbacks may arrive asynchronously and must not race buffer cleanup. The `cb_ctx` field is exposed but not centrally managed in this subset.

## Test Signals

Compile coverage of all exported prototypes, successful component and port setup, stream callbacks with correct buffer metadata, tunnel setup between ports, and teardown without leaked contexts or callbacks after free are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-vchiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/Kconfig

## Purpose

This Kconfig file defines the Microsoft Surface platform-driver menu and the user-selectable options for Surface-specific WMI, ACPI, hotplug, power, input, platform-profile, DTX, and Surface Aggregator support.

## Important APIs, Types, And Functions

The top-level `menuconfig SURFACE_PLATFORMS` gates the menu on `ARM64 || X86 || COMPILE_TEST` and defaults to enabled on ARM64/X86. Configs include `SURFACE3_WMI`, `SURFACE_3_POWER_OPREGION`, `SURFACE_ACPI_NOTIFY`, `SURFACE_AGGREGATOR_CDEV`, `SURFACE_AGGREGATOR_HUB`, `SURFACE_AGGREGATOR_REGISTRY`, `SURFACE_AGGREGATOR_TABLET_SWITCH`, `SURFACE_DTX`, `SURFACE_GPE`, `SURFACE_HOTPLUG`, `SURFACE_PLATFORM_PROFILE`, and `SURFACE_PRO3_BUTTON`. It sources `drivers/platform/surface/aggregator/Kconfig` for the SSAM core.

## Control Flow

There is no runtime control flow. Build-time selection controls which object files in the Surface Makefile and aggregator subdirectory are compiled. Dependency declarations force required subsystems such as ACPI, WMI, DMI, SPI, INPUT, GPIOLIB, and Surface Aggregator support.

## State And Persistence

The only state is Kconfig build configuration. It persists in `.config` and determines available modules or built-in drivers.

## Dependencies And Integration Points

The file integrates the Surface platform subtree with kernel Kconfig, the Surface Aggregator Kconfig, ACPI/WMI/input/GPIO/SPI support, and ACPI platform profile support. Several drivers depend on `SURFACE_AGGREGATOR` or `SURFACE_AGGREGATOR_BUS`.

## Risks

Incorrect dependencies can allow invalid builds or hide needed drivers. `SURFACE_DTX` can be built without the aggregator bus, but help text warns that some devices will then be unsupported. Options that instantiate client devices require both registry/hub providers and actual client drivers, so users can select incomplete combinations.

## Test Signals

Validation is mostly configuration-matrix testing: `allyesconfig`, `allmodconfig`, targeted Surface configs, `COMPILE_TEST`, and module-name checks. Runtime signals are successful probing of selected Surface devices and absence of unresolved symbols when options are built as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/Makefile

## Purpose

This Makefile maps Surface platform Kconfig symbols to the object files and subdirectories built under `drivers/platform/surface`.

## Important APIs, Types, And Functions

The key entries bind `CONFIG_SURFACE3_WMI` to `surface3-wmi.o`, `SURFACE_3_POWER_OPREGION` to `surface3_power.o`, `SURFACE_ACPI_NOTIFY` to `surface_acpi_notify.o`, `SURFACE_AGGREGATOR` to the `aggregator/` directory, `SURFACE_AGGREGATOR_CDEV` to `surface_aggregator_cdev.o`, `SURFACE_AGGREGATOR_HUB` to `surface_aggregator_hub.o`, `SURFACE_AGGREGATOR_REGISTRY` to `surface_aggregator_registry.o`, `SURFACE_AGGREGATOR_TABLET_SWITCH` to `surface_aggregator_tabletsw.o`, and the remaining Surface drivers to their corresponding objects.

## Control Flow

There is no runtime behavior. Kbuild evaluates `obj-$(CONFIG_...)` assignments and compiles built-in or module objects according to the current kernel configuration.

## State And Persistence

The file has no runtime state. Its effects persist only in build artifacts and module layout for a configured kernel build.

## Dependencies And Integration Points

It integrates with Kbuild and the Kconfig symbols defined in the neighboring `Kconfig` and aggregator Kconfig. The `aggregator/` subdirectory is included only when `CONFIG_SURFACE_AGGREGATOR` is enabled.

## Risks

The Makefile must stay aligned with Kconfig symbol names and source filenames. A mismatch causes selected options to silently build nothing or fail the build. Since multiple client drivers depend on the aggregator core, missing the `aggregator/` descent would break a large portion of Surface support.

## Test Signals

`make M=drivers/platform/surface`, `allmodconfig`, `allyesconfig`, and module packaging checks should confirm each selected config emits the expected object or module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Kconfig

## Purpose

This Kconfig file defines the Surface System Aggregator Module core, optional SSAM client bus, and optional error-injection support. It controls the SAM-over-SSH controller driver and the kernel interface used by Surface client drivers.

## Important APIs, Types, And Functions

`menuconfig SURFACE_AGGREGATOR` is a tristate requiring `SERIAL_DEV_BUS`, `ACPI`, and `!RISCV`, and selecting `CRC_ITU_T`. `CONFIG_SURFACE_AGGREGATOR_BUS` is a boolean extension that defaults to yes and provides a dedicated SSAM bus/device type. `CONFIG_SURFACE_AGGREGATOR_ERROR_INJECTION` depends on `FUNCTION_ERROR_INJECTION` and enables transport/communication failure injection hooks.

## Control Flow

There is no runtime control flow. These symbols select whether `surface_aggregator.o` is built, whether `bus.o` is linked into it, and whether error-injection sites are compiled in related request/packet layers.

## State And Persistence

The state is build configuration only. It determines whether the controller exists, whether SSAM client devices can bind through a bus, and whether test-only failure injection is available.

## Dependencies And Integration Points

The core integrates with serdev, ACPI, CRC-ITU-T, Surface Aggregator clients, and the parent Surface platform Kconfig. The bus option is a dependency for registry, hub, tablet-switch, and other SSAM device drivers.

## Risks

The `ACPI && !RISCV` dependency constrains the core even though `core.c` has OF fallback paths for some setup values. Disabling `SURFACE_AGGREGATOR_BUS` keeps the core available but removes bus-based clients, which can surprise configurations that select higher-level functionality. Error injection must remain development-only.

## Test Signals

Configuration tests should cover core built-in, core as module, bus enabled/disabled, and compile-test where supported. Runtime tests are serdev probe, firmware version query, and SSAM client-driver binding through the bus when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Makefile

## Purpose

This Makefile builds the Surface Aggregator core module from controller, serial-hub, packet/request layer, parser, optional bus, and trace-support sources.

## Important APIs, Types, And Functions

`CFLAGS_core.o = -I$(src)` lets trace headers resolve through the local source directory. `obj-$(CONFIG_SURFACE_AGGREGATOR) += surface_aggregator.o` creates the aggregate object. `surface_aggregator-y` includes `core.o`, `ssh_parser.o`, `ssh_packet_layer.o`, `ssh_request_layer.o`, and `controller.o`; `surface_aggregator-$(CONFIG_SURFACE_AGGREGATOR_BUS)` conditionally adds `bus.o`.

## Control Flow

There is no runtime control flow. Kbuild links the listed objects into the `surface_aggregator` built-in object or module according to `CONFIG_SURFACE_AGGREGATOR`.

## State And Persistence

The file has no runtime state. It controls build artifacts and whether bus support is present in the resulting object.

## Dependencies And Integration Points

It integrates the aggregator Kconfig symbols with Kbuild and supports tracepoint generation in `core.o`. It assumes packet/request/parser sources exist in the same directory and are compiled into one module with shared internal headers.

## Risks

Object ordering matters for init/exit dependencies only indirectly, but omitting `bus.o` when `CONFIG_SURFACE_AGGREGATOR_BUS=y` would remove exported bus symbols. Trace include path changes can break `CREATE_TRACE_POINTS` compilation in `core.c`.

## Test Signals

Build tests with `CONFIG_SURFACE_AGGREGATOR=m/y` and `CONFIG_SURFACE_AGGREGATOR_BUS=y/n`, plus module symbol checks for bus exports, validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.c

## Purpose

This source implements the optional Surface Aggregator bus and client-device model. It lets non-enumerable SSAM devices be represented as kernel devices with SSAM UIDs, matched to SSAM device drivers, populated from firmware nodes, and removed before controller shutdown.

## Important APIs, Types, And Functions

Important exports include `ssam_device_type`, `ssam_device_alloc()`, `ssam_device_add()`, `ssam_device_remove()`, `ssam_device_id_match()`, `ssam_device_get_match()`, `ssam_device_get_match_data()`, `__ssam_device_driver_register()`, `ssam_device_driver_unregister()`, `__ssam_register_clients()`, and `ssam_remove_clients()`. Internal helpers implement modalias sysfs/uevent generation, UID parsing from `ssam:dd:cc:tt:ii:ff` firmware-node names, device matching by `SSAM_MATCH_TARGET`, `INSTANCE`, and `FUNCTION`, and bus register/unregister.

## Control Flow

The core registers the bus during aggregator init. Client providers allocate an `ssam_device`, attach the controller and optional firmware node, and call `ssam_device_add()`. Addition takes the controller state read lock and rejects devices unless the controller is `SSAM_CONTROLLER_STARTED`. Driver registration sets the bus and prefers asynchronous probing so SSAM I/O can occur during probe. Firmware-child registration scans each child node, ignores non-SSAM nodes, and rolls back already added clients on error.

## State And Persistence

Runtime state is represented by registered `struct device` objects, controller references held by devices, firmware-node references, and driver bindings. The bus stores no persistent registry of its own. Device existence lasts until explicit `ssam_device_remove()` or parent child-removal during controller teardown.

## Dependencies And Integration Points

The file depends on Linux driver core, device properties/fwnodes/OF, Surface Aggregator controller and device public headers, and local controller locking. It integrates with client registry/hub drivers and with `core.c` teardown through `ssam_remove_clients()`.

## Risks

Lifetime correctness depends on controller parentage or explicit removal before shutdown. `ssam_remove_clients()` only removes direct children. UID parsing depends on firmware node names with the `ssam:` prefix and exactly five hex bytes. Match tables must end in a zero entry. Async probe means client drivers must correctly handle request failures and ordering. `ssam_device_add()` protects state during `device_add()`, but callers that change parentage must ensure suspend/remove ordering themselves.

## Test Signals

Signals include bus registration, modalias strings and uevents, module autoload from SSAM IDs, client device creation from firmware nodes, match-data retrieval, async probe of client drivers that issue SSAM requests, rollback on child-add failure, and reverse-order removal before controller shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.h -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.h

## Purpose

This internal header exposes Surface Aggregator bus registration hooks to the core while compiling to no-op stubs when `CONFIG_SURFACE_AGGREGATOR_BUS` is disabled.

## Important APIs, Types, And Functions

The only APIs are `ssam_bus_register()` and `ssam_bus_unregister()`. With bus support enabled, they are implemented in `bus.c`; otherwise static inline stubs return success or do nothing.

## Control Flow

`core.c` calls these functions during module init and exit. The stubs keep the core init sequence identical regardless of bus configuration.

## State And Persistence

The header owns no state. When enabled, bus registration state belongs to the Linux driver core. When disabled, no bus object exists.

## Dependencies And Integration Points

It includes the public Surface Aggregator controller header for shared type visibility and is used by `core.c`. It is tied to `CONFIG_SURFACE_AGGREGATOR_BUS` from the aggregator Kconfig.

## Risks

The no-op stub means higher-level code must be properly gated by Kconfig; otherwise a build without bus support may appear to initialize successfully while bus clients cannot exist. Keeping the prototypes aligned with `bus.c` avoids link or type mismatches.

## Test Signals

Build both with and without `CONFIG_SURFACE_AGGREGATOR_BUS`. With bus enabled, verify bus registration and client binding. With it disabled, verify core probe still succeeds and no bus symbols are required by selected clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.c

## Purpose

This source implements the main Surface System Aggregator Module controller: SSH sequence/request ID allocation, event notification dispatch, event activation reference counting, asynchronous event completion, controller lifecycle/state transitions, synchronous request submission, internal SAM requests, notifier registration, and wakeup IRQ management.

## Important APIs, Types, And Functions

Important exported APIs include `ssam_controller_init/start/shutdown/destroy`, `ssam_controller_get/put`, `ssam_controller_statelock/stateunlock`, `ssam_request_write_data()`, `ssam_request_sync_alloc/free/init/submit`, `ssam_request_do_sync()`, `ssam_request_do_sync_with_buffer()`, `ssam_get_firmware_version()`, display/D0 notification helpers, notifier register/unregister/event enable/disable functions, `ssam_notifier_disable_registered()`, `ssam_notifier_restore_registered()`, and IRQ setup/free/arm/disarm. Key private systems are `ssh_seq_counter`, `ssh_rqid_counter`, SRCU notifier heads, RB-tree event refcounts, the `ssam_cplt` workqueue, controller capability loading via ACPI `_DSM` or OF defaults, and `ssam_handle_event()`.

## Control Flow

Initialization loads controller capabilities, resets counters, creates the completion workqueue/notifier system, initializes the request transport layer, and enters `INITIALIZED`. Start launches the transport layer and enters `STARTED`. Requests are serialized by `ssam_request_write_data()` through `ssh_msgb.h`, submitted to the request transport, completed by callbacks, and copied into caller response buffers. Incoming events are allocated, routed by target ID and event RQID to a completion queue, then processed in bounded workqueue batches through registered notifiers. Shutdown flushes the transport, drains completions, unregisters notifiers, shuts down the request layer, and enters `STOPPED`.

## State And Persistence

State includes the controller kref, rwsem-protected state machine, transport layer, completion queues, notifier SRCU lists, event refcount RB-tree, sequence/RQID counters, IRQ number/wakeup flag, and capability values. No disk persistence exists. EC-side event enables, display/D0 state, and pending requests persist in firmware until explicitly changed, reset, or power-state transition.

## Dependencies And Integration Points

The controller depends on ACPI, GPIO, IRQ, serdev, workqueues, SRCU, rbtrees, unaligned little-endian helpers, public Surface Aggregator controller/serial-hub headers, local SSH request layer, `ssh_msgb.h`, and tracepoints. It is driven by `core.c` and consumed by SSAM bus clients and non-bus clients.

## Risks

Request submission only performs a superficial `STARTED` check; callers must hold lifecycle guarantees or use device links. Notifier enable/disable has EC side effects while holding the notifier lock, so slow firmware can stall registration paths. Wake IRQ event release is explicitly incomplete; the handler only acknowledges and comments describe missing GPIO callback processing. Refcount mismatch or inconsistent flags can leave firmware events enabled or disabled unexpectedly. Hibernation paths rely on disable/restore of registered events. Large event payloads allocate dynamically and require robust memory-pressure behavior.

## Test Signals

Validation should cover request/response success, timeout/error paths, response-buffer-too-small handling, concurrent request ID allocation, event notifier priority/stop/handled bits, duplicate register/unregister, event refcount enable/disable sequencing, suspend/resume/freeze/thaw/poweroff/restore, wake IRQ arm/disarm, shutdown with active requests/events, and error injection through `SURFACE_AGGREGATOR_ERROR_INJECTION`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.h -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.h

## Purpose

This internal header defines the Surface Aggregator controller's core state structures and private function interface shared between `controller.c`, `core.c`, and related SSH transport files.

## Important APIs, Types, And Functions

Important types are `ssh_seq_counter`, `ssh_rqid_counter`, `ssam_nf_head`, `ssam_nf`, `ssam_event_item`, `ssam_event_queue`, `ssam_event_target`, `ssam_cplt`, `enum ssam_controller_state`, `ssam_controller_caps`, and `ssam_controller`. The controller embeds a kref, rwsem, state enum, request transport layer, completion system, sequence/RQID counters, IRQ state, and capability values. Inline helpers bridge serdev callbacks to `ssh_ptl_rx_rcvbuf()` and `ssh_ptl_tx_wakeup_transfer()`. Prototypes expose lifecycle, notifier PM helpers, IRQ helpers, state locks, firmware/display/D0 requests, suspend/resume, and event-item cache init/destroy.

## Control Flow

The header defines the state machine used by `controller.c`: uninitialized, initialized, started, stopped, and suspended. `core.c` uses the inline receive/write-wakeup helpers from serdev callbacks and calls lifecycle/PM/IRQ functions in probe, remove, shutdown, and suspend/resume flows.

## State And Persistence

The structures describe runtime state only. Controller references are kref-managed; state transitions are guarded by the rwsem; notifiers and event queues are memory-resident and torn down with the controller. Capabilities are loaded at initialization and cached for the controller lifetime.

## Dependencies And Integration Points

The header includes Linux kref/list/mutex/rbtree/rwsem/serdev/spinlock/srcu/workqueue types, public Surface Aggregator headers, and the local SSH request layer. It connects the high-level core driver with the lower request/packet transport.

## Risks

Because this is an internal shared contract, layout or semantic changes affect multiple files. Consumers must respect lock requirements around state transitions and request submission. The `ssam_controller_receive_buf()` inline returns transport errors directly to `core.c`, which maps negative receive results to zero consumed bytes. Kref release calls back into destroy logic and assumes no unexpected outstanding users.

## Test Signals

Build coverage across PM and bus configurations, lockdep during controller state transitions, kref leak detection, serdev receive/write wakeup tests, and suspend/resume ordering with client devices validate this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/core.c

## Purpose

This source is the Surface Serial Hub serdev driver and module entry point for the Surface Aggregator subsystem. It binds the controller to the serial device, exposes a global controller reference, creates device links for clients, configures UART parameters from ACPI or defaults, implements sysfs firmware-version reporting, manages PM notifications, registers wake IRQs, and initializes shared caches/bus support.

## Important APIs, Types, And Functions

Important exports are `ssam_get_controller()`, `ssam_client_link()`, and `ssam_client_bind()`. Probe/remove logic lives in `ssam_serial_hub_probe()` and `ssam_serial_hub_remove()`. Serdev glue is `ssam_receive_buf()`, `ssam_write_wakeup()`, and `ssam_serdev_ops`. Setup helpers include ACPI CRS parsing, GPIO mapping, and `ssam_serdev_setup()`. PM callbacks include prepare/complete, suspend/resume, freeze/thaw, poweroff/restore, plus shutdown. Module setup uses `ssam_core_init()` and `ssam_core_exit()`.

## Control Flow

At `subsys_initcall`, the driver registers the optional bus, packet cache, event item cache, and serdev driver. Probe maps ACPI GPIOs, allocates and initializes the controller, opens/configures serdev, starts the controller, logs firmware version, sends D0-entry and display-on notifications, creates sysfs, sets up IRQ, publishes the global controller, and clears ACPI dependencies. Remove clears the global reference, frees IRQ/sysfs, removes clients, sends display-off/D0-exit notifications, shuts down the controller, closes serdev, and drops the controller reference.

## State And Persistence

State includes the global controller pointer under spinlock, serdev driver data, sysfs `sam/firmware_version`, wakeup capability, ACPI GPIO mappings, optional DT platform hub registration, and controller-owned state. No disk persistence exists. PM callbacks intentionally manipulate EC display/D0/event state across system sleep and hibernation.

## Dependencies And Integration Points

The file depends on ACPI, GPIO descriptors, OF, platform devices, PM, serdev, sysfs, units constants, Surface Aggregator public headers, local bus/controller headers, and tracepoint creation. It integrates with ACPI ID `MSHW0084` and OF compatible `microsoft,surface-sam`.

## Risks

The static controller model assumes a single provider. Wakeup is marked capable but disabled by default because wake event classification is incomplete. PM sequencing is firmware-sensitive: display-off/on and D0-exit/entry failures can leave EC event delivery impaired. The DT path registers a platform hub but does not store the returned platform device for later unregister in this file. `ssam_client_bind()` returns a controller pointer after dropping its own kref and relies on the device link for lifetime.

## Test Signals

Signals include serdev probe via ACPI and OF, UART parameter setup from ACPI CRS, firmware version sysfs reads, D0/display notification success on boot and PM, suspend/resume/hibernate cycles with keyboard/touchpad/battery events still working, client device removal before shutdown, IRQ setup and wake arm/disarm, module unload cleanup, and lockdep/kref checks around global controller access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_msgb.h -->
# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_msgb.h

## Purpose

This header provides small inline builders for Surface Serial Hub protocol messages. It writes SYN markers, frame headers, ACK/NAK packets, command payloads, and CRCs into caller-supplied buffers for the Surface Aggregator request path.

## Important APIs, Types, And Functions

`struct msgbuf` tracks begin/end/current pointers. Helpers are `msgb_init()`, `msgb_bytes_used()`, `msgb_push_u16()`, `msgb_push_syn()`, `msgb_push_buf()`, `msgb_push_crc()`, `msgb_push_frame()`, `msgb_push_ack()`, `msgb_push_nak()`, and `msgb_push_cmd()`. Internal push helpers write raw `u8` and little-endian `u16` values. `msgb_push_cmd()` builds a DATA_SEQ frame containing `struct ssh_command`, request IDs, target/category/source/instance/command fields, payload, and CRC.

## Control Flow

Callers initialize `msgbuf` with a pre-sized span, push a SYN marker, push a frame header and frame CRC, write optional command payload, then append payload CRC. `ssam_request_write_data()` in `controller.c` is the primary command-message caller and checks payload and total message size before using these helpers.

## State And Persistence

The only state is the transient buffer cursor. The header owns no persistent state and performs no allocation. Resulting bytes are queued into the SSH packet/request transport.

## Dependencies And Integration Points

It depends on unaligned little-endian helpers, Surface Aggregator controller and serial-hub public headers, `ssh_crc()`, SSH frame constants, `struct ssh_frame`, `struct ssh_command`, and `struct ssam_request`. It is tightly coupled to `controller.c` request serialization.

## Risks

Some helpers check capacity (`msgb_push_u16()`, `msgb_push_frame()`, command header check), but `msgb_push_buf()` does not check bounds itself and depends on caller prevalidation. If a warning path returns early, later pushes may still execute in some callers, so total size checks before construction are essential. CRC coverage must match the EC protocol exactly: frame CRC covers the frame header, and command CRC covers command struct plus payload.

## Test Signals

Useful tests are byte-for-byte command frame fixtures, ACK/NAK fixture tests, CRC validation, boundary payload sizes at `SSH_COMMAND_MAX_PAYLOAD_SIZE`, undersized-buffer warning tests, and integration tests where EC accepts requests serialized by `ssam_request_write_data()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_msgb.h -->
