<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.h

**Purpose:** Declares the static `StringTk` API and inline helpers for string/numeric conversion, safe copying, entry-ID timestamp extraction, vector joining, and multi-line joining.

**Important APIs/types/functions:** Public declarations match `StringTk.cpp`. Inline overloads accept `std::string`, `strToDouble`, `strncpyTerminated`, `timeStampFromEntryID`, template `implode`, and template `implodeMultiLine`.

**Control flow:** `timeStampFromEntryID` parses entry IDs of the form `counter-timestamp-node`, returning special IDs unchanged when no separator exists and returning `FhgfsOpsErr_INTERNAL` when only one separator exists. Template `implode` streams vector values with a delimiter. `implodeMultiLine` accumulates delimited elements until a maximum line length would be exceeded.

**State and persistence behavior:** Stateless. The extracted timestamp feeds storage chunk path layout but is not persisted here.

**Dependencies and integration points:** Includes BeeGFS common and storage error definitions. The `STRINGTK_ID_SEPARATOR` contract is shared with storage entry ID generation and chunk path derivation.

**Risks:** Inline parsers inherit weak C conversion behavior. `strncpyTerminated` does nothing when `count == 0`, leaving destination untouched. `implodeMultiLine` uses stream position as element length and can produce leading delimiter behavior after line breaks.

**Test signals:** Entry ID format validation tests in `TestEntryIdTk.cpp` are adjacent but do not directly test `timeStampFromEntryID`; such coverage would be useful for special IDs and malformed IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/StringTk.h -->
