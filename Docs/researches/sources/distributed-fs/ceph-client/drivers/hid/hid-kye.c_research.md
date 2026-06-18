# sources/distributed-fs/ceph-client/drivers/hid/hid-kye.c

## Purpose

`hid-kye.c` supports Kye/Genius mice, keyboards, and tablets with non-compliant descriptors. It patches incorrect mouse/keyboard consumer-control descriptors, replaces tablet descriptors with model-specific sane descriptors, adds optional mouse/control collections, and sends a feature report that enables absolute tablet mode.

## Important APIs, Types, and Functions

- Static control descriptors such as `easypen_m406_control_rdesc`, `pensketch_m912_control_rdesc`, and `mousepen_m508x_control_rdesc`: model-specific consumer-control reports for tablet buttons.
- `kye_tablet_rdesc` and `kye_tablet_mouse_rdesc`: descriptor templates for stylus and optional mouse-mode reports.
- `struct kye_tablet_info`: per-product logical/physical maxima, units, mouse support, and optional control descriptor metadata.
- `kye_consumer_control_fixup(...)`: clamps overly broad Consumer Control usage maxima in several Genius devices.
- `kye_tablet_fixup(...)`: replaces the descriptor with templates and patches model-specific X/Y/pressure ranges and units using unaligned little-endian writes.
- `kye_report_fixup(...)`: dispatches product-specific descriptor fixes.
- `kye_tablet_enable(...)`: finds feature report id 5, fills seven magic values, and sends `HID_REQ_SET_REPORT` to enable full tablet mode.
- `kye_probe(...)`: parses, starts HID hardware, applies a Manticore open/close workaround, and enables tablet mode for tablet products.

## Control Flow

Descriptor parsing calls `kye_report_fixup`. Older mice get byte-level descriptor edits; gaming keyboards/mice get Consumer Control usage maximums reduced; tablet products get a synthesized descriptor assembled from templates and `kye_tablets_info`. After `hid_hw_start`, probe applies runtime workarounds: Manticore is opened once so all interfaces become functional, and tablets receive the feature report that switches them from relative mouse behavior to absolute stylus behavior.

## State and Persistence Behavior

The driver has no heap state of its own. Persistent runtime effects are in the HID core: the modified descriptor, parsed reports, input devices, and any device-side tablet mode enabled by feature report id 5. Descriptor template data is static. Tablet mode is device state and may need reapplication after unplug or reset, but this file has no explicit resume hook.

## Dependencies and Integration Points

The driver depends on HID parser/start/request APIs, unaligned endian helpers, model IDs from `hid-ids.h`, and generic HID input mapping for the corrected descriptors. It integrates with HID feature reports for tablet mode switching and with userspace through standard digitizer, mouse, and consumer-control input events.

## Risks and Edge Cases

- `kye_tablet_fixup` assumes template byte offsets remain synchronized with comments; changing template bytes without updating offsets corrupts ranges/units.
- Descriptor replacement reuses the original descriptor buffer and requires the original `*rsize` to be large enough for all appended templates.
- Unknown tablet products in the switch but missing from `kye_tablets_info` fail fixup with an error and keep the original descriptor.
- `kye_tablet_enable` linearly searches for feature report id 5 and assumes at least seven values in field 0.
- There is no reset-resume re-enable path for tablet mode.
- The Manticore open/close workaround ignores the return except to close on success-like paths, so behavior relies on device side effects.

## Test Signals

Replay descriptors for each listed product and verify patched usage maxima, stylus axes, pressure ranges, optional mouse report, and control buttons. Hardware tests should confirm tablets report absolute coordinates after probe, Manticore extra interfaces work after the open/close workaround, feature report id 5 is present, and no descriptor buffer overrun warnings occur. Input tests should verify consumer buttons map to expected standard keys.
