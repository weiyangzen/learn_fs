# File Research: sources/block-storage/stratisd/src/bin/utils/generators/lib.rs

Shared helpers for systemd generators.

Key behavior:
- Defines a logger that forwards log records to `stratisd::systemd::syslog`.
- `setup_logger()` installs the systemd logger at `Info`.
- `get_kernel_cmdline()` reads `/proc/cmdline` and returns a map from option name to optional list of values.
- Handles repeated kernel parameters by accumulating values.
- Bare flags are represented as `None`.
- `write_unit_file()` creates/truncates a destination file and writes generated unit contents.

Used by both Stratis rootfs and Clevis setup generators.
