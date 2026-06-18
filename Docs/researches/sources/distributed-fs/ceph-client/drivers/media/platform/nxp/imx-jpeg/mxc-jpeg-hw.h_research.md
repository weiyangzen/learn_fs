# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg-hw.h

Purpose: Hardware register and bitfield definition header for the i.MX8 JPEG wrapper/CAST block, plus low-level helper prototypes.

Important APIs, types, and functions: Defines wrapper offsets (`GLB_CTRL`, `COM_STATUS`, buffer/stream/image fields), CAST status/control aliases, per-slot register offsets via `MXC_SLOT_OFFSET()`, GLB/COM/STM/SLOT field macros, next-descriptor enable and decoder exit-idle values, and `enum mxc_jpeg_image_format`. Declares all helper functions implemented in `mxc-jpeg-hw.c`.

Control flow: No runtime control flow. `mxc-jpeg.c` uses these constants to encode descriptors, inspect IRQ status, query version, and control encode/decode phases.

State and persistence behavior: No software state; describes hardware register state and descriptor bit encodings.

Dependencies and integration points: Includes Linux `bitfield.h` and `mxc-jpeg.h` for descriptor structures. It is the contract between the core driver and helper implementation.

Risks: CAST decoder and encoder control registers alias status offsets, requiring mode-aware access. `GLB_CTRL_CUR_VERSION()` derives encoder config behavior; wrong masks select the wrong descriptor/manual config flow. Image format enum values must match hardware `STM_CTRL_IMAGE_FORMAT()`.

Test signals: Compile tests validate macro/prototype consistency. Runtime encode/decode on v0 and v1 hardware validates version-dependent paths, image format encodings, slot offsets, and status bit handling.
