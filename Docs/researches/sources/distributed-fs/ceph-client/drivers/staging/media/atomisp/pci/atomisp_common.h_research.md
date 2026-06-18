# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_common.h

## Purpose

`atomisp_common.h` contains small shared definitions used by AtomISP PCI driver code: debug/padding globals, CSS trace and zoom constants, an ISP pipe-version flag, and two format-description structs. It is a lightweight common header that connects V4L2 media-bus pixel formats to CSS frame formats and user-visible V4L2 pixelformats.

## Important APIs, Types, and Constants

- External globals `dbg_level`, `dbg_func`, `pad_w`, and `pad_h` are declared here. `pad_w` and `pad_h` are used by command/format paths as default sensor padding when crop-aware padding cannot be derived.
- `ISP2400_MIN_PAD_W` and `ISP2400_MIN_PAD_H` define minimum padding requirements for BYT/ISP2400 paths. `atomisp_get_padding()` uses these as lower bounds when not running ISP2401.
- `CSS_DTRACE_VERBOSITY_LEVEL` and `CSS_DTRACE_VERBOSITY_TIMEOUT` define debug trace verbosity levels used by CSS diagnostic paths elsewhere.
- `MRFLD_MAX_ZOOM_FACTOR` is the digital zoom scale constant used by `atomisp_digital_zoom()`.
- `ATOMISP_CSS_ISP_PIPE_VERSION_2_7` identifies the ISP2401 CSS pipe version used by conditional code paths.
- `struct atomisp_format_bridge` maps a V4L2 `pixelformat`, bit `depth`, media-bus code, CSS `ia_css_frame_format`, textual description, and planar flag.
- `struct atomisp_fmt` records concrete format dimensions and sizes: pixelformat, depth, bytesperline, framesize, imagesize, width, height, and bayer order.

## Control Flow and Integration

This header defines data contracts, not executable flow. `struct atomisp_format_bridge` is consumed by format lookup helpers such as `atomisp_get_format_bridge()` and `get_atomisp_format_bridge_from_mbus()`, then used by `atomisp_try_fmt()`, `atomisp_set_fmt()`, and `atomisp_fill_pix_format()` to translate V4L2 requests into CSS pipe configuration. The padding and zoom constants feed command-layer calculations.

## State and Persistence Behavior

The header declares global debug/padding variables but does not define them. Runtime state is held by the defining compilation unit and by the caller's format structures. There is no disk persistence. The values influence live sensor/ISP setup: padding affects requested sensor dimensions and crop behavior, while format bridge records determine bytesperline, sizeimage, CSS frame format, and media-bus propagation.

## Dependencies and Integration Points

The header includes the AtomISP userspace ABI header, Linux V4L2 media-bus definitions, videobuf2 V4L2 definitions, `atomisp_compat.h`, and `ia_css.h`. This makes it a shared bridge between Linux V4L2/vb2 types and Intel CSS types. It is included by `atomisp_cmd.c` and other AtomISP files that need common format metadata.

## Risks and Edge Cases

- Global `pad_w`/`pad_h` are externally mutable module parameters or globals; invalid values can affect sensor requests and format negotiation.
- `description[32]` mirrors V4L2 format descriptions and must stay bounded by table initializers.
- `struct atomisp_format_bridge` mixes user-visible and firmware-visible formats, so table mistakes can produce subtle bytesperline, padding, raw-order, or CSS output bugs.
- Constants are hardware-generation-specific; applying ISP2400 padding rules to ISP2401 paths, or vice versa, can regress format setup.

## Test Signals

Format enumeration, `VIDIOC_TRY_FMT`, `VIDIOC_S_FMT`, and sensor media-bus propagation tests are the best behavioral signals. Static checks should verify that all bridge table entries have consistent depth, planar flag, media-bus code, and CSS format. Runtime debug around `atomisp_get_padding()` and `atomisp_fill_pix_format()` can catch mismatches between bridge metadata and generated V4L2 `bytesperline`/`sizeimage`.
