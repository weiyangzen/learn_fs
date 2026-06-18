# sources/distributed-fs/ceph-client/net/kcm/Kconfig

## Purpose
Defines the KCM socket feature. KCM multiplexes message-oriented application protocols over kernel connections such as TCP sockets.

## Important APIs, types, and functions
The symbol is `CONFIG_AF_KCM`, a tristate named "KCM sockets". It depends on `INET` and selects `BPF_SYSCALL` and `STREAM_PARSER`.

## Control flow
No runtime control flow. Enabling the symbol causes Kbuild to build the KCM module/object and ensures required BPF and stream parser infrastructure is present.

## State and persistence behavior
Only build configuration state exists. It determines whether PF_KCM can be registered at runtime.

## Dependencies and integration points
Integrates with TCP/INET sockets, BPF socket-filter programs used as message parsers, and the stream parser library.

## Risks and test signals
Risks are missing selected dependencies or unsupported builds without INET. Test modular and built-in builds, dependency resolution, and PF_KCM socket creation when enabled.
