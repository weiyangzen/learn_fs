# File Research: sources/block-storage/kvdo/vdo/type-defs.h

This small compatibility header includes kernel standard/type headers, defines `byte` as `unsigned char`, and defines several integer limit macros (`CHAR_BIT`, `INT64_MAX`, `UCHAR_MAX`, `UINT8_MAX`, `UINT16_MAX`, `UINT64_MAX`) using casts.

It is a foundational include used by many VDO/UDS headers for fixed-width type and byte naming consistency in kernel code.
