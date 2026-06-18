# subset-b-006824 Research

Grouped source research for Linux selftests BPF verifier fixtures, BPF/XDP/AF_XDP tools, breakpoint tests, cachestat tests, capability execve tests, and cgroup selftest build metadata. Each source file has a marker-delimited section for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/precise.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/precise.c

## Purpose

This BPF verifier fixture defines targeted instruction-array tests for the verifier precision-marking machinery. The tests cover scalar precision propagation through map-value pointer subtraction, forced state checkpoints, cross-frame pruning, stack stores and spills, constant allocation sizes for ringbuf reserve, and a branch-pruning case that must reject an unbounded map-value offset.

## Important APIs, Types, and Functions

The file is declarative verifier-test data rather than standalone C logic. It uses BPF instruction macros such as `BPF_MOV64_IMM`, `BPF_LD_MAP_FD`, `BPF_EMIT_CALL`, `BPF_JMP_IMM`, `BPF_STX_MEM`, `BPF_LDX_MEM`, and raw helper calls for `bpf_get_prandom_u32`, `bpf_map_lookup_elem`, `bpf_probe_read_kernel`, `bpf_ringbuf_reserve`, and `bpf_ringbuf_submit`. Per-test metadata uses `.prog_type`, `.flags`, `.fixup_map_array_48b`, `.fixup_map_ringbuf`, `.result`, `.retval`, and `.errstr`.

## Control Flow

The harness includes this file into a larger verifier test table. Each entry provides a synthetic BPF program. Runtime flow is verifier-driven: the harness loads the program, applies map fixups, passes selected flags such as `BPF_F_TEST_STATE_FREQ`, and compares accept/reject plus verbose log substrings. The precision tests deliberately create branch points, helper calls, and stack accesses that force `mark_precise` to walk earlier verifier states.

## State and Persistence Behavior

No persistent state is owned by the file. State exists inside the verifier during one program load: register bounds, stack slots, parent states, and map/ringbuf fixups are allocated by the harness and discarded after the test case.

## Dependencies and Integration Points

It depends on the selftests verifier table format, BPF instruction macros, map-fixup support, verifier verbose-log matching, and kernel helper semantics. It integrates with BPF verifier regression testing for precision propagation and state-pruning safety.

## Risks and Test Signals

Risks include brittle verbose log substrings, architecture-specific unaligned-access handling, and false confidence if expected rejection strings are too broad. Strong signals are exact accept/reject outcomes, stable `mark_precise` log chains under checkpoint frequency, ringbuf allocation-size rejection, and rejecting the unbounded-min-value branch-pruning case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/precise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/scale.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/scale.c

## Purpose

This small verifier fixture registers two scale tests that exercise large generated BPF programs through the shared `bpf_fill_scale` helper. It validates that the verifier accepts stress-sized scheduler-classifier programs and returns the expected values.

## Important APIs, Types, and Functions

The entries are table data with empty `.insns` and `.data`, `.fill_helper = bpf_fill_scale`, `.prog_type = BPF_PROG_TYPE_SCHED_CLS`, `.result = ACCEPT`, and distinct `.retval` values of `1` and `2`. The important API is the harness fill-helper contract: instead of listing instructions inline, the harness calls `bpf_fill_scale` to synthesize the program body.

## Control Flow

The verifier harness discovers each entry, invokes `bpf_fill_scale`, loads the generated classifier program, and checks the result and return value. The source file itself has no local loops or branches; all execution shape is delegated to the fill helper.

## State and Persistence Behavior

No state persists across tests. Generated instruction buffers, verifier states, and return-value checks are harness-owned and per-test.

## Dependencies and Integration Points

The file depends on the BPF verifier selftest data format, `bpf_fill_scale`, scheduler-classifier program loading, and the harness return-value runner. It integrates with verifier scalability coverage, especially instruction/state growth limits.

## Risks and Test Signals

Risks are primarily indirect: if `bpf_fill_scale` changes, these tests change behavior without local edits; if the verifier limit logic changes, failures may be broad. Test signals are successful loads, expected return values, and runtime that stays within verifier complexity limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/scale.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/sleepable.c

## Purpose

This verifier fixture validates which BPF program/attach types may use `BPF_F_SLEEPABLE`. It accepts sleepable fentry, fexit-style tracing metadata, fmod_ret, iterator, LSM, and uprobe cases, and rejects an unsupported raw tracepoint sleepable program with an exact verifier diagnostic.

## Important APIs, Types, and Functions

Each case is a minimal two-instruction program (`r0 = 0`, `exit`) with metadata fields including `.prog_type`, `.expected_attach_type`, `.kfunc`, `.flags = BPF_F_SLEEPABLE`, `.runs = -1`, `.result`, and optional `.errstr`. Covered attach/program signals include `BPF_PROG_TYPE_TRACING`, `BPF_TRACE_FENTRY`, `BPF_MODIFY_RETURN`, `BPF_TRACE_ITER`, `BPF_PROG_TYPE_LSM`, `BPF_LSM_MAC`, and `BPF_PROG_TYPE_KPROBE`.

## Control Flow

The harness loads each minimal program with a sleepable flag and target symbol/attach type. The verifier performs compatibility checks before runtime execution; most cases accept without being run, while the raw tracepoint case must fail before execution.

## State and Persistence Behavior

There is no file-owned state. The only meaningful state is verifier load context: program type, expected attach type, kernel function/target name, and sleepable flag.

## Dependencies and Integration Points

The fixture depends on tracing/LSM/iterator/uprobe verifier attach rules and on kfunc/test symbol availability such as `bpf_fentry_test1` and `task`. It integrates with BPF verifier regression coverage for sleepable-program policy.

## Risks and Test Signals

Risks include attach-type rule drift, renamed test symbols, and error-string brittleness when verifier diagnostics change. Signals are accept results for supported sleepable classes and rejection with the expected unsupported raw-tracepoint message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/sleepable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/wide_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/wide_access.c

## Purpose

This verifier fixture checks 64-bit loads and stores against `struct bpf_sock_addr` IPv6 address fields. It ensures that aligned doubleword accesses are accepted and misaligned or out-of-range context accesses are rejected with precise offsets.

## Important APIs, Types, and Functions

The file defines two table-entry generator macros: `BPF_SOCK_ADDR_STORE(field, off, res, err, flgs)` and `BPF_SOCK_ADDR_LOAD(field, off, res, err, flgs)`. Generated programs use `BPF_STX_MEM(BPF_DW, ...)` or `BPF_LDX_MEM(BPF_DW, ...)` against `offsetof(struct bpf_sock_addr, field[off])`. Metadata targets `BPF_PROG_TYPE_CGROUP_SOCK_ADDR` with `BPF_CGROUP_UDP6_SENDMSG`, optional `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS`, and expected error strings.

## Control Flow

The harness expands the macros into store and load cases for `user_ip6[]` and `msg_src_ip6[]`. Each program performs one context access and exits. The verifier checks the context offset/size alignment and field accessibility before accepting or rejecting.

## State and Persistence Behavior

The fixture owns no runtime state. The tested state is the verifier's context-access model for `bpf_sock_addr` field layout and architecture unaligned-access policy.

## Dependencies and Integration Points

It depends on UAPI layout for `struct bpf_sock_addr`, BPF context access validation, cgroup sock_addr attach semantics, and the verifier selftest error-matching harness.

## Risks and Test Signals

Risks include ABI layout changes, architecture-specific unaligned rules, and stale expected offset strings. Signals are acceptances for aligned slots and rejections at offsets 12, 20, 44, 52, and 56 according to the field/element combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/wide_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verify_sig_setup.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verify_sig_setup.sh

## Purpose

This shell helper prepares and cleans up keys, keyrings, and fs-verity artifacts used by eBPF signature-verification selftests. It can generate a long-lived test X.509 certificate/key pair, add the DER certificate to the session keyring, create a dedicated keyring, sign a test file for fs-verity, and enable fs-verity on demand.

## Important APIs, Types, and Functions

Main functions are `usage`, `genkey`, `setup`, `cleanup`, `fsverity_create_sign_file`, `fsverity_enable_file`, `catch`, and `main`. External APIs are `openssl req`, `openssl x509`, `keyctl padd/newring/link/unlink/search`, `dd`, and `fsverity sign/enable`. The embedded `x509_genkey_content` defines a 2048-bit non-CA digital-signature certificate with subject key and authority key identifiers.

## Control Flow

`main` requires an action and existing temp directory. `setup` calls `genkey`, imports `signing_key.der` as asymmetric key `ebpf_testing_key`, creates `ebpf_testing_keyring`, and links the key. Cleanup unlinks both key and keyring and removes the temp directory. A trap calls `catch`, which prints the buffered log only on failure when quiet mode is active.

## State and Persistence Behavior

State is external: generated `x509.genkey`, `signing_key.pem`, `signing_key.der`, random `data-file`, `sig-file`, and session keyring objects. Cleanup removes temp files and keyring links, but failures before cleanup can leave session-keyring entries.

## Dependencies and Integration Points

It depends on bash strict mode, OpenSSL, keyutils, fs-verity tooling, writable temp storage, and a filesystem supporting fs-verity for the fs-verity actions. It integrates with BPF selftests that validate signed eBPF object or xattr/fs-verity signature paths.

## Risks and Test Signals

Risks include missing tools, insufficient keyring permissions, unsupported fs-verity filesystem, unquoted temp paths, and cleanup failure if key names are absent. Signals are successful key insertion/linking, generated PEM/DER files, fs-verity signature creation, fs-verity enablement, and quiet logs that surface only when an action fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verify_sig_setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.c

## Purpose

`veristat.c` is a command-line tool for measuring, replaying, sorting, filtering, and comparing BPF verifier statistics for BPF object files. It can load each program from one or more objects, collect verifier duration/state/instruction/stack/JIT-size/memory metrics, emit table or CSV output, replay saved CSV, and compare a baseline CSV against a comparison CSV with absolute and percentage deltas.

## Important APIs, Types, and Functions

Core data types are `enum stat_id`, `enum stat_variant`, `struct verif_stats`, `struct verif_stats_join`, `struct stat_specs`, `struct filter`, `struct rvalue`, `struct field_access`, and `struct var_preset`. Key functions include `parse_arg`, `append_filter`, `append_file`, `parse_stat`, `parse_verif_log`, `guess_prog_type_by_ctx_name`, `fixup_obj_maps`, `fixup_obj`, `create_stat_cgroup`, `process_prog`, `append_var_preset`, `set_global_vars`, `process_obj`, `parse_stats_csv`, `handle_comparison_mode`, `output_prog_stats`, `handle_verif_mode`, `handle_replay_mode`, and `main`. It uses libbpf, BTF, libelf, cgroup v2 memory accounting, argp, and optional `bpftool` dumps.

## Control Flow

Startup parses argp options into global `env`, resolves default output/sort specs, and selects comparison, replay, or live verification mode. Live mode optionally creates `/sys/fs/cgroup/veristat-accounting-<pid>` for memory peak accounting, opens each BPF ELF object, disables pinning, normalizes map sizes, applies BTF global-variable presets, prepares the object, clones each program with verifier log options, parses verifier log tail lines, fetches JIT info, optionally dumps xlated/JIT code, sorts results, and emits output. Replay parses one CSV and uses the normal output path. Comparison parses two CSVs, validates matching columns, sorts by file/program key, joins mismatched rows with missing sides, applies comparison filters, and emits A/B/diff columns.

## State and Persistence Behavior

Most state is process-local in `env`: input filenames, filters, stat arrays, presets, cgroup paths, and output specs. External state includes temporary loaded BPF programs, optional cgroup v2 accounting directory, open memory.peak fd, and possible `bpftool` subprocess output. Cleanup closes BPF objects/program fds, destroys the stat cgroup, frees allocations, and restores libbpf print callbacks.

## Dependencies and Integration Points

The tool integrates with selftests BPF object output, libbpf object/program/map APIs, BTF datasec/global variable metadata, verifier log format, cgroup v2 `memory.peak`, ELF object detection, and CI workflows that track verifier performance regressions. `veristat.cfg` provides a default object glob set for complex selftest objects.

## Risks and Test Signals

Risks include verifier log format drift, CSV parser limitations around commas/escaping, cgroup v2 unavailability, BTF preset resolution edge cases, assumptions in freplace context-type guessing, map-size fixups hiding object bugs, and command injection exposure if untrusted program IDs reach the `bpftool` command path. Signals include successful object skip/load accounting, stable CSV round-trips, comparison joins with missing rows, filter correctness for name/stat filters, memory-peak availability, BTF global preset application including arrays/enums, and accurate parsing of verifier duration/processed/stack lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.cfg -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.cfg

## Purpose

This configuration file lists BPF object-name glob patterns that are interesting for tracking BPF verifier performance. The selected names are complex or historically expensive selftests such as flow dissectors, loop benchmarks, profilers, pyperf, strobemeta, redirect/load-balancer programs, sysctl/TCP header tests, USDT, verifier scale, XDP noinline, XDP synproxy, and search pruning.

## Important APIs, Types, and Functions

There is no executable API. The file is line-oriented input for tools such as `veristat` or wrapper scripts. Supported syntax is simple pattern text plus comments; the patterns include wildcards like `bpf_flow*`, `loop*`, `test_sysctl*`, `test_verif_scale*`, and `xdp_synproxy*`.

## Control Flow

Consumer tooling reads the file line by line, skips comments, and interprets each remaining line as an object/program selection pattern. The control flow is therefore external to this file.

## State and Persistence Behavior

No runtime state is owned here. The file persists a curated test selection under version control.

## Dependencies and Integration Points

It depends on BPF selftest object naming conventions and integrates with verifier-stat collection workflows that need a stable benchmark corpus. Renames in `tools/testing/selftests/bpf` must be reflected here to avoid silently dropping coverage.

## Risks and Test Signals

Risks are stale globs, overly broad matches that inflate CI runtime, and missing new expensive verifier cases. Signals are non-empty expansion of each glob against built selftest objects and stable `veristat` output for the configured corpus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/vmtest.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/vmtest.sh

## Purpose

`vmtest.sh` builds a kernel and BPF selftests, prepares a Debian-based rootfs image, injects the selftests and an init script, launches QEMU, and retrieves test logs. It is the local/CI runner for executing BPF selftests in a controlled VM across supported platforms.

## Important APIs, Types, and Functions

The script defines platform-specific `QEMU_BINARY`, console, host/cross QEMU flags, `BZIMAGE`, and `ARCH` for `s390x`, `x86_64`, `aarch64`, `riscv64`, and `ppc64el`. Important functions are `usage`, `populate_url_map`, `newest_rootfs_version`, `download_rootfs`, `load_rootfs`, `recompile_kernel`, `mount_image`, `unmount_image`, `update_selftests`, `update_init_script`, `create_vm_image`, `run_vm`, `copy_logs`, `is_rel_path`, `do_update_kconfig`, `update_kconfig`, `catch`, and `main`.

## Control Flow

`main` resolves the kernel checkout, parses options for local rootfs, image update, output directory, job count, and debug shell, validates cross-compile requirements, builds a make command including `O`/`KBUILD_OUTPUT`, refreshes a cached config from BPF selftest config fragments, recompiles the kernel, creates or reuses a 2GB ext4 rootfs, rebuilds and copies selftests into `/root/bpf`, writes `/etc/rcS.d/S50-startup` to run the requested command or shell, starts QEMU, then mounts the image again to copy logs and exit status back.

## State and Persistence Behavior

Persistent state lives in `$HOME/.bpf_selftests` by default: `root.img`, `latest.config`, mounted `mnt`, timestamped logs, and exit-status files. The script mutates the rootfs image and cached kernel config. Trap cleanup unmounts the image and returns the in-VM exit status when available.

## Dependencies and Integration Points

Dependencies include QEMU for the selected platform, curl, zstd, tar, sudo mount/umount, mkfs.ext4, chattr, make, kernel build prerequisites, and libbpf CI rootfs index URLs. It integrates with the kernel tree at `tools/testing/selftests/bpf`, BPF CI rootfs artifacts, and kselftest command execution.

## Risks and Test Signals

Risks include privileged mount operations, stale rootfs indexes, missing QEMU/zstd, cross-compile mismatches, unquoted command injection in init-script generation, failed unmounts, and rootfs corruption after interrupted runs. Signals are successful kernel build, image creation/update, selftest copy, VM boot to the selected console, copied log plus exit-status file, and correct propagation of the VM command exit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/vmtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.c

## Purpose

This userspace test validates that a netdev's advertised XDP feature flags match behavior detected by traffic. It can run as a device-under-test service or as a tester peer, coordinates over a TCP control channel, sends UDP echo traffic, attaches generated XDP skeleton programs, and reports whether a selected feature is detected and advertised.

## Important APIs, Types, and Functions

The global `env` stores verbosity, interface, tester/DUT role, selected `netdev_xdp_act`/`xdp_action`, and socket addresses. Key functions are `get_xdp_feature`, `get_xdp_feature_str`, `parse_arg`, `set_env_default`, `dut_echo_thread`, `dut_run_echo_thread`, `dut_attach_xdp_prog`, `recv_msg`, `dut_run`, `tester_collect_detected_cap`, `send_and_recv_msg`, `send_echo_msg`, `tester_run`, and `main`. It uses `xdp_features.skel.h`, `xdp_features.h`, libbpf XDP attach/query APIs, cpumap/devmap updates, and `network_helpers`.

## Control Flow

`main` initializes defaults, parses CLI options, opens/loads/attaches the skeleton, seeds rodata addresses, then branches into DUT or tester mode. The DUT accepts one control connection, handles TLV commands for start/stop/capability/stats, attaches an XDP program matching the requested feature, starts a UDP echo thread, and returns BPF map stats. The tester queries advertised features, attaches a receive/tx-check program, asks the DUT to start, sends echo datagrams repeatedly, fetches DUT stats, stops the DUT, and compares detected behavior with advertised flags.

## State and Persistence Behavior

State is process-local except for temporary XDP attachments and BPF maps inside the loaded skeleton. Signal handling sets `exiting`; cleanup destroys the skeleton and detaches XDP in role-specific paths.

## Dependencies and Integration Points

It depends on libbpf strict mode, skeleton-generated BPF programs/maps, IPv6 or IPv4-mapped IPv6 sockets, cpumap/devmap support, netdev XDP feature querying, and the shared TLV protocol in `xdp_features.h`.

## Risks and Test Signals

Risks include network timing, uninitialized address length/state bugs, driver-only mode limitations, stale XDP attachments on abnormal exit, and feature mismatch caused by traffic not reaching the BPF path. Signals are successful control handshake, XDP attach/query, nonzero DUT/tester map counters when expected, and final `[DETECTED]/[ADVERTISED]` comparison for each feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.h

## Purpose

This header defines the tiny control protocol shared by the XDP features tester and DUT programs. It standardizes command IDs, default control/data UDP/TCP ports, and the TLV header used to exchange commands, acknowledgments, capability flags, and counters.

## Important APIs, Types, and Functions

`enum test_commands` defines `CMD_STOP`, `CMD_START`, `CMD_ECHO`, `CMD_ACK`, `CMD_GET_XDP_CAP`, and `CMD_GET_STATS`. `DUT_CTRL_PORT` is `12345`; `DUT_ECHO_PORT` is `12346`. `struct tlv_hdr` contains network-order `type`, network-order `len`, and a flexible `data[]` payload.

## Control Flow

There is no executable flow in this header. `xdp_features.c` serializes each control action as a `tlv_hdr`, waits for `CMD_ACK`, and optionally copies payload bytes from `data[]`.

## State and Persistence Behavior

No storage is owned. It defines wire-format state for one control session.

## Dependencies and Integration Points

It depends on kernel integer types (`__be16`, `__u8`) and is included by both userspace control code and companion BPF/user helpers that need matching command constants.

## Risks and Test Signals

Risks include mismatched byte order, length values smaller than the header, and command additions not handled by both peers. Signals are successful `CMD_GET_XDP_CAP`, `CMD_START`, `CMD_GET_STATS`, and `CMD_STOP` exchanges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_hw_metadata.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_hw_metadata.c

## Purpose

`xdp_hw_metadata.c` is a functional hardware test for XDP RX metadata and AF_XDP TX metadata. It diverts UDP port 9091 packets into AF_XDP sockets, verifies RX timestamp/RSS/VLAN metadata, optionally sends a TX reply with checksum, timestamp, and launch-time metadata requests, and checks SKB timestamp delivery on a UDP socket.

## Important APIs, Types, and Functions

Important state includes `struct xsk`, global `bpf_obj`, `bind_flags`, `rx_xsk`, `ifname`, `ifindex`, `rxq`, `skip_tx`, timestamp tracking, and launch-time queue settings. Key functions are `open_xsk`, `close_xsk`, `refill_rx`, `kick_tx`, `kick_rx`, `gettime`, `print_tstamp_delta`, `print_vlan_tci`, `verify_xdp_metadata`, `verify_skb_metadata`, `complete_tx`, `ping_pong`, `verify_metadata`, `rxq_num`, `hwtstamp_ioctl`, `hwtstamp_enable`, `cleanup`, `timestamping_enable`, `read_args`, `clean_existing_configurations`, and `main`.

## Control Flow

`main` parses options, counts RX queues, removes existing qdisc/filter state, enables hardware timestamping, optionally configures mqprio/ETF and VLAN steering for launch time, creates one AF_XDP socket per RX queue, opens and loads the dev-bound XDP skeleton, starts a UDP SKB endpoint on port 9092, populates the XSK map, attaches the XDP program, and enters `verify_metadata`. The verification loop polls all XSK fds and the SKB server, kicks RX, validates metadata from the first packet segment, optionally mirrors the packet back through AF_XDP TX, waits for TX completion metadata, releases descriptors, and refills RX buffers.

## State and Persistence Behavior

The program mutates external NIC state: XDP attachment, hardware timestamp config, tc qdisc/filter state, ethtool filters, VLAN offload, and AF_XDP socket mappings. `atexit` restores the saved hwtstamp config, while explicit cleanup detaches XDP, closes sockets, destroys the skeleton, and removes qdisc/filter state at the end.

## Dependencies and Integration Points

It depends on real NIC hardware support for XDP driver mode, AF_XDP, metadata kfuncs exposed by the companion skeleton, hardware timestamping, ethtool channels/filters, tc mqprio/ETF/flower, UDP test traffic, and the shared metadata layout in `xdp_metadata.h`.

## Risks and Test Signals

Risks include privileged host configuration changes, stale qdisc/filter state, hardware-specific metadata availability, multi-buffer descriptor handling, timeout sensitivity, and incomplete cleanup after fatal `error()`. Signals are printed RX hash/timestamp/VLAN metadata, SKB hardware timestamps, successful TX completion timestamps, checksum request behavior, packet counters in BPF BSS, and clean XDP detach/restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_hw_metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_metadata.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_metadata.h

## Purpose

This header defines shared protocol constants and the metadata block used by XDP metadata selftests. The companion BPF program writes `struct xdp_meta` before packet data, and userspace reads it to validate hardware RX hints.

## Important APIs, Types, and Functions

The header provides fallback Ethernet protocol constants for IPv4, IPv6, 802.1Q, and 802.1AD, a fallback `BIT()` macro, `XDP_CHECKSUM_MAGIC`, `enum xdp_meta_field`, and `struct xdp_meta`. The metadata struct carries timestamp or timestamp error, XDP timestamp, RX hash, hash type or error, VLAN proto/TCI or error, and a `hint_valid` bitmask.

## Control Flow

No code runs here. Producers set fields and `hint_valid` bits; consumers branch on `XDP_META_FIELD_TS`, `XDP_META_FIELD_RSS`, and `XDP_META_FIELD_VLAN_TAG` to interpret union members as either values or errors.

## State and Persistence Behavior

The layout is transient per packet and stored adjacent to XDP packet data, usually in AF_XDP UMEM. It has no file-backed persistence.

## Dependencies and Integration Points

It integrates BPF-side metadata extraction with userspace validation in `xdp_hw_metadata.c`. It depends on Linux fixed-width integer types and common Ethernet protocol IDs.

## Risks and Test Signals

Risks are ABI drift between BPF and userspace, incorrect union interpretation when `hint_valid` is wrong, and endianness mistakes in VLAN protocol fields. Signals are userspace printing correct metadata values or explicit error codes per field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_synproxy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_synproxy.c

## Purpose

`xdp_synproxy.c` is a userspace controller for an XDP/TC SYN-cookie proxy BPF program. It can attach the companion BPF object to an interface, discover an already attached program by ID, update TCP/IP option and allowed-port maps, and periodically report the total number of generated SYNACKs.

## Important APIs, Types, and Functions

Global state tracks `ifindex`, `attached_prog_id`, and whether a TC hook was attached. Key functions are `cleanup`, `usage`, `parse_arg_ul`, `parse_options`, `syncookie_attach`, `syncookie_open_bpf_maps`, and `main`. It uses libbpf BPF object loading, `bpf_xdp_attach`, `bpf_xdp_query_id`, `bpf_tc_hook_create`, `bpf_tc_attach`, `bpf_tc_hook_destroy`, `bpf_prog_get_info_by_fd`, `bpf_map_get_info_by_fd`, and map update/lookup APIs.

## Control Flow

CLI parsing requires either `--iface` or `--prog`, validates optional `--mss4/--mss6/--wscale/--ttl` as an all-or-nothing TCP/IP option tuple, parses comma-separated `--ports`, and handles `--single`/`--tc`. If no program ID is provided, it queries an existing XDP program or loads `<argv0>_kern.bpf.o` and attaches `syncookie_xdp` or `syncookie_tc`. It opens maps named `values` and `allowed_ports`, updates requested options/ports, then either exits after configuration or loops reading counter key `1`.

## State and Persistence Behavior

External state includes XDP or TC ingress attachments and BPF map contents. Signal cleanup detaches only programs attached by this process; map updates persist while the BPF program/map lives.

## Dependencies and Integration Points

It depends on a companion kernel object with `syncookie_xdp`/`syncookie_tc`, maps named `values` and `allowed_ports`, libbpf, netdev ifindex resolution, and privileges for XDP/TC/map operations.

## Risks and Test Signals

Risks include map-name coupling, stale TC hook if attach partially fails, conflicting existing XDP programs, port-list overflow relative to map size, and option packing assumptions. Signals are successful attach/discover, map fd discovery, printed port/option updates, increasing SYNACK counters, and clean detach on SIGINT/SIGTERM for process-owned attachments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_synproxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.c

## Purpose

`xdping.c` is a userspace runner for XDP ICMP ping acceleration tests. It loads a companion BPF object, attaches either client or server XDP program to an interface, drives ordinary `ping`, and reads an eBPF map containing XDP-measured RTT samples.

## Important APIs, Types, and Functions

Global state is `ifindex` and `xdp_flags`. Functions are `cleanup`, `get_stats`, `show_usage`, and `main`. It uses libbpf strict mode, `bpf_prog_test_load`, `bpf_object__find_program_by_name`, `bpf_xdp_attach/detach`, BPF map lookup/update/delete, `getaddrinfo`, and the shared `struct pinginfo` from `xdping.h`.

## Control Flow

`main` parses count, interface, driver/SKB mode, and server/client mode. It resolves the destination in client mode, loads `<argv0>_kern.bpf.o`, selects `xdping_server` or `xdping_client`, finds the first map, installs signal cleanup, attaches XDP, and either idles forever in server mode or seeds the map with remote address/count, waits for setup, runs system `ping`, then prints XDP RTT data from the map and detaches.

## State and Persistence Behavior

State includes the temporary XDP attachment and map entry keyed by remote IPv4 address. Cleanup detaches XDP and client mode deletes the map entry after reading stats.

## Dependencies and Integration Points

It depends on the companion BPF object, ICMP traffic through the selected interface, IPv4-only name resolution, libbpf, shell `ping`, and XDP attach mode support. It integrates userspace orchestration with BPF RTT measurement state.

## Risks and Test Signals

Risks include network disruption from XDP attach, command construction through `system`, relying on final regular ping RTT behavior, map discovery by first-map order, and stale attachment on abrupt process death. Signals are successful attach, normal ping success, exactly `count` nonzero RTT samples, and map entry deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.h

## Purpose

This header defines shared XDP ping limits and the map value used by the XDP ping client/server programs and userspace runner.

## Important APIs, Types, and Functions

It defines `XDPING_MAX_COUNT` as `10`, `XDPING_DEFAULT_COUNT` as `4`, and `struct pinginfo` with `start`, network-order `seq`, `count`, padding, and `times[XDPING_MAX_COUNT]` nanosecond RTT samples.

## Control Flow

No executable flow exists here. Userspace seeds `seq` and `count`, the BPF program records start/time samples, and userspace later iterates `times[]` until `count` samples are present.

## State and Persistence Behavior

Instances persist only as BPF map values keyed by remote IPv4 address for the duration of an xdping run.

## Dependencies and Integration Points

It is shared by `xdping.c` and the companion kernel BPF object. Its layout is an ABI between userspace and BPF.

## Risks and Test Signals

Risks include count larger than the array, endian mismatch for `seq`, and layout drift between userspace and BPF builds. Signals are populated `times[]` values and successful BPF map lookup/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.c

## Purpose

`xsk.c` is a local AF_XDP userspace access library used by BPF selftests. It creates and tears down UMEMs and AF_XDP sockets, maps fill/completion/RX/TX rings, supports shared UMEM contexts, attaches/detaches XDP programs, updates XSK maps, queries attach mode, and changes interface MTU through rtnetlink.

## Important APIs, Types, and Functions

Core private types are `struct xsk_umem`, `struct xsk_ctx`, `struct xsk_socket`, and `struct nl_mtu_req`. Public functions include `xsk_umem__fd`, `xsk_socket__fd`, `xsk_umem__create`, `xsk_is_in_mode`, `xsk_set_mtu`, `xsk_attach_xdp_program`, `xsk_detach_xdp_program`, `xsk_clear_xskmap`, `xsk_update_xskmap`, `xsk_socket__create_shared`, `xsk_socket__create`, `xsk_umem__delete`, and `xsk_socket__delete`. Internal helpers configure defaults, read `XDP_MMAP_OFFSETS`, map rings, receive netlink ACKs, and manage shared contexts.

## Control Flow

UMEM creation validates arguments, opens an AF_XDP socket, registers user memory through `XDP_UMEM_REG`, and maps fill/completion rings. Socket creation configures RX/TX ring sizes, reuses or creates a context for ifindex/queue, maps RX/TX rings, binds `sockaddr_xdp`, and handles shared-UMEM fd selection. Deletion releases contexts, unmaps rings using current mmap offsets, closes fds when appropriate, and enforces UMEM refcount rules.

## State and Persistence Behavior

Persistent process state is heap-allocated UMEM/socket/context objects, kernel AF_XDP sockets, mmapped rings, and UMEM reference counts. External state includes XDP program attachments, XSK map entries, and interface MTU changes requested by callers.

## Dependencies and Integration Points

It depends on AF_XDP UAPI, mmap offsets, libbpf attach helpers, route netlink, ethtool/socket headers, list helpers, and memory barriers exposed in `xsk.h`. It is consumed by XSK selftests and XDP hardware metadata tests.

## Risks and Test Signals

Risks include reference-count leaks, incorrect unmap lengths, ring-size power-of-two assumptions, shared UMEM lifetime bugs, errno sign inconsistencies, and leaving interface MTU/XDP state to callers. Signals are successful UMEM/socket creation in copy/zero-copy/shared modes, descriptor ring progress, clean `-EBUSY` when deleting active UMEMs, and no leaks across repeated teardown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.h

## Purpose

This header exposes the AF_XDP test library API and inline ring helpers used by selftests. It mirrors the libbpf xsk API shape closely enough for tests to create UMEMs, sockets, manipulate producer/consumer rings, and access UMEM data.

## Important APIs, Types, and Functions

`DEFINE_XSK_RING` defines `struct xsk_ring_prod` and `struct xsk_ring_cons`. Inline helpers include `xsk_ring_prod__fill_addr`, `xsk_ring_cons__comp_addr`, `xsk_ring_prod__tx_desc`, `xsk_ring_cons__rx_desc`, `xsk_ring_prod__needs_wakeup`, `xsk_ring_prod__reserve`, `xsk_ring_prod__submit`, `xsk_ring_prod__cancel`, `xsk_ring_cons__peek`, `xsk_ring_cons__cancel`, `xsk_ring_cons__release`, and UMEM address helpers. Public structs are `xsk_umem_config` and `xsk_socket_config`; public prototypes cover UMEM/socket creation, deletion, fd access, XDP attach/map operations, mode query, and MTU setting.

## Control Flow

The inline ring flow caches producer/consumer indices, uses acquire loads when refreshing peer pointers, advances cached indices on reserve/peek, and uses release stores when submitting or releasing entries. Higher-level creation/deletion flow is implemented in `xsk.c`.

## State and Persistence Behavior

Ring structs store mmapped kernel/user shared pointer locations, masks, sizes, flags, and cached indices. UMEM and socket objects are opaque and owned by `xsk.c`.

## Dependencies and Integration Points

It depends on `<linux/if_xdp.h>`, libbpf BPF program/map types, atomic builtins, and exact AF_XDP ring semantics. It is included by AF_XDP tests and `xdp_hw_metadata.c`.

## Risks and Test Signals

Risks include memory-barrier regressions, cached index underflow/overflow, non-power-of-two ring sizes, and UMEM unaligned-address interpretation mistakes. Signals are correct packet ordering, no descriptor reuse before release, need-wakeup behavior, and stable multi-buffer/unaligned tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_prereqs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_prereqs.sh

## Purpose

This shell helper validates and runs the `xskxceiver` AF_XDP selftest under expected prerequisites. It checks root privileges, `ip` utility availability, veth support, manages test status output, performs interface cleanup, and invokes the compiled `xskxceiver` binary with veth interface arguments.

## Important APIs, Types, and Functions

It defines kselftest status constants, `XSKOBJ=xskxceiver`, and functions `validate_root_exec`, `validate_veth_support`, `test_status`, `test_exit`, `cleanup_iface`, `clear_configs`, `cleanup_exit`, `validate_ip_utility`, and `exec_xskxceiver`. Important external commands are `ip link add/del/set` and `./xskxceiver`.

## Control Flow

Callers source or execute the script around AF_XDP test setup. Validation fails or skips via `test_exit`; veth support is probed by trying to create and delete a veth; cleanup restores MTU and removes XDP/xdpgeneric attachments. `exec_xskxceiver` appends busy-poll arguments when requested, executes the binary against `VETH0` and `VETH1`, and records status/name arrays unless list mode is active.

## State and Persistence Behavior

The script mutates network interface state and shell arrays such as `statusList` and `nameList`. It relies on environment variables including `VETH0`, `VETH1`, `ARGS`, `busy_poll`, `list`, and `TEST_NAME`.

## Dependencies and Integration Points

It integrates with AF_XDP shell test orchestration and the `xskxceiver` binary. Dependencies are root privileges, iproute2, veth kernel support, and interfaces created by the surrounding test script.

## Risks and Test Signals

Risks include global shell-variable coupling, incomplete cleanup after interruption, treating root requirement as failure instead of skip in one path, and stale XDP state on shared devices. Signals are prerequisite pass/skip output, successful veth probe, `xskxceiver` exit status, and restored interface MTU/XDP mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_prereqs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_xdp_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_xdp_common.h

## Purpose

This shared header provides tiny constants and a counter layout used by AF_XDP/XDP selftest programs.

## Important APIs, Types, and Functions

It defines `MAX_SOCKETS` as `2`, `PKT_HDR_ALIGN` as Ethernet header size plus two bytes for packet data alignment, and `struct xdp_info` with an aligned 64-bit `count` field.

## Control Flow

There is no executable flow. Producers and consumers use the constants to size arrays and align packet headers; BPF/user code can share `struct xdp_info` for counters.

## State and Persistence Behavior

`struct xdp_info` instances are transient counter values, typically in BPF maps or shared test state. The header itself owns no storage.

## Dependencies and Integration Points

It depends on `struct ethhdr` being visible where `PKT_HDR_ALIGN` is evaluated. It integrates `xskxceiver.c`, AF_XDP helper code, and companion XDP skeleton programs.

## Risks and Test Signals

Risks are include-order issues for `struct ethhdr`, alignment assumptions changing with packet layout, and counter false-sharing if alignment is altered. Signals are successful build and consistent packet/counter validation in XSK tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xsk_xdp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.c

## Purpose

`xskxceiver.c` is the main AF_XDP packet xceiver selftest binary. It drives a large test matrix across SKB, native/driver, and zero-copy modes, validating packet ordering, content, socket teardown, bidirectional sockets, statistics, bpf_link persistence, unaligned mode, descriptor validation, 2K frames, jumbo/multi-buffer cases, and CI skip cases.

## Important APIs, Types, and Functions

Important globals are `opt_print_tests`, `opt_mode`, and `opt_run_test`. Key functions are `test__fail`, `__exit_with_error`, `ifobj_zc_avail`, `print_usage`, `validate_interface`, `parse_command_line`, `xsk_unload_xdp_programs`, `run_pkt_test`, `is_xdp_supported`, `print_tests`, and `main`. It uses types and helpers from `prog_tests/test_xsk.h`, `xsk_xdp_progs.skel.h`, `xsk.h`, `xskxceiver.h`, `xsk_xdp_common.h`, `network_helpers`, and kselftest.

## Control Flow

`main` initializes libbpf strict mode and two interface objects, reads cache-line and max-frag values from procfs, computes UMEM tailroom, parses two `-i` interfaces and mode/test options, lists tests if requested, determines shared-UMEM mode, probes native XDP and zero-copy support, reads/restores hardware ring size when supported, initializes RX/TX interfaces, creates default packet streams, sets the kselftest plan, and loops through selected modes and tests. Each test is initialized, run through its function pointer, reported as pass/skip/fail, and restored to default packet stream state.

## State and Persistence Behavior

The program mutates interface state, AF_XDP sockets/UMEMs, XDP programs, hardware ring settings, packet streams, and test descriptors. Cleanup deletes packet streams, destroys skeletons, deletes interface objects, and resets hardware ring size if changed.

## Dependencies and Integration Points

It depends on root/network setup supplied by shell tests, veth or physical interfaces, AF_XDP support, optional zero-copy support, procfs values, ethtool ring APIs, generated skeletons, and a large helper/test table in `prog_tests/test_xsk.h`.

## Risks and Test Signals

Risks include hardware/driver feature variance, shared-interface behavior, resource leaks across many tests, busy-poll timing, and descriptor edge cases that can fail only in certain modes. Signals are kselftest plan/result counts, per-mode test messages, zero-copy probing, repeated teardown success, restored hardware ring sizes, and final pass/fail based on `failed_tests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.h

## Purpose

This header centralizes AF_XDP xceiver selftest constants and compatibility fallbacks. It keeps common socket family values and test-size constants available to the main xceiver and helper code.

## Important APIs, Types, and Functions

It defines fallback `SOL_XDP`, `AF_XDP`, and `PF_XDP`, plus `MAX_TEARDOWN_ITER`, `MAX_ETH_JUMBO_SIZE`, `SOCK_RECONF_CTR`, `RX_FULL_RXQSIZE`, `UMEM_HEADROOM_TEST_SIZE`, `XSK_UMEM__INVALID_FRAME_SIZE`, `RUN_ALL_TESTS`, and `NUM_MAC_ADDRESSES`. It includes the generated XDP skeleton and `xsk_xdp_common.h`.

## Control Flow

No executable control flow exists. The values parameterize test loops, packet sizes, invalid descriptor cases, and command-line selection.

## State and Persistence Behavior

There is no storage. The constants influence runtime state allocated by `xskxceiver.c` and helper files.

## Dependencies and Integration Points

It depends on generated `xsk_xdp_progs.skel.h`, shared XDP constants, and kernel UAPI values when present. It integrates the main AF_XDP test binary with helper code.

## Risks and Test Signals

Risks include constants drifting from kernel AF_XDP limits or test expectations, especially jumbo and invalid frame sizes. Signals are successful compilation and expected pass/skip behavior across the xceiver test matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xskxceiver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/Makefile

## Purpose

This Makefile selects and builds breakpoint-related kselftest programs for the current architecture. It always builds the suspend/single-step test and conditionally builds x86 or arm64 hardware breakpoint/watchpoint tests.

## Important APIs, Types, and Functions

It normalizes `ARCH` from `uname -m`, maps i386/x86_64 to `x86`, sets `TEST_GEN_PROGS := step_after_suspend_test`, adds `breakpoint_test` for x86, adds `breakpoint_test_arm64` for `aarch64`/`arm64`, and includes `../lib.mk`.

## Control Flow

Make evaluates the architecture conditionals and lets kselftest `lib.mk` compile the selected generated programs.

## State and Persistence Behavior

No runtime state is owned. Build outputs are produced under the kselftest output directory.

## Dependencies and Integration Points

It integrates with kselftest build infrastructure and architecture-specific ptrace/debug-register tests.

## Risks and Test Signals

Risks include incorrect architecture normalization or missing an architecture that supports a test. Signals are expected binaries appearing in `TEST_GEN_PROGS` for x86 and arm64 builds and successful kselftest build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test.c

## Purpose

This x86 kselftest validates hardware instruction breakpoints, write watchpoints, read/write watchpoints, ICEBP traps, and `int3` traps through `ptrace` debug-register programming. It exercises the `do_debug()` path and verifies that a traced child traps exactly when expected.

## Important APIs, Types, and Functions

Important constants are `COUNT_ISN_BPS`, `COUNT_WPS`, and breakpoint modes `BP_X`, `BP_RW`, and `BP_W`. Key functions are `set_breakpoint_addr`, `toggle_breakpoint`, dummy functions/variables, `check_trapped`, `write_var`, `read_var`, `trigger_tests`, `check_success`, `launch_instruction_breakpoints`, `launch_watchpoints`, `launch_tests`, and `main`. It uses `PTRACE_POKEUSER`, `PTRACE_PEEKUSER`, `PTRACE_POKEDATA`, `PTRACE_CONT`, x86 `struct user.u_debugreg`, signals, wait status, and kselftest reporting.

## Control Flow

The parent forks a child. The child calls `PTRACE_TRACEME`, signals readiness, then executes the exact sequence of dummy function calls, watched writes/reads, ICEBP, and int3. The parent sets DR addresses and DR7 control bits for each local/global/type/length combination, resumes the child, waits for SIGTRAP, confirms the child-side sequence counter matches the parent, pokes `trapped = 1`, reports pass/fail, disables the breakpoint, and continues to the next case.

## State and Persistence Behavior

State is in child debug registers, shared-by-ptrace child globals `nr_tests` and `trapped`, and parent `child_pid`. It leaves no persistent state after the child exits.

## Dependencies and Integration Points

It depends on x86 debug register layout, ptrace permissions, signal delivery, and kselftest. The Makefile limits it to x86.

## Risks and Test Signals

Risks include ptrace policy restrictions, DR7 encoding mistakes, sequence desynchronization, and false failures if the child exits early. Signals are planned pass results for all breakpoint/watchpoint/trap combinations and final `ksft_exit_pass`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test_arm64.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test_arm64.c

## Purpose

This arm64 kselftest validates hardware watchpoint byte-selection behavior across write sizes and offsets. It checks that a watchpoint triggers only when the watched byte range overlaps the child write and that negative-offset boundary cases work.

## Important APIs, Types, and Functions

Important state is aligned volatile `var[96]`. Key functions are `child`, `set_watchpoint`, `run_test`, `sigalrm`, and `main`. It uses `PTRACE_TRACEME`, `PTRACE_SETREGSET` with `NT_ARM_HW_WATCH`, `PTRACE_CONT`, `PTRACE_GETSIGINFO`, `TRAP_HWBKPT`, `struct user_hwdebug_state`, `iovec`, and kselftest.

## Control Flow

For each write size from 1 to 32 bytes and nearby watchpoint offsets, `main` forks a child. The child stops under ptrace, writes using scalar stores or arm64 pair stores for 16/32-byte cases, and exits. The parent sets one hardware watchpoint with a byte mask derived from size and address offset, resumes the child with an alarm timeout, waits for SIGTRAP, validates `si_code == TRAP_HWBKPT`, kills the child, and compares the result to expected overlap.

## State and Persistence Behavior

State is limited to child watchpoint registers and the static `var` buffer. No persistent system state is modified.

## Dependencies and Integration Points

It depends on arm64 hardware watchpoint support, ptrace regset availability, and kselftest. The Makefile selects it only for arm64/aarch64.

## Risks and Test Signals

Risks include hardware lacking watchpoint support (`EIO`), incorrect byte-mask calculation for larger-than-8-byte writes, timeouts, and ptrace restrictions. Signals are 213 planned kselftest results, pass when `wr == wp` for overlap cases, pass for negative boundary checks, and final pass/fail aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test_arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/step_after_suspend_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/step_after_suspend_test.c

## Purpose

This kselftest verifies that `PTRACE_SINGLESTEP` still works on every available CPU after an optional suspend/resume cycle. It targets debug/single-step state restoration across system suspend.

## Important APIs, Types, and Functions

Functions are `child`, `run_test`, `get_suspend_success_count_or_fail`, `suspend`, and `main`. It uses CPU affinity APIs, `PTRACE_TRACEME`, `PTRACE_SINGLESTEP`, `PTRACE_CONT`, wait status inspection, `/sys/power/suspend_stats/success`, `/sys/power/state`, `timerfd_create(CLOCK_BOOTTIME_ALARM)`, and kselftest constants.

## Control Flow

`main` parses `-n` to skip suspend, enumerates available CPUs, optionally calls `suspend`, sets a test plan, and runs one test per CPU. Each child pins itself to a CPU, enters ptrace stop, and exits after being continued. The parent single-steps the child, expects a SIGTRAP stop, continues it, expects normal exit, and reports pass/skip/fail.

## State and Persistence Behavior

The test temporarily triggers system suspend unless `-n` is provided and creates a boottime alarm timerfd to wake the system. It reads suspend success counters but does not persist files.

## Dependencies and Integration Points

It depends on root privileges for suspend, working `/sys/power` suspend support, timerfd wake alarms, ptrace single-step support, CPU affinity, and kselftest.

## Risks and Test Signals

Risks include disrupting the host by suspending it, unsupported single-step returning `EIO`, suspend failure, CPU hotplug/race behavior, and timer wake failure. Signals are increased suspend success count, SIGTRAP after single-step for each CPU, normal child exit after continue, and skip output for unsupported single-step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/step_after_suspend_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/Makefile

## Purpose

This Makefile builds the cachestat syscall kselftest program.

## Important APIs, Types, and Functions

It sets `TEST_GEN_PROGS := test_cachestat`, appends `$(KHDR_INCLUDES)` and `-Wall` to `CFLAGS`, links `-lrt`, and includes `../lib.mk`.

## Control Flow

Kselftest `lib.mk` compiles `test_cachestat.c` into the generated test binary using kernel headers.

## State and Persistence Behavior

No runtime state is owned. Build artifacts are produced by kselftest.

## Dependencies and Integration Points

It depends on exported kernel headers containing cachestat syscall types and on librt availability. It integrates with the selftests build/run framework.

## Risks and Test Signals

Risks are stale headers or missing syscall definitions on older trees. Signals are successful compilation and execution of `test_cachestat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/test_cachestat.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/test_cachestat.c

## Purpose

This kselftest validates the `cachestat` syscall on invalid fds, device/proc files, normal files, fsync behavior, shmem files, and mmap-populated files. It checks that cached plus evicted page counts match expected ranges and that fsync clears dirty pages on non-tmpfs files.

## Important APIs, Types, and Functions

Key functions are `print_cachestat`, `write_exactly`, `is_on_tmpfs`, `test_cachestat`, `file_type_str`, `run_cachestat_test`, and `main`. It uses `struct cachestat`, `struct cachestat_range`, `syscall(__NR_cachestat, ...)`, `open`, `shm_open`, `ftruncate`, `mmap`, `fsync`, `fstatfs`, `TMPFS_MAGIC`, `/dev/urandom`, and kselftest reporting. `NR_TESTS` is `9`; `dev_files` covers `/dev/zero`, `/dev/null`, `/dev/urandom`, `/proc/version`, and `/proc`.

## Control Flow

`main` first probes syscall availability with a bad fd and expects `EBADF` or skips on `ENOSYS`. It then iterates device/proc files, tests a created normal file with random data, repeats normal-file testing with fsync validation, and runs shmem and mmap tests over a half-file page range. Helpers write exact random buffers, call cachestat, print counters, and validate `nr_cache + nr_evicted` against expected page counts.

## State and Persistence Behavior

Temporary files `tmpfilecachestat` and `tmpshmcstat` are created and removed/unlinked. mmap memory and file descriptors are process-local. The test may leave temporary files only on early fatal paths.

## Dependencies and Integration Points

It depends on the cachestat syscall, page cache behavior, tmpfs/shmem, `/dev/urandom`, kernel headers, and kselftest. It integrates directly with VM/file-cache syscall regression coverage.

## Risks and Test Signals

Risks include page-cache races, filesystem-specific fsync semantics, tmpfs skip behavior, missing `munmap` in the mmap helper, and huge-page/readahead effects changing counters. Signals are `EBADF` recognition, zero syscall return for supported files, expected cached/evicted totals, skipped fsync on tmpfs, and dirty count zero after fsync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/test_cachestat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/Makefile

## Purpose

This Makefile builds Linux capability execve selftests and their validation helper.

## Important APIs, Types, and Functions

It sets `TEST_GEN_FILES := validate_cap`, `TEST_GEN_PROGS := test_execve`, adds `-O2 -g -std=gnu99 -Wall $(KHDR_INCLUDES)` to `CFLAGS`, links `-lcap-ng -lrt -ldl`, and includes `../lib.mk`.

## Control Flow

Kselftest builds the helper as a generated file and `test_execve` as the executable test. The main test copies `validate_cap` at runtime into a private tmpfs for setuid/setgid scenarios.

## State and Persistence Behavior

No runtime state is owned by the Makefile. Build outputs are used by runtime tests.

## Dependencies and Integration Points

It depends on libcap-ng and kernel capability headers. It integrates with the capabilities selftest directory and kselftest build infrastructure.

## Risks and Test Signals

Risks include missing libcap-ng development files or helper not being available beside `test_execve`. Signals are successful build and runtime discovery/copying of `validate_cap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/test_execve.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/test_execve.c

## Purpose

This kselftest validates Linux capability transformations across `execve`, especially ambient capabilities, inheritable/permitted/effective sets, user namespaces, and setuid/setgid executable transitions. It runs separate root and non-root scenarios and delegates post-exec capability validation to `validate_cap`.

## Important APIs, Types, and Functions

Important globals are `nerrs` and `mpid`. Key functions are `vmaybe_write_file`, `maybe_write_file`, `write_file`, `create_and_enter_ns`, `chdir_to_tmpfs`, `copy_fromat_to`, `fork_wait`, `exec_other_validate_cap`, `exec_validate_cap`, `do_tests`, and `main`. It uses libcap-ng, `unshare`, uid/gid maps, `PR_SET_KEEPCAPS`, `PR_CAP_AMBIENT_*`, `setresuid`, `setresgid`, `mount` of private tmpfs, `chown`, `chmod`, fork/exec/wait, and kselftest.

## Control Flow

`main` locates the test directory, then forks one root-style scenario and one uid-1 scenario. `do_tests` creates either a privileged mount namespace or a user+mount namespace, remounts private, mounts tmpfs over the working directory, copies `validate_cap`, optionally creates setuid/setgid variants, clears/sets capability sets, tests ambient raise failure cases, raises/clears ambient caps, execs the helper for expected E/P/I/A states, and runs privileged SUID/SGID transition cases only when the outer namespace has real privilege.

## State and Persistence Behavior

The test mutates process credentials/capabilities, namespaces, mount namespace state, a private tmpfs, copied helper files, file ownership/mode bits, and ambient capability state. These changes are isolated in forked children/namespaces where possible.

## Dependencies and Integration Points

It depends on libcap-ng, user namespace support or root, mount namespace support, tmpfs, capability xforms in the kernel, and the `validate_cap` helper built beside the test.

## Risks and Test Signals

Risks include user namespace denial, filesystem or LSM restrictions on setuid/setgid, capability behavior differences under secureexec, skipped privileged cases when not root, and global count confusion across forks. Signals are planned kselftest results, expected failure of invalid ambient raises, expected helper observations for E/P/I/A sets, and skipped SUID/SGID tests without outer privilege.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/test_execve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/validate_cap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/validate_cap.c

## Purpose

`validate_cap.c` is the execed helper for the capability selftest. It verifies that `CAP_NET_BIND_SERVICE` is present or absent in the effective, permitted, inheritable, and ambient sets exactly as specified by command-line arguments.

## Important APIs, Types, and Functions

Functions are `bool_arg` and `main`. It uses `capng_get_caps_process`, `capng_have_capability`, `prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_IS_SET, ...)`, optional `getauxval(AT_SECURE)`, and kselftest message helpers. Arguments `argv[1]` through `argv[4]` are boolean strings for effective, permitted, inheritable, and ambient.

## Control Flow

`main` requires exactly four expected-state arguments, records whether `AT_SECURE` is set when glibc supports `getauxval`, loads current process capabilities with libcap-ng, compares each capability set and ambient state with `bool_arg`, prints a mismatch and exits nonzero on the first failure, otherwise prints success.

## State and Persistence Behavior

It is read-only with respect to capability state. It observes current process credentials after exec and exits.

## Dependencies and Integration Points

It depends on libcap-ng, capability UAPI, `prctl` ambient-capability support, and glibc `getauxval` where available. It is copied and executed by `test_execve.c`, including setuid/setgid variants.

## Risks and Test Signals

Risks include helper escaping with elevated file mode, unsupported ambient capability API, wrong boolean arguments, and secureexec environment effects. Signals are exact match of E/P/I/A states and diagnostic inclusion of `AT_SECURE` state for mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/validate_cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/Makefile

## Purpose

This Makefile builds and registers the cgroup kselftest suite. It covers core cgroup behavior plus CPU, cpuset, freezer, hugetlb memcg, kill, kmem, memcontrol, pids, and zswap tests.

## Important APIs, Types, and Functions

It adds `-Wall -pthread`, defines `TEST_FILES := with_stress.sh`, `TEST_PROGS := test_stress.sh test_cpuset_prs.sh test_cpuset_v1_hp.sh`, `TEST_GEN_FILES := wait_inotify`, and a sorted `TEST_GEN_PROGS` list. `LOCAL_HDRS` references clone3 and pidfd selftest headers. It includes `../lib.mk` and `lib/libcgroup.mk`, then declares each generated C test depends on `$(LIBCGROUP_O)`.

## Control Flow

Make builds helper programs and generated tests, pulling in the cgroup helper library object. Shell scripts are registered as runtime tests, and `with_stress.sh` is installed as a support file.

## State and Persistence Behavior

No runtime state is owned by the Makefile. Build artifacts and linked helper objects are produced under kselftest output directories.

## Dependencies and Integration Points

It integrates the cgroup test directory with shared kselftest infrastructure and local libcgroup helpers. It depends on pthread support and headers from clone3/pidfd selftest directories.

## Risks and Test Signals

Risks include missing local helper headers, stale dependency list when adding tests, and unsorted test lists causing maintenance churn. Signals are successful compilation/linking of every `TEST_GEN_PROGS` entry and availability of shell/runtime support files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/config

## Purpose

This kselftest config fragment declares kernel configuration options required for the cgroup selftests.

## Important APIs, Types, and Functions

It enables `CONFIG_CGROUPS`, `CONFIG_CGROUP_CPUACCT`, `CONFIG_CGROUP_FREEZER`, `CONFIG_CGROUP_SCHED`, `CONFIG_MEMCG`, and `CONFIG_PAGE_COUNTER`.

## Control Flow

There is no executable flow. Test runners or VM build scripts merge the fragment into a kernel config before building/running cgroup tests.

## State and Persistence Behavior

The file is persistent build metadata. It does not alter runtime state directly.

## Dependencies and Integration Points

It integrates with kselftest config aggregation and VM/kernel build tooling. The selected options support CPU accounting/scheduling, freezer, memory cgroups, and page counters needed by the cgroup suite.

## Risks and Test Signals

Risks include missing newer cgroup options required by added tests and false skips/failures when the fragment is not applied. Signals are kernel `.config` entries set to `y` and cgroup tests finding the expected controllers/features at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/config -->
