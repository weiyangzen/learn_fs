# subset-b-005860 research

Grouped research for Linux kernel headers under `sources/distributed-fs/ceph-client/include/linux`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hfs_common.h -->
# sources/distributed-fs/ceph-client/include/linux/hfs_common.h

## Purpose
`hfs_common.h` is a shared on-disk format header for HFS and HFS+ filesystem code. It defines magic values, fixed geometry constants, catalog/extents/attributes B-tree keys and records, Finder metadata structures, POSIX permission records, fork descriptors, and HFS+ volume header layout. The file is a schema contract: implementation files parse, validate, create, and update disk blocks using these packed big-endian structures.

## Important APIs, Types, And Functions
The header exports no callable functions, but its typedefs and structures are core APIs. Important items include `hfsplus_cnid`, `hfsplus_unichr`, `struct hfs_name`, `struct hfsplus_unistr`, `struct hfsplus_fork_raw`, `struct hfs_mdb`, `struct hfsplus_vh`, `struct hfs_cat_key`, `struct hfsplus_cat_key`, `struct hfs_ext_key`, `struct hfsplus_ext_key`, `hfs_cat_rec`, `hfsplus_cat_entry`, `struct hfsplus_attr_key`, and `hfsplus_attr_entry`. Constants such as `HFS_SUPER_MAGIC`, `HFSPLUS_VOLHEAD_SIG`, CNID constants, catalog record type constants, fork type constants, and B-tree attribute bits drive validation and dispatch.

## Control Flow And State
Control flow is implicit. Mount and B-tree code read sector or node buffers, compare signatures and type fields, choose a union member, and interpret offsets and key lengths based on HFS versus HFS+. Persistent state is entirely on disk: volume headers, MDB fields, B-tree headers, catalog nodes, extent records, fork sizes, file counts, folder counts, CNID allocation, xattr records, and finder metadata. All multibyte persistent values are big-endian or explicitly packed; callers must convert with endian helpers before arithmetic.

## Dependencies And Integration Points
This header depends on kernel integer and endian types supplied by Linux headers included by filesystem implementation files. It integrates with HFS/HFS+ superblock, catalog, extents, attributes, inode, and xattr code. It also bridges legacy Mac OS metadata (`FInfo`, `DInfo`, `FXInfo`, `DXInfo`) into Linux inode and xattr semantics.

## Risks
The main risks are structure packing drift, endian misuse, union member confusion, malformed key lengths, extent count overflow, and trusting disk-provided sizes. `HFSPLUS_MAX_INLINE_DATA_SIZE` and string length constants protect fixed node layouts only if callers validate lengths before copying. CNID and B-tree constants are externally persistent ABI values and cannot be changed without breaking filesystem compatibility.

## Test Signals
Useful tests include mounting HFS and HFS+ images, HFSX case-sensitive key behavior, malformed volume headers, bad B-tree node type/key length cases, catalog records for files/directories/threads, inline and forked xattrs, resource fork extents, hardlink/symlink creator/type mappings, and endian checks on known-good images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hfs_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-debug.h -->
# sources/distributed-fs/ceph-client/include/linux/hid-debug.h

## Purpose
`hid-debug.h` declares HID debugfs support used by HID core and HID drivers to expose parsed devices, fields, report descriptors, input reports, and live event logs. It is conditionally compiled: with `CONFIG_DEBUG_FS` it provides real declarations and the `hid_debug_list` FIFO state; otherwise every debug operation becomes a no-op macro.

## Important APIs, Types, And Functions
The debug API includes `hid_dump_input()`, `hid_dump_report()`, `hid_dump_device()`, `hid_dump_field()`, `hid_resolv_usage()`, `hid_debug_register()`, `hid_debug_unregister()`, `hid_debug_init()`, `hid_debug_exit()`, and `hid_debug_event()`. `HID_DEBUG_BUFSIZE` and `HID_DEBUG_FIFOSIZE` size debug buffers. `struct hid_debug_list` stores the per-reader kfifo, async notification pointer, HID device pointer, list link, and read mutex.

## Control Flow And State
When debugfs is enabled, devices register debug entries during HID device setup and unregister during teardown. Events are pushed into per-reader FIFOs and readers block or use fasync notification. When debugfs is disabled, all calls compile away, so callers must not depend on side effects from debug helpers.

## Dependencies And Integration Points
The file depends on `linux/kfifo.h` only under `CONFIG_DEBUG_FS`, plus HID core types declared elsewhere. It integrates with `struct hid_device` debugfs fields in `hid.h`, seq_file formatting, and user-visible debugfs files under HID device directories.

## Risks
Risks include debug FIFO overflow, stale `hid_device` pointers if unregister ordering is wrong, locking mistakes between event producers and readers, and format drift that makes debug output misleading. The `hid_resolv_usage()` no-op macro expands to `do { } while (0)` in non-debug builds, so code must not use its return value unless compiled under debugfs-compatible paths.

## Test Signals
Test by enabling `CONFIG_DEBUG_FS`, probing a HID device, reading descriptor and event debugfs files, generating input events, checking fasync/read behavior, and building without debugfs to ensure all callers compile with no-op definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-over-i2c.h -->
# sources/distributed-fs/ceph-client/include/linux/hid-over-i2c.h

## Purpose
`hid-over-i2c.h` defines the wire-level constants and packed structures for the HID over I2C protocol. It is a transport contract for I2C HID controller drivers: it describes report packets, command encoding, report/power/opcode enums, and the fixed HID-I2C device descriptor.

## Important APIs, Types, And Functions
The important types are `enum hidi2c_report_type`, `enum hidi2c_power_state`, `enum hidi2c_opcode`, `struct hidi2c_report_packet`, and `struct hidi2c_dev_descriptor`. Macros such as `HIDI2C_PACKET_LEN()`, `HIDI2C_DATA_LEN()`, `HIDI2C_CMD_REPORT_ID`, `HIDI2C_CMD_REPORT_TYPE`, `HIDI2C_CMD_OPCODE`, `HIDI2C_CMD_3RD_BYTE`, and `HIDI2C_DEV_DESC_LEN` define packet length and bitfield extraction rules. There are no functions.

## Control Flow And State
Drivers read a device descriptor from the descriptor register, use register addresses and maximum report sizes from that descriptor, issue command words through `cmd_reg` and optional data through `data_reg`, and read/write report packets through input/output registers. State lives in device hardware and driver-private transport state; this header only defines serialized little-endian fields.

## Dependencies And Integration Points
It depends on `linux/bits.h` and kernel integer types. It integrates with HID core through low-level `hid_ll_driver` operations that parse descriptors, send `GET_REPORT`/`SET_REPORT`, set power, and deliver input packets as HID reports.

## Risks
Important risks are incorrect little-endian conversion, off-by-two length handling around the leading length field, invalid optional report ID encoding for IDs >= 15, duplicate `HIDI2C_CMD_OPCODE` macro definition, and trusting descriptor-provided `max_input_len`/`max_output_len` without buffer bounds. Protocol BCD and fixed descriptor length validation are critical.

## Test Signals
Test signals include descriptor length/version checks, short and extended report IDs, reset/get/set report commands, sleep/on transitions, maximum-sized input reports, malformed short packets, and HID core report parsing through an I2C transport driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-over-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-over-spi.h -->
# sources/distributed-fs/ceph-client/include/linux/hid-over-spi.h

## Purpose
`hid-over-spi.h` defines HID over SPI protocol packet formats. It gives SPI HID drivers the enums, headers, size macros, and descriptor layout needed to request descriptors, send commands, move reports, handle fragmentation, and interpret response bodies.

## Important APIs, Types, And Functions
The central definitions are `enum input_report_type`, `enum output_report_type`, `enum hidspi_power_state`, `struct input_report_body_header`, `struct input_report_body`, `struct output_report_header`, `struct output_report`, and `struct hidspi_dev_descriptor`. Bit masks such as `HIDSPI_INPUT_HEADER_VER`, `HIDSPI_INPUT_HEADER_REPORT_LEN`, `HIDSPI_INPUT_HEADER_LAST_FLAG`, and `HIDSPI_INPUT_HEADER_SYNC` describe the 32-bit input header. `HIDSPI_INPUT_BODY_SIZE()` and `HIDSPI_OUTPUT_REPORT_SIZE()` size variable payload packets.

## Control Flow And State
Transport code sends output reports for descriptor reads, feature reports, input report requests, output reports, and command content. Incoming SPI frames are validated via protocol version, sync byte, length, last-fragment flag, body type, content length, and content ID. Fragmented input bodies are accumulated until the last flag. Persistent state is hardware descriptor values, power state, pending command/report transactions, and any driver buffers used for fragment assembly.

## Dependencies And Integration Points
The header depends on `linux/bits.h` and `linux/types.h`. It integrates with HID core as a low-level transport beneath report descriptor parsing and raw report request/output callbacks.

## Risks
Risks include frame length calculation mistakes because header length is measured in 32-bit words, missing `__packed` on `struct hidspi_dev_descriptor`, accepting invalid report type enum values, failing to validate fixed protocol version `0x0300`, and fragment reassembly buffer overflow. Power transitions and command response matching must be serialized by the implementation.

## Test Signals
Tests should cover device/report descriptor responses, fragmented data reports, reset and command responses, get/set feature, output reports, power on/sleep/off, invalid sync/version, content length mismatch, and maximum fragment/report sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-over-spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-roccat.h -->
# sources/distributed-fs/ceph-client/include/linux/hid-roccat.h

## Purpose
`hid-roccat.h` is the small shared interface for legacy Roccat HID device support. It declares a Roccat-specific ioctl for report size and in-kernel helper functions used by Roccat HID drivers to expose device reports through a class/minor interface.

## Important APIs, Types, And Functions
`ROCCATIOCGREPSIZE` is an `_IOR('H', 0xf1, int)` ioctl that reports the device report size. Under `__KERNEL__`, the file declares `roccat_connect()`, `roccat_disconnect()`, and `roccat_report_event()`. The helpers connect a HID device to the Roccat class, release by minor, and forward raw report data.

## Control Flow And State
A Roccat-specific HID driver calls `roccat_connect()` during probe after HID setup, stores the returned minor, forwards reports through `roccat_report_event()`, and calls `roccat_disconnect()` during remove. State is owned by the Roccat class implementation, not this header, and keyed by the allocated minor plus report size.

## Dependencies And Integration Points
It includes `linux/hid.h` and `linux/types.h`, so it integrates directly with `struct hid_device` and HID raw event paths. It also exports a userspace ABI through the ioctl constant.

## Risks
The ioctl number and report-size behavior are ABI and must remain stable. Risks include minor lifetime mismatches, forwarding events after disconnect, wrong report size advertised to userspace, and hidden dependency on the Roccat class being initialized before device probe paths call `roccat_connect()`.

## Test Signals
Probe/remove a supported Roccat HID device, verify minor allocation and cleanup, issue `ROCCATIOCGREPSIZE`, stream reports to userspace, and test disconnect while readers are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-roccat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-sensor-hub.h -->
# sources/distributed-fs/ceph-client/include/linux/hid-sensor-hub.h

## Purpose
`hid-sensor-hub.h` defines the kernel-facing API for HID sensor hubs and HID sensor IIO client drivers. It describes sensor attribute metadata, synchronous read tracking, hub instance data, callback registration, feature access, common sensor attributes, scale/timestamp helpers, batching, and sampling-frequency/hysteresis accessors.

## Important APIs, Types, And Functions
Key structures are `struct hid_sensor_hub_attribute_info`, `struct sensor_hub_pending`, `struct hid_sensor_hub_device`, `struct hid_sensor_hub_callbacks`, and `struct hid_sensor_common`. Public functions include `sensor_hub_device_open()`, `sensor_hub_device_close()`, callback register/remove helpers, `sensor_hub_input_get_attribute_info()`, `sensor_hub_input_attr_get_raw_value()`, `sensor_hub_set_feature()`, `sensor_hub_get_feature()`, common-attribute parsing, raw hysteresis and sampling frequency read/write helpers, usage indexing, scale formatting, timestamp conversion, batch-mode query, and report latency get/set.

## Control Flow And State
Sensor hub core parses HID reports into attribute metadata. Client drivers register callbacks per sensor usage ID; incoming HID samples call `capture_sample()` and then `send_event()`. Feature reports configure poll interval, report state, power state, sensitivity, and latency. Synchronous reads use `sensor_hub_pending`, a completion, usage IDs, and a raw-data buffer to match the eventual response. `hid_sensor_common` stores IIO-facing persistent runtime state such as poll interval, hysteresis, latency, data-ready and user-requested state atomics, runtime PM enable flag, trigger, timestamp scale, and work item.

## Dependencies And Integration Points
The header depends on HID core, sensor usage IDs, IIO device/trigger APIs, mutexes, completions, atomics, platform devices, and workqueues. It integrates HID sensor collections with IIO drivers and platform devices.

## Risks
Risks include callback lifetime races, synchronous read timeouts or mismatched usage IDs, sign-extension mistakes for sub-32-bit data, unit exponent conversion errors, feature buffer size mismatch, and inconsistent runtime PM versus user requested state. The inline exponent converter handles HID 4-bit signed exponent encoding; callers must not treat arbitrary larger values as valid.

## Test Signals
Use HID sensor hub devices or emulation to test accelerometer/gyro/ALS/proximity clients, callback registration/removal, sync and async raw reads, feature report updates, sensitivity and poll interval conversion, timestamp scaling, runtime suspend/resume, batching/report latency, and disconnect during pending read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-sensor-hub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-sensor-ids.h -->
# sources/distributed-fs/ceph-client/include/linux/hid-sensor-ids.h

## Purpose
`hid-sensor-ids.h` is the shared HID sensor usage ID catalog. It maps HID sensor page usages, data fields, units, properties, power/reporting states, and custom-field helpers into named constants consumed by HID sensor hub core and IIO sensor drivers.

## Important APIs, Types, And Functions
The file exports only macros. Important groups include physical sensor usages such as `HID_USAGE_SENSOR_ACCEL_3D`, `HID_USAGE_SENSOR_ALS`, `HID_USAGE_SENSOR_PROX`, `HID_USAGE_SENSOR_PRESSURE`, `HID_USAGE_SENSOR_TEMPERATURE`, `HID_USAGE_SENSOR_GYRO_3D`, compass/orientation/inclinometer usages, and time usages. Data field constants define axis, light, pressure, humidity, orientation, and custom values. Unit constants and property constants describe scaling and controls. `HID_USAGE_SENSOR_DATA_FIELD_CUSTOM_VALUE(x)` computes custom value usage IDs.

## Control Flow And State
There is no runtime control flow. The constants drive descriptor scanning, report field lookup, client callback routing, IIO channel construction, unit conversion, and feature report control. Persistent behavior derives from HID report descriptors and feature values, not this header.

## Dependencies And Integration Points
It has no includes and is included by `hid-sensor-hub.h` and sensor client drivers. The constants are tied to the HID Usage Tables and to Linux IIO mappings.

## Risks
The main risks are typo or value drift: a misspelled macro such as `HID_USAGE_SENSOR_PROY_POWER_STATE` or `HID_USAGE_SENSOR_DATA_FIELE_TIME_SINCE_SYS_BOOT` may already be part of in-tree caller expectations despite spelling errors. Numeric IDs are protocol values and must not be renumbered. Unit constants must match HID unit encodings, or IIO scale computations become wrong.

## Test Signals
Build all HID sensor drivers, parse descriptors containing each supported usage family, verify IIO channel names/scales, test property feature reads/writes, and include custom value indices near bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid-sensor-ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid.h -->
# sources/distributed-fs/ceph-client/include/linux/hid.h

## Purpose
`hid.h` is the central kernel HID core interface. It defines HID descriptor item constants, usage IDs, quirk flags, device groups, parser state, report/field/usage structures, `struct hid_device`, driver callbacks, low-level transport callbacks, report parsing and I/O APIs, input mapping helpers, power/wakeup wrappers, and logging macros.

## Important APIs, Types, And Functions
Core types include `struct hid_item`, `struct hid_global`, `struct hid_local`, `struct hid_collection`, `struct hid_usage`, `struct hid_field`, `struct hid_report`, `struct hid_report_enum`, `struct hid_input`, `struct hid_battery`, `struct hid_device`, `struct hid_parser`, `struct hid_driver`, and `struct hid_ll_driver`. Driver registration uses `hid_register_driver()`, `hid_unregister_driver()`, and `module_hid_driver()`. Device/report APIs include `hid_add_device()`, `hid_destroy_device()`, `hid_parse_report()`, `hid_open_report()`, `hid_parse()`, `hid_connect()`, `hid_disconnect()`, `hid_input_report()`, `hid_safe_input_report()`, `hid_hw_start()`, `hid_hw_stop()`, `hid_hw_open()`, `hid_hw_close()`, `hid_hw_raw_request()`, `hid_hw_output_report()`, and `hid_report_raw_event()`.

## Control Flow And State
Low-level bus drivers allocate a `hid_device`, attach a `hid_ll_driver`, parse or provide a report descriptor, add the device, and start hardware. HID core parses descriptor items into collections, reports, fields, and usages. Matching HID drivers bind through ID tables and callbacks. Input reports flow from transport to BPF hooks, hidraw/hiddev/debug, raw driver events, parsed fields/usages, and input devices. Output/feature requests flow from core/hidraw/drivers down through low-level callbacks. State is held in parsed descriptor arrays, report ID hashes, input list, claimed flags, status/quirks bits, low-level open count and lock, driver data, debugfs state, batteries, hidraw/hiddev pointers, and optional HID-BPF data.

## Dependencies And Integration Points
The header depends on input, workqueue, mutex/semaphore, power_supply, uapi HID, and `hid_bpf.h`. It integrates USB, Bluetooth, I2C, SPI, hidraw, hiddev, input, force feedback, debugfs, power management, BPF, and module/device-driver infrastructure.

## Risks
Risks are high because this is shared ABI inside the kernel. Descriptor parser bounds (`HID_MAX_USAGES`, `HID_MAX_FIELDS`, `HID_MAX_IDS`), report buffer sizing, report ID handling, quirk semantics, BPF recursion/source tracking, lock ordering around `driver_input_lock`, and input mapping bounds all need careful validation. Driver hooks have nuanced return conventions. `report_fixup()` lifetime rules are easy to violate.

## Test Signals
Test with descriptor fuzzing, hid-tools/selftests, USB/Bluetooth/I2C/SPI devices, hidraw userspace, hiddev when enabled, BPF attach paths, input mapping edge cases, battery reports, suspend/resume/reset_resume, force feedback, quirk matching, disconnect during open, and high report ID/count limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid_bpf.h -->
# sources/distributed-fs/ceph-client/include/linux/hid_bpf.h

## Purpose
`hid_bpf.h` defines the HID-BPF interface that lets BPF programs inspect or alter HID report descriptors, incoming device events, raw feature/input/output requests, and output reports. It also defines HID core internal dispatch hooks and per-device BPF state.

## Important APIs, Types, And Functions
`struct hid_bpf_ctx` is the user-facing BPF context with `hid`, `allocated_size`, and mutable `size`/`retval`. `struct hid_ops` exposes HID core callbacks to BPF internals. `struct hid_bpf_ops` is a BPF struct_ops callback table with `hid_device_event`, `hid_rdesc_fixup`, `hid_hw_request`, and `hid_hw_output_report`. `struct hid_bpf` stores device data, attached programs, locks, SRCU, descriptor fixup ops, and destruction state. Under `CONFIG_HID_BPF`, dispatch and lifecycle functions are declared; otherwise inline stubs return pass-through success or original data.

## Control Flow And State
When enabled, HID core initializes device BPF state, connects attached operations by HID ID, optionally replaces report descriptors through `hid_rdesc_fixup`, dispatches incoming reports through device-event programs, and intercepts raw/output report calls. Program execution can continue, modify buffer size, or abort with an error. Per-device state persists in `hid_device.bpf`, including dynamically allocated data buffers, program lists protected by mutex for updates and SRCU for reads, and a `destroyed` flag that prevents new assignment during teardown.

## Dependencies And Integration Points
The header depends on BPF, mutex, SRCU, and uapi HID definitions. It is included from `hid.h`, and its dispatch functions sit on HID core input and request/output paths. It also identifies request sources such as kernel or hidraw file pointers.

## Risks
Risks include breaking user-facing BPF ABI, buffer size enforcement bugs, recursion when BPF-originated requests reenter HID paths, SRCU lifetime mistakes, descriptor fixup memory ownership, and mismatch between `allocated_size` and changed `size`. The comments warn that the user-facing portion must be edited carefully because out-of-tree BPF programs can depend on it.

## Test Signals
Run HID-BPF selftests for descriptor fixup, event rewrite/drop, raw request interception, output report interception, attach/detach during device removal, multiple programs and `BPF_F_BEFORE` ordering, disabled-config stubs, and boundary sizes including the 4 KiB descriptor fixup buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hid_bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hidden.h -->
# sources/distributed-fs/ceph-client/include/linux/hidden.h

## Purpose
`hidden.h` pushes GCC symbol visibility to `hidden` for position-independent code. It tells the compiler that external-linkage symbols referenced after this include will be resolved at link time, avoiding Global Offset Table indirections and associated relocation/COW overhead for kernel-style images built with `-fPIC` or older `-fPIE`.

## Important APIs, Types, And Functions
The file has no types or functions. Its single operative statement is `#pragma GCC visibility push(hidden)`.

## Control Flow And State
There is no runtime control flow and no data state. The effect is compile-time and persists until a corresponding visibility pop or end of translation unit. It changes symbol reference generation rather than kernel behavior.

## Dependencies And Integration Points
It depends on GCC-compatible visibility pragmas. It integrates with architecture/kernel build code that compiles position-independent objects but does not want default ELF symbol preemption semantics for internal kernel symbols.

## Risks
Because this is a push pragma, include placement matters. Including it too broadly can hide symbols that must remain externally visible to linkers, loaders, modules, or tooling. Including it without a matching pop in contexts that expect default visibility can create difficult link-time failures.

## Test Signals
Build affected architectures/configurations with PIE/PIC options, inspect symbol visibility and relocations, run module/link tests, and verify no exported symbol unexpectedly becomes hidden.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hidden.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hiddev.h -->
# sources/distributed-fs/ceph-client/include/linux/hiddev.h

## Purpose
`hiddev.h` defines the in-kernel side of the legacy USB HIDDEV interface, which exposes parsed HID device events and reports to userspace through the hiddev character-device ABI in `uapi/linux/hiddev.h`.

## Important APIs, Types, And Functions
`struct hiddev` stores the minor number, existence/open counters, existence mutex, wait queue, associated `hid_device`, list node, list lock, and initialization flag. When `CONFIG_USB_HIDDEV` is enabled, the header declares `hiddev_connect()`, `hiddev_disconnect()`, `hiddev_hid_event()`, and `hiddev_report_event()`. Disabled builds provide inline stubs where connect fails and event/disconnect calls do nothing.

## Control Flow And State
HID core or USB HID code connects hiddev during `hid_connect()` when requested or forced by quirks. Parsed field/usage events call `hiddev_hid_event()`, and report completion calls `hiddev_report_event()`. Disconnect flips existence state, wakes waiters, and releases the character-device path. State persists per hiddev minor while userspace has files open.

## Dependencies And Integration Points
It includes the userspace ABI header and references HID core structures. It integrates with `struct hid_device` hiddev callback pointers and claimed flags in `hid.h`.

## Risks
Risks include use-after-free across disconnect/open files, stale events after `exist` is cleared, wait queue wakeup omissions, and divergence between parsed HID events and the userspace ABI expectations. Disabled-config stubs returning `-1` rather than a symbolic errno are an integration quirk callers should tolerate.

## Test Signals
Build with and without `CONFIG_USB_HIDDEV`, connect a USB HIDDEV-capable device, read events and reports through the char device, test forced hiddev quirks, disconnect during blocking reads, and ensure callbacks are no-ops in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hiddev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hidraw.h -->
# sources/distributed-fs/ceph-client/include/linux/hidraw.h

## Purpose
`hidraw.h` defines the in-kernel structures and entry points for the hidraw character device interface. Hidraw exposes raw HID reports to userspace without input-layer interpretation.

## Important APIs, Types, And Functions
`struct hidraw` tracks a minor, existence/open counters, wait queue, underlying `hid_device`, device node, list lock, and open reader list. `struct hidraw_report` stores a report buffer and length. `struct hidraw_list` is per-open-file state with a ring buffer of `HIDRAW_BUFFER_SIZE` reports, head/tail, fasync pointer, backpointer, list node, read mutex, and revoked flag. With `CONFIG_HIDRAW`, functions include `hidraw_init()`, `hidraw_exit()`, `hidraw_report_event()`, `hidraw_connect()`, and `hidraw_disconnect()`; otherwise stubs compile away the feature.

## Control Flow And State
HID core connects hidraw during device setup, forwards raw input reports via `hidraw_report_event()`, and disconnects during teardown. Per-file ring buffers retain reports until userspace reads them. The revoked flag and existence state prevent further use after disconnect. Raw feature/output requests from userspace flow through HID core low-level request paths and may be visible to HID-BPF as file-sourced operations.

## Dependencies And Integration Points
It includes `uapi/linux/hidraw.h` and references HID core structures. It integrates with `hid_device.hidraw`, `HID_CLAIMED_HIDRAW`, character devices, fasync, wait queues, and BPF source tracking for hidraw-originated requests.

## Risks
Risks include report buffer lifetime, ring overflow policy, disconnect races with blocking readers, fasync notification ordering, and leaking raw reports from devices that should be ignored or claimed only by special drivers. Disabled-config stubs make `hidraw_connect()` fail with `-1`.

## Test Signals
Exercise hidraw open/read/poll/fasync, raw descriptor and report ioctls from userspace, disconnect while open, large reports near `HID_MAX_BUFFER_SIZE`, multiple readers, and builds with `CONFIG_HIDRAW=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hidraw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/highmem-internal.h -->
# sources/distributed-fs/ceph-client/include/linux/highmem-internal.h

## Purpose
`highmem-internal.h` provides the internal architecture/configuration split for highmem and local kmap APIs. It implements or declares the low-level behavior behind public highmem helpers, handling `CONFIG_HIGHMEM`, `CONFIG_KMAP_LOCAL`, `CONFIG_PREEMPT_RT`, and architecture flush hooks.

## Important APIs, Types, And Functions
For local mappings it declares `__kmap_local_pfn_prot()`, `__kmap_local_page_prot()`, `kunmap_local_indexed()`, `kmap_local_fork()`, schedule-in/out hooks, and `kmap_assert_nomap()`. Under `CONFIG_HIGHMEM` it declares `kmap_high()`, `kunmap_high()`, `__kmap_flush_unused()`, and `__kmap_to_page()`, and implements `kmap()`, `kunmap()`, `kmap_local_page()`, `kmap_local_folio()`, atomic kmap variants, highpage counters, and `is_kmap_addr()`. Without highmem, it maps directly through `page_address()`/`folio_address()` and returns zero highmem counts. `kunmap_atomic()` and `kunmap_local()` macros enforce that callers pass addresses, not `struct page *`.

## Control Flow And State
The file selects between global highmem mappings, local per-task/per-CPU mappings, and direct lowmem addresses. Atomic mappings disable page faults and either migration or preemption depending on RT. Local mappings must be unmapped in reverse nesting order. Persistent state belongs to architecture kmap slots, current task kmap control, and per-CPU fixmap state.

## Dependencies And Integration Points
It depends on architecture `asm/highmem.h` when highmem is enabled, page/folio APIs, preemption/migration controls, pagefault controls, fixmap constants, and optional flush hooks. Public `highmem.h` includes this header.

## Risks
Risks include wrong unmap order, assuming atomic kmap side effects, calling sleeping `kmap()` in atomic context, stale mappings across fork/schedule paths, missing architecture flushes, and passing page pointers to unmap macros. Panic-safe mapping returns NULL for highmem pages and callers must handle that.

## Test Signals
Build matrix with and without HIGHMEM/KMAP_LOCAL/PREEMPT_RT, DEBUG_KMAP_LOCAL checks, nested local mapping tests, atomic mapping pagefault/preemption state assertions, fork/schedule hooks, and highmem page copy/zero callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/highmem-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/highmem.h -->
# sources/distributed-fs/ceph-client/include/linux/highmem.h

## Purpose
`highmem.h` is the public helper layer for accessing pages and folios that may not have a permanent kernel virtual address. It documents and wraps long-term `kmap()`, temporary `kmap_local_page()`/`kmap_local_folio()`, deprecated `kmap_atomic()`, user-page zero/copy helpers, machine-check tolerant copy helpers, and page/folio memcpy/memset utilities.

## Important APIs, Types, And Functions
Important APIs include `kmap()`, `kunmap()`, `kmap_to_page()`, `kmap_flush_unused()`, `kmap_local_page()`, `kmap_local_folio()`, `kmap_atomic()`, highpage counters, `clear_user_page()`, `clear_user_pages()`, `clear_user_highpage()`, `clear_user_highpages()`, `vma_alloc_zeroed_movable_folio()`, `clear_highpage()`, `zero_user_segments()`, `copy_user_highpage()`, `copy_highpage()`, `copy_mc_user_highpage()`, `copy_mc_highpage()`, `memcpy_page()`, `memcpy_folio()`, `memset_page()`, `memcpy_from_page()`, `memcpy_to_page()`, `memzero_page()`, `memcpy_from_folio()`, `memcpy_to_folio()`, `folio_zero_tail()`, `folio_fill_tail()`, `memcpy_from_file_folio()`, `folio_zero_segments()`, `folio_zero_segment()`, `folio_zero_range()`, and `folio_release_kmap()`.

## Control Flow And State
Callers map a page/folio, operate on the returned address, flush dcache when needed for user-visible or DMA-visible writes, and unmap in reverse nesting order. Large folio helpers split copies at page boundaries when only partial highmem mapping is possible. Machine-check variants queue memory failure on source page errors. Allocation helpers may clear pages only when the architecture requires explicit zeroing.

## Dependencies And Integration Points
It depends on memory management, uaccess, cacheflush, KMSAN, KASAN tags, hardirq context rules, `highmem-internal.h`, file/VMA folio allocation, and architecture copy/clear hooks. It is used by filesystems, page cache, block, networking, and memory-management code.

## Risks
Risks include using local mapping addresses outside the caller context, unmapping in the wrong order, missing dcache flushes after writes, copying beyond page/folio boundaries, mishandling large highmem folios, ignoring machine-check copy failures, and relying on `kmap_atomic()` preemption behavior in new code.

## Test Signals
Run highmem-enabled 32-bit tests, large folio page-cache tests, KMSAN/KASAN metadata checks, userfault and page-fault paths, copy_mc error injection, boundary offsets at page edges, and filesystem inline-data paths using `folio_fill_tail()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/highuid.h -->
# sources/distributed-fs/ceph-client/include/linux/highuid.h

## Purpose
`highuid.h` provides compatibility conversion helpers for systems or filesystems that need to represent UIDs/GIDs in old 16-bit forms. It defines overflow values for old user APIs and filesystem on-disk formats while keeping kernel-private code on full `uid_t`/`gid_t`.

## Important APIs, Types, And Functions
The key external variables are `overflowuid`, `overflowgid`, `fs_overflowuid`, and `fs_overflowgid`, with defaults set to 65534. Under `CONFIG_UID16`, `high2lowuid()`, `high2lowgid()`, `low2highuid()`, and `low2highgid()` perform old syscall compatibility conversion. `SET_UID()` and `SET_GID()` assign to possibly narrower fields through `__convert_uid()`/`__convert_gid()`. Filesystem helpers include `fs_high2lowuid()`, `fs_high2lowgid()`, `low_16_bits()`, and `high_16_bits()`.

## Control Flow And State
There is no runtime control flow beyond macro expansion. State is global overflow UID/GID policy, configurable elsewhere, and on-disk or userspace fields receiving converted IDs. High UIDs written to 16-bit filesystems are mapped to filesystem overflow IDs rather than truncated.

## Dependencies And Integration Points
It depends on kernel type definitions. It integrates with old system calls, architecture compatibility code, filesystem on-disk encoding, and UID/GID assignment sites that need field-width-aware conversion.

## Risks
Incorrect use can silently truncate or misrepresent ownership. Callers must use filesystem overflow helpers for 16-bit disk formats and old syscall helpers only for legacy userspace interfaces. The special `-1` handling in low-to-high conversion is required for chown/setreuid semantics.

## Test Signals
Test high UID/GID stat/chown behavior through old 16-bit APIs, filesystem write/read of high IDs on 16-bit formats, overflow sysctl/default behavior, and builds with `CONFIG_UID16` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/highuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hil.h -->
# sources/distributed-fs/ceph-client/include/linux/hil.h

## Purpose
`hil.h` defines Hewlett Packard Human Interface Loop protocol constants, packet layout, command codes, response decoding macros, locale names, keyboard translation tables, and poll record flags. It supports legacy HP-HIL input devices such as keyboards, mice, tablets, and other loop peripherals.

## Important APIs, Types, And Functions
`typedef u32 hil_packet` is the canonical packet representation. The file defines wire bit positions, packet bit masks, error/control bits, loop command enum values, device ID and describe-record masks, macros such as `HIL_IDD_LEN()`, `HIL_IDD_AXIS_MAX()`, `HIL_IDD_NUM_BUTTONS()`, `HIL_EXD_LEN()`, and `HIL_EXD_LOCALE()`, plus `HIL_LOCALE_MAP`, `HIL_KEYCODES_SET1`, `HIL_KEYCODES_SET3`, and `HIL_POL_*` poll flags.

## Control Flow And State
HIL controller and input drivers send commands, receive response records, decode device capabilities with IDD/EXD macros, map keyboard packets through static key tables, and interpret poll records for axes, buttons, character sets, status, and flow control. Loop state is external to this header and stored in HIL MLC/controller code.

## Dependencies And Integration Points
It includes architecture integer types and uses Linux input key codes in keycode tables, so implementation files must include input definitions appropriately. It integrates with `hil_mlc.h`, HP SDC MLC drivers, serio devices, and input subsystem device registration.

## Risks
Macros assume packet arrays in exact receive order and can read incorrect offsets if callers do not validate response lengths. `HIL_IDD_NUM_PROMPTS()` references `HIL_IDD_IOD_NPROMPT_MASK`, while the defined mask is `HIL_IDD_IOD_PROMPT_MASK`, so code paths using that macro may fail to compile or rely on an external definition. Legacy timing constants and raw packet bits are hardware-sensitive.

## Test Signals
Test HP-HIL autoconfiguration, IDD/EXD parsing, keyboard keycode translation, relative and absolute pointer reports, locale handling, malformed short records, loop error flags, and poll records with status pending or CTS set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hil_mlc.h -->
# sources/distributed-fs/ceph-client/include/linux/hil_mlc.h

## Purpose
`hil_mlc.h` defines the HP-HIL Master Link Controller abstraction and its state-engine nodes. It lets backend controller drivers implement low-level CTS/output/input operations while common MLC logic discovers devices, runs command sequences, and creates serio endpoints.

## Important APIs, Types, And Functions
Key definitions are `enum hilse_act`, `hilse_func`, `struct hilse_node`, backend callback typedefs `hil_mlc_cts`, `hil_mlc_out`, and `hil_mlc_in`, `struct hil_mlc_devinfo`, `struct hil_mlc_serio_map`, and `struct hil_mlc`. Public functions are `hil_mlc_register()` and `hil_mlc_unregister()`.

## Control Flow And State
The common MLC executes a state engine indexed by `seidx`. Nodes perform output, busy checks, input waits, expected-packet matching, last/discovery-device addressing, or callback functions. Semaphores signal loop idle, output dispatch, and input arrival. The controller tracks last operational device, discovery throttling, device info records, live device maps, serio devices, pending output packets, input packet buffers, timeouts, and a tasklet to drive progress.

## Dependencies And Integration Points
It depends on `hil.h`, time, interrupts, semaphores, serio, and lists. Backend drivers such as HP SDC MLC fill callback pointers and private data before registration. Serio children integrate discovered HIL devices with Linux input drivers.

## Risks
Risks include state-engine branch mistakes, timeout unit confusion (`suseconds_t` and usec args), semaphore imbalance, tasklet versus interrupt locking bugs, stale serio maps after reconfiguration, and overrun of fixed 16-entry device/info/input arrays. Discovery throttling fields must prevent endless loop reconfiguration storms.

## Test Signals
Test registration/unregistration, device discovery, lost-device reconfiguration, state-engine timeout/error branches, serio child creation/removal, concurrent interrupt input while output is pending, and backend failure injection for CTS/out/in callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hil_mlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hisi_acc_qm.h -->
# sources/distributed-fs/ceph-client/include/linux/hisi_acc_qm.h

## Purpose
`hisi_acc_qm.h` is the shared framework header for HiSilicon accelerator Queue Manager devices. It defines hardware register constants, mailbox and doorbell encodings, capabilities, queue-manager and queue-pair state, DMA buffers, debugfs/DFX state, error recovery hooks, SR-IOV/uacce integration, scatter-gather mapping helpers, and common lifecycle APIs.

## Important APIs, Types, And Functions
Major types include `struct hisi_qm`, `struct hisi_qp`, `struct hisi_qm_status`, `struct hisi_qp_status`, `struct hisi_qm_err_ini`, `struct hisi_qm_err_info`, `struct qm_debug`, `struct qm_err_isolate`, `struct qm_rsv_buf`, `struct hisi_qm_list`, and `struct hisi_qm_cap_tables`. Public APIs include `hisi_qm_init()`, `hisi_qm_start()`, `hisi_qm_stop()`, `hisi_qp_send()`, SR-IOV configure helpers, error handlers, mailbox helpers, SGL map/unmap and pool helpers, QP allocation/free, algorithm register/unregister, PM hooks, DFX access/register dump helpers, capability query helpers, and PF driver accessors for migration.

## Control Flow And State
PCI accelerator drivers initialize `hisi_qm`, allocate DMA rings for SQC/CQC/EQ/AEQ and queue pairs, configure capabilities, start the QM, register algorithms/uacce, and submit messages through QPs. Completion/event queues and polling work update queue state. Reset/error flows stop QPs or functions, collect DFX registers, isolate devices after thresholds, and recover or request reset based on `hisi_qm_err_ini` callbacks. SR-IOV paths configure PF/VF resources and VF state. Persistent runtime state spans MMIO bases, DMA addresses, IDR-managed QPs, locks, workqueues, debugfs files, atomic flags/counters, and capability tables.

## Dependencies And Integration Points
It depends on PCI, DMA, debugfs, iopoll, module parameters, bitfield helpers, uacce, crypto accelerator drivers, VFIO ACC live migration, workqueues, IDR, scatterlists, and PCI error recovery.

## Risks
Risks include hardware register bit drift between QM versions, queue-depth/base mismatch, mailbox timeout/deadlock, DMA mapping leaks, QP state races during reset, SR-IOV PF/VF resource accounting errors, uacce SVA mode validation, debugfs access during reset, and module parameter bounds. Error isolation state needs correct locking to avoid masking recoverable devices or continuing on fatal ECC.

## Test Signals
Run accelerator driver probe/remove, QP allocation/send/completion, mailbox read/write timeout injection, SR-IOV enable/disable/configure, PCI error recovery, suspend/resume, reset storms, debugfs DFX reads/clears, SGL map/unmap under DMA API debug, uacce mode validation, and VFIO migration PF driver lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hisi_acc_qm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hmm-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/hmm-dma.h

## Purpose
`hmm-dma.h` defines a small DMA mapping helper interface for HMM PFN arrays. It lets device drivers allocate parallel PFN and DMA-address arrays, map individual HMM PFNs including P2P DMA cases, and unmap them later.

## Important APIs, Types, And Functions
`struct hmm_dma_map` contains `struct dma_iova_state state`, `unsigned long *pfn_list`, `dma_addr_t *dma_list`, and `dma_entry_size`. Public functions are `hmm_dma_map_alloc()`, `hmm_dma_map_free()`, `hmm_dma_map_pfn()`, and `hmm_dma_unmap_pfn()`.

## Control Flow And State
A driver allocates an HMM DMA map for a range, fills or receives PFNs from HMM faulting, maps PFNs by index to DMA addresses, stores results in `dma_list`, and unmaps indices when no longer needed. Mapping may use `pci_p2pdma_map_state` for peer-to-peer memory. State is the allocated arrays, IOVA state, per-entry DMA addresses, and implicit DMA API mappings.

## Dependencies And Integration Points
It depends on `linux/dma-mapping.h`, forward-declared `dma_iova_state`, and PCI P2PDMA map state. It integrates with `hmm.h` range-fault results and device DMA APIs.

## Risks
Risks include mismatched entry size, double map/unmap, forgetting to unmap on partial failure, stale DMA addresses after MMU invalidation, and treating P2P/bus-mapped PFNs as ordinary system memory. The caller must coordinate HMM validity and DMA lifetime.

## Test Signals
Test allocation/free, mapping normal system PFNs, P2P PFNs and bus mappings, partial failure unwind, DMA API debug, repeated map/unmap of the same index, and MMU invalidation while device access is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hmm-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hmm.h -->
# sources/distributed-fs/ceph-client/include/linux/hmm.h

## Purpose
`hmm.h` defines the Heterogeneous Memory Management range-fault interface used by devices to mirror CPU virtual address ranges into device page tables. It describes PFN flag encoding, conversion helpers, `struct hmm_range`, and `hmm_range_fault()`.

## Important APIs, Types, And Functions
`enum hmm_pfn_flags` defines output flags such as `HMM_PFN_VALID`, `HMM_PFN_WRITE`, `HMM_PFN_ERROR`, `HMM_PFN_DMA_MAPPED`, `HMM_PFN_P2PDMA`, and `HMM_PFN_P2PDMA_BUS`, plus input request flags `HMM_PFN_REQ_FAULT` and `HMM_PFN_REQ_WRITE`. Helpers `hmm_pfn_to_page()`, `hmm_pfn_to_phys()`, and `hmm_pfn_to_map_order()` extract page, physical address, and mapping order. `struct hmm_range` stores notifier, sequence, virtual range, PFN array, default flags, mask, and device-private owner. `hmm_range_fault()` populates the range.

## Control Flow And State
Drivers register/use an `mmu_interval_notifier`, begin an interval read, fill an `hmm_range`, call `hmm_range_fault()`, consume PFN results under the caller lock, and retry if notifier sequence invalidates. Input flags request faulting and write access. Output flags report current validity/access/error/P2P state. Persistent state is in the caller's PFN array and the MMU notifier sequence.

## Dependencies And Integration Points
It depends on `linux/mm.h` and MMU interval notifiers. It integrates with GPU/accelerator drivers, device-private memory migration, P2PDMA, DMA mapping helpers, and process address-space invalidation.

## Risks
Risks include consuming PFNs outside the notifier-read critical section, missing invalidation retry, confusing input request bits with output validity bits, ignoring `HMM_PFN_ERROR`, using `hmm_pfn_to_page()` before checking valid, and mishandling high-order mapping edge cases whose aligned extent may exceed the requested range.

## Test Signals
Use HMM selftests and device driver tests for read/write faults, no-fault queries, invalid VMA/special/poisoned pages, device-private owner filtering, P2PDMA flags, high-order mappings, concurrent munmap/mprotect/migration, and default flag masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/host1x.h -->
# sources/distributed-fs/ceph-client/include/linux/host1x.h

## Purpose
`host1x.h` defines the public interface for NVIDIA Tegra host1x clients, buffer objects, syncpoints, channels, jobs, logical host1x devices, and memory contexts. It is used by DRM/media/accelerator drivers that submit command streams through host1x engines.

## Important APIs, Types, And Functions
Core types include `enum host1x_class`, `struct host1x_client`, `struct host1x_client_ops`, `struct host1x_bo`, `struct host1x_bo_mapping`, `struct host1x_bo_ops`, `struct host1x_syncpt`, `struct host1x_channel`, `struct host1x_job`, `struct host1x_reloc`, `struct host1x_driver`, `struct host1x_device`, and `struct host1x_memory_context`. Public APIs cover DMA mask lookup, BO cache init/destroy, BO pin/unpin/mmap, syncpoint lookup/read/increment/wait/alloc/request/fence creation, channel request/get/stop/put, job allocation/add gather/add wait/get/put/pin/unpin/submit, host1x driver registration, client registration/suspend/resume, device init/exit, and IOMMU-backed memory context allocation/reference management.

## Control Flow And State
Client drivers initialize/register `host1x_client`, request channels and syncpoints, allocate jobs, add command gathers/relocations/waits, pin buffer objects, submit jobs, and track completion through syncpoints and DMA fences. BO mappings may be cached until explicitly released. Logical devices group subdevices and clients. Memory contexts provide stream IDs for engine isolation when IOMMU support is enabled. State persists in client use counts/locks/cache, BO mapping refs and DMA addresses, job refs/fences/pinned buffers, syncpoint thresholds, and device client lists.

## Dependencies And Integration Points
It depends on Linux device model, DMA direction/fence APIs, spinlocks/mutexes/krefs/refcounts, IOMMU groups, OF IDs, and DMA-buf attachments. It integrates Tegra DRM/KMS, media engines, IOMMU context bus, and scheduler/fence users.

## Risks
Risks include BO mapping cache leaks, refcount imbalance, stale DMA mappings, relocation validation/firewall bypass, syncpoint timeout/recovery mistakes, job cancellation races, IOMMU stream ID misprogramming, and client registration double-initialization. The BO cache is not automatically evicted, so owners must release cached mappings.

## Test Signals
Test client probe/remove, multi-engine logical devices, job submit/completion/timeout, syncpoint waits and fences, BO pin/unpin cache reuse and teardown, relocation firewall validation, suspend/resume, memory context allocation with and without IOMMU, and DMA API debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/host1x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/host1x_context_bus.h -->
# sources/distributed-fs/ceph-client/include/linux/host1x_context_bus.h

## Purpose
`host1x_context_bus.h` declares the optional host1x context device bus type used for Tegra host1x memory/context isolation devices.

## Important APIs, Types, And Functions
When `CONFIG_TEGRA_HOST1X_CONTEXT_BUS` is enabled, it declares `extern const struct bus_type host1x_context_device_bus_type`. There are no other functions or structures.

## Control Flow And State
There is no local control flow. Bus registration and device matching happen in the implementation guarded by the same config option. State is owned by the Linux device model and host1x context device code.

## Dependencies And Integration Points
It includes `linux/device.h` for `struct bus_type`. It integrates with `host1x_memory_context` and drivers that need a distinct context-device bus for IOMMU or stream-ID handling.

## Risks
Consumers must guard references with the same config or otherwise avoid unresolved symbols. The header intentionally exposes only the bus symbol, so behavior changes belong in the bus implementation.

## Test Signals
Build with `CONFIG_TEGRA_HOST1X_CONTEXT_BUS=y/m/n`, verify context devices bind on the bus when enabled, and confirm no symbol references remain in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/host1x_context_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hp_sdc.h -->
# sources/distributed-fs/ceph-client/include/linux/hp_sdc.h

## Purpose
`hp_sdc.h` defines the HP i8042 System Device Controller interface used on legacy HP systems for timer, HIL, cooked keyboard, RTC/beeper, and controller register access. It describes IRQ hook registration, queued SDC transactions, action flags, status/command/register constants, and the `hp_i8042_sdc` runtime state.

## Important APIs, Types, And Functions
Public callback type `hp_sdc_irqhook` receives irq, device ID, status, and data. Registration helpers request/release timer, HIL, and cooked IRQ hooks. `hp_sdc_transaction` describes queued command/data sequences with callback or semaphore completion. Queue APIs are `__hp_sdc_enqueue_transaction()`, `hp_sdc_enqueue_transaction()`, and `hp_sdc_dequeue_transaction()`. `hp_i8042_sdc` stores locks, IRQ/NMI lines, IO ports, interrupt mask, controller register cache, hook pointers, transaction queue, read/write progress, device pointer, kicker timer, and tasklet.

## Control Flow And State
Clients enqueue transactions consisting of atomic acts. The SDC driver serializes command/data register access, handles status interrupts, calls hooks in IRQ/tasklet context, signals semaphores for synchronous transactions, and uses a tasklet/timer kicker to keep progress moving. State persists in interrupt masks, pending transaction queue, current read/write indices, cached i8042 registers, hook lists, and architecture device registration data.

## Dependencies And Integration Points
It depends on interrupt, timer, time, types, and HPPA or m68k architecture device support. It integrates with HP-HIL MLC, keyboard input, timer/RTC/beeper support, and low-level IO port access.

## Risks
Risks include transaction queue overflow, action flag misuse such as combining data input with deallocation in one act, interrupt mask races, IBF polling timeout, tasklet/use-after-free during unregister, and architecture guard failures on unsupported platforms. Hook callbacks may run in interrupt or tasklet context and must not sleep.

## Test Signals
Test IRQ hook register/release, synchronous and callback transactions, dequeue/cancel, HIL command/data routing, timer status interrupts, RTC/beeper commands, IBF timeout handling, queue full behavior, and probe/build on supported HPPA/m68k configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hp_sdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hpet.h -->
# sources/distributed-fs/ceph-client/include/linux/hpet.h

## Purpose
`hpet.h` defines kernel HPET register layout and allocation metadata. It mirrors the memory-mapped HPET block, timer register fields, capability/configuration masks, and the data structure used when registering an HPET instance.

## Important APIs, Types, And Functions
`struct hpet` models the HPET MMIO register block with capability, configuration, interrupt status, main counter, and flexible timer array. Nested `struct hpet_timer` models timer config/compare/FSB registers. `struct hpet_data` stores physical/MMIO address, IRQ count, allocation bitmask, and IRQ numbers. `hpet_reserve_timer()` marks a timer allocated, and `hpet_alloc()` registers/allocates an HPET described by `hpet_data`.

## Control Flow And State
Platform code fills `hpet_data`, reserves timers as needed, and calls `hpet_alloc()`. HPET implementation code maps registers, reads capabilities, configures counters/timers, routes interrupts, and records allocated timers in `hd_state`. Hardware state persists in MMIO registers; software state persists in `hpet_data`.

## Dependencies And Integration Points
It includes `uapi/linux/hpet.h` and uses `void __iomem`. It integrates with platform/ACPI discovery, clocksource/clockevent setup, interrupt routing, and the legacy HPET userspace API.

## Risks
Risks include incorrect MMIO structure assumptions, 32-bit versus 64-bit counter access, timer count/IRQ bounds, FSB routing bit mistakes, and allocation bit overflow if timer indices exceed supported width. Register fields are hardware ABI and must not be renumbered.

## Test Signals
Test HPET discovery/allocation, reserved timer masks, clockevent operation, periodic/one-shot timers, 32-bit counter mode, FSB interrupt routing, interrupt status clearing, and systems with maximum timer counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hpet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer.h -->
# sources/distributed-fs/ceph-client/include/linux/hrtimer.h

## Purpose
`hrtimer.h` is the public high-resolution timer API. It combines mode definitions, sleeper support, expiry manipulation helpers, high-resolution enablement hooks, timerfd notifications, initialization/start/cancel/query/forward APIs, precise sleep helpers, queue execution, CPU hotplug hooks, and debug/sysrq support.

## Important APIs, Types, And Functions
`enum hrtimer_mode` defines absolute/relative, pinned, soft/hard, and lazy-rearm modes. `struct hrtimer_sleeper` combines a timer with a task pointer. Important helpers include `hrtimer_set_expires*()`, `hrtimer_add_expires*()`, `hrtimer_get_expires()`, `hrtimer_cb_get_time()`, `hrtimer_expires_remaining*()`, `hrtimer_setup()`, `hrtimer_setup_on_stack()`, `hrtimer_start_range_ns()`, `hrtimer_start()`, `hrtimer_cancel()`, `hrtimer_try_to_cancel()`, `hrtimer_start_expires()`, `hrtimer_get_remaining()`, `hrtimer_active()`, `hrtimer_is_queued()`, `hrtimer_update_function()`, `hrtimer_forward()`, `hrtimer_forward_now()`, nanosleep/schedule timeout helpers, `hrtimer_run_queues()`, `hrtimers_init()`, and CPU hotplug functions.

## Control Flow And State
Callers initialize a timer with callback, clock ID, and mode; set/start expiry; the timerqueue stores it on a per-CPU/per-clock base; clockevent interrupts or softirq processing run callbacks; callbacks return restart or no-restart. Sleepers wake tasks by clearing the task pointer. Relative low-resolution timers adjust remaining time for added resolution slack. State lives in `struct hrtimer`, per-CPU bases, active timer queues, running callback pointers, highres static key, timerfd notifications, and CPU hotplug state.

## Dependencies And Integration Points
It depends on `hrtimer_defs.h`, `hrtimer_rearm.h`, `hrtimer_types.h`, ktime, timerqueue, percpu tick devices, PREEMPT_RT, timerfd, clockevents, scheduler sleep, and CPU hotplug.

## Risks
Risks include cancel races with running callbacks, updating functions while queued, mode confusion between soft/hard on RT, lazy rearm causing extra expiry, wrong absolute/relative mode, and using lockless queue state as stable truth. On-stack timers need debug-object destruction.

## Test Signals
Run hrtimer selftests, nanosleep/schedule_hrtimeout tests, timerfd clock-set/resume tests, PREEMPT_RT cancel/wait paths, CPU hotplug migration, highres enabled/disabled builds, lazy hrtick rearm behavior, and callback restart/forward loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_api.h -->
# sources/distributed-fs/ceph-client/include/linux/hrtimer_api.h

## Purpose
`hrtimer_api.h` is a compatibility/convenience shim that includes `linux/hrtimer.h`. It provides no independent API beyond re-exporting the main hrtimer declarations.

## Important APIs, Types, And Functions
There are no local types or functions. Including this header is equivalent to including `linux/hrtimer.h`.

## Control Flow And State
There is no control flow or state in this file. All behavior comes from `hrtimer.h` and its included support headers.

## Dependencies And Integration Points
It depends directly on `linux/hrtimer.h`. It exists for include-path compatibility with code that expects an `hrtimer_api.h` name.

## Risks
The only practical risk is include recursion or unnecessary layering if hrtimer headers are reorganized. Removing it can break source compatibility for existing include users.

## Test Signals
Build all users that include `linux/hrtimer_api.h` and verify they see the same hrtimer symbols as direct `linux/hrtimer.h` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/hrtimer_defs.h

## Purpose
`hrtimer_defs.h` defines the internal per-clock and per-CPU base structures that organize hrtimers. These structures back the public hrtimer API but are split out so type definitions can be shared without pulling in the full API.

## Important APIs, Types, And Functions
`struct hrtimer_clock_base` stores the owning CPU base, base index, clock ID, sequence counter, next expiry, running timer pointer, active timerqueue head, and clock offset. `enum hrtimer_base_type` enumerates monotonic, realtime, boottime, TAI, and soft variants. `struct hrtimer_cpu_base` stores the raw spinlock, CPU number, active base bitmap, clock-set sequence, high-resolution/deferred/online/softirq state, highres statistics, PREEMPT_RT wait/softirq locks, next expiry/timer caches, deferred expiry cache, clock base array, and call-single data.

## Control Flow And State
Hrtimer enqueue/dequeue/interrupt paths lock the CPU base, choose a clock base, insert/remove timerqueue nodes, update next-expiry caches, run callbacks, and coordinate highres clockevent programming. Clock-set and CPU hotplug paths update sequence and online/migration state. PREEMPT_RT adds softirq expiry and cancel-wait state.

## Dependencies And Integration Points
It depends on ktime, timerqueue, seqlock, raw spinlocks, per-CPU call-single data, high-resolution timer config, and PREEMPT_RT. `hrtimer.h` includes it.

## Risks
These structures are concurrency-critical. Risks include false sharing/alignment regressions, stale `next_timer` dereference despite comments saying it is only an optimization, sequence counter misuse around running callbacks, and missing updates to active/next expiry state when adding new base types.

## Test Signals
Stress timer enqueue/cancel/run under CPU hotplug, clock changes, PREEMPT_RT, highres interrupts, soft timers, deferred rearm, and lockdep/RT lock validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_rearm.h -->
# sources/distributed-fs/ceph-client/include/linux/hrtimer_rearm.h

## Purpose
`hrtimer_rearm.h` defines optional deferred hrtimer rearm hooks used when `CONFIG_HRTIMER_REARM_DEFERRED` is enabled. It allows CPU-local timer reprogramming to be deferred until safe exit or scheduling points, reducing expensive clockevent reprogramming in some paths.

## Important APIs, Types, And Functions
Enabled builds declare `__hrtimer_rearm_deferred()` and define inline helpers `hrtimer_test_and_clear_rearm_deferred_tif()`, `hrtimer_rearm_deferred_user_irq()`, `hrtimer_rearm_deferred_tif()`, `hrtimer_rearm_deferred()`, and `hrtimer_test_and_clear_rearm_deferred()`. `TIF_REARM_MASK` combines reschedule and hrtimer rearm thread flags. Disabled builds provide no-op/false stubs.

## Control Flow And State
The current thread's `_TIF_HRTIMER_REARM` flag signals that rearm work is pending. IRQ/user exit and scheduler paths test and clear the flag with interrupts disabled, optionally invoke `__hrtimer_rearm_deferred()`, and avoid entering slower loops when rearm was the only pending work. State is CPU-local and stored in thread flags plus hrtimer CPU-base deferred fields.

## Dependencies And Integration Points
It depends on `linux/thread_info.h` when enabled, thread flag helpers, lockdep IRQ assertions, scheduler exit-to-user paths, irqentry exit, and hrtick/time-slice extension logic.

## Risks
Risks include calling with interrupts enabled, missing rearm when reschedule flags are also present, clearing the wrong thread flag, or making assumptions in disabled configs where helpers are no-ops. Since it participates in scheduler/interrupt return paths, small ordering bugs can cause lost timer interrupts or unnecessary latency.

## Test Signals
Test with `CONFIG_HRTIMER_REARM_DEFERRED` on and off, scheduler hrtick workloads, user/IRQ exit paths, reschedule flag combinations, lockdep IRQ assertions, and virtualized workloads sensitive to clockevent reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_rearm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_types.h -->
# sources/distributed-fs/ceph-client/include/linux/hrtimer_types.h

## Purpose
`hrtimer_types.h` defines the basic hrtimer object and callback return values, separated from the larger hrtimer API to reduce include coupling.

## Important APIs, Types, And Functions
`enum hrtimer_restart` has `HRTIMER_NORESTART` and `HRTIMER_RESTART` callback outcomes. `struct hrtimer` contains a timerqueue node with expiry, a clock-base pointer, flags for queued/relative/soft/hard/lazy state, `_softexpires`, and the private callback function pointer.

## Control Flow And State
Hrtimer code initializes this structure, inserts `node` into a timerqueue, sets `base`, tracks queued state, records mode-derived flags, and invokes `function` when expired. Callback return controls whether the timer is rearmed. `_softexpires` is the earliest expiry while `node.expires` may include slack.

## Dependencies And Integration Points
It depends on basic types and timerqueue types. It integrates with `hrtimer_defs.h` per-CPU bases and `hrtimer.h` public operations.

## Risks
Risks include direct field manipulation by callers instead of using APIs, callback pointer update while queued, confusing hard and soft expiry, and stale `base` assumptions after migration. The callback is marked `__private`, signaling callers should use provided helpers.

## Test Signals
Build all hrtimer users, run callback restart/no-restart tests, slack/range timer tests, migration/cancel tests, and compile checks that discourage direct private callback access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hrtimer_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hsi/hsi.h -->
# sources/distributed-fs/ceph-client/include/linux/hsi/hsi.h

## Purpose
`hsi/hsi.h` defines the High Speed Synchronous Serial Interface core API. It models HSI controllers, ports, clients, board info, TX/RX configuration, messages, port events, and client-driver registration.

## Important APIs, Types, And Functions
Important definitions include HSI message transfer types, configuration enums for stream/frame mode, synchronized/pipelined flow, round-robin/priority arbitration, message status values, and port event IDs. Core structures are `struct hsi_channel`, `struct hsi_config`, `struct hsi_board_info`, `struct hsi_client`, `struct hsi_client_driver`, `struct hsi_msg`, `struct hsi_port`, and `struct hsi_controller`. APIs include board info registration, port event register/unregister, client-driver register/unregister, message alloc/free, controller alloc/register/unregister, client creation/removal, DT client addition, `hsi_async()`, channel-name lookup, port claim/release, setup/flush, async read/write, and start/stop TX.

## Control Flow And State
Controller drivers allocate/register controllers and ports. Board info or DT creates clients under ports. Client drivers claim a port, configure TX/RX parameters, register event handlers, allocate scatterlist-backed messages, submit async reads/writes, start/stop TX, and receive completion callbacks. Ports serialize claims with a mutex, track shared/claimed state, hold current TX/RX config, invoke controller callbacks, and notify clients through a blocking notifier chain.

## Dependencies And Integration Points
It depends on the Linux device model, mutexes, scatterlists, lists, modules, and notifier chains. It integrates HSI controller drivers, HSI client protocol drivers, platform data/DT enumeration, and DMA-capable async transfer implementations.

## Risks
Risks include submitting operations without claiming the port, incompatible shared-port configurations, message lifetime and destructor ordering during flush, scatterlist ownership mistakes, notifier callback sleepability assumptions, and concurrent start/stop TX races. Inline helpers return `-EACCES` when the port is not claimed.

## Test Signals
Test controller registration, DT/board client creation, claim/release exclusive and shared modes, setup/flush permission failures, async read/write completion/error/destructor paths, port event notification, start/stop TX, and remove while messages are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hsi/hsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hsi/ssi_protocol.h -->
# sources/distributed-fs/ceph-client/include/linux/hsi/ssi_protocol.h

## Purpose
`hsi/ssi_protocol.h` declares helper hooks for SSIP slave support on top of the HSI core. It coordinates slave/master relationships, TX start/stop, reset events, running state, and wake-test control.

## Important APIs, Types, And Functions
The file declares `ssip_slave_get_master()`, `ssip_slave_start_tx()`, `ssip_slave_stop_tx()`, `ssip_reset_event()`, `ssip_slave_running()`, and `ssi_waketest()`. `ssip_slave_put_master()` is currently an empty inline helper. All APIs operate on `struct hsi_client *`.

## Control Flow And State
Slave protocol clients obtain their master client, request TX start/stop through the master, notify reset events, query running state, and optionally enable wake-test behavior. State is owned by the SSIP implementation and HSI client driver data, not this header.

## Dependencies And Integration Points
It includes `linux/hsi/hsi.h` and integrates with HSI client drivers implementing SSIP master/slave protocols.

## Risks
Risks include null or stale master pointers, unbalanced get/put semantics because `ssip_slave_put_master()` is a no-op, TX state races around reset, and callers assuming wake-test exists on all controllers.

## Test Signals
Test slave/master lookup, start/stop TX sequencing, reset event delivery, running-state transitions, wake-test toggling, and remove paths with outstanding master references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hsi/ssi_protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hte.h -->
# sources/distributed-fs/ceph-client/include/linux/hte.h

## Purpose
`hte.h` defines the Hardware Timestamp Engine provider/consumer API. It lets providers register timestamp-capable chips and consumers request timestamping for logical lines, receive primary non-sleeping callbacks, optionally run secondary sleepable callbacks, enable/disable timestamps, and query clock source information.

## Important APIs, Types, And Functions
Important types are `enum hte_edge`, `enum hte_return`, `struct hte_ts_data`, `struct hte_clk_info`, callback typedefs `hte_ts_cb_t` and `hte_ts_sec_cb_t`, `struct hte_line_attr`, `struct hte_ts_desc`, `struct hte_ops`, and `struct hte_chip`. Enabled APIs include `devm_hte_register_chip()`, `hte_push_ts_ns()`, `hte_init_line_attr()`, `hte_ts_get()`, `hte_ts_put()`, `hte_request_ts_ns()`, `devm_hte_request_ts_ns()`, `of_hte_req_count()`, `hte_enable_ts()`, `hte_disable_ts()`, and `hte_get_clk_src_info()`. Disabled builds return `-EOPNOTSUPP`.

## Control Flow And State
Providers populate `hte_chip` with operations, line count, translation callbacks, and private data, then register it. Consumers initialize a descriptor, acquire a timestamp line from DT or platform data, request callbacks, and enable timestamping. Providers push timestamp data with translated line IDs. The HTE core invokes primary callbacks in non-sleeping context and runs secondary callbacks when requested. State persists in descriptors' subsystem private data, provider chip registration, line attributes, callback bindings, and clock metadata.

## Dependencies And Integration Points
It depends on errno, device model types, OF phandle arguments, clock IDs, and optional `CONFIG_HTE`. It integrates with GPIO/IRQ-like timestamp providers and consumers that need accurate edge timestamps.

## Risks
Risks include invalid line translation, edge flag mismatch with consumer IRQ setup, sleeping in primary callbacks, stale descriptor `hte_data` after put, provider pushing timestamps after unregister, sequence counter wrap assumptions, and disabled-config API signature mismatch: the stub for `hte_push_ts_ns()` takes `const struct hte_ts_data *` while the enabled declaration takes non-const.

## Test Signals
Test provider registration/unregistration, DT and platform line translation, request/put lifecycle, primary and secondary callback paths, enable/disable, rising/falling/no-setup edge modes, clock source query, timestamp sequence ordering, provider push after disable, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hte.h -->
