# sources/distributed-fs/ceph-client/include/linux/net/intel/libie/rx.h

Purpose: provides Intel Ethernet receive buffer/frame sizing constants and a safe wrapper for converting hardware packet types into parsed libeth RX packet-type metadata.

Important APIs and types: `LIBIE_MAX_RX_BUF_LEN` is the hardware maximum per descriptor, `LIBIE_RX_BUF_LEN(hr)` clamps libeth page length by headroom to hardware max, `__LIBIE_MAX_RX_FRM_LEN` is the hardware scatter/gather frame limit, `LIBIE_MAX_RX_FRM_LEN(hr)` clamps chained descriptor frame length, and `LIBIE_MAX_MTU` subtracts link-layer overhead. `LIBIE_RX_PT_NUM` sizes the packet-type lookup table. `libie_rx_pt_lut[]` is the external parsed packet-type table, and `libie_rx_pt_parse()` bounds-checks a 10-bit hardware packet type, maps out-of-range values to zero, and returns `struct libeth_rx_pt`.

Control flow: RX descriptor handling reads the hardware packet type and calls `libie_rx_pt_parse()` instead of indexing the LUT directly. Buffer sizing macros are used during RX ring setup and MTU validation to choose hardware-writable buffer sizes and maximum frame limits.

State and persistence: no mutable state is owned here; the lookup table is static read-only data defined elsewhere. Runtime RX rings and buffers live in drivers/libeth.

Dependencies and integration points: depends on `net/libeth/rx.h` for headroom, link-layer length, and parsed packet-type definitions. It connects Intel i40e/ice/iavf-style packet type encodings with shared libeth RX parsing.

Risks and test signals: risks include direct LUT indexing without bounds checks, MTU calculations drifting from descriptor-chain limits, headroom-dependent buffer underestimation, and packet-type table mismatch with hardware. Test out-of-range packet types, every valid LUT entry, max MTU validation, RX buffer sizing with different headroom, jumbo frames, and chained descriptor receive paths.
