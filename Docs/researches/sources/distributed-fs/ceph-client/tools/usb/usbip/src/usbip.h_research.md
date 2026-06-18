# sources/distributed-fs/ceph-client/tools/usb/usbip/src/usbip.h

Purpose: `usbip.h` is the internal CLI header for `usbip` subcommands.

Important APIs: it conditionally includes generated `config.h` and declares command entry points `usbip_attach()`, `usbip_detach()`, `usbip_list()`, `usbip_bind()`, `usbip_unbind()`, and `usbip_port_show()`, plus usage functions for commands that have argument help.

Control flow and integration: `usbip.c` dispatches through these prototypes; each subcommand implements its own getopt parsing and returns `0` or negative failure.

State, dependencies, risks, and tests: the header has no state. It depends on the source files matching function signatures. Risks are minimal but adding a command requires coordinated updates to this header and the command table. Test signals are successful CLI build and all command symbols resolving at link time.
