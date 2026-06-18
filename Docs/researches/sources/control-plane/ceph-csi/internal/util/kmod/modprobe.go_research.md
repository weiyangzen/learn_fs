<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/kmod/modprobe.go -->
## sources/control-plane/ceph-csi/internal/util/kmod/modprobe.go

**Purpose:** Ensures a Linux kernel module is available, loading it with `modprobe` only if it is not already present under `/sys/module`.

**Important APIs and functions:** `Modprobe(ctx, kmod)` checks `/sys/module/<kmod>` with `os.Stat`, returns nil if found, wraps unexpected stat errors, and otherwise runs `util.ExecCommand(ctx, "modprobe", kmod)`.

**Control flow, state, and persistence:** The function mutates kernel module state when `modprobe` succeeds. It logs warnings on stat or load failure and includes stderr in load errors.

**Dependencies and integration points:** Depends on `os`, internal command execution, and logging. It integrates with node setup paths that require kernel modules for storage features.

**Risks and test signals:** Requires host privileges and `modprobe` availability. `ExecCommand` has no timeout, so module loading can hang. Module names are used directly in a command after caller selection. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/kmod/modprobe.go -->
