<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.h -->
## sources/distributed-fs/beegfs/storage/tests/TestConfig.h

### Purpose
Declares the GoogleTest fixture and constants for storage configuration tests.

### Important APIs, Types, And Functions
Defines DUMMY_NOEXIST_CONFIG_FILE, DUMMY_EMPTY_CONFIG_FILE, DEFAULT_CONFIG_FILE_RELATIVE, APP_NAME, and class TestConfig with SetUp/TearDown plus dummyConfigFile and emptyConfigFile members.

### Control Flow
The fixture provides reusable path state for tests that construct Config with synthetic argv arrays.

### State, Persistence, And Dependencies
State is per-test strings; cleanup is performed in TearDown in the cpp file. Depends on Config, LogContext, gtest, ConnAuthFileException, and libgen.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include a semicolon embedded in APP_NAME macro expansion and fixed /tmp names shared across parallel test runs.

### Test Signals
Test signal is successful fixture setup/teardown around the TestConfig.cpp cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.h -->
