<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/common.c -->
# sources/distributed-fs/ceph-client/tools/bpf/bpftool/common.c

Purpose: this file contains shared bpftool utilities for diagnostics, resource limits, bpffs/tracefs mounting, pinned object access, object pinning, fd/type parsing, object lookup by id/name/tag/path, device printing, kernel config reading, and small formatting helpers.

Important APIs/functions: diagnostics are `p_err()` and `p_info()`. `set_max_rlimit()` probes memcg-vs-rlimit accounting and raises `RLIMIT_MEMLOCK` when needed. Mount helpers include `mount_tracefs()`, `create_and_mount_bpffs_dir()`, and `mount_bpffs_for_file()`. Object helpers include `open_obj_pinned()`, `open_obj_pinned_any()`, `do_pin_fd()`, and `do_pin_any()`. Parsers include `prog_parse_fds()`, `prog_parse_fd()`, `map_parse_fds()`, `map_parse_fd()`, `map_parse_fd_and_info()`, and `parse_u32_arg()`. Other helpers include pinned-object table building, `get_prog_full_name()`, fdinfo reading, network device/offload printing, attach type string conversion, and `read_kernel_config()`.

Control flow: most helpers are called by command modules. Program/map parsing consumes `argc/argv` tokens by handle type (`id`, `name`, `tag`, `pinned`), opens matching FDs, and returns one or many descriptors. Name/tag lookup enumerates kernel IDs and filters info records. Pinning ensures a bpffs mount exists unless `--nomount` blocked it. Kernel config reading tries `/boot/config-$(uname -r)` then `/proc/config.gz`, validates the generated-file marker, and extracts requested `CONFIG_` values.

State and persistence: persistent mutations include mounting tracefs/bpffs, creating directories for pinning, and pinning BPF objects. Static transient state includes page-size cache and globals used by `nftw()` callbacks for pinned-object tables. Returned FDs and allocated strings/hashmaps transfer cleanup responsibility to callers.

Dependencies and integration points: it depends on libbpf, BTF APIs, zlib, Linux mount/proc/sysfs files, bpftool globals from `main.h`, and hashmap utilities. Nearly every bpftool command module uses these helpers for object handles and output.

Risks: `known_to_need_rlimit()` temporarily sets process soft memlock to zero; bpftool is single-threaded, but embedding this code elsewhere would be unsafe. Auto-mounting bpffs/tracefs changes system mount state unless `--nomount` is used. Name-based program/map lookup can match multiple objects and returns errors where a single FD is required. `get_fd_type()` relies on `/proc/self/fd` symlink text containing `bpf-map`, `bpf-prog`, or `bpf-link`. Kernel config parsing assumes the second line is the generated-file marker and may skip valid distro configs with different headers.

Test signals: command tests should cover every object handle form, multiple matches, stale IDs, pinned paths outside bpffs, auto-mount allowed/blocked, pin path already exists, map read-only open flags, program full-name fallback to BTF func info, offload device printing, kernel config fallback paths, and cleanup of allocated pinned-object tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpftool/common.c -->
