# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/Makefile

Purpose: wires SGI XP-related modules into the kernel build for `CONFIG_SGI_XP`. It defines object composition for the XP base module, XPC communication module, and xpnet module.

Important build entries: `xp.o` is built from `xp_main.o xp_uv.o`; `xpc.o` is built from `xpc_main.o xpc_channel.o xpc_partition.o xpc_uv.o`; `xpnet.o` is also selected by `CONFIG_SGI_XP`.

Control flow: there is no runtime control flow, but build-time composition determines which implementation files are linked into each module. The UV-specific files are included directly in the object lists, so the C code performs runtime/platform gating through `is_uv_system()` and compile-time guards.

State and persistence: no persistent state. The Makefile controls module boundaries and symbol ownership.

Dependencies and integration: `xp.o` exports the public XP interface and UV address/copy hooks. `xpc.o` consumes those XP hooks and provides channel/partition messaging. `xpnet.o` likely uses XP/XPC channels for network transport outside this work item.

Risks: because both `xp.o` and `xpc.o` are gated by the same config, callers may still see XP loaded without XPC initialized until `xpc_set_interface()` runs. Build failures in `xpc_uv.o` or `xpnet.o` can surface even when this subset looks self-contained.

Test signals: kernel build with `CONFIG_SGI_XP=y/m`, module link symbol checks, and load/unload sequencing for `xp`, `xpc`, and `xpnet`.
