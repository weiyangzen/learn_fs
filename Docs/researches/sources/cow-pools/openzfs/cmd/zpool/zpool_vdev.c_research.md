# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_vdev.c

This file converts zpool CLI vdev arguments into validated nvlist vdev trees. It performs userland validation before handing configurations to libzfs/kernel code.

Primary responsibilities:
- Parse device, file, mirror, raidz, dRAID, spare, log, cache, special, and dedup vdev specifications.
- Validate that devices exist and are usable.
- Detect devices already in use.
- Validate replication consistency.
- Prepare, partition, label, and update whole-disk vdev nvlists.
- Build root vdev nvlists for create/add/replace flows.
- Build split-mirror vdev specifications.

Global state:
- `error_seen`: tracks whether `vdev_error()` has already printed the invalid-spec header.
- `is_force`: controls whether error text says `-f` may override issues or manual repair is required.

Error reporting:
- `vdev_error()` prints a single grouped header followed by formatted validation errors.

Leaf vdev construction:
- `make_leaf_vdev()` accepts:
  - full paths;
  - shorthand device names resolved with `zfs_resolve_shortname()`;
  - dRAID spare names;
  - regular files.
- It distinguishes disk vs file using whole-disk detection and `stat64`.
- It stores `ZPOOL_CONFIG_PATH`, `ZPOOL_CONFIG_TYPE`, optional `ZPOOL_CONFIG_WHOLE_DISK`, enclosure sysfs path, and optional `ZPOOL_CONFIG_ASHIFT`.
- If ashift was not explicitly provided, it checks a sector-size database and converts sector size to ashift.

Device-use checks:
- `check_file_generic()` opens a file and asks `zpool_in_use()` whether it belongs to an active/exported/potentially-active/spare pool.
- Active pools and spare reservations are hard errors; exported/potentially active pools may be force-overridden depending on state.
- `is_spare()` identifies dRAID spares and labeled hot spares, optionally checking a supplied pool config’s spare GUID list.
- `is_device_in_use()` recursively walks children, spares, and L2ARC devices and dispatches to `check_device()` or `check_file()`.

Replication validation:
- `replication_level_t` captures vdev type, child count, and parity.
- `get_replication()` walks top-level non-log, non-hole, non-indirect vdevs and detects:
  - mixed files and disks inside a group;
  - child size mismatches beyond `ZPOOL_FUZZ` of 16 MiB;
  - inconsistent vdev types;
  - inconsistent parity;
  - inconsistent mirror/raidz width.
- dRAID is treated as raidz-like for redundancy comparisons.
- raidz and mirror combinations are accepted only when their tolerated disk failures match.
- `check_replication()` compares new specs against existing pool replication when adding to a pool and allows all-log/spare-only specs to bypass replication checks.

Disk preparation:
- `make_disks()` recursively finds disk leaves.
- For non-whole disks it updates multipath device strings if needed and zeros the first 4 KiB unless the path is a spare.
- For whole disks it:
  - resolves the raw device path;
  - derives the partition path with `zfs_append_partition()`;
  - handles udev symlink removal for `/dev/disk` paths;
  - calls `zpool_prepare_and_label_disk()`;
  - waits for the partition path with `zpool_label_disk_wait()`;
  - zeros the partition label area;
  - updates `ZPOOL_CONFIG_PATH` to the partition path;
  - updates device id strings.
- Disk labeling is skipped during dry runs.

Grouping and dRAID parsing:
- `get_parity()` parses raidz/dRAID parity suffixes and enforces maximum parity.
- `is_grouping()` recognizes `raidz*`, `draid*`, `mirror`, `spare`, `log`, `special`, `dedup`, and `cache`, returning min/max child counts and canonical type.
- `draid_config_by_type()` parses `draid[parity][:<data>d][:<children>c][:<spares>s][:<width>w]`.
- dRAID validation handles failure groups/domains, data/parity/spare layout, width consistency, maximum children, and group-count calculation before storing:
  - `ZPOOL_CONFIG_NPARITY`
  - `ZPOOL_CONFIG_DRAID_NDATA`
  - `ZPOOL_CONFIG_DRAID_NSPARES`
  - `ZPOOL_CONFIG_DRAID_NGROUPS`
  - `ZPOOL_CONFIG_DRAID_NCHILDREN`

Spec construction:
- `construct_spec()` parses the CLI argv stream.
- It validates `ashift` from pool properties.
- It tracks context flags for log, special, dedup, and spare sections.
- It enforces single `spare`, `log`, and `cache` sections.
- Log grouped vdevs only support mirrors.
- It supports dRAID `fgroup` / `failure_group` and `fdomain` / `failure_domain` markers and validates consistent group/domain sizes.
- Failure domains are reordered before nvlist insertion so children are laid out appropriately.
- It builds a root nvlist with `VDEV_TYPE_ROOT`, top-level children, optional `ZPOOL_CONFIG_SPARES`, and optional `ZPOOL_CONFIG_L2CACHE`.
- It rejects an empty spec with no top-level, spare, or cache device.

Exported functions:
- `split_mirror_vdev()` optionally constructs a target device spec, labels disks unless dry-run, rejects grouping keywords as split target devices, then calls `zpool_vdev_split()`.
- `make_root_vdev()` is the main exported builder. It:
  - constructs the spec;
  - obtains current pool config when adding/replacing;
  - checks for in-use devices;
  - optionally checks replication;
  - ensures new pools contain at least one normal top-level vdev;
  - labels disks unless dry-run;
  - returns the final root nvlist.

Notable constraints:
- The parser deliberately performs many userland checks before kernel submission.
- Error paths often skip cleanup because the command will fail immediately, but successful paths free temporary child nvlists after copying them into parent arrays.
- Auxiliary vdevs such as logs, special, dedup, cache, and spares are treated differently from normal data vdevs during validation.
