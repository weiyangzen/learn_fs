<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit.go -->
## sources/control-plane/ceph-csi/internal/util/pidlimit.go

**Purpose:** Reads and writes the current process cgroup PID limit through `pids.max`, supporting cgroup v1 and v2 layouts.

**Important APIs and functions:** `getCgroupPidsFile` parses `/proc/self/cgroup` and builds the matching `pids.max` path using v1 or v2 format strings. `GetPIDLimit` reads `pids.max`, returning `-1` for `max`. `SetPIDLimit` writes a numeric limit or `max` for `-1`.

**Control flow, state, and persistence:** The helper scans cgroup lines for v2 `0::...` first match or v1 `:pids:` subsystem. Reading is non-mutating. Writing opens the cgroup control file with `os.Create`, truncates it, writes the limit string, and closes it.

**Dependencies and integration points:** Depends on `/proc`, `/sys/fs/cgroup`, buffered IO, strconv, and strings. It integrates with process resource tuning for Ceph-CSI containers.

**Risks and test signals:** Path construction assumes standard cgroup mount layout. Writing requires privileges and can fail in restricted containers. `os.Create` truncates the control file before write, though cgroup pseudo-files handle this differently than regular files. Tests are skipped unless `CEPH_CSI_RUN_ALL_TESTS` is set and only lightly exercise get/set.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/pidlimit.go -->
