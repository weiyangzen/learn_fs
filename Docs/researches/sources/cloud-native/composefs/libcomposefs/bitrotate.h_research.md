# sources/cloud-native/composefs/libcomposefs/bitrotate.h

Purpose: vendored/gnulib-style inline helpers for rotating unsigned integer bits of multiple widths.

Important APIs/types/functions: macros `_GL_INLINE`, `_GL_ATTRIBUTE_CONST`, `BITROTATE_INLINE`; functions `rotl64`, `rotr64`, `rotl32`, `rotr32`, `rotl_sz`, `rotr_sz`, `rotl16`, `rotr16`, `rotl8`, and `rotr8`.

Control flow: pure inline arithmetic using shifts and masks; no runtime state.

State/persistence: header-only compile-time utility.

Dependencies/integration: depends on standard integer limits/types and is likely used by hashing/filter code such as EROFS xattr filters or CRC-related helpers.

Risks/test signals: callers must respect documented shift ranges for 32/64/size_t helpers to avoid undefined behavior at zero/full-width shifts. Compile coverage is the primary signal.
