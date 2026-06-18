# sources/distributed-fs/ceph-client/net/bluetooth/hci_debugfs.h

## Purpose

`hci_debugfs.h` is the debugfs integration boundary for the HCI core. It declares the debugfs creation functions used by core/setup code when Bluetooth debugfs support is enabled and provides no-op inline stubs when `CONFIG_BT_DEBUGFS` is disabled. This lets callers unconditionally invoke debugfs setup without scattering preprocessor checks through protocol code.

## Important APIs, Types, and Functions

When `IS_ENABLED(CONFIG_BT_DEBUGFS)` is true, the header declares:

- `hci_debugfs_create_common(struct hci_dev *hdev)`
- `hci_debugfs_create_bredr(struct hci_dev *hdev)`
- `hci_debugfs_create_le(struct hci_dev *hdev)`
- `hci_debugfs_create_conn(struct hci_conn *conn)`
- `hci_debugfs_create_basic(struct hci_dev *hdev)`

When debugfs is disabled, each function is defined as an empty `static inline` with the same signature. The header relies on prior visibility of `struct hci_dev` and `struct hci_conn`, normally supplied by `hci_core.h` or nearby Bluetooth headers in the including C file.

## Control Flow

There is no runtime control flow beyond compile-time selection. Enabled builds link to the implementations in `hci_debugfs.c`. Disabled builds compile calls away as empty inline functions. This pattern preserves call-site readability while eliminating runtime branches and object dependencies in non-debugfs configurations.

## State and Persistence Behavior

The header owns no state. Its compile-time branch determines whether debugfs entries are created at all. In disabled builds, no debugfs files, directories, or mutable debug knobs from `hci_debugfs.c` exist, and all related side effects are absent.

## Dependencies and Integration Points

The header depends on `CONFIG_BT_DEBUGFS` and Linux `IS_ENABLED()` semantics. It is included by `hci_core.c` and any setup path that wants to create debugfs files without direct preprocessor guards. It forms the ABI-like internal contract between HCI core code and the debugfs implementation.

## Risks and Edge Cases

The main risk is signature drift: implementations in `hci_debugfs.c`, enabled declarations, and disabled stubs must stay identical. If a call site depends on side effects from debugfs creation, that logic would silently disappear in non-debugfs builds, so debugfs functions must remain observational or diagnostic rather than required for protocol correctness.

## Test Signals

Build testing should cover both `CONFIG_BT_DEBUGFS=y/m` and disabled configurations. Enabled builds should link `hci_debugfs.c` and expose files; disabled builds should compile callers with no unresolved symbols and no debugfs behavior. Static analysis should flag any new debugfs creation function added to `hci_debugfs.c` but not represented in both header branches.
