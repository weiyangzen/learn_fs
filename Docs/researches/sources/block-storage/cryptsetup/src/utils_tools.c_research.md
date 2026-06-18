# File Research: sources/block-storage/cryptsetup/src/utils_tools.c

This file provides common command-line utility support used across cryptsetup tools.

Key responsibilities:
- Global interrupt handling through `quit`, SIGINT/SIGTERM handlers, and signal blocking/unblocking.
- Common logging callbacks for normal, verbose, error, and debug output.
- Interactive confirmation prompts requiring uppercase `YES`.
- Exit/status translation and user-facing command status messages.
- UUID shorthand conversion for `UUID=<uuid>` into `/dev/disk/by-uuid/<uuid>`.
- POPT usage cleanup and version/debug command reporting.
- Keyslot/token success and token error messages.
- Device-size string parsing with binary/decimal/unit suffixes.
- Volume key file read/write helpers.
- Package feature flag printing.
- Device-mapper name validation.

Important functions:
- `set_int_handler()`, `set_int_block()`, `check_signal()` implement cooperative cancellation semantics used by reencryption and wipe/progress loops.
- `tool_log()` and `quiet_log()` are callbacks passed into libcryptsetup.
- `yesDialog()` and `noDialog()` wrap `_dialog()` and temporarily unblock signals while reading from the terminal.
- `translate_errno()` maps negative errno-style results into cryptsetup’s compact exit codes.
- `tools_string_to_size()` parses suffixes such as sectors, K/M/G/T, KiB/MiB/GiB/TiB, and decimal KB/MB/GB/TB.
- `tools_read_vk()` reads an exact-size volume key into secure memory.
- `tools_write_mk()` creates a new key file with exclusive create semantics.
- `tools_check_newname()` rejects overlong dm names and names containing `/`.

Behavioral notes:
- `uuid_or_device()` uses a static buffer and only rewrites strings with a valid `UUID=` prefix containing hex digits and dashes.
- `tools_token_error_msg()` distinguishes missing PIN, wrong keyslot passphrase, missing resource, and no usable token.
- Dialogs default to their caller-provided answer if stdin is not a TTY.
- `tools_write_mk()` creates files with read permission for the owner only.
