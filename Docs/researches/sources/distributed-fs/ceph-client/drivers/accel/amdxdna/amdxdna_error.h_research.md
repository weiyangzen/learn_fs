# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_error.h

Purpose: defines compact AMD XDNA AIE error encoding values used to report critical AIE hardware errors and extra row/column location metadata.

Important APIs/types: `enum amdxdna_error_num` enumerates AIE saturation, floating-point, stream, access, bus, instruction, ECC, lock, DMA, memory parity, and unknown errors. `enum amdxdna_error_module` enumerates AIE core, memory, shim, NOC, PL, and unknown modules. `AMDXDNA_ERROR_ENCODE()` packs error number, driver ID, severity, module, and class into a 64-bit value using fixed masks. `AMDXDNA_EXTRA_ERR_ENCODE()` packs row/column location into auxiliary error data.

Control flow: async error and query paths include this header to translate firmware or hardware error details into UAPI-facing encoded values.

State and persistence: no state; it is a pure encoding contract. Encoded values can persist in in-memory async error records until queried.

Dependencies: Linux bitfield and bit mask helpers.

Risks: masks are part of a UAPI-visible interpretation; changing field positions breaks consumers. Constants assume AIE driver/class/severity assignments remain stable.

Test signals: compile-time coverage, unit-style checks for mask packing/unpacking, async-error query validation, and userspace decoder compatibility for known row/column/module/number combinations.
