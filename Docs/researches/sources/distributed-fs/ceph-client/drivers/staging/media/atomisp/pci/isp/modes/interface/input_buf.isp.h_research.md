# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/input_buf.isp.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/input_buf.isp.h` defines the ISP input-buffer geometry used by continuous capture: double-buffer height, line count, fixed VMEM base address, extra left-padding vectors, and the maximum vectors per input line.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_INPUT_BUF_ISP_H_`, `INPUT_BUF_HEIGHT`, `INPUT_BUF_LINES`, `ENABLE_CONTINUOUS`, `EXTRA_INPUT_VECTORS`, `MAX_VECTORS_PER_INPUT_LINE_CONT`, `INPUT_BUF_ADDR`

Control flow: Continuous-mode binaries and SP-side assumptions use a fixed input-buffer size and address so the SP can address ISP input memory consistently.

State and persistence behavior: No persistent storage exists. Values are compile-time constants or per-binary memory-address contracts consumed during ISP/SP pipeline setup.

Dependencies and integration points: These headers integrate generated Hive/ISP code, CSS host runtime, frame allocation, input formatter setup, and stream-format selection.

Risks and edge cases: `ENABLE_CONTINUOUS` defaults to zero here, but the constants remain compiled; sensor widths near `SH_CSS_MAX_SENSOR_WIDTH` depend on correct `DIV_ROUND_UP()` and padding.

Test signals: Validate continuous and non-continuous builds, maximum sensor width alignment, frame-plane address wiring, raw/YUV/binary stream format selection, and compile compatibility with generated ISP code.
