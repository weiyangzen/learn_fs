## sources/distributed-fs/lizardfs/src/mount/polonaise/setup.cc

Purpose: defines the global `Setup gSetup` used by the Polonaise server.

Important behavior: no logic beyond storage definition.

State and integration: `gSetup` is populated by `parse_command_line` and consumed by `main` to initialize `LizardClient` and choose transport settings.

Risks and tests: global mutable configuration makes repeated in-process server startup hard to test. Tests should reset or avoid sharing process state.
