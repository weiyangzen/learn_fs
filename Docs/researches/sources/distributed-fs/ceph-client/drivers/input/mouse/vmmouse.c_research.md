<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.c

## Purpose
`vmmouse.c` implements the VMware/QEMU virtual PS/2 mouse protocol. It detects the hypervisor channel, enables absolute pointer mode, creates a second input device for absolute coordinates, and multiplexes button state between relative and absolute devices.

## Important APIs, Types, and Functions
Public entry points are `vmmouse_detect()` and `vmmouse_init()`. `struct vmmouse_data` stores the absolute input device and names. Hypervisor interaction is done with `vmware_hypercall*()` commands in `vmmouse_enable()`, `vmmouse_disable()`, and `vmmouse_report_events()`. PS/2 data integration uses `vmmouse_process_byte()`, while lifecycle callbacks are `vmmouse_reset()`, `vmmouse_disconnect()`, and `vmmouse_reconnect()`.

## Control Flow
Detection first checks `x86_hyper_type` against VMware/KVM and verifies the VMware hypervisor magic/version. Initialization resets psmouse, enables the absolute pointer channel, allocates and registers an absolute input device, adds wheel capability to the existing relative psmouse device, and installs the vmmouse packet handler. The handler accepts the PS/2 notification bytes and then drains hypervisor queue entries. Each entry is classified as relative or absolute, reports motion to the preferred device, reports wheel on the relative device for userspace compatibility, reports buttons on whichever device already holds the button if pressed, and syncs both devices.

## State and Persistence
State is per psmouse binding in `psmouse->private` and is freed on disconnect. Hypervisor mode is disabled on cleanup, disconnect, reset, and before reconnect. No state persists beyond the active virtual device session.

## Dependencies and Integration Points
The driver depends on x86 hypervisor detection, VMware backdoor hypercalls, psmouse/libps2, serio, and Linux input. `vmmouse.h` declares the public psmouse hooks and `VMMOUSE_PSNAME`.

## Risks and Edge Cases
Queue length must be a multiple of four or the driver forces bad data to trigger psmouse recovery. The event loop caps processing at 255 packets to avoid indefinite drain. `vmmouse_disable()` warning logic is suspicious because it warns when status does not equal the error sentinel after disable. Button ownership across two input devices is subtle and needed to keep release events on the device that reported the press.

## Test Signals
Run under supported VMware/KVM environments, verify detection fails on unsupported hypervisors, absolute and relative motion both report correctly, wheel events reach the relative device, reconnect after suspend re-enables the channel, and malformed queue/status values trigger recovery without crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vmmouse.c -->
