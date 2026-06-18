## sources/distributed-fs/ceph-client/include/linux/cdx/bitfield.h

**Purpose:** This header provides CDX firmware/protocol bitfield helpers for little-endian 32-bit dwords.

**Important APIs/types/functions:** It defines field-attribute helpers `CDX_VAL`, `CDX_LOW_BIT`, `CDX_WIDTH`, and `CDX_HIGH_BIT`, `struct cdx_dword` wrapping `__le32`, `CDX_DWORD_VAL()`, `CDX_DWORD_FIELD()`, `CDX_INSERT_FIELD()`, `CDX_INSERT_FIELDS()`, `CDX_POPULATE_DWORD()`, arity adapters `CDX_POPULATE_DWORD_1..7`, and `CDX_SET_DWORD()`.

**Control flow, state, persistence:** Helpers are pure macro transformations. They extract or populate protocol fields using `FIELD_GET/PREP`, masks built from `_LBN/_WIDTH` constants, and CPU/little-endian conversions.

**Dependencies/integration:** Depends on `linux/bitfield.h` and byteorder helpers. Used by CDX MCDI protocol code and generated command headers.

**Risks and test signals:** Risks include undefined field metadata, values too wide for the field, endian omissions, and macro argument ordering mistakes. Test signals include compile-time field metadata checks, protocol encode/decode round trips, sparse endian warnings, and firmware command traces.
