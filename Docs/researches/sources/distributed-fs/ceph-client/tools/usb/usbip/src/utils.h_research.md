# sources/distributed-fs/ceph-client/tools/usb/usbip/src/utils.h

Purpose: `utils.h` declares the usbip CLI utility function for editing `usbip-host` match state.

Important API: `int modify_match_busid(char *busid, int add);` returns `0` on write success and `-1` on failure.

Control flow and integration: the bind and unbind subcommands include this header to coordinate driver match-table changes with sysfs bind/unbind operations.

State, dependencies, risks, and tests: the header has no state and no external dependencies beyond matching the implementation signature. Risks are minimal; semantics of `add` are implicit rather than an enum. Test signals are clean command compilation and bind/unbind behavior.
