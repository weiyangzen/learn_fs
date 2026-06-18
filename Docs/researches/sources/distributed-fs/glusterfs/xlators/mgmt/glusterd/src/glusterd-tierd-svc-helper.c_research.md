# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-tierd-svc-helper.c

## Purpose
`glusterd-tierd-svc-helper.c` provides helper routines for glusterd's tier daemon service paths and volfile comparison checks. It builds runtime, socket, pidfile, volfile, and log paths for a tiered volume and verifies whether an existing tierd volfile matches a newly generated rebalance volfile either byte-for-byte or by topology.

This file is part of the older tiering service support. Its functions are small, but they sit on the boundary between volume metadata, service management, volfile generation, and filesystem cleanup.

## Important APIs and Functions
`glusterd_svc_build_tierd_rundir()` derives the tier work directory with `GLUSTERD_GET_TIER_DIR()` and appends `/run`.

`glusterd_svc_build_tierd_socket_filepath()` builds a node-specific raw socket path under the tierd run directory as `run-<MY_UUID>`, then passes it to `glusterd_set_socket_filepath()` so final socket path handling respects glusterd's socket path rules.

`glusterd_svc_build_tierd_pidfile()` builds `<rundir>/<volname>-tierd.pid`.

`glusterd_svc_build_tierd_volfile_path()` derives the volume directory with `GLUSTERD_GET_VOLUME_DIR()` and appends `<volname>-tierd.vol`.

`glusterd_svc_build_tierd_logdir()` builds `<conf->logdir>/tier/<volname>`, and `glusterd_svc_build_tierd_logfile()` appends `tierd.log`.

`glusterd_svc_check_tier_volfile_identical()` creates a secure temporary file under `/tmp`, generates a rebalance volfile into it with `build_rebalance_volfile()`, and compares it with the existing tierd volfile using `glusterd_check_files_identical()`.

`glusterd_svc_check_tier_topology_identical()` follows the same temporary-volfile pattern but compares only topology with `glusterd_check_topology_identical()`.

## Control Flow
Path builders are direct string-construction helpers. They read `THIS->private` as `glusterd_conf_t`, use path macros for the volume or tier work directory, and write into caller-provided buffers using `snprintf()`.

The socket helper first builds the run directory, formats a UUID-specific socket basename, checks for `snprintf()` truncation or error, zeroes the source path on failure, and delegates final path normalization to `glusterd_set_socket_filepath()`.

Both comparison functions start by building the current tierd volfile path. They allocate a `/tmp/g<svc_name>-XXXXXX` template with `gf_asprintf()`, call `mkstemp()`, mark the temp file for cleanup, generate a fresh rebalance volfile, compare it against the current volfile, then close and unlink the temp file and free the template string.

## State and Persistence Behavior
The path builders do not create directories or files; they only fill buffers. The comparison functions create a temporary file with mode 0600 through `mkstemp()`, write generated volfile content through `build_rebalance_volfile()`, compare it, and unlink it before return. The persistent tierd volfile path is read for comparison but not modified here.

The functions rely on `THIS->private` for `glusterd_conf_t`, including workdir and logdir configuration. They use `MY_UUID` to make socket names node-specific.

## Dependencies and Integration Points
The file includes `glusterd.h`, `glusterd-utils.h`, `glusterd-tierd-svc-helper.h`, `glusterd-messages.h`, `glusterd-volgen.h`, and `glusterfs/syscall.h`. It integrates with path macros such as `GLUSTERD_GET_TIER_DIR()` and `GLUSTERD_GET_VOLUME_DIR()`, service path normalization in `glusterd_set_socket_filepath()`, volfile generation in `build_rebalance_volfile()`, file comparison helpers, and syscall wrappers `sys_unlink()` and `sys_close()`.

The generated paths are expected to be consumed by glusterd service-management code for tierd start, stop, volfile refresh, pid tracking, socket communication, and logging.

## Risks and Edge Cases
Several path helpers use `snprintf()` without checking truncation, except for the intermediate socket path. Callers provide buffer lengths, so too-small buffers can silently receive truncated rundir, pidfile, volfile, logdir, or logfile paths.

`glusterd_svc_build_tierd_logdir()` declares `glusterd_conf_t *conf = THIS->private` but formats with `priv->logdir`. Unless `priv` is provided by a macro or outer scope not visible in this file, that is a compile-time defect; the apparent intended variable is `conf->logdir`.

The comparison functions create temp files in `/tmp` and pass the name to `build_rebalance_volfile()`. `mkstemp()` makes the file securely, but the generated pathname still exists until cleanup. Cleanup is careful but depends on `tmpclean` or `need_unlink` being set only after successful `mkstemp()`.

The temp file descriptor remains open while `build_rebalance_volfile()` writes by path. This may be fine on POSIX systems, but tests should verify the generator truncates or writes the intended file content when the descriptor already exists.

`identical` validation differs between the two comparison functions. The byte comparison function uses `GF_VALIDATE_OR_GOTO()` for `identical`; the topology comparison checks `(!identical) || (!this->private)` manually and then validates `conf`. Null `volinfo` and null `svc_name` are not explicitly checked in either function.

## Test Signals
Path tests should assert exact rundir, socket, pidfile, volfile, logdir, and logfile outputs for representative volume names and UUIDs, including long names near `PATH_MAX` and small caller buffers.

Comparison tests should cover identical volfiles, changed volfile contents with same topology, topology changes, `mkstemp()` failure, `build_rebalance_volfile()` failure, comparison helper failure, null `identical`, and cleanup of temp files and descriptors on every exit path.

Build or static-analysis tests should catch the likely `priv->logdir` variable error in `glusterd_svc_build_tierd_logdir()` and any missing prototype mismatch with `glusterd-tierd-svc-helper.h`.
