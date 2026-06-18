<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.h

**Purpose:** Declares static unit-conversion helpers for binary sizes, human-readable strings, durations, and quota block display.

**Important APIs/types/functions:** Public declarations for all conversion and validation functions plus inline `std::string` overloads for `strHumanToInt64` and `timeStrHumanToInt64`.

**Control flow:** Header is a namespace-like class with private constructor and static functions only. Callers pass output unit strings by pointer for display conversion functions.

**State and persistence behavior:** Stateless declaration. Values converted by this API feed configuration and persistent override behavior elsewhere.

**Dependencies and integration points:** Includes BeeGFS quota definitions. Used by configuration parsing, storage capacity overrides, and CLI output.

**Risks:** Pointer output parameters must be non-null. Header does not document overflow/error behavior; implementation uses permissive numeric parsing.

**Test signals:** Compile-time use is broad; unit tests should include string overloads and null-pointer avoidance by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.h -->
