<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned.h -->
# sources/distributed-fs/ceph-client/include/linux/unaligned.h

Purpose: provides generic helpers for safe unaligned loads and stores in native, little-endian, big-endian, 24-bit, and 48-bit formats.

Important APIs and types: generic `get_unaligned()`/`put_unaligned()` use typed packed-struct access. Endian helpers cover `get_unaligned_le16/32/64`, `put_unaligned_le16/32/64`, `get_unaligned_be16/32/64`, `put_unaligned_be16/32/64`, plus manual byte assembly for 24-bit little/big endian and 48-bit big endian values.

Control flow: parsers and protocol code call these helpers when fields may not be naturally aligned. Fixed-width helpers read or write packed values and convert to/from CPU endian order; 24/48-bit helpers explicitly combine bytes.

State and persistence: no state is stored. Effects are immediate memory reads/writes at caller-provided addresses.

Dependencies and integration points: includes packed-struct unaligned primitives, architecture byteorder conversions, and VDSO unaligned helpers. It is used heavily by filesystem, networking, USB, storage, and binary protocol parsers.

Risks and test signals: risks include pointer type side effects in generic macros, assuming buffer length is sufficient, endian confusion, truncating 24/48-bit values, and architectures with strict unaligned access rules. Test protocol parsing on strict-alignment architectures, KASAN bounds checks, endian conversion tests, and round-trip put/get cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned.h -->
