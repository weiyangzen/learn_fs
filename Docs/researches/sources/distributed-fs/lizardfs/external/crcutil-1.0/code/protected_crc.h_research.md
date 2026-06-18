# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/protected_crc.h

## Purpose

`protected_crc.h` defines `ProtectedCrc`, a thin wrapper that lets a CRC implementation compute a CRC over its own table/object memory. The goal is to detect corrupted CRC tables before corrupted tables poison application data.

## Important APIs and types

`ProtectedCrc<CrcImplementation>` publicly inherits from the implementation and exports `typedef typename CrcImplementation::Crc Crc`. Its only method is `SelfCheckValue()`, which calls `CrcDefault(this, sizeof(*this), 0)` and returns the resulting check value. The returned value is intended to be compared with a trusted precomputed constant.

## Control flow, state, and persistence

The wrapper does not add fields. It depends entirely on the base implementation's initialized table state. The comments warn that computing a self-check once after initialization and storing it next to the object is insufficient if the initialization itself was corrupt; the trusted value should come from outside the potentially corrupt runtime state.

## Dependencies and integration points

It assumes the implementation has no virtual functions because a runtime vptr would make the object memory unstable across runs. It also assumes `CrcDefault()` can safely read the complete object representation. It uses `GCC_ALIGN_ATTRIBUTE(16)` from `platform.h`, but this header does not include `platform.h` itself, so it depends on include order from users.

## Risks and test signals

CRC over raw object memory can be sensitive to padding bytes, compiler layout, and uninitialized fields. Public inheritance means object layout equals base fields plus no added state, but changes to base classes can change the trusted check value. Test signals include deterministic self-check values across clean builds with the same compiler/options, deliberate bit flips in table memory, and checks after CRC mismatch paths before data is accepted or written.
