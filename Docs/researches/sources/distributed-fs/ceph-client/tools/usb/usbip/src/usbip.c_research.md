# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.c

Purpose: `usbip.c` is the top-level command dispatcher for the `usbip` CLI.

Important APIs and functions: `struct command` maps command names to implementation functions, help text, and usage callbacks. The command table includes `help`, `version`, `attach`, `detach`, `list`, `bind`, `unbind`, and `port`. `usbip_help()` prints global or command-specific help. `usbip_version()` prints `PACKAGE_STRING`. `main()` handles global `--debug`, `--log`, and `--tcp-port`.

Control flow: after global option parsing, `main()` identifies the subcommand, rewrites `argc/argv` to start at that command, resets `optind`, and calls `run_command()`. Invalid options or unknown commands print usage/help and return failure.

State and dependencies: global logging flags from `usbip_common` and global port state from `usbip_network` are modified. It depends on command implementations declared in `usbip.h`. Risks include global `optind` reuse across subcommands, default command failure when no command is provided, and syslog opened with an empty ident. Test signals are `usbip help`, per-command help, `usbip version`, custom port selection, and debug output.
