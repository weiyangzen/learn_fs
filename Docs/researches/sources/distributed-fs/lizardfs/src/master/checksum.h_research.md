# sources/distributed-fs/lizardfs/src/master/checksum.h

Purpose: shared metadata checksum mode/status enums for master modules.

Important APIs/types: `enum class ChecksumMode { kGetCurrent, kForceRecalculate }`; `enum class ChecksumRecalculationStatus { kDone, kInProgress }`.

Control flow: callers pass `ChecksumMode` to checksum functions and receive background recalculation progress states where supported.

State and persistence: none.

Dependencies and integration: used by `chunks.cc` and likely other metadata checksum modules.

Risks: no behavioral logic; changes must stay source-compatible with checksum callers.

Test signals: compile-time use by checksum implementations.
