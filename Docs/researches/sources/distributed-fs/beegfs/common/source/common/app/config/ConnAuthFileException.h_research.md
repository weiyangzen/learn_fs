<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ConnAuthFileException.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/ConnAuthFileException.h

### Purpose
This header defines the named exception type used for connection-authentication file configuration errors.

### Important APIs, Types, And Functions
`DECLARE_NAMEDEXCEPTION(ConnAuthFileException, "ConnAuthFileException")` expands to a BeeGFS named exception class.

### Control Flow
There is no runtime control flow in the header. `AbstractConfig::initConnAuthHash` throws this type when the auth file is missing or cannot be opened.

### State, Persistence, And Dependencies
The exception carries message state inherited from `NamedException`. Dependencies are `NamedException.h` and `Common.h`.

### Integration Points
Config initialization and app startup can catch this specific type separately from generic invalid config errors if they want auth-specific user messaging.

### Risks
The type has no extra fields, so callers must parse or preserve the message for details.

### Test Signals
Config tests should assert missing/unreadable auth file paths throw `ConnAuthFileException` rather than a generic exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ConnAuthFileException.h -->
