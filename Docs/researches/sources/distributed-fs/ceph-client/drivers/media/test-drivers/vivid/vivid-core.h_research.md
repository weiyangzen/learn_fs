# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-core.h

## Purpose
`vivid-core.h` defines the central data model and shared constants for the VIVID virtual video test driver.

## Important APIs, types, and functions
The header defines maximum counts, geometry limits, tuner frequency ranges, SDR buffer sizes, HDMI/S-Video menu constants, and `VIVID_MAX_DEVS`. It declares global output-connection menu state, workqueues, device arrays, and shared rectangles.

`struct vivid_fmt` describes pixel formats, color encoding, overlay support, plane/buffer layout, offsets, and bit depth. `struct vivid_buffer` wraps `vb2_v4l2_buffer` for active-list use. Enums describe input types, signal modes, and colorspaces. `struct vivid_cec_xfer` stores one pending CEC transfer.

`struct vivid_dev` is the driver’s main per-instance object. It embeds V4L2/media/video devices, many control handlers and controls, capability flags, input/output topology, connection mappings, framebuffer/overlay state, error injection state, current capture/output formats and rectangles, vb2 queues and active lists, stream-generation thread state, SDR/radio/RDS state, CEC adapters/thread/transfer queue, OSD string, and metadata flags. Inline helpers classify the current input/output type.

## Control flow
The header does not implement the lifecycle, but its fields are initialized and consumed across `vivid-core.c` and all subsystem files. The inline helpers guide ioctl behavior and format/timing decisions.

## State and persistence
Nearly all VIVID runtime state is represented here. Per-instance state persists from `vivid_create_instance()` until `vivid_dev_release()`. Global arrays and workqueues persist for the module lifetime.

## Dependencies and integration points
It depends on framebuffer, workqueue, CEC, vb2, V4L2 device/control, TPG, RDS, and VBI generator headers. It is the shared contract for the full VIVID module.

## Risks and test signals
Risks include structure bloat and cross-file coupling, conditional fields under media-controller/CEC/OSD configs, and shared global topology state that must be synchronized. Test signals are broad build coverage, static analysis for uninitialized fields, and runtime tests that exercise each node class and topology link.
