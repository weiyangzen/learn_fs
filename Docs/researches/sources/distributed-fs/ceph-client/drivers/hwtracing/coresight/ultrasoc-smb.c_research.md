# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.c

## Purpose

`ultrasoc-smb.c` implements the Siemens/UltraSoc System Memory Buffer as a CoreSight sink. It configures the hardware logical buffer, exposes a miscdevice for sysfs-style reads, supports perf AUX copying, and uses ACPI DSM calls to enable or disable upstream UltraSoc hardware.

## Important APIs, Types, and Functions

Buffer helpers are `smb_buffer_not_empty`, `smb_update_data_size`, `smb_update_read_ptr`, and `smb_reset_buffer`. File operations are `smb_open`, `smb_read`, and `smb_release`. CoreSight sink operations are `smb_enable`, `smb_disable`, `smb_alloc_buffer`, `smb_free_buffer`, and `smb_update_buffer`. Probe helpers include `smb_init_data_buffer`, `smb_init_hw`, `smb_register_sink`, and `smb_config_inport`.

## Control Flow

Probe maps register space, initializes hardware defaults, maps the data buffer resource with write-back memory, enables upstream hardware with ACPI DSM, resets the buffer, initializes locking and pid state, registers a CoreSight buffer sink, and registers a miscdevice. Sysfs/misc reads are mutually exclusive with active CoreSight capture. Perf enable associates the sink with the event owner pid and enables hardware. Perf update disables hardware, calculates available circular data, trims to perf AUX size if needed, copies into perf pages, resets the SMB, and reports truncation when not in snapshot mode.

## State and Persistence Behavior

`smb_drv_data` persists MMIO base, CoreSight device, buffer mapping, miscdevice, raw spinlock, reading flag, and owner pid. `smb_data_buffer` tracks hardware base, CPU mapping, total size, data size, and read pointer. Hardware read pointer is updated after every copied or discarded segment.

## Dependencies and Integration Points

The driver depends on platform ACPI matching (`HISI03A1`), CoreSight sink APIs, perf AUX `cs_buffers`, circular buffer macros, miscdevice, memremap, and ACPI DSM UUID `82ae1283-7f6a-4cbe-aa06-53e8fb24db18`.

## Risks and Edge Cases

The driver assumes a 32-bit buffer hardware base. It serializes reads and tracing with `raw_spinlock`, but copy-to-user occurs outside that lock in `smb_read` after open-time exclusion. Perf copying must handle circular wrap correctly and advances the hardware read pointer destructively. ACPI DSM failure prevents probe.

## Test Signals

Test probe resource validation, DSM enable/disable, misc open rejection during capture, duplicate open rejection, circular read wrap, buffer-full detection, perf truncation, snapshot behavior, register sysfs reads, and remove cleanup ordering.
