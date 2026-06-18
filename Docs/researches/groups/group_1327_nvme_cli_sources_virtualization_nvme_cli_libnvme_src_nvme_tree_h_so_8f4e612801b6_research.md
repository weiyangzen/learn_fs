# Group Research: group_1327_nvme_cli_sources_virtualization_nvme_cli_libnvme_src_nvme_tree_h_so_8f4e612801b6

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/nvme-cli` is included in subset A. All listed files were read completely, including the zero-byte JSON fixture.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.h

## Purpose
Public libnvme topology/tree API header. It defines opaque handles for hosts, subsystems, controllers, namespaces, namespace heads, paths, and stats, plus traversal macros and public operations over the scanned NVMe object graph.

## Main Interfaces
- Opaque types: `libnvme_host_t`, `libnvme_subsystem_t`, `libnvme_ctrl_t`, `libnvme_ns_t`, `libnvme_path_t`, `libnvme_ns_head_t`.
- Global context helpers: application string setters/getters, namespace scan skipping, cached FD release.
- Host identity APIs: `libnvme_get_host()`, `libnvme_host_get_ids()`, PDC flag setters/getters.
- Iterators and macros for host, subsystem, controller, namespace, and path traversal, including safe variants for deletion during iteration.
- Topology lifecycle: scan controller, scan namespace, scan topology, rescan controller, refresh topology, free/unlink controller/subsystem/host/namespace.
- Config APIs: read JSON config, dump JSON config, dump internal tree.
- Sysfs accessors for subsystem/controller/namespace/path attributes.

## Behavior and Design Notes
The header exposes libnvme’s internal topology as a hierarchical object tree rooted in `struct libnvme_global_ctx`, while preserving ABI opacity for concrete structs. It supports both physical controller/namespace relationships and multipath namespace/path relationships. Public getters include identity, model/serial/firmware, ANA/path attributes, transport handle access, controller state, and namespace/controller stats.

## Filesystem/Storage Relevance
This is the main API surface for discovering and representing NVMe block devices and NVMe-oF fabrics topology. It is relevant to block-storage enumeration, multipath path-state inspection, sysfs-driven device metadata, and user-space storage tooling integration.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/types.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/types.h

## Purpose
Compatibility header for Linux-style fixed-width integer types.

## Behavior
On Linux it includes `<linux/types.h>`. On non-Linux platforms it maps `__u8`, `__u16`, `__u32`, `__u64`, signed variants, and endian-tagged aliases like `__le32`/`__be32` to standard C integer types.

## Relevance
This file supports portable compilation of libnvme headers and structs outside Linux, especially Windows, while preserving Linux/NVMe naming conventions used across the library.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/uring.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/uring.c

## Purpose
Implements asynchronous NVMe passthrough submission using `io_uring` and `IORING_OP_URING_CMD`.

## Main Logic
- Probes kernel support for `IORING_OP_URING_CMD`.
- Opens/closes an `io_uring` queue with SQE128/CQE32 setup and 16 entries.
- Wraps each async command in `struct libnvme_async_req`, preserving passthrough command, cookie, user data, opcode, and dry-run queue linkage.
- Submits admin and I/O passthrough via `LIBNVME_URING_CMD_ADMIN` or `LIBNVME_URING_CMD_IO`.
- Reaps completions, calls transport submit callbacks, handles retry decisions, and returns completion status/cookie.
- Supports dry-run mode by queueing requests internally and completing them without kernel submission.

## Error Handling
Returns `-ENODEV` for missing handles, `-ENOTSUP` when io_uring is unavailable, `-EAGAIN` for full queues or no completions, and propagates allocation/submission errors. Closing drains pending completions before freeing the ring.

## Relevance
This is the async command path for high-throughput NVMe passthrough operations, falling back elsewhere when unsupported.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/uring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/util-fabrics.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/util-fabrics.c

## Purpose
NVMe-oF fabrics utility implementation for extended attributes, interface caching, and host entity metadata strings.

## Main Logic
- `libnvmf_exat_ptr_next()` advances over variable-sized `struct nvmf_ext_attr` records using encoded extended-attribute length.
- `libnvmf_getifaddrs()` lazily caches `getifaddrs()` results in the global context.
- `libnvmf_get_entity_name()` returns the local hostname in a zero-filled buffer.
- `libnvmf_get_entity_version()` builds a version string from `/proc/sys/kernel/ostype`, `/proc/sys/kernel/osrelease`, and `NAME`/`VERSION_ID` in `/etc/os-release`.

## Parsing Details
Local helpers strip trailing whitespace/newlines, strip quotes around os-release values, and copy bounded values into caller buffers.

## Relevance
Supports fabrics discovery-controller metadata and host-interface matching infrastructure used by NVMe-oF connection and discovery flows.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/util-fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/util.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/util.c

## Purpose
Core libnvme utility implementation: status/error conversion, string tables, hostname/address helpers, key-value parsing, UUID utilities, interface address matching, basename, and fabrics config copying.

## Main Logic
- Maps NVMe generic, command-specific, and fabrics status codes to errno-like values.
- Converts NVMe status codes and kernel errors to readable strings, including generic, command-specific, NVM, fabrics, media, path, and vendor-specific classes.
- Maps libnvme connect errors such as resolve failure, invalid transport, already connected, unsupported, ignored, or missing TLS key.
- Resolves hostnames to transport addresses when `NVME_HAVE_NETDB` is available.
- Provides `startswith()`, `kv_strip()`, and `kv_keymatch()` for simple config-style text parsing.
- Provides project/git version getters.
- Converts UUIDs to/from string form, generates RFC 4122-style random UUIDs, and searches identify UUID lists.
- Compares numeric IPv4/IPv6 addresses, including IPv4-mapped IPv6 cases, and locates matching network interfaces.
- Implements a stable `libnvme_basename()` independent of libc variant behavior.
- Provides `libnvme_fabrics_config_copy()` as the single copy point for fabrics config structs.

## Portability
Uses Windows BCrypt for random bytes when available, otherwise `/dev/urandom`. Network helpers degrade to logging and unsupported/false results when libnss/netdb support is absent.

## Relevance
This file supplies common support for command-result interpretation, NVMe-oF address handling, identity generation, and configuration parsing used throughout libnvme.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/util.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/util.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/util.h

## Purpose
Public/internal utility declarations for libnvme.

## Main Interfaces
- `enum libnvme_connect_err` defines libnvme-specific connection error codes starting at 1000.
- Status conversion APIs: `libnvme_status_to_errno()`, `libnvme_status_to_string()`, opcode-specific status helper, connect error string helper, and `libnvme_strerror()`.
- Inline opcode-specific status strings for sanitize namespace and set-features command-specific statuses.
- Fabrics extended-attribute iterator: `libnvmf_exat_ptr_next()`.
- Version selectors and `libnvme_get_version()`.
- UUID conversion/generation/search helpers.
- `libnvme_basename()`.

## Relevance
This header is the shared utility contract for libnvme callers and internal modules, especially around error presentation and portable identifiers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/util.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/config-diff.sh -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/config-diff.sh

## Purpose
Test wrapper for config JSON/sysfs fixture diff tests.

## Behavior
Parses `--sysfs-tar` and `--config-json`, unpacks a sysfs tarball into the build directory when provided, sets `LIBNVME_SYSFS_PATH`, `LIBNVME_HOSTNQN`, and `LIBNVME_HOSTID`, runs the requested test binary with the config JSON path, captures output, and compares it to the expected `.out` file with `diff -u`.

## Relevance
Provides deterministic config/topology tests without depending on the host machine’s real NVMe sysfs state.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/config-diff.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/config-dump.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/config-dump.c

## Purpose
Small test binary that scans topology, reads a JSON config, and dumps the merged config.

## Behavior
Creates a global context, scans topology while tolerating `-ENOENT`, reads the supplied config file, dumps JSON config to stdout, and exits success/failure.

## Relevance
Used by fixture diff tests to validate JSON import/export and sysfs-discovered topology merging.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/config-dump.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/config-pcie-with-tcp-config.json -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/config-pcie-with-tcp-config.json

## Purpose
JSON config fixture with two hosts and TCP subsystem ports.

## Contents
Defines two host entries, each with host NQN/host ID and one subsystem `nqn.io-1`. Each subsystem has two TCP ports at `192.168.154.144` with services `4420` and `4421`, both using `dhchap_key:"none"`.

## Relevance
Exercises merging mocked PCIe/sysfs topology with explicit TCP fabrics configuration.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/config-pcie-with-tcp-config.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/config-pcie.json -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/config-pcie.json

## Purpose
Empty JSON fixture.

## Contents
Zero-byte file.

## Relevance
Used to validate config dumping when topology comes only from the mocked PCIe sysfs fixture and there is no JSON-supplied configuration.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/config-pcie.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/hostnqn-order.json -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/hostnqn-order.json

## Purpose
JSON fixture for host identity precedence/order testing.

## Contents
Defines two host entries with different host NQN/host ID pairs, each containing subsystem `nqn.io-1` and two TCP ports at `192.168.154.144:4420` and `:4421`.

## Relevance
The first host entry acts as the default JSON host identity for `libnvme_host_get_ids()` when command-line/env IDs are absent.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/hostnqn-order.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-1.json -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-1.json

## Purpose
TLS key JSON fixture without explicit PSK identity.

## Contents
Defines one host and one TCP subsystem port with `tls:true`, `dhchap_key:"none"`, and an encoded `tls_key`.

## Relevance
Used to verify libnvme imports/exports encoded TLS keys and can dump normalized config.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-1.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-2.json -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-2.json

## Purpose
TLS key JSON fixture with explicit TLS PSK identity.

## Contents
Same basic host/subsystem/port structure as `tls_key-1.json`, but includes `tls_psk_identity` alongside the encoded `tls_key`.

## Relevance
Covers preservation/serialization of both PSK identity and key material in JSON config tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/data/tls_key-2.json -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/hostnqn-order.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/hostnqn-order.c

## Purpose
Tests precedence order for host NQN and host ID selection.

## Test Cases
- `command_line()` passes explicit hostnqn/hostid arguments and verifies they override other sources.
- `json_config()` clears environment values, reads JSON before scanning, and verifies the first JSON host is selected by default.
- `from_file()` sets `LIBNVME_HOSTNQN` and `LIBNVME_HOSTID` environment values and verifies they are selected when no command-line args are given.

## Relevance
Validates the documented host identity resolution order used by Linux NVMe and libnvme config flows.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/hostnqn-order.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/meson.build

## Purpose
Meson test definitions for libnvme config fixtures.

## Behavior
Requires `diff`, builds `test-config-dump`, `test-hostnqn-order`, and `test-psk-json`, then registers tests through `config-diff.sh`. It wires sysfs tarballs and JSON fixtures for PCIe/config merge tests, host identity order tests, and TLS key JSON tests.

## Relevance
Connects deterministic config fixtures into the libnvme test suite.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/psk-json.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/config/psk-json.c

## Purpose
Tests TLS key import/export through JSON config.

## Behavior
Reads config, iterates all hosts/subsystems/controllers, imports each controller TLS key with `libnvme_import_tls_key_versioned()`, exports it back with `libnvme_export_tls_key_versioned()`, resets the controller TLS key, then dumps config to stdout.

## Relevance
Validates that encoded TLS PSK material round-trips through libnvme’s JSON representation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/config/psk-json.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/cpp.cc -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/cpp.cc

## Purpose
C++ compile/use smoke test for libnvme public headers.

## Behavior
Creates a global context, scans topology while tolerating missing/inaccessible sysfs, traverses hosts/subsystems/controllers/namespaces/paths with public macros, and prints selected attributes with C++ iostreams.

## Relevance
Ensures libnvme headers and traversal APIs are usable from C++ translation units.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/cpp.cc -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/hkdf_add1.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/hkdf_add1.c

## Purpose
OpenSSL HKDF behavior probe/test.

## Behavior
Builds two HKDF contexts with the same SHA-256 salt/key. One derives with two `EVP_PKEY_CTX_add1_hkdf_info()` calls (`a` then `b`), the other with only `b`. If outputs match, the API behaved like set/replace and the test fails; if different, it prints `add` and succeeds.

## Relevance
Confirms OpenSSL HKDF info accumulation semantics needed by libnvme crypto/TLS key derivation expectations.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/hkdf_add1.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/ana.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/ana.c

## Purpose
Mock-ioctl tests for atomic ANA log retrieval.

## Test Coverage
Covers invalid retry count, too-small header buffer, no groups, one/multiple ANA groups with and without namespace ID lists, RGO groups-only mode, multi-PDU reads, change-count retry/refetch behavior, max retry exhaustion, and buffer-too-short handling.

## Behavior
Each test constructs expected mock admin Get Log Page commands with precise `cdw10`, RAE/LSP bits, LPOL offsets, transfer lengths, and output data. It then calls `libnvme_get_ana_log_atomic()` and compares returned log bytes and adjusted length.

## Relevance
Validates robust ANA multipath state log retrieval, especially consistency under changing `chgcnt` and log sizes larger than one PDU.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/ana.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/async.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/async.c

## Purpose
Tests passthrough async API behavior when io_uring support is unavailable.

## Test Coverage
- Async admin submit returns `-ENOTSUP`.
- Async I/O submit returns `-ENOTSUP`.
- Async reap returns `-ENOTSUP`.
- Synchronous admin and I/O passthrough still work through mock ioctl.
- Batched submit pattern falls back to sync execution, while `libnvme_wait_passthru()` reports unsupported without io_uring.

## Relevance
Ensures no-uring environments have predictable fallback behavior for passthrough command users.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/async.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/discovery.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/discovery.c

## Purpose
Mock tests for NVMe-oF discovery log retrieval.

## Test Coverage
Covers empty discovery logs, four-entry single fetch, five-entry multi-fetch chunking, generation-counter changes requiring refetch, max retry exhaustion, and errors during initial header fetch, entries fetch, and generation-counter verification.

## Behavior
Uses `libnvmf_discovery_args` with configurable max retries, calls `libnvmf_get_discovery_log()`, and validates returned headers/entries. Fixture helpers create valid printable ASCII fields and account for space-padded log strings.

## Relevance
Validates consistency and retry behavior for fabrics discovery log reads, which are central to NVMe-oF target enumeration.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/discovery.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/features.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/features.c

## Purpose
Large mock-ioctl test suite for NVMe Get Features and Set Features command initializer helpers.

## Test Coverage
Covers generic set/get features plus feature-specific helpers for arbitration, power management, LBA range, temperature threshold, error recovery, volatile write cache, number of queues, IRQ coalescing/config, write atomicity, async events, APST, host memory buffer, timestamp, KATO, HCTM, non-operational power state config, read recovery level, PLM config/window, LBA status interval, host behavior, sanitize, endurance event config, IOCS profile, software progress, host ID extended/non-extended, reservation notification mask, reservation persistence, namespace write protect, and live migration controller data queue.

## Behavior
Each case asserts exact command shape: opcode, NSID, FID, save/select bits, CDW packing, data buffer direction/length, timeout where applicable, result propagation, and returned data copies. Shared tail-call paths are tested for both NVMe status-code errors and negative kernel errors.

## Relevance
Protects the correctness of high-level feature helper APIs that build low-level NVMe admin passthrough commands.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/features.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/identify.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/identify.c

## Purpose
Mock-ioctl test suite for NVMe Identify command initializer helpers.

## Test Coverage
Covers identify namespace/controller, active namespace list, namespace descriptors, NVM set list, CSI namespace/controller forms, ZNS identify namespace/controller, CSI active namespace list, independent namespace identify, allocated namespace/list, namespace controller list, controller list, primary/secondary controller structures, namespace granularity, UUID list, domain list, endurance group list, CSI allocated namespace list, command set structure, namespace user data format, and CSI namespace user data format.

## Behavior
Each test builds a mock admin identify command with expected CNS, NSID, CDW11/CDW14 fields and data length, executes passthrough, and compares copied output data. Error tests verify both NVMe status code and kernel errno propagation.

## Relevance
Validates the libnvme identify API layer, which is foundational for discovering NVMe controller, namespace, command-set, and endurance/domain capabilities.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/identify.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/logs.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/logs.c

## Purpose
Mock-ioctl test suite for Get Log Page initializer helpers.

## Test Coverage
Covers sanitize, management address list, supported log pages, error, SMART, firmware slot, changed namespace list, command effects, self-test, telemetry host/controller, endurance group, predictable latency, FDP configs/RUH usage/stats/events, ANA, LBA status, endurance group events, FID/MI supported effects, boot partition, rotational media, dispersed namespace participating NVM subsystems, PHY RX EOM, reachability groups/associations, changed allocated namespace list, discovery, host discovery, AVE discovery, pull-model DDC request, media unit status, supported capacity config list, reservation notification, ZNS changed zones, persistent event, and lockdown logs.

## Behavior
Asserts LID, LSP, RAE, NUMD, NSID, CSI, offsets, domain/endurance/NVM-set selectors, and data-copy behavior by comparing mock output payloads to caller buffers.

## Relevance
Protects the command construction layer for diverse NVMe telemetry, health, topology, fabrics, FDP, ZNS, and namespace event logs.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/logs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/meson.build

## Purpose
Meson build/test definitions for ioctl mock tests.

## Behavior
Configures whether the platform has glibc-style `ioctl`, builds `mock-ioctl` from `mock.c` and `util.c`, sets it in `LD_PRELOAD`, configures ASAN preload ordering, and registers test executables for ANA, async, features, identify, logs, zns, misc, and discovery when fabrics is enabled.

## Relevance
Provides the test harness that intercepts ioctl calls so libnvme passthrough APIs can be verified without real NVMe hardware.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/meson.build -->