# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mountbroker.c

## Purpose

`glusterd-mountbroker.c` implements GlusterD's mountbroker support. It parses configured mount specifications, checks a user's mount request against those specifications, creates a controlled mountpoint/cookie path under `mountbroker-root`, and launches `glusterfs` with the approved mount arguments. It is designed to let limited users obtain mounts, especially geo-replication mounts, without unrestricted command execution.

## Important APIs, types, and functions

The file operates on `gf_mount_spec_t` and `gf_mount_pattern_t` from `glusterd-mountbroker.h`. `parse_mount_pattern_desc()` parses the mount-spec language into an array of patterns. Supported set relations are `SUB`, `SUP`, `EQL`, `MEET`, and `SUB+`; a leading `-` negates a pattern. `make_georep_mountspec()` builds a geo-replication-oriented specification using `georep_mnt_desc_template`, `GF_CLIENT_PID_GSYNCD`, a root user map, log directory, and one or more volume names.

Request evaluation is split into helpers. `seq_dict_foreach()` walks dictionary keys named `0`, `1`, `2`, and so on in order. `match_comp()` compares requested argument components with pattern components, treating the suffix after `=` as fnmatch-capable. `relate_sets()` computes whether the request has private elements, the pattern has private elements, and whether they share common elements. `evaluate_mount_request()` applies every pattern and returns the mapped root UID parsed from `user-map-root=...`, or a negative errno. `glusterd_do_mount()` is the exported execution path.

## Control flow

Configuration parsing starts with a descriptor string such as `SUP(...)SUB+(...)MEET(...)`. `parse_mount_pattern_desc()` counts pattern groups by closing parentheses, allocates `mspec->patterns`, parses condition names and component lists, supports `SUB+` by copying the most recent `SUP` component set into the current pattern, and stores each component as a string. On syntax errors it logs an invalid-entry message and returns `-1`.

At request time, `glusterd_do_mount()` first reads `mountbroker-root` from translator options and validates the label. It finds the matching `gf_mount_spec_t` in `priv->mount_specs`, evaluates the argument dictionary against the configured patterns, extracts `volfile-id=...`, and requires that the named volume exists and is started. It then creates or verifies a per-UID directory under the root, creates a unique temporary mount directory with `mkdtemp()`, reserves a cookie name in `MB_HIVE` with `mkstemp()`, creates a private symlink from the cookie to the mountpoint, and invokes `SBIN_DIR "/glusterfs"` with each argument converted to `--<arg>` plus the mountpoint path.

## State and persistence behavior

Mount specs are held in memory on `glusterd_conf_t::mount_specs`. The mount operation creates filesystem state under `mountbroker-root`: per-user directories named `user<uid>`, temporary mountpoint directories, cookie entries under `mb_hive`, and symlinks from cookie paths to mountpoints. On success, ownership of the cookie path is returned via `*path`; on failure, the code attempts to unlink the temporary cookie symlink, remove the temporary mountpoint, and unlink the reserved cookie file. No Gluster volume metadata is persisted by this file, but it depends on live `glusterd_volinfo_t` state to reject mounts for missing or stopped volumes.

## Dependencies and integration points

The implementation uses Gluster utility APIs (`dict_t`, `runner_t`, `gf_asprintf`, `GF_CALLOC`, `gf_strdup`, logging and message IDs), POSIX account lookup (`getpwnam()`), filesystem syscalls through Gluster wrappers, and `fnmatch()` for wildcard matching. It integrates with GlusterD options (`this->options`), private config (`THIS->private`), volume lookup (`glusterd_volinfo_find()`), started-state checks (`glusterd_is_volume_started()`), and the `glusterfs` binary path from `SBIN_DIR`.

## Risks and edge cases

The parser mutates the descriptor string in place by replacing separators with NUL or spaces, so callers must pass mutable storage. Syntax and allocation failure cleanup is intentionally incomplete because comments assume termination on parse failure; that is a leak risk if parsing becomes recoverable. `make_georep_mountspec()` sets `ret = -1` if any of its temporary buffers are NULL during cleanup, which means a partially successful path with an optional NULL would be treated as failure; in the current flow all three are expected after success.

Mount execution is security-sensitive. Correctness depends on matching only approved `--` arguments, finding exactly one valid `user-map-root`, checking per-user directory mode/owner/group, and not following attacker-controlled paths. The code uses `mkdtemp()`, `mkstemp()`, `lstat()`, `chown()`, and strict mode checks, but failure cleanup manipulates `mtptemp` by toggling the hidden `/cookie` suffix and assumes `cookieswitch` was initialized. Tests should cover failures before and after `cookieswitch` assignment. `seq_dict_foreach()` stops at the first missing numeric key, so sparse argument dictionaries silently ignore later keys.

## Test signals

Focused tests should cover parsing of empty descriptors, valid `SUB`/`SUP`/`EQL`/`MEET`/negated/`SUB+` descriptors, malformed descriptors with `&`, missing parentheses, and wildcard matching after `=`. Request tests should verify label miss, missing `mountbroker-root`, empty label, missing `volfile-id`, stopped/missing volume, ambiguous or nonexistent `user-map-root`, sparse dict keys, and mismatched set relations. Filesystem integration tests should assert user directory attributes, cookie symlink layout under `mb_hive`, glusterfs runner arguments, and cleanup after failures at mkdir, mkdtemp, mkstemp, symlink/rename, and runner execution.
