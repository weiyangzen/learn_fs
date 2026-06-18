<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h` defines USB4 sideband register offsets, sideband opcodes, metadata fields, and lane-margining bit masks used for routers and retimers. The source was read as a complete 112-line file.

## Important APIs, Types, and Functions

The header defines sideband registers such as `USB4_SB_VENDOR_ID`, `USB4_SB_PRODUCT_ID`, `USB4_SB_FW_VERSION`, `USB4_SB_OPCODE`, `USB4_SB_METADATA`, `USB4_SB_LINK_CONF`, `USB4_SB_VERSION`, and `USB4_SB_DATA`. `enum usb4_sb_opcode` covers command/status values for errors, online status, router offline, enumerate retimers, inbound SBTX set/unset, last/cable retimer queries, NVM sector/offset/block/auth/read operations, and lane-margining operations. The rest of the file defines capability/result/control masks for hardware and software lane margining.

## Control Flow

There is no executable flow. USB4 sideband accessors use these offsets/opcodes to construct transactions and parse returned metadata/data for retimer discovery, NVM operations, and margining.

## State and Persistence Behavior

The file describes live sideband register state. It does not own memory. Sideband commands may change retimer/router state, NVM offsets, inbound SBTX mode, or margining operation state in hardware.

## Dependencies and Integration Points

The header is included by `retimer.c` and USB4 sideband/margining code. It assumes bit helpers such as `BIT()` and `GENMASK()` are available. It is a protocol contract between the kernel and USB4 sideband targets.

## Risks and Edge Cases

Opcode constants are four-character little-endian command encodings; wrong values can trigger the wrong sideband operation. Margining masks have overlapping per-capability semantics, so code must use the mask set for the specific opcode/result. Metadata `USB4_SB_METADATA_NVM_AUTH_WRITE_MASK` constrains auth-write lengths.

## Test Signals

Sideband read/write tests for vendor/product/version, retimer enumeration, NVM read/write/authentication, inbound SBTX set/unset, and debugfs lane-margining capability/result parsing validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/sb_regs.h -->
