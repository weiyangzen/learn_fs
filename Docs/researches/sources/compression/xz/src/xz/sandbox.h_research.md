# Research: sources/compression/xz/src/xz/sandbox.h
## sources/compression/xz/src/xz/sandbox.h

Purpose: Declares sandbox feature detection and public sandbox lifecycle functions.

Important APIs: Defines `ENABLE_SANDBOX` when pledge, Linux Landlock, or Capsicum support is configured. Declares early `sandbox_init()`, read-only `sandbox_enable_read_only()`, strict-mode permission flag `sandbox_allow_strict()`, and `sandbox_enable_strict_if_allowed(src_fd, pipe_event_fd, pipe_write_fd)`.

Control flow and integration: `main.c` controls early and read-only sandbox phases; `file_io.c` invokes strict mode after source open. The pipe fd parameters tie strict sandboxing to the self-pipe signal design in `file_io.c`.

State and persistence: Runtime state is internal to `sandbox.c`; process sandbox restrictions persist after enabling.

Risks: Consumers must pass valid fds and only call strict enable after all future file opens are unnecessary. The macro enables code paths in multiple modules, so build coverage is important.

Test signals: Compile with each sandbox backend and without sandbox support; exercise read-only and strict transitions through CLI modes.
