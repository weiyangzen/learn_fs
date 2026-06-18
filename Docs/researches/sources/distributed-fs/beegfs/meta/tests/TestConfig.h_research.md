## sources/distributed-fs/beegfs/meta/tests/TestConfig.h

Purpose: Declares the GoogleTest fixture and constants for metadata config tests.

Important APIs/types/functions: Defines dummy config paths, relative default config path, app name, and `TestConfig` with `SetUp()`/`TearDown()`, `LogContext`, and path members.

Control flow: Header only declares fixture lifecycle.

State and persistence: Fixture owns path strings used by tests and cleanup.

Dependencies and integration: Includes metadata config, logging, GoogleTest, connection-auth exception, and `libgen.h`.

Risks and test signals: Hard-coded `/tmp` paths can collide across parallel test runs. Tests should use unique temp paths to avoid environmental flakes.
