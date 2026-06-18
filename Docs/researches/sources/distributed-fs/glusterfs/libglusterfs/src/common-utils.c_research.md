# sources/distributed-fs/glusterfs/libglusterfs/src/common-utils.c

## Purpose
`common-utils.c` is a broad libglusterfs utility module. It collects process/runtime helpers, hashing and GFID generation, path and directory utilities, graph dumping, crash backtraces, string and numeric parsers, network/address validation, host identity checks, volfile server parsing, logging-path selection, thread helpers, pid/service checks, recursive removal, FOP metadata helpers, fd closing, group lookup, SHA-256, safe string copy, and miscellaneous conversion utilities.

## Important APIs, Types, And Functions
Hashing and identity helpers include `gf_xxh64_wrapper`, `gf_xxh64_hash_wrapper`, `gf_gfid_generate_from_xxh64`, `uuid_utoa`, `uuid_utoa_r`, `lkowner_utoa`, `leaseid_utoa`, `gf_leaseid_get`, `gf_existing_leaseid`, `gfid_to_ino`, and `glusterfs_compute_sha256`.

Filesystem/path helpers include `mkdir_p`, `gf_lstat_dir`, `gf_path_strip_trailing_slashes`, `gf_canonicalize_path`, `recursive_rmdir`, `gf_set_timestamp`, `gf_unlink`, `gf_nread`, `gf_nwrite`, `gf_pipe`, `close_fds_except_custom`, and `close_fds_except`.

Parsing helpers include `gf_trim`, `gf_strstr`, `gf_string2time`, `gf_string2percent`, the `gf_string2*` signed/unsigned/integer/double family, base-10 variants, `gf_string2bytesize_range`, `gf_string2percent_or_bytesize`, `gf_str_to_long_long`, `gf_string2boolean`, `gf_strn2boolean`, token iteration helpers, `gf_uint64_2human_readable`, and `gf_rebalance_thread_count`.

Networking helpers include `valid_host_name`, `valid_ipv4_address`, `valid_ipv6_address`, `valid_internet_address`, `gf_is_ip_in_net`, `mask_match`, `gf_get_hostname_from_ip`, `gf_interface_search`, `gf_is_loopback_localhost`, `gf_is_local_addr`, `gf_is_same_address`, `get_host_name`, `gf_process_getspec_servers_list`, `gf_set_volfile_server_common`, and reserved-port parsing through `gf_process_reserved_ports`.

Runtime and diagnostics helpers include `gf_assert`, `gf_log_dump_graph`, `gf_print_trace`, `generate_glusterfs_ctx_id`, `get_mem_size`, thread naming/creation helpers, `gf_is_service_running`, `gf_backtrace_save`, `fop_log_level`, `fop_enum_to_pri_string`, `gf_fop_string`, `gf_fop_int`, `gf_inode_type_to_str`, `gf_is_zero_filled_stat`, `gf_is_valid_xattr_namespace`, `gf_bits_count`, `gf_bits_index`, `gf_getgrouplist`, `find_xlator_option_in_cmd_args_t`, `gf_d_type_from_ia_type`, `gf_nanosleep`, `get_xattrs_to_heal`, `gf_gethostname`, and `gf_set_nofile`.

## Control Flow
Most helpers are direct wrappers with validation, conversion, and GlusterFS logging. Numeric parsing clears `errno`, calls `strto*`, validates tails and ranges, then restores old errno on success. Path creation walks slash boundaries and checks symlink policy. Graph dumping walks translators depth-first and prints volume blocks. Crash tracing flushes logs, disables suppression/syslog as needed, emits pending frames, revision/config data, backtrace, and re-raises the signal. Network locality resolves names with `getaddrinfo`, converts addresses, checks loopback and local interfaces, and frees resolver data.

## State And Persistence Behavior
The module touches several forms of runtime state: `gf_signal_on_assert`, thread names, signal masks, `THIS`, `global_ctx->hostname`, command-line server lists, log file paths, pid files, and process file descriptors. It can create directories, recursively delete directories, set file timestamps, unlink files, read `/proc/sys/net/ipv4/ip_local_reserved_ports`, inspect `/proc/self/fd`, and create temporary backtrace files under `/tmp` that are immediately unlinked. It does not own a single persistent data store but many helpers affect process or filesystem state.

## Dependencies And Integration Points
Dependencies include POSIX libc, pthreads, networking APIs, OpenSSL, xxhash, GlusterFS syscall wrappers, logging, stack/graph structures, ACL/xattr constants, command-line argument structures, and platform conditionals for Linux, BSD, Darwin, Solaris, and NetBSD. Because this file is in libglusterfs, it is integrated across most translators and daemon entry points.

## Risks And Edge Cases
`gf_strstr()` calls `strdup(str)` before validating `str`, so NULL input can crash before the intended validation. Some numeric wrappers assign narrowed values even when the parse helper failed or before range validation, so callers should honor return codes strictly. `gf_string2bytesize_range()` multiplies integer values before checking overflow, which can wrap before the max comparison. `valid_ipv4_address()` and `valid_ipv6_address()` use `tmp[length - 1]` after allocation without first checking allocation success. `recursive_rmdir()` treats failure to open a directory as success, which may hide permission or race failures. `gf_getgrouplist()` can return `GF_MAX_AUX_GROUPS` after a failed call without guaranteeing a complete successful population. Many helpers rely on `THIS` or `global_ctx`, which makes standalone use fragile. Address validation is custom and should be kept aligned with tests and platform resolver behavior.

## Test Signals
There is an explicit source comment requiring changes to `gf_is_ip_in_net()` to be mirrored in `tests/utils/ip-in-cidr.c`. Additional tests should cover numeric parser tails/ranges/overflow, byte-size fractional and overflow inputs, NULL validation for string/address helpers, mkdir symlink policy, canonical path normalization, reserved-port range parsing, local-address detection with IPv4 and IPv6 including scoped IPv6, volfile server duplicate handling, log path generation, thread naming truncation, pidfile handling, recursive delete error propagation, fd closing preserve lists, SHA-256 vectors, and FOP log-level mapping.
