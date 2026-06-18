<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Kconfig -->
# sources/distributed-fs/ceph-client/net/netlabel/Kconfig

## Purpose
`net/netlabel/Kconfig` defines the build-time option for the NetLabel subsystem, which provides explicit network packet labeling protocols such as CIPSO and RIPSO for Linux security modules.

## Important APIs, Types, and Functions
This file defines `config NETLABEL` as a boolean option. It depends on `SECURITY`, selects `CRC_CCITT` when IPv6 is enabled, defaults to `n`, and presents help text pointing users to kernel documentation and netlabel tools.

## Control Flow, State, and Persistence
There is no runtime control flow. The selected Kconfig value determines whether NetLabel objects are built into the kernel. Because it is boolean in this tree, NetLabel is built-in when enabled rather than a standalone module.

## Dependencies and Integration Points
The option gates compilation of the NetLabel source files in the directory and ties the subsystem to the broader Linux security framework. The IPv6 conditional CRC selection supports CALIPSO-style IPv6 labeling support.

## Risks and Test Signals
Risks include enabling NetLabel without the expected LSM policy users, missing CRC support for IPv6 label protocols, and assuming module unloadability when the option is boolean. Tests should cover Kconfig dependency resolution with and without `SECURITY`, IPv6 builds selecting CRC support, allnoconfig/default behavior, and successful compilation of NetLabel users when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Kconfig -->
