## sources/distributed-fs/beegfs/meta/tests/TestConfig.cpp

Purpose: Tests basic metadata daemon configuration-file handling.

Important APIs/types/functions: `TestConfig::SetUp()` sets dummy config paths. `TearDown()` removes a generated empty config file if present. `missingConfigFile` builds argv with `cfgFile=<missing>` and expects `InvalidConfigException`. `defaultConfigFile` locates the binary directory through `/proc/self/exe`, constructs `dist/etc/beegfs-meta.conf`, and attempts `Config` construction, accepting `ConnAuthFileException`.

Control flow: The missing-file test ensures the dummy path does not exist by appending an integer if needed. The default-config test fails on `readlink` errors or truncation, then constructs argv strings with explicit null terminators.

State and persistence: Uses `/tmp` dummy paths and reads the test-installed default config. It may delete `/tmp/emptyConfigFile.conf.meta` if created.

Dependencies and integration: Depends on metadata `Config`, BeeGFS `StorageTk`, logging, GoogleTest, `ConnAuthFileException`, and `dirname()`.

Risks and test signals: Tests depend on Linux `/proc/self/exe` and copied config layout. The default-config test treats auth-file failures as acceptable because parsing reached that stage. It does not validate individual config fields.
