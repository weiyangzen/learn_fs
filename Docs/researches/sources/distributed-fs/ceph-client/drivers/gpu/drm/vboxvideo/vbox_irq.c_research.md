# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_irq.c

## Purpose

`vbox_irq.c` handles VirtualBox graphics IRQs and host mode-hint hotplug events. It reads host flags from the shared guest heap, schedules hotplug work, validates host-provided monitor positions, updates connector mode hints, and registers/frees the shared PCI IRQ.

## Important APIs, Types, and Functions

- `vbox_irq_handler`: shared IRQ handler that checks `HGSMIHOSTFLAGS_IRQ`, detects hotplug/cursor capability events, clears IRQs, and returns handled status.
- `vbox_report_hotplug`: schedules the deferred hotplug worker.
- `vbox_update_mode_hints`: queries host mode hints, validates positions, updates connector/CRTC hint fields, reports display blank/disable transitions, and emits KMS hotplug later through the worker.
- `validate_or_set_position_hints`: replaces overlapping or invalid enabled-screen positions with a left-to-right layout.
- `vbox_irq_init` and `vbox_irq_fini`: initialize hotplug work, perform an initial hint update, request/free the PCI IRQ, and flush work.

## Control Flow

Init sets up work, fetches current hints, then registers a shared IRQ. On interrupt, the handler reads host flags from `guest_heap + HOST_FLAGS_OFFSET`; if the IRQ bit is absent, it returns `IRQ_NONE`. Hotplug/cursor flags without VSYNC schedule work, then the handler clears host IRQ state by writing all ones to `VGA_PORT_HGSMI_HOST`. The worker refreshes hints and calls `drm_kms_helper_hotplug_event`.

## State and Persistence Behavior

Persistent guest state includes `vbox->last_mode_hints`, each connector's `mode_hint`, CRTC `x_hint`, `y_hint`, and `disconnected` fields. Host flags are shared memory written by the host and cleared through I/O. Workqueue state persists until flushed in teardown.

## Dependencies and Integration Points

It depends on PCI IRQs, DRM connector iteration/locking, KMS hotplug helpers, HGSMI mode-hint commands, and display-info reporting from `modesetting.c`. Connector mode probing in `vbox_mode.c` consumes the updated hints.

## Risks and Edge Cases

- Historical host bugs leave hotplug/cursor flags set; the VSYNC check is a compatibility workaround.
- `validate_or_set_position_hints` masks dimensions with `0x8fff`, which reflects protocol quirks and must be preserved carefully.
- Hint updates occur under the connection mutex but also send HGSMI display updates; avoid deadlocks with atomic modeset paths.
- `request_irq` uses a shared interrupt, so false positives must return `IRQ_NONE`.

## Test Signals

Hotplug monitor add/remove in a VM, cursor capability changes, invalid/overlapping host hints, IRQ sharing behavior, connector status updates, KMS hotplug uevents, and teardown with pending hotplug work.
