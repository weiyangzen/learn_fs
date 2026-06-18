<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.cpp

Purpose: Implements string-map file parsing/writing and selected map copy helpers.

Important APIs/functions: `addLineToStringMap` parses key/value lines into `StringMap`. `loadStringMapFromFile` reads a config-like file. `saveStringMapToFile` writes map entries. `copyUInt64VectorMap` deep-copies maps of vector pointers.

Control flow/state/persistence: File load skips comments/blank lines through parser behavior. Save opens an output file and throws `InvalidConfigException` on failures. Copy helper allocates new vectors for each entry.

Dependencies/integration: Uses C++ streams, BeeGFS string/map aliases, and invalid-config exceptions. Used for config-style persistence.

Risks/test signals: Tests should cover duplicate keys, malformed lines, comments, write errors, deep-copy ownership, and exception messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.cpp -->
