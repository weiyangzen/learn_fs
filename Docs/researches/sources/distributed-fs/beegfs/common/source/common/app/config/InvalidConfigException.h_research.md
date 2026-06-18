<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/InvalidConfigException.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/InvalidConfigException.h

### Purpose
This header defines the named exception type used for invalid BeeGFS configuration.

### Important APIs, Types, And Functions
`DECLARE_NAMEDEXCEPTION(InvalidConfigException, "InvalidConfigException")` creates the exception class with BeeGFS named-exception behavior.

### Control Flow
There is no local control flow. Config parsing, PID-file setup, and logger setup throw this type when validation fails.

### State, Persistence, And Dependencies
The exception stores its inherited message only. Dependencies are `NamedException.h` and `Common.h`.

### Integration Points
It is the primary error type for startup configuration failures across common app/config code.

### Risks
No structured error codes are attached, so callers must rely on catch type and message text.

### Test Signals
Startup/config tests should assert invalid values, unknown keys, bad files, and PID path problems throw `InvalidConfigException` where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/InvalidConfigException.h -->
