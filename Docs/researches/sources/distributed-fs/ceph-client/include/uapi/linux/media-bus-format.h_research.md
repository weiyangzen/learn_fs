# sources/distributed-fs/ceph-client/include/uapi/linux/media-bus-format.h

Purpose: enumerates stable media bus format codes used to describe pixel or metadata formats transferred across media subdevice links.

Important APIs and types: `MEDIA_BUS_FMT_FIXED` and many `MEDIA_BUS_FMT_*` constants cover RGB, YUV/greyscale, Bayer raw formats from 8 to 20 bits, JPEG, vendor-specific interleaved formats, HSV, fixed metadata, and generic line-based metadata widths. Values are explicitly assigned and grouped by format family; comments track the next free value per category.

Control flow: subdevice drivers advertise and negotiate these codes through V4L2/media-subdevice pad format APIs. Pipeline setup chooses compatible bus codes between sensors, bridges, ISPs, and capture devices.

State and persistence: active bus formats are runtime media pipeline state. The header only defines stable numeric identifiers.

Dependencies and integration points: standalone UAPI header integrated with V4L2 subdev format negotiation, media controller pipelines, camera sensors, display bridges, CSI/parallel/LVDS buses, ISPs, and metadata capture.

Risks and test signals: risks include renumbering existing codes, adding values in the wrong range, ambiguous sample order names, and driver disagreement about padding/endian semantics. Test media-ctl/v4l2-ctl format enumeration, sensor-to-bridge negotiation, raw Bayer capture for each bit depth, metadata formats, and userspace header compatibility.
