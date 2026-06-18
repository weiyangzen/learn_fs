# sources/distributed-fs/ceph-client/net/x25/Makefile

Purpose: maps `CONFIG_X25` to the packet-layer object set and conditionally includes sysctl support.

Important build mappings: `obj-$(CONFIG_X25) += x25.o`; `x25-y` aggregates `af_x25.o`, device, facilities, input, link, output, route, subroutine, timer, proc, and forwarding files. `x25-$(CONFIG_SYSCTL)` adds `sysctl_net_x25.o`.

Control flow: kbuild links all listed `x25-y` objects into the built-in or modular `x25.o` target. The sysctl object is included only when both X.25 and generic sysctl support are enabled.

State and persistence: no runtime state is managed here. The file is the persistent build contract for module contents and must remain synchronized with code references and Kconfig help.

Dependencies and integration: aligns with the AF_X25 module initialization in `af_x25.c`, optional `/proc/sys/net/x25` registration in `sysctl_net_x25.c`, and proc diagnostics in `x25_proc.c`.

Risks and test signals: missing objects cause unresolved symbols or silently absent features. Tests should include `CONFIG_X25=y/m`, `CONFIG_SYSCTL=y/n`, module load/unload, and symbol resolution for route/link/proc/forwarding helpers.
