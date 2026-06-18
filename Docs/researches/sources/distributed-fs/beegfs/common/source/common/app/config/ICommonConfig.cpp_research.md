<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.cpp

### Purpose
This file implements shared helper loading for simple line-based configuration files.

### Important APIs, Types, And Functions
`ICommonConfig::loadStringListFile` reads a file into a `StringList`, trimming whitespace and skipping empty lines and lines beginning with `STORAGETK_FILE_COMMENT_CHAR`.

### Control Flow
The function opens an `ifstream`, throws `InvalidConfigException` on open failure, loops through lines until EOF/failure, trims each line, appends meaningful non-comment lines, and closes the stream.

### State, Persistence, And Dependencies
It does not persist state; it fills the caller-provided list. Dependencies include `StringTk`, `StorageTk`, and `ICommonConfig`.

### Integration Points
Used by interface list loading, network filter loading, and any common config path that takes newline-separated files.

### Risks
Inline comments after values are not stripped; only full-line comments are ignored. Stream failures after partial reads are not surfaced except through omitted lines.

### Test Signals
Tests should cover missing file, whitespace trimming, empty lines, full-line comments, and values containing comment characters not in column zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.cpp -->
