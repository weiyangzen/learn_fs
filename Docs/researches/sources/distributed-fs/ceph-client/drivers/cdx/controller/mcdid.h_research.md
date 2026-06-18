# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdid.h

## Purpose
This private header defines CDX MCDI helper macros and forward declarations that bridge generic CDX bitfield accessors with the CDX protocol header.

## Important APIs, Types, and Functions
It defines debug warning macros, `MCDI_BUF_LEN`, `cdx_mcdi_if()`, declarations for `cdx_mcdi_rpc_async()` and `cdx_mcdi_wait_for_quiescence()`, and field access helpers `MCDI_BYTE`, `MCDI_WORD`, `MCDI_POPULATE_DWORD_1`, `MCDI_SET_QWORD`, and `MCDI_QWORD`.

## Control Flow
MCDI source files use `cdx_mcdi_if()` to access the active interface if initialized. Request-building code uses the field macros to populate and read protocol buffers without open-coding offsets.

## State and Persistence Behavior
No state is allocated. The inline accessor returns a pointer into `struct cdx_mcdi` state when present.

## Dependencies and Integration Points
It includes mutex, kref, rpmsg headers and `mc_cdx_pcol.h`. It depends on lower-level `MCDI_PTR`, `_MCDI_DWORD`, and CDX dword helpers from public CDX MCDI/bitfield headers.

## Risks
The macros enforce field widths for some accesses with `BUILD_BUG_ON_ZERO`, but they still rely on correct protocol constants. 64-bit access is split into two 32-bit dwords to avoid alignment assumptions; bypassing these macros would be risky. Debug warning macros compile to no-ops without `DEBUG`, so paranoid checks are not production safeguards.

## Test Signals
Build with and without `DEBUG`, compile protocol helper users, and validate qword/word/byte extraction against known little-endian MCDI buffers.
