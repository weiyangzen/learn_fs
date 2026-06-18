# `sources/distributed-fs/ceph-client/include/linux/ihex.h`

Purpose: compact binary Intel HEX firmware record format and helpers for safe iteration and firmware request validation.

Important APIs/types/functions: packed `struct ihex_binrec`, `ihex_binrec_size`, `__ihex_next_binrec`, `ihex_next_binrec`, `ihex_validate_fw`, and `request_ihex_firmware`.

Control flow and state: firmware is treated as a sequence of 4-byte-aligned binary records ending in a zero-length record. Validation walks records and only succeeds when the terminator is exactly at the computed end location. Request helper loads firmware, validates it, logs/release on invalid input, and returns a retained firmware pointer on success.

Dependencies/integration: depends on firmware loader and device logging. Used by drivers that want pre-converted IHEX firmware without parsing text in kernel.

Risks: validation assumes `fw->size >= sizeof(*end)`; malformed lengths can skip past data until loop fails; callers must release firmware after success; addresses/lengths are big-endian; alignment is part of the format.

Test signals: valid multi-record firmware, missing terminator, truncated header/data, unaligned record size padding, zero-length-only image, request failure/release path, and endian conversion checks.
