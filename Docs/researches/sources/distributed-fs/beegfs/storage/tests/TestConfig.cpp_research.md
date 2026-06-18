<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.cpp -->
## sources/distributed-fs/beegfs/storage/tests/TestConfig.cpp

### Purpose
Implements GoogleTest coverage for storage daemon configuration file handling.

### Important APIs, Types, And Functions
Test fixture methods SetUp() and TearDown() initialize dummy config paths and remove generated empty config files. Tests are missingConfigFile and defaultConfigFile.

### Control Flow
missingConfigFile constructs argv with a guaranteed non-existent cfgFile path and asserts Config construction throws InvalidConfigException. defaultConfigFile resolves the test binary path through /proc/self/exe, builds the relative default config path, constructs Config, and treats ConnAuthFileException as an acceptable return path.

### State, Persistence, And Dependencies
State is temporary path strings and possible /tmp empty config cleanup. No repository persistence is changed. Depends on TestConfig.h, Config, StorageTk::pathExists, StringTk, readlink, dirname, GoogleTest, and ConnAuthFileException.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include fixed /tmp filenames, Linux-specific /proc/self/exe, mutable std::string buffers used as argv entries, and defaultConfigFile not asserting success beyond absence of unexpected exceptions.

### Test Signals
Test signals are the tests themselves; additional coverage should include empty config file cleanup and invalid auth-file paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.cpp -->
