# sources/control-plane/mayastor/libnvme-rs/src/nvme_tree.rs

Purpose: RAII and iterator adapters over libnvme's scanned topology tree.

Important APIs/types/functions: `NvmeRoot` owns `*mut nvme_root` and frees it in `Drop`. Iterators `NvmeHostIterator`, `NvmeSubsystemIterator`, `NvmeCtrlrIterator`, `NvmeNamespaceIterator`, and `NvmeNamespaceInCtrlrIterator` wrap libnvme `first`/`next` traversal functions.

Control flow: each iterator stores the current raw pointer; `next` calls the relevant first function when null, otherwise next function, returning `None` on null.

State/persistence: owns a libnvme tree snapshot for the lifetime of `NvmeRoot`; child pointers are valid only while the root/tree remains alive.

Dependencies/integration: used by `nvme_uri.rs` for block device discovery, disconnect, and listing.

Risks: raw pointers and lifetimes are only partially encoded. Iterators other than host do not tie their lifetime to `NvmeRoot`, so misuse outside current module patterns could access freed tree memory.

Test signals: device list/disconnect tests exercise traversal across hosts, subsystems, controllers, and namespaces.
