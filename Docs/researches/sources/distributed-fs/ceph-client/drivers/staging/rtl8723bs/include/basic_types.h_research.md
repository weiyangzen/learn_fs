# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/basic_types.h

Purpose: this header supplies legacy Realtek basic constants, pointer-size aliases, endian conversion helpers, little-endian bitfield accessors, alignment macros, and flag helpers.

Important APIs/types/macros: `SUCCESS`/`FAIL`, `SIZE_PTR`, `SSIZE_PTR`, `EF1BYTE`/`EF2BYTE`/`EF4BYTE`, `BIT_LEN_MASK_*`, `BIT_OFFSET_LEN_MASK_*`, `LE_BITS_TO_*`, `LE_BITS_CLEARED_TO_*`, `SET_BITS_TO_LE_*`, `N_BYTE_ALIGMENT`, and flag macros `TEST_FLAG`, `SET_FLAG`, `CLEAR_FLAG`, `TEST_FLAGS`.

Control flow and integration: there is no runtime control flow. Descriptor, EFUSE, C2H, and register bitfield code uses these macros to extract or set fields from little-endian byte streams. `N_BYTE_ALIGMENT` is used by the SDIO receive initialization to align the receive-buffer array.

State and persistence: macros mutate caller-provided memory for `SET_BITS_TO_LE_*`; there is no standalone state. The macros are often used on hardware descriptor buffers, so writes become part of data sent to hardware or parsed from hardware.

Dependencies: includes Linux types and stddef. It assumes unaligned pointer casts are acceptable in the caller context, which can be architecture-sensitive.

Risks and test signals: `BIT_LEN_MASK_*` shifts by width minus bitlen, so a bit length of zero or greater than width must be avoided by callers. `SET_BITS_TO_LE_4BYTE` writes through `u32 *` rather than `__le32 *`, so endian and alignment assumptions are important. Tests should include descriptor field extraction/setting on little-endian buffers, alignment computations, and build coverage on architectures with stricter alignment rules.
