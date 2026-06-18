# Research: sources/compression/xz/src/xz/sandbox.c
## sources/compression/xz/src/xz/sandbox.c

Purpose: Implements optional platform sandboxing for OpenBSD pledge, Linux Landlock, and FreeBSD Capsicum.

Important APIs and functions: Public functions are `sandbox_init()`, `sandbox_enable_read_only()`, `sandbox_allow_strict()`, and `sandbox_enable_strict_if_allowed()`. `prepare_for_strict_sandbox()` preloads translation, strerror, and multibyte/iconv resources and checks whether strict mode was allowed. Landlock support uses `enable_landlock()` to build a restrictive ruleset minus required rights.

Control flow: `main.c` calls `sandbox_init()` early when enabled. After argument parsing, if operation is stdout-only/test/list/read-only, `main.c` calls `sandbox_enable_read_only()` and may call `sandbox_allow_strict()` for exactly one source to stdout. `file_io.c` calls `sandbox_enable_strict_if_allowed()` after opening the source and creating the abort pipe, so strict sandboxing can deny future opens.

State and persistence: Static `strict_sandbox_allowed` gates strict mode. Sandbox effects persist at kernel/process level and are intentionally irreversible.

Dependencies and integration points: Depends on platform feature macros from `sandbox.h`, `private.h`, `message_fatal()`, file descriptors from `file_io.c`, and Landlock helper wrappers. Pledge profiles distinguish full initial access, read-only access, and strict stdio-only access. Capsicum limits rights on source/stdin/stdout/stderr and abort pipe fds.

Risks: Strict sandboxing can fail if locale, gettext, iconv, or other lazy-loaded files were not preloaded. Landlock ABI differences require careful rights masks. Capsicum silently ignores ENOSYS but fatals on other failures. Error messages in `sandbox_init()` are intentionally untranslated because gettext is not initialized yet.

Test signals: Run on OpenBSD, Linux with/without Landlock and different ABI versions, FreeBSD with/without Capsicum, stdout-only compression/decompression/test/list, one-file strict mode, `--files` disabling strict mode, and locale/translations under strict sandbox.
