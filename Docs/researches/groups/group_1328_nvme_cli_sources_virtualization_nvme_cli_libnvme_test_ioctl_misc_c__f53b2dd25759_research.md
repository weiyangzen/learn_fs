# Group Research: group_1328_nvme_cli_sources_virtualization_nvme_cli_libnvme_test_ioctl_misc_c__f53b2dd25759

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/misc.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/misc.c

## Role

`misc.c` is a libnvme ioctl-path conformance test for many NVMe command initializer helpers. It does not talk to real hardware; it opens the synthetic `NVME_TEST_FD64` transport handle and relies on the local mock `ioctl()` interposer to validate the exact passthrough command layout.

## Behavior

The file builds expected `struct mock_cmd` entries and then calls libnvme initializer APIs plus `libnvme_exec_admin_passthru()` or `libnvme_exec_io_passthru()`. Each test validates command opcode, namespace ID, command dwords, payload direction, payload length, copied response data, and `cmd.result`.

Admin-side coverage includes format NVM, namespace management create/delete, fabrics property get/set, namespace attach/detach, firmware download/commit, security send/receive, LBA status, directives, capacity management, lockdown, sanitize, device self-test, virtualization management, discovery information management, controller data queue, track send, and live migration send/receive.

I/O-side coverage includes flush, read, write, compare, write zeroes, write uncorrectable, verify, DSM, copy descriptor formats f0/f1, reservations acquire/register/release/report, I/O management send/receive, and FDP reclaim unit handle helpers.

The copy tests explicitly check serialized descriptor bytes, including little-endian field placement for SLBAs, PI fields, ELBAT/ELBATM, and copy command dword fields. The migration and live-migration tests check wide offset splitting and count-to-byte conversions.

## Dependencies

- Includes `<libnvme.h>`.
- Uses `mock.h` for expected ioctl sequences.
- Uses `util.h` for `check`, `cmp`, random buffer filling, and cleanup helpers.
- Depends on the libnvme test fd URI handling and ioctl mock implementation.

## Filesystem/Storage Relevance

This is storage-command plumbing rather than filesystem code. Its value for `learn_fs` is in showing how libnvme maps higher-level NVMe storage operations into Linux passthrough ioctl command fields.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.c

## Role

`mock.c` implements the ioctl interception layer used by the libnvme ioctl tests. It replaces `ioctl()` for NVMe admin and I/O passthrough requests and validates each call against a preloaded sequence of `struct mock_cmd` expectations.

## Behavior

The file maintains two independent command queues: one for admin commands and one for I/O commands. Test code calls `set_mock_admin_cmds()` or `set_mock_io_cmds()` before invoking libnvme, and `end_mock_cmds()` verifies all expected calls were consumed.

The `execute_ioctl` macro validates opcode, flags, namespace ID, command dwords 2-3 and 10-15, metadata pointer content, data length, data payload for input commands, timeout, and result width. For output commands it copies synthetic bytes from `mock_cmd.out_data` into the caller-provided data buffer and writes the mocked result field.

The interposed `ioctl()` dispatches `LIBNVME_IOCTL_ADMIN_CMD`, `LIBNVME_IOCTL_ADMIN64_CMD`, `LIBNVME_IOCTL_IO_CMD`, and `LIBNVME_IOCTL_IO64_CMD`. Unknown ioctls are delegated with `dlsym(RTLD_NEXT, "ioctl")` when available, otherwise rejected with `-ENOTTY`.

The file also defines `io_uring_get_probe()` to return `0`, forcing tests away from io_uring probing and onto the ioctl path.

## Dependencies

- Uses internal `nvme/private.h` Linux passthrough command structures.
- Uses `mock.h` for expectations.
- Uses `util.h` for assertions and byte comparisons.
- Needs platform-specific ioctl signature handling via `NVME_HAVE_GLIBC_IOCTL`.

## Filesystem/Storage Relevance

This is a deterministic mock for NVMe storage ioctl ABI testing. It is central to validating libnvme command encoding without requiring a kernel NVMe device.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.h

## Role

`mock.h` declares the ioctl-test expectation structure and the functions used to install and finalize mock NVMe passthrough command sequences.

## API

`struct mock_cmd` models one expected passthrough ioctl invocation. It records opcode, flags, namespace ID, command dwords, metadata, input payload, data length, timeout, output payload, result value, and ioctl return/error behavior.

`set_mock_fd()` sets the expected file descriptor. `set_mock_admin_cmds()` and `set_mock_io_cmds()` install ordered slices of expected admin and I/O commands. `end_mock_cmds()` checks that no expected commands remain unexecuted.

## Design Notes

The struct distinguishes `in_data` from `out_data`: `in_data` means the test expects libnvme to submit those bytes, while `out_data` is copied back into the caller’s buffer. `out_data_len` can override `data_len` for partial output copying.

The `result` documentation explicitly notes 64-bit result handling: if a result cannot fit in `u32`, the test must use a 64-bit ioctl path.

## Filesystem/Storage Relevance

This header defines the test contract for Linux NVMe passthrough command encoding.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.c

## Role

`util.c` provides small support routines for ioctl tests: fatal assertion reporting, byte-buffer comparison, and pseudo-random test data generation.

## Behavior

`fail()` prints a formatted error to stderr and aborts. `cmp()` compares two buffers and, on mismatch, prints a hex dump of actual and expected bytes before aborting. `arbitrary()` fills a buffer with `rand()` bytes. `arbitrary_range()` returns a random value modulo a caller-supplied maximum.

The internal `hexdump()` formats bytes in uppercase hex, separating every 16 bytes with a newline.

## Dependencies

- Standard C stdio, stdarg, stdlib, string, and stdint.
- Paired with `util.h`.

## Filesystem/Storage Relevance

This is generic test infrastructure, but it supports byte-exact validation of NVMe storage command payloads.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.h

## Role

`util.h` declares the ioctl test helper API and defines assertion and cleanup convenience macros.

## API

It declares `fail()`, `cmp()`, `arbitrary()`, and `arbitrary_range()`. The `check(condition, fmt...)` macro aborts via `fail()` when a condition is false.

It also defines `__cleanup(fn)`, `freep()`, and `__cleanup_free`, enabling GNU cleanup-based automatic freeing in the tests.

## Filesystem/Storage Relevance

This is local test scaffolding for storage command validation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/zns.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/zns.c

## Role

`zns.c` tests libnvme ioctl command initializers for Zoned Namespace commands using the same mock ioctl infrastructure as `ioctl/misc.c`.

## Behavior

The test opens the synthetic `NVME_TEST_FD` handle and runs four tests: ZNS append, report zones, management send, and management receive.

`test_zns_append()` validates opcode, NSID, zone SLBA splitting, NLB/control encoding, variable-size tag setup through `nvme_init_var_size_tags()`, application tag setup through `nvme_init_app_tag()`, and copied data.

`test_zns_report_zones()` validates management receive command fields for report options, extended reporting, partial reporting, data length in dwords, and response payload copying.

`test_zns_mgmt_send()` and `test_zns_mgmt_recv()` validate action-specific fields in CDW13 and payload behavior.

## Dependencies

- Includes `<libnvme.h>`.
- Uses `mock.h` and `util.h`.
- Relies on libnvme ZNS command initializer helpers.

## Filesystem/Storage Relevance

This is directly relevant to zoned block-storage behavior: it verifies userspace command construction for ZNS zone append and zone management operations.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/ioctl/zns.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/meson.build

## Role

`test/meson.build` is the main Meson test orchestration file for libnvme’s test directory. It defines developer executables, unit tests, conditional feature tests, and subdirectories.

## Behavior

It runs Python-based public symbol and public header checks when Python is available. It builds hardware-oriented developer executables such as `main-test`, plus unit-test executables for C++, registers, ZNS, MI, MCTP, UUID, topology tree, fabrics helpers, utility helpers, PSK helpers, and headers.

Conditional blocks depend on build options and detected libraries: C++ compiler availability, `want_mi`, `want_fabrics`, `NVME_HAVE_NETDB`, `json_c_dep`, and `openssl_dep`.

For `mock-ifaddrs`, it builds a preloadable library and sets `LD_PRELOAD` plus `ASAN_OPTIONS=verify_asan_link_order=0` for tests needing deterministic interface enumeration.

It enters `subdir('ioctl')`, optionally `subdir('nbft')`, and, when JSON-C is present, `subdir('sysfs')` and `subdir('config')`.

The final loop generates one self-sufficiency test per public `<nvme/*.h>` header from `test-header.c.in`.

## Dependencies

- Meson build variables from the parent project: dependencies, feature flags, generated link args, and header list.
- Test sources in this directory and subdirectories.

## Filesystem/Storage Relevance

This file describes how libnvme validates its storage-management API surface across ioctl, MI, fabrics, sysfs topology, NBFT discovery, and header compatibility.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/mi-mctp.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/mi-mctp.c

## Role

`mi-mctp.c` is a full fake-MCTP transport test for libnvme Management Interface behavior over MCTP sockets. It wraps socket creation, `sendmsg`, `recvmsg`, `poll`, and MCTP tag ioctls so MI/MCTP behavior can be tested without a real endpoint.

## Test Harness

`struct test_peer` stores linear RX and TX buffers from the device perspective. RX is data sent from libnvme to the fake device; TX is data returned from the fake device to libnvme. Buffers include the NVMe-MI message type byte so tests can compare protocol diagrams directly.

The wrapped `sendmsg()` gathers iovecs into `rx_buf`. The wrapped `recvmsg()` either calls a per-test TX callback or synthesizes a minimal response, computes and appends MIC, scatters bytes into iovecs, and clears the TX buffer. `poll()` can be overridden per test. MCTP tag allocation/drop ioctls are simulated when the platform exposes the relevant constants.

## Coverage

Basic negative-path tests cover send errors, no response, receive errors, short responses, poll errors, poll timeout, and invalid response sizing.

MI/Admin response tests cover MI status errors, admin-over-MI errors, every 4-byte-aligned response size up to 4096 plus header, unaligned controller lists, and direct submit behavior with exact response lengths.

More Processing Required coverage simulates MPR followed by final success for MI and Admin commands, including a quirk where a drive returns an Admin-shaped MPR response. Additional tests validate endpoint timeout use, MPR-provided timeout values, maximum MPR clamping, and zero-MPR fallback.

AEM coverage is extensive. It simulates getting currently enabled events, disabling endpoint-enabled events, enabling host-requested events, receiving asynchronous event occurrence lists, invoking the handler, reading queued events with `libnvme_mi_aem_get_next_event()`, ACK responses, disable flows, invalid API usage, get-enabled behavior, and malformed endpoint responses at several protocol stages.

## Dependencies

- Uses libnvme public and private MI headers.
- Uses Linux MCTP headers or libnvme compatibility headers.
- Uses `utils.h` logging helpers.
- Calls internal CRC helper `libnvme_mi_crc32_update()`.

## Filesystem/Storage Relevance

This is storage-management transport testing. It validates reliability and protocol parsing for NVMe-MI over MCTP, which is relevant to out-of-band storage device management.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/mi-mctp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/mi.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/mi.c

## Role

`mi.c` tests libnvme’s Management Interface command and Admin-over-MI implementation using an in-memory custom MI transport. It avoids real MCTP sockets and instead directly inspects MI request/response headers and payloads.

## Test Harness

The file defines `test_transport`, whose submit callback initializes a default response, mirrors the request’s NMP response bit, and optionally invokes a per-test callback. `libnvme_mi_open_test()` creates an endpoint with this transport and marks quirks as already probed unless a test resets that state.

`test_transport_resp_calc_mic()` computes the response MIC using libnvme’s internal CRC helper. Tests use this to distinguish valid protocol failures from MIC failures.

## Coverage

Endpoint and controller lifecycle tests verify global endpoint lists and per-endpoint controller lists. Transport description tests verify fallback and custom endpoint descriptions.

Protocol validation covers successful MI data reads, transport failure, invalid MIC, too-small response headers, response-as-request errors, invalid message type, command slot indicator request setting, and CSI mismatch handling.

Admin-over-MI tests inspect raw request bytes for identify controller, identify namespace/list variants, namespace management create/delete, namespace attach/detach, firmware download and commit, format NVM, sanitize NVM, get/set features, and split get-log behavior. They also validate error propagation from MI response status and NVMe completion status.

Format validation rejects unaligned request/response sizes, bad offsets, too-large responses, impossible payload combinations, and invalid MI transfer lengths before any transport submission happens.

Additional tests cover configuration get/set operations, MCTP MTU endianness, SMBus frequency acceptance/rejection, endpoint quirk probing, and Admin transfer DLEN/DOFF field behavior for request and response payloads.

## Dependencies

- Uses public `<libnvme.h>` and `<libnvme-mi.h>`.
- Includes private libnvme headers for endpoint and transport internals.
- Uses CCAN endian and array-size helpers.
- Uses `utils.h` log helpers.

## Filesystem/Storage Relevance

This file validates NVMe management command construction and response parsing, especially for admin commands tunneled through an out-of-band management path.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/mi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/misc.cc -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/misc.cc

## Role

`misc.cc` is a small C++ compatibility test for libnvme headers.

## Behavior

It includes `<algorithm>` and `<libnvme.h>`, then checks that `std::min()` and `std::max()` still work. The intended regression guard is that libnvme headers must not leak `min` or `max` macros that would corrupt the C++ standard namespace.

`main()` returns the result of that check as the process exit code.

## Dependencies

- C++ compiler.
- Public libnvme header.

## Filesystem/Storage Relevance

No direct filesystem behavior. It protects C++ consumers of libnvme storage APIs from namespace pollution.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/misc.cc -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/mock-ifaddrs.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/mock-ifaddrs.c

## Role

`mock-ifaddrs.c` provides deterministic replacements for `getifaddrs()` and `freeifaddrs()` for fabrics and topology tests.

## Behavior

`getifaddrs()` allocates four `ifaddrs_storage` entries and returns a linked list with:

- `eth0` IPv4 address `192.168.1.20`.
- `eth0` IPv6 link-local address `fe80::dead:beef`.
- `lo` IPv4 loopback `127.0.0.1`.
- `lo` IPv6 loopback `::1`.

Each entry stores address, netmask, broadcast address, interface name, and flags in one allocation. `freeifaddrs()` frees the allocation starting from the first returned node.

## Dependencies

- Standard networking headers for `ifaddrs`, socket address structures, address families, and interface name sizes.
- Used by Meson through a preloadable shared library.

## Filesystem/Storage Relevance

This supports deterministic NVMe-oF address parsing and topology tests, especially link-local IPv6 scope behavior.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/mock-ifaddrs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/gen-nbft-diffs.sh.in -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/gen-nbft-diffs.sh.in

## Role

`gen-nbft-diffs.sh.in` is a Meson-configured helper for regenerating expected NBFT parser output files.

## Behavior

The script iterates over every file in `@TABLES_DIR@`, runs the configured `@NBFT_DUMP_PATH@` executable on it, and writes output to `@DIFF_DIR@/<table basename>`.

## Dependencies

- Substituted Meson variables: `TABLES_DIR`, `NBFT_DUMP_PATH`, and `DIFF_DIR`.
- POSIX shell.

## Filesystem/Storage Relevance

It maintains golden outputs for NVMe Boot Firmware Table parsing tests.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/gen-nbft-diffs.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/meson.build

## Role

`test/nbft/meson.build` defines NBFT parser tests over stored ACPI NBFT binary fixtures.

## Behavior

It builds `nbft-dump` from `nbft-dump.c`, configures helper scripts for diffing and regenerating expected output, and adds a `nbft-diffs` run target.

When `diff` is available, each good table fixture is tested by piping `nbft-dump` output into a unified diff against its stored expected output. Bad fixtures are registered as expected failures, using `expected_fail` for Meson >= 1.11.0 and `should_fail` for older Meson.

## Fixtures

Good tables include IPv4/IPv6, DHCP/static, discovery, multipath, Dell PowerEdge examples, half IPv4/IPv6 discovery, and empty-table cases. Bad tables include an old-spec table and random noise.

## Dependencies

- Meson.
- `diff` for golden-output comparisons.
- libnvme NBFT parser via `nbft-dump`.

## Filesystem/Storage Relevance

NBFT describes boot-time NVMe-oF discovery and connection configuration. These tests validate libnvme’s ability to parse that storage boot metadata.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump-diff.sh.in -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump-diff.sh.in

## Role

`nbft-dump-diff.sh.in` is a Meson-configured wrapper that compares one NBFT table’s parsed output with its expected diff fixture.

## Behavior

It requires two arguments: `TABLE` and `DIFF`. If the argument count is wrong it prints usage and exits `255`. Otherwise it runs `@NBFT_DUMP_PATH@ TABLE` and pipes stdout into `diff -u DIFF -`.

## Dependencies

- Substituted Meson variable `NBFT_DUMP_PATH`.
- POSIX shell and `diff`.

## Filesystem/Storage Relevance

It is test glue for validating deterministic parsing of NVMe boot firmware metadata.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump-diff.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump.c

## Role

`nbft-dump.c` is a deterministic dumper for parsed NBFT data. It is used by the NBFT golden-output tests.

## Behavior

`main()` creates a libnvme context, parses the NBFT table file path supplied on the command line with `libnvmf_read_nbft()`, prints a structured text representation, frees the parsed table, and exits nonzero on usage or parse errors.

`print_nbft()` prints raw table size, host UUID/NQN/configuration flags, primary flag, HFI entries, TCP properties, security entries, discovery entries, and subsystem namespace entries. It follows object relationships by printing referenced HFI, security, and discovery indexes.

`print_hex()` prints raw byte arrays such as UUIDs, MAC addresses, and namespace identifiers without separators.

## Dependencies

- Public libnvme API and NBFT structures.
- Standard C stdio/stdlib/string/unistd.

## Filesystem/Storage Relevance

The file validates libnvme’s parsing of NVMe-oF boot configuration exposed through ACPI NBFT tables.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/psk.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/psk.c

## Role

`psk.c` is a fixed-vector test for libnvme TLS PSK import/export and TLS key identity generation helpers.

## Behavior

The file defines known PSK byte arrays, lengths, versions, HMAC algorithm IDs, expected exported key strings, and expected identity strings.

It tests:

- `libnvme_export_tls_key()`.
- `libnvme_import_tls_key()`.
- `libnvme_export_tls_key_versioned()`.
- `libnvme_import_tls_key_versioned()`.
- `libnvme_generate_tls_key_identity()`.
- `libnvme_generate_tls_key_identity_compat()`.

The import tests validate parsed HMAC, length, and raw PSK bytes. Export and identity tests compare generated strings exactly. Identity generation treats `-ENOTSUP` as a permissible skip, likely for builds without required crypto support.

`test_rc` accumulates failures and controls process exit.

## Dependencies

- Public libnvme API.
- CCAN `array_size`.
- Optional crypto capability behind libnvme’s TLS identity functions.

## Filesystem/Storage Relevance

This supports NVMe/TCP secure connection setup by validating TLS PSK serialization and identity derivation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/psk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/register.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/register.c

## Role

`register.c` is a hardware-oriented utility that maps an NVMe controller PCI resource BAR and prints decoded NVMe controller registers.

## Behavior

`main()` expects an `nvme<X>` controller name, builds `/sys/class/nvme/<name>/device/resource0`, opens it read-only synchronous, maps one page, calls `nvme_print_registers()`, unmaps, and exits.

`nvme_print_registers()` reads 32-bit and 64-bit MMIO registers using endian-safe helpers, then prints raw register values and decoded bitfields for CAP, VS, INTMS/INTMC, CC, CSTS, NSSR, AQA, ASQ/ACQ, CMB, boot partition, PMR, and related capability/status registers.

## Dependencies

- Linux sysfs PCI resource layout.
- `mmap()`, `open()`, and page-size APIs.
- NVMe register offsets and field macros from libnvme.
- CCAN endian helpers.

## Filesystem/Storage Relevance

This is storage device introspection tooling. It interacts with sysfs and PCI MMIO rather than filesystem data structures.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/register.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/sysfs/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/sysfs/meson.build

## Role

`test/sysfs/meson.build` defines sysfs topology golden-output tests.

## Behavior

If `diff` is found, it builds `test-tree-dump` from `tree-dump.c`, declares two sysfs fixture names (`tree-pcie` and `tree-apple-nvme`), locates `tree-diff.sh`, and registers one test per fixture.

Each test passes the build directory, dumper path, compressed sysfs fixture tarball, and expected output file to `tree-diff.sh`.

## Dependencies

- Meson.
- `diff`.
- `tree-diff.sh`.
- libnvme dependency.

## Filesystem/Storage Relevance

This validates libnvme’s sysfs topology scanning against captured NVMe device trees.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/sysfs/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-diff.sh -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-diff.sh

## Role

`tree-diff.sh` is the sysfs topology fixture runner and comparator.

## Behavior

The script takes build directory, tree-dump executable, compressed sysfs input, and expected output. It removes any prior extracted fixture directory, creates a fresh directory, extracts the tarball, and runs `tree-dump` with deterministic environment variables:

- `LIBNVME_SYSFS_PATH` points at the extracted fixture.
- `LIBNVME_HOSTNQN` is a fixed host NQN.
- `LIBNVME_HOSTID` is a fixed host ID.

It captures output into `<test>.out` and compares it to the expected file with `diff -u`.

## Dependencies

- Bash with `-e`.
- `tar`, `diff`.
- `tree-dump` executable.

## Filesystem/Storage Relevance

It is a filesystem-backed fixture harness: libnvme scans an extracted fake sysfs tree instead of the host’s real `/sys`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-diff.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-dump.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-dump.c

## Role

`tree-dump.c` is a small executable that scans libnvme topology and dumps the resulting tree for sysfs fixture tests.

## Behavior

It creates a libnvme context, calls `libnvme_scan_topology()`, tolerates `ENOENT` and `EACCES`, then calls `libnvme_dump_tree()` and prints a trailing newline. It exits success only if scanning and dumping succeed.

The actual sysfs path and host identity are supplied through environment variables by `tree-diff.sh`.

## Dependencies

- Public libnvme topology APIs.
- Standard C errno and process exit APIs.

## Filesystem/Storage Relevance

This directly tests libnvme’s interpretation of NVMe controller, subsystem, namespace, and path state represented in sysfs.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-dump.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test-fabrics.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/test-fabrics.c

## Role

`test-fabrics.c` unit-tests static helper functions from `src/nvme/fabrics.c` by including that source file directly after redefining `static` away.

## Behavior

The file uses a small `CHECK` macro and `test_rc` accumulator to print pass/fail status. It tests:

- `strchomp()` trailing-space removal.
- `hostid_from_hostnqn()` UUID extraction.
- Argument-building helpers for boolean, hex, integer, integer-or-minus-one, and string arguments.
- `inet4_pton()` IPv4 parsing and error handling.
- `inet_pton_with_scope()` IPv4/IPv6 parsing, scoped IPv6, null service, and port overflow.
- `traddr_is_hostname()` classification, especially ensuring scoped IPv6 like `fe80::1%lo` is not misclassified as a hostname.
- `unescape_uri()` percent decoding, explicit length truncation, invalid percent sequences, and truncated percent sequences.

A real libnvme context is created because some helper error paths log through `libnvme_msg()`.

## Dependencies

- Direct inclusion of `../src/nvme/fabrics.c`.
- Public and internal libnvme symbols.
- Network address parsing APIs.
- Built with `-fgnu89-inline` in Meson to avoid inline linkage problems caused by redefining `static`.

## Filesystem/Storage Relevance

This validates NVMe-oF connection argument construction and address classification, which affects how storage targets are discovered and connected.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test-fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test-header.c.in -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/test-header.c.in

## Role

`test-header.c.in` is a template used to generate one compile test per public libnvme header.

## Behavior

Meson substitutes `@HDR@` and generates a C file that includes `<nvme/@HDR@.h>` as the first and only header, then defines an empty `main()` returning zero.

The purpose is to ensure every public header is self-sufficient and does not require prior includes.

## Dependencies

- Meson configuration substitution.
- Public libnvme header installation layout.

## Filesystem/Storage Relevance

No direct storage behavior. It protects consumers of libnvme storage APIs from header dependency bugs.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test-header.c.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test-util.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/test-util.c

## Role

`test-util.c` tests public and private utility helpers from libnvme’s utility layer.

## Behavior

It validates `libnvme_get_version()` for project version, git version, and invalid version type. It tests `libnvme_ipaddrs_eq()` across equal IPv4, compressed/equivalent IPv6, null pairs, IPv4-mapped IPv6 equivalence, unequal IPv4/IPv6, invalid strings, and null/non-null cases.

It exhaustively checks `nvme_id_ns_flbas_to_lbaf_inuse()` for `flbas` values `0x00` through `0x7f`, comparing against the expected LBA format index mapping.

The test prints aligned pass/fail status and exits failure if any group fails.

## Dependencies

- Public `<libnvme.h>`.
- Internal `<nvme/private.h>`.
- Network database headers.

## Filesystem/Storage Relevance

The LBA format helper is directly storage-relevant because it interprets namespace format state. IP comparison supports NVMe-oF address handling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test-util.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/test.c

## Role

`test.c` is a hardware-facing exploratory libnvme test program. Unlike the unit tests, it scans real topology and issues many admin commands to discovered controllers and namespaces.

## Behavior

The program creates a libnvme context, scans topology with a subsystem NQN filter, prints discovered hosts/subsystems/controllers, optionally scans one named controller, walks the full topology, and prints namespace identity information including LBA size/count, EUI64, NGUID, UUID, CSI, and path ANA state.

`test_ctrl()` issues identify controller, SMART log, allocated/active namespace lists, controller lists, primary/secondary controller identify, namespace granularity, UUID list, sanitize/reservation/ANA/endurance/telemetry/self-test/command-effects/changed-namespace/firmware/error logs, and many get-features commands. It prints whether each command succeeded.

`test_namespace()` identifies a namespace, computes active LBA format, prints size information, issues identify allocated namespace, identify namespace descriptors, and write-protect feature queries.

The program is not registered as a Meson unit test because it requires real NVMe hardware and meaningful user inspection of output.

## Dependencies

- Public libnvme topology, controller, namespace, and command APIs.
- Internal `nvme/private.h`.
- CCAN endian helpers.
- Real sysfs/NVMe device access for meaningful execution.

## Filesystem/Storage Relevance

This is a broad NVMe storage-device smoke test. It exercises topology scanning and admin/log/feature commands that describe block namespace properties used by higher storage layers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/test.c -->