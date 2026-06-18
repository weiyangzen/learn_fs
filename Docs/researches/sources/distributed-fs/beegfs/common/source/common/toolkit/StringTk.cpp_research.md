<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.cpp

**Purpose:** Implements common string trimming, splitting/joining, numeric conversion, formatting, timespan formatting, vector conversion, numeric validation, and random alphanumeric string generation.

**Important APIs/types/functions:** `trim`, `explode`, `explodeEx`, `implode`, `strToInt`, `strToUInt`, `strHexToUInt`, `strOctalToUInt`, `strToInt64`, `strToUInt64`, `strToBool`, integer/hex/double formatters, `timespanToStr`, `uint16VecToStr`, `strToUint16Vec`, `isNumeric`, and `genRandomAlphaNumericString`.

**Control flow:** Split functions walk delimiter positions and skip empty elements; `explodeEx` optionally trims before insertion. Numeric parsing intentionally uses legacy `atoi`, `atoll`, and `sscanf` behavior with weak error reporting. Formatting uses fixed-size stack buffers and `snprintf`/`sprintf`. Random string generation appends characters chosen from digits and ASCII letters via `Random`.

**State and persistence behavior:** Stateless except for caller-provided output containers/strings. No persistence.

**Dependencies and integration points:** Used broadly for config parsing, ID handling, unit conversion, storage path generation, and display. Depends on `Random` for random strings and BeeGFS common typedefs.

**Risks:** Legacy parsers silently accept malformed input or overflow according to C library behavior. `timespanToStr` appears to compute `seconds = seconds % 60` after initializing seconds to zero when minutes are present, so seconds for spans >=60 are always zero. `strToUint16Vec` casts through signed `int16_t` despite returning unsigned vector values. Random generation is not security-grade.

**Test signals:** No direct `StringTk` tests in this subset, but `EntryIdTk`, `UnitTk`, `SessionTk`, and storage helpers depend on its conversions. Dedicated tests should pin legacy parsing semantics before refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.cpp -->
