<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.cpp

**Purpose:** Implements binary size conversion, human-readable size/time parsing and formatting, and quota block count conversion.

**Important APIs/types/functions:** Byte conversion functions for KiB through PiB, `byteToMebibyte`, `byteToXbyte`, `mebibyteToXbyte`, `xbyteToByte`, `strHumanToInt64`, `int64ToHumanStr`, `isValidHumanString`, `timeStrHumanToInt64`, `isValidHumanTimeString`, `quotaBlockCountToByte`, and `quotaBlockCountToHumanStr`.

**Control flow:** Size parsing inspects the last character and multiplies the numeric prefix by binary powers for K/M/G/T/P; no suffix falls back to integer parsing. Formatting chooses the largest binary unit that divides evenly. Display conversion repeatedly divides by 1024 and optionally rounds to one decimal. Time parsing supports D/H/M suffixes; validation also accepts S/s even though parser treats seconds by falling back to raw parsing.

**State and persistence behavior:** Stateless conversions. Used for config values, free-space override files, quota display, and user-facing output.

**Dependencies and integration points:** Depends on `StringTk` and quota filesystem type enums. `StorageTk::statStoragePathOverride` uses `strHumanToInt64` for override files.

**Risks:** Uses integer parsing with weak error behavior inherited from `StringTk`. `xbyteToByte` has no EiB branch despite display supporting EiB. `timeStrHumanToInt64("10s")` falls back to parsing `"10s"` as integer, which works with `atoi`-style behavior but is implicit. Multiplication can overflow.

**Test signals:** No direct tests in this subset. Tests should pin suffix parsing, validation/parser mismatch for seconds, quota XFS 512-byte conversion, and round formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/UnitTk.cpp -->
