<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestEntryIdTk.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestEntryIdTk.cpp

**Purpose:** Tests entry ID token and full entry ID format validation.

**Important APIs/types/functions:** Tests `EntryIdTk::isValidHexToken` and `EntryIdTk::isValidEntryIdFormat`.

**Control flow:** Token tests accept non-empty hex strings up to eight characters and reject empty, too-long, and non-hex tokens. Format tests accept three dash-separated hex tokens and reject extra, missing, leading-empty, trailing-empty, and all-empty separator cases.

**State and persistence behavior:** No persistent state; validates textual ID contracts used by storage metadata.

**Dependencies and integration points:** Depends on `EntryIdTk` and GoogleTest. Entry ID format is tied to `StorageTk::generateFileID` and `StringTk::timeStampFromEntryID`.

**Risks:** Tests are concise and do not cover lowercase/uppercase variants exhaustively, root/special IDs, or numeric range semantics beyond token length.

**Test signals:** Good guard against accepting malformed separators and non-hex characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestEntryIdTk.cpp -->
