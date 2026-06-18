# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_ch_setup.h

## Purpose

`hgsmi_ch_setup.h` defines HGSMI setup-channel command and host-flag structures used by the guest to tell the VirtualBox host where to write event flags.

## Important APIs, Types, and Functions

- `HGSMI_CC_HOST_FLAGS_LOCATION`: setup command id for host flags location reporting.
- `struct hgsmi_buffer_location`: guest VRAM offset and length pair sent to the host.
- `HGSMIHOSTFLAGS_*`: bits for pending commands, IRQ, VSYNC, hotplug, and cursor capability notifications.
- `struct hgsmi_host_flags`: 16-byte shared flag block written by the host.

## Control Flow

`hgsmi_report_flags_location` sends `struct hgsmi_buffer_location` on the HGSMI setup channel. IRQ code later reads `struct hgsmi_host_flags` at the configured guest-heap offset.

## State and Persistence Behavior

The definitions describe a persistent shared-memory contract. The host owns writes to `host_flags`; the guest reads and clears IRQ state through I/O ports.

## Dependencies and Integration Points

Used by `vbox_drv.h`, `hgsmi_base.c`, `vbox_irq.c`, and hardware init/mode probing. The offsets interact with `GUEST_HEAP_OFFSET` and `HOST_FLAGS_OFFSET` in `vbox_drv.h`.

## Risks and Edge Cases

Changing structure packing, size, or bit values would break the VirtualBox host ABI. IRQ handling also relies on historical behavior where some flags may not be cleared independently.

## Test Signals

Verify packed structure sizes, host flag offset reporting, hotplug/cursor capability IRQ delivery, and no regressions with older hosts that keep hotplug flags set.
