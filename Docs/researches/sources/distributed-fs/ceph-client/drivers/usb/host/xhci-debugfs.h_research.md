# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-debugfs.h

Purpose: declares debugfs register offsets, helper data structures, and exported debugfs lifecycle hooks for xHCI.

Important APIs and types: offset macros describe capability, operational, runtime, legacy-support, protocol, and DbC extended capability registers. `dump_register()` creates `debugfs_reg32` entries. `struct xhci_regset` tracks dynamically allocated regset metadata in `xhci->regset_list`; `struct xhci_file_map` maps debugfs filenames to seq show functions; `struct xhci_ep_priv` and `struct xhci_slot_priv` hold per-endpoint/per-slot debugfs metadata and live xHCI pointers. Public functions cover root/controller/device/endpoint/stream debugfs creation and removal.

Control flow: with `CONFIG_DEBUG_FS`, `xhci.c`, device allocation, endpoint configuration, and stream setup call the declared functions to maintain the debugfs tree. Without debugfs, inline stubs preserve call-site simplicity and compile out all side effects.

State and persistence: structures store debugfs-only runtime metadata. The header itself persists no data; it defines names, fixed maximum debugfs name length, and live pointer containers used by `xhci-debugfs.c`.

Dependencies and integration points: depends on Linux debugfs and xHCI core types. It is included by `xhci-debugfs.c` and by xHCI memory/lifecycle code that needs conditional calls.

Risks: register offset macros must remain synchronized with xHCI layout and the C source arrays. Per-slot `eps[31]` assumes xHCI endpoint index bounds. Stub functions silently do nothing, so debug-only diagnostics must not be required for functional behavior.

Test signals: `CONFIG_DEBUG_FS=y/n` builds; compile coverage for every declared function; debugfs path creation/removal in controller and endpoint lifecycle; review of offsets against xHCI spec and `xhci.h` register definitions.
