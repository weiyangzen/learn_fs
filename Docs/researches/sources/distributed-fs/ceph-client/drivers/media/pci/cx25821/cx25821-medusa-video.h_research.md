# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.h

Purpose: defines Medusa video color-control ranges and default procamp values.

Important APIs and constants: includes decoder IDs from `cx25821-medusa-defines.h`; defines `VIDEO_PROCAMP_MIN`/`MAX` as 0/10000, signed and unsigned byte target ranges, and defaults for sharpness, saturation, brightness, contrast, and hue.

Control flow: procamp setter functions use these ranges to map V4L2 control values to register byte values. `cx25821-video.c` uses matching defaults when creating V4L2 controls, especially brightness 6200 and contrast/saturation/hue 5000.

State and persistence: no state. Constants guide hardware value mapping and control defaults.

Dependencies and integration points: included by `cx25821-medusa-video.c` and other driver code needing Medusa defaults. Tied to V4L2 control setup and Medusa register programming.

Risks: defaults must stay consistent with V4L2 control initialization; drift can make reported defaults differ from hardware programming. Sharpness default is defined but not wired to a V4L2 control in this subset.

Test signals: V4L2 control default inspection and procamp mapping tests at min/mid/max values.
