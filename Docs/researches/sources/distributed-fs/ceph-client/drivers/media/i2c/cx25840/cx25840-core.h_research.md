# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-core.h

## Purpose
This internal header defines the shared data model and function contracts for the composite CX25840 driver. It lets the core, audio, firmware, VBI, and IR translation units share chip-family predicates, private state, and internal register helper declarations.

## Important APIs, Types, And Functions
`enum cx25840_model` identifies CX23885/7/8 AV cores, CX2310X AV, CX25840/1/2/3, and CX25836/7. `enum cx25840_media_pads` defines the optional media-controller sink/source pads. `struct cx25840_state` is the central per-device state. Inline helpers `to_state()`, `to_sd()`, `is_cx2583x()`, `is_cx2584x()`, `is_cx231xx()`, `is_cx2388x()`, `is_cx23885()`, `is_cx23887()`, and `is_cx23888()` are used throughout. Function declarations expose register helpers, firmware loading, audio path/clock ops, VBI format/decode ops, and IR ops.

## Control Flow
The header itself has no runtime control flow, but its predicates drive nearly every branch in the implementation. The shared `struct cx25840_state` is recovered from subdev/control callbacks and feeds model-specific initialization, audio programming, VBI offsets, and IRQ support.

## State And Persistence
The state struct persists for the I2C device lifetime and stores both software cache and hardware intent: selected standards/routes, audio clock and mode, generic-mode output configuration, firmware initialization status, VBI offsets, platform workaround flag, and IR substate. Its fields are the source of truth used to reapply hardware setup after resets or route changes.

## Dependencies And Integration Points
It includes V4L2 device/control headers and Linux I2C. It also depends on public media driver-interface definitions for video/audio input enums through included implementation files. The header is included by all CX25840 component files and forms the private ABI of the composite module.

## Risks
Because this is a private cross-file ABI, changing `struct cx25840_state` semantics can silently break sibling files. Model predicates are simple enum checks; any new model must be added consistently to all predicates and switch statements. Optional media-controller fields are compiled conditionally, so code must respect `CONFIG_MEDIA_CONTROLLER`.

## Test Signals
Build coverage across media-controller enabled/disabled configurations, all object files including this header, and runtime paths for every model predicate are key signals. Static analysis can catch missing declarations or stale function prototypes after refactors.
