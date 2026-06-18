<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestListTk.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestListTk.cpp

**Purpose:** Tests bounded advancement of a list iterator through BeeGFS `ListTk`.

**Important APIs/types/functions:** Single `TEST(ListTk, advance)` uses `ListTk::advance`.

**Control flow:** Builds a 10-element integer list, advances from begin by 5 and expects value 5, then advances by 44 and expects the iterator to equal `end`.

**State and persistence behavior:** Test-only list state; no persistence.

**Dependencies and integration points:** Depends on `ListTk`, BeeGFS integer list typedefs, and GoogleTest.

**Risks:** Only covers forward advancement from a valid iterator and overshoot to end. It does not cover zero advancement, already-end iterators, negative values if the API permits signed counts, or empty lists.

**Test signals:** Confirms safe end clamping for large positive advance values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestListTk.cpp -->
