# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ddp.h

## Purpose
`ice_ddp.h` defines the binary package layout, section IDs, package state enum, parser table structures, buffer-builder structures, and exported DDP helper prototypes for `ice_ddp.c` and package-consuming flow/switch code.

## Important APIs, Types, And Functions
Version constants define supported package major/minor (`1.3`) and package format (`1.0.0.0`). `enum ice_ddp_state` provides success, already-loaded variants, firmware mismatch, invalid file, unsupported version, signature/revision, load, and generic errors. Package structures describe headers (`ice_pkg_hdr`, `ice_generic_seg_hdr`), ICE device segments, NVM tables, 4 KiB package buffers, runtime config segments, signing segments, section entries, metadata, labels, field vectors, boost TCAM entries, marker PTYPE TCAM entries, XLT sections, and profile redirection sections.

The header declares package upload/update, buffer allocation/building, section/entry enumeration, and Tx topology configuration APIs. `struct ice_pkg_enum` captures enumeration state; `struct ice_buf_build` wraps a mutable package buffer plus reserved section-entry count.

## Control Flow
The structures support two principal flows. First, package initialization validates and enumerates immutable package content using segment, buffer table, section, label, field-vector, and TCAM structures. Second, runtime updates allocate a new `ice_buf_build`, reserve section entries, allocate section payload space, then send built buffers through update-package AdminQ commands.

## State And Persistence
The header defines in-memory views of firmware package content. Package contents are little-endian and frequently point directly into package memory retained by `hw->seg`/`hw->pkg_copy`. Persistent firmware effects occur when buffers matching these structures are downloaded or updated through AdminQ.

## Dependencies And Integration Points
It includes `ice_type.h` for package version/name and hardware-facing types. Section IDs are shared with switch, ACL, FD, RSS, parser, label, and Tx topology code. Field-vector structures and profile IDs are consumed by switch recipe/profile lookup code.

## Risks
This header encodes binary layout contracts; changing packing, constants, section IDs, or min/max bounds can break package compatibility. Flexible-array structures require strict size checks before access. All package contents must be interpreted little-endian. The broad section ID namespace makes accidental ID reuse risky.

## Test Signals
Compile-time structure layout review, package fixture parsing, endian-sensitive tests, section builder tests for alignment and capacity, enumeration tests across multiple buffers/sections, and compatibility tests against E810/E830/E825 package variants are appropriate.
