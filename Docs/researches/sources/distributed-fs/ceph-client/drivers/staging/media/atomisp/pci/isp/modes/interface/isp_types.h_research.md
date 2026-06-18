# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/isp_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/isp_types.h` defines shared ISP mode types: stream-format classes and `s_isp_frames`, a large table of XMEM base pointers for output, second output, input YUV/raw, VF, overlay, GDC, and post-ISP buffers.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_3a_output`, `sh_stream_format`, `s_isp_frames`; `_ISP_TYPES_H_`

Control flow: Every ISP binary can receive or share this frame-address structure so firmware and host agree on memory locations for planes and intermediate products.

State and persistence behavior: No persistent storage exists. Values are compile-time constants or per-binary memory-address contracts consumed during ISP/SP pipeline setup.

Dependencies and integration points: These headers integrate generated Hive/ISP code, CSS host runtime, frame allocation, input formatter setup, and stream-format selection.

Risks and edge cases: The struct is a pointer ABI with many similarly named plane fields; wrong plane assignment causes silent frame corruption.

Test signals: Validate continuous and non-continuous builds, maximum sensor width alignment, frame-plane address wiring, raw/YUV/binary stream format selection, and compile compatibility with generated ISP code.
