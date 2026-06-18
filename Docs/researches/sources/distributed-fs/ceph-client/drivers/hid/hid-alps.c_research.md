# sources/distributed-fs/ceph-client/drivers/hid/hid-alps.c

## Purpose

`hid-alps.c` is an ALPS HID touchpad and DualPoint driver. It bypasses generic HID input mapping, initializes ALPS-specific register modes through HID feature reports, decodes raw touch reports, and optionally registers a second input device for a pointing stick. It supports U1-family devices and T4 buttonless devices, each with different register protocols and report layouts.

## Important APIs, Types, and Functions

- `struct alps_dev` stores the primary input device, optional stick input device, HID device, detected ALPS family, max finger count, stick support, button metadata, active dimensions, coordinate ranges, and button counts.
- `struct t4_contact_data` and `struct t4_input_report` model the packed T4 input report used by `t4_raw_event()`.
- `t4_calc_check_sum()` computes the T4 command/report checksum over bounded feature-report ranges.
- `t4_read_write_register()` and `u1_read_write_register()` implement family-specific register read/write commands over HID feature reports via `hid_hw_raw_request()`.
- `T4_init()` and `u1_init()` switch devices into absolute reporting modes, read geometry and button configuration, and populate `struct alps_dev`.
- `t4_raw_event()` decodes T4 multitouch contacts, inverts Y into the configured coordinate range, reports pressure, button state, and MT slots.
- `u1_raw_event()` handles U1 touch reports, feature/mouse report IDs, and stick absolute reports converted into relative `REL_X` and `REL_Y`.
- `alps_input_configured()` opens the low-level device, starts HID I/O, initializes hardware, configures input axes/buttons/MT slots, and registers the optional stick input device.
- `alps_post_reset()` and `alps_post_resume()` restore absolute reporting modes after reset or resume.

## Control Flow

Probe allocates `struct alps_dev`, stores it as HID driver data, sets `HID_QUIRK_NO_INIT_REPORTS`, parses the HID descriptor, classifies the product as T4, U1, or unknown, and starts hardware with `HID_CONNECT_DEFAULT`.

The driver returns `-1` from `alps_input_mapping()` so generic HID usages are not mapped into ordinary input events. Instead, `alps_input_configured()` takes over after the HID input device exists. It opens the HID hardware, calls `hid_device_io_start()` to permit report traffic, runs `T4_init()` or `u1_init()`, then configures the primary input device with multitouch axes, pressure, button capabilities, resolution if known, and `INPUT_MT_POINTER` slots. If U1 initialization detected stick support, it allocates and registers a second input device named `DualPoint Stick` with relative axes, stick properties, and button bits. Finally it stops temporary I/O and closes the HID hardware; normal input open/close later controls the device.

Raw report flow is centralized in `alps_raw_event()`. It ignores reports unless HID input is claimed and the primary input device is ready. T4 products dispatch to `t4_raw_event()`; all others dispatch to `u1_raw_event()`. Each decoder reports MT slot state and synchronizes the input device, returning `1` when it consumed a report and `0` for ignored report IDs.

## State and Persistence Behavior

`struct alps_dev` persists for the HID device lifetime and is devm-managed. Geometry, button counts, family type, and stick presence are read during input configuration and reused by the raw event path. Hardware reporting mode is persistent device state: initialization writes registers to enable absolute touchpad mode and, for supported U1 devices, stick absolute mode. Resume and reset paths rewrite those mode bits because firmware or power transitions can clear them.

The optional stick input device is manually allocated with `input_allocate_device()` and registered through the input core. Once registered, the input subsystem owns it; on registration failure it is freed locally. The primary device is owned by the HID input path.

## Dependencies and Integration Points

- Depends on HID core parsing, raw feature requests, report open/close, PM hooks, and `hid-ids.h` ALPS IDs.
- Depends on the input subsystem for multitouch slots, absolute axes, pressure, relative stick movement, button bits, and input properties.
- Uses unaligned helpers for U1 register addresses and report fields; T4 verification currently reads some fields through casts.
- Integrates with power management through `.resume = pm_ptr(alps_post_resume)` and `.reset_resume = pm_ptr(alps_post_reset)`.
- Uses `HID_QUIRK_NO_INIT_REPORTS` to avoid generic initialization reports that may disturb device state.

## Risks and Edge Cases

- T4 readback validation uses direct casts such as `*(u32 *)&readbuf[6]` and `*(u16 *)&readbuf[10]`, which can be unaligned and endian-sensitive. U1 uses `put_unaligned_le32()` for writes, but T4 validation does not use `get_unaligned_le*()`.
- `t4_calc_check_sum()` rejects `offset + length >= 50`, so exactly boundary-sized checks return zero. That may be intentional for report limits but should be validated against the hardware protocol.
- `t4_raw_event()` casts raw report bytes directly to `struct t4_input_report`; layout padding assumptions matter even though the field order is byte-heavy with a trailing `u16`.
- Raw event decoders do limited `size` validation. They assume report lengths match the selected family before indexing contact arrays and fixed offsets.
- Unknown products still start hardware and dispatch to U1 raw decoding by default in `alps_raw_event()`, although the match table only lists known IDs.
- `input_mt_init_slots()` return value is not checked. Allocation failure could leave later MT reporting misconfigured.
- The second stick device has a fixed `BUS_I2C` bustype even though the HID transport may be broader because IDs match `HID_BUS_ANY`.

## Test Signals

- Feature-report tests should verify U1 and T4 register read/write framing, checksum generation, readback validation, and error handling on bad checksum/address/size.
- Initialization tests should check that U1 absolute mode, U1 stick mode, and T4 advanced absolute mode are written during configuration and restored after resume/reset.
- Raw report tests should feed U1 multitouch, U1 stick, and T4 reports with active and inactive contacts and verify MT slot state, pressure, button events, coordinate inversion for T4, and input synchronization.
- Device capability tests should confirm coordinate min/max/resolution, pressure range, buttonpad property, button count, and optional stick input registration.
- Robustness tests should fuzz short reports and malformed report IDs to catch out-of-bounds access in raw event handlers.
- Manual testing on supported ALPS hardware should verify touch movement, click buttons, suspend/resume recovery, and DualPoint stick open/close behavior.
