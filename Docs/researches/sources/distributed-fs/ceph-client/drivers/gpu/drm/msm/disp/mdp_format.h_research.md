# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp_format.h

Purpose: Declares the MSM display format metadata structure and helper flags/macros used by MDP and DPU plane programming.

Important APIs/types: `enum msm_format_flags` defines YUV, DX, compressed, tight unpack, and MSB-aligned unpack bits. `struct msm_format` describes DRM fourcc, component bit widths, element order, fetch type, chroma sampling, alpha presence, unpack count, bytes per pixel, flags, number of planes including metadata, fetch mode, and tile height. Macros classify YUV, DX, linear, tile, and UBWC formats.

Control flow/state: This is a pure metadata contract. Runtime callers receive `struct msm_format` from lookup code and branch on macros during validation and hardware programming.

Dependencies/integration: Depends on generated `mdp_common.xml.h` enums and is included by `mdp_kms.h`, MDP5 plane code, and other MSM display blocks.

Risks and test signals: Misclassified compressed or plane-count fields can cause incorrect framebuffer IOVA programming. Compile coverage and framebuffer validation tests should include linear RGB, YUV, UBWC RGB/YUV, and DX/P010 formats.
