# Group Research: group_1329_nvme_cli_sources_virtualization_nvme_cli_libnvme_test_tree_fabrics__e6e8074d1488

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/tree-fabrics.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/tree-fabrics.c

This file is a libnvme unit test for NVMe-oF/transport-aware tree controller lookup and matching behavior. It constructs in-memory `libnvme_global_ctx` trees with hosts, subsystems, and controllers, then validates that controller identity matching behaves correctly for TCP, RDMA, FC, PCIe, loop, discovery controllers, source-address extraction, and paginated lookup.

Key structures and helpers:
- `struct test_data` holds input `libnvmf_context`, subsystem name, expected subsystem/controller pointers, and a generated controller id.
- `DEFAULTS(...)` seeds fabric controller params for TCP/RDMA/FC test cases.
- `create_tree()` builds one host/subsystem and creates controllers from `test_data` using `libnvme_get_subsystem()` and `libnvme_lookup_ctrl()`.
- `show_ctrl()` and `match_ctrl()` print and validate controller attributes through getters such as `libnvme_ctrl_get_transport()`, `libnvme_ctrl_get_traddr()`, `libnvme_ctrl_get_host_traddr()`, and `libnvme_ctrl_get_trsvcid()`.
- `ctrl_match()` is the central table-test helper: it creates a reference controller, optionally fakes sysfs-style `name` and `address`, calls `libnvmf_ctrl_find()` before `libnvme_lookup_ctrl()`, and checks whether candidate params should match or create a distinct controller.
- `ctrl_config_match()` separately tests `libnvmf_ctrl_match_config()` against a reference controller.

Major test coverage:
- `test_lookup()` verifies controller creation, tree count, deduplication, and lookup relaxation rules. TCP lookups test combinations of `trsvcid`, `host_traddr`, and `host_iface`; non-TCP default lookup clears host interface and service id.
- `test_src_addr()` directly mutates private `c->address` strings and checks `libnvme_ctrl_get_src_addr()` for NULL/empty input, missing `src_addr`, IPv4, IPv6, and IPv6 zone/scope suffix stripping.
- `test_ctrl_match_fc()` validates FC matching by transport, traddr, trsvcid, and host_traddr, with relaxed matching when candidate host binding is absent.
- `test_ctrl_match_rdma()` mirrors FC-style cases for RDMA, using IP address equality for traddr/host_traddr.
- `test_ctrl_match_tcp()` is the largest matrix. It validates IPv4 and IPv6 TCP candidate/reference matching against mocked interfaces:
  - `eth0`: `192.168.1.20`, `fe80::dead:beef`
  - `lo`: `127.0.0.1`, `::1`
  It tests unspecified source binding, explicit `host_traddr`, explicit `host_iface`, matching/non-matching local addresses, loopback behavior, and sysfs `address` strings with `src_addr=...`.
- `test_ctrl_config_match()` checks config-level matching for TCP, including subsystem NQN behavior.
- `test_ctrl_match_pcie()` verifies PCIe matching by transport and case-insensitive BDF-style `traddr`; NULL candidate `traddr` is treated as a match.
- `test_ctrl_match_loop()` verifies loop transport matching by transport alone.
- `test_well_known_nqn()` checks `NVME_DISC_SUBSYS_NAME`: candidates for the well-known discovery NQN only match controllers marked with `libnvme_ctrl_set_discovery_ctrl(..., true)`.
- `test_none_normalization()` validates that `"none"` for `host_traddr` or `host_iface` behaves like NULL.
- `test_ctrl_config_match_rdma()` and `test_ctrl_config_match_fc()` validate `libnvmf_ctrl_match_config()` for those transports.
- `test_lookup_ctrl_pagination()` checks the `p` argument to `libnvme_lookup_ctrl()`: searches begin after `p`, so earlier matches are skipped and later duplicate candidates can be created/found.

Dependencies and integration:
- Includes public libnvme and private headers: `<libnvme.h>`, `<nvme/private.h>`, `<nvme/private-fabrics.h>`.
- Relies on private struct access (`c->address`, `reference_ctrl->name`) for test setup.
- Meson wires it as `libnvme - tree-fabrics` only when the mocked ifaddrs support is available, using `mock-ifaddrs.c`/environment per `libnvme/test/meson.build`.

Risk and maintenance notes:
- The test intentionally assigns string literals to private `reference_ctrl->address` and resets fields to NULL before freeing to avoid freeing non-owned memory. Future ownership changes in controller internals could make this brittle.
- The table matrix encodes subtle matching policy. Any change to `_candidate_init*`, `libnvmf_ctrl_find()`, interface probing, source address normalization, or `libnvmf_ctrl_match_config()` should update expected cases here.
- Error paths in `ctrl_match()` return before `libnvme_free_global_ctx()` in several failure branches, acceptable for a short-lived failing test but still a leak under failure diagnostics.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/tree-fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/tree.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/tree.c

This file is a focused unit test for non-fabrics libnvme tree operations: host lookup/deduplication, subsystem lookup/deduplication, getters, and iteration macros.

Test cases:
- `test_host_dedup()` confirms `libnvme_lookup_host(ctx, hostnqn, hostid)` returns the same pointer for identical host credentials and a different pointer for different credentials.
- `test_hostid_from_hostnqn()` verifies that passing NULL `hostid` derives the host UUID from an NQN of the form `nqn.2014-08.org.nvmexpress:uuid:<uuid>`.
- `test_host_attrs()` validates `libnvme_host_get_hostnqn()` and `libnvme_host_get_hostid()`.
- `test_host_iteration()` creates three hosts and verifies `libnvme_for_each_host()` visits exactly three.
- `test_subsystem_dedup()` checks `libnvme_lookup_subsystem()` pointer reuse for identical name/NQN and distinct objects for different subsystem identities.
- `test_subsystem_attrs()` validates `libnvme_subsystem_get_name()` and `libnvme_subsystem_get_subsysnqn()`.
- `test_subsystem_iteration()` verifies `libnvme_for_each_subsystem()` count.

Integration:
- Uses `libnvme_create_global_ctx(stdout, LIBNVME_LOG_ERR)` and frees it after each test.
- Includes `<nvme/private.h>` to access tree-related types/macros.
- Meson builds it as `test-tree` and registers `libnvme - tree`.

Risk and maintenance notes:
- The tests assert allocation success, so they abort rather than report graceful failure on setup errors.
- Coverage is intentionally in-memory; it does not scan `/sys` or require hardware.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/tree.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/tree.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/tree.py

This is a minimal Python binding smoke script. It imports `libnvme`, creates `libnvme.nvme_root()`, and prints every host, subsystem, and controller reachable through the Python object model.

Behavior:
- Iterates `r.hosts()`.
- For each host, iterates `h.subsystems()`.
- For each subsystem, iterates `s.controllers()`.

Integration:
- Exercises generated/manual Python bindings enough to verify traversal methods are callable and printable.
- It depends on the runtime environment’s observable NVMe topology; on systems with no devices it may produce no topology output but still validates import/root creation.

Risk and maintenance notes:
- No assertions are present; this is diagnostic/smoke coverage rather than a strict unit test.
- Output depends on host state.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/tree.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/uriparser.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/uriparser.c

This file is a table-driven unit test for libnvme’s NVMe URI parser.

Core data:
- `struct test_data` stores an input URI plus expected parsed fields: scheme, host, user, protocol, port, path segments, query, and fragment.
- `test_data[]` covers valid URI forms.
- `test_data_bad[]` covers malformed strings expected to fail parsing.

Valid URI coverage includes:
- Basic `nvme://host` with optional trailing slash.
- TCP/RDMA protocol suffixes such as `nvme+tcp://...` and `nvme+rdma://...`.
- IPv4 and bracketed IPv6 hosts.
- Ports and absent ports.
- Path normalization with repeated slashes and trailing slashes.
- Query and fragment parsing, including ordering where `#fragment?query` treats `?query` as fragment content.
- Userinfo, including password-like `user:pass` and user strings containing bracketed IPv6-looking text.
- Percent-decoding in host, user, path, query, and fragment.

Test flow:
- `test_uriparser()` loops valid cases, calls `libnvmf_uri_parse()`, asserts every getter result, checks NULL path termination, frees via `libnvmf_uri_free()`, and prints OK.
- `test_uriparser_bad()` verifies malformed strings return failure and leave `parsed_data == NULL`.

Integration:
- Uses `<ccan/array_size/array_size.h>` for static table sizing.
- Uses public parser APIs: `libnvmf_uri_parse()`, `libnvmf_uri_get_scheme()`, `libnvmf_uri_get_protocol()`, `libnvmf_uri_get_host()`, `libnvmf_uri_get_port()`, `libnvmf_uri_get_path_segments()`, `libnvmf_uri_get_query()`, `libnvmf_uri_get_fragment()`, and `libnvmf_uri_free()`.
- Meson builds it only when fabrics support is enabled.

Risk and maintenance notes:
- The test relies on `assert()`, so compiling with `NDEBUG` would neuter validation.
- The fixed `path[7]` expectation array is sufficient for current cases but should be enlarged if deeper paths are added.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/uriparser.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/utils.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/utils.c

This file provides shared test log-buffer utilities.

Functions:
- `test_setup_log()` creates a temporary file with `tmpfile()` and exits via `err(EXIT_FAILURE, ...)` on failure.
- `test_close_log(FILE *fd)` closes the log file.
- `test_print_log_buf(FILE *logfd)` prints buffered log output only if `ftell(logfd)` indicates content exists. It rewinds, copies data to stdout in 4096-byte chunks, prints begin/end sentinels, rewinds again, and truncates the temp file with `ftruncate()`.

Integration:
- Used by libnvme tests that want to capture noisy library logs and display them only after failure or at selected checkpoints.
- Depends on POSIX `fileno()`/`ftruncate()`.

Risk and maintenance notes:
- `ftell(logfd)` errors are not separately handled; a negative value would be treated as nonzero.
- `fwrite()` partial writes are handled in a loop, but a zero-length write breaks without surfacing an error.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/utils.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/utils.h

This header declares common libnvme test utility functions:
- `FILE *test_setup_log(void);`
- `void test_print_log_buf(FILE *logfd);`
- `void test_close_log(FILE *fd);`

It uses `#pragma once` and includes `<stdio.h>` for `FILE`.

Integration:
- Paired with `utils.c`.
- Intended for tests with strict setup failure handling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/uuid.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/uuid.c

This file tests libnvme UUID formatting, parsing, and random UUID generation.

Coverage:
- `test_data[]` maps raw 16-byte UUID values to canonical lowercase string forms.
- `tostr_test()` calls `libnvme_uuid_to_string()` and compares against expected strings.
- `fromstr_test()` calls `libnvme_uuid_from_string()` and compares raw bytes.
- `random_uuid_test()` calls `libnvme_random_uuid()` twice, checks the values differ, converts both to strings, and prints them.

Helpers:
- `check_str()` reports string mismatches and sets global `test_rc`.
- `check_uuid()` reports byte mismatches in hex. It does not set `test_rc`, which looks like a minor test bug: a parse mismatch would print an error but not fail unless another error set `test_rc`.

Integration:
- Uses `NVME_UUID_LEN` and `NVME_UUID_LEN_STRING` from libnvme.
- Meson registers it as `libnvme - uuid`.

Risk and maintenance notes:
- Randomness equality check is probabilistic but practically safe for UUID-sized values.
- `check_uuid()` should set `test_rc = 1` on mismatch for strict failure semantics.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/zns.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/test/zns.c

This file is a hardware/topology-oriented ZNS diagnostic test. It scans the NVMe topology and prints Zoned Namespace properties for namespaces whose command set identifier is `NVME_CSI_ZNS`.

Core flow:
- `main()` creates a global context, calls `libnvme_scan_topology(ctx, NULL, NULL)`, tolerates `-ENOENT` and `-EACCES`, and walks hosts, subsystems, controllers, and namespaces.
- It checks both controller namespaces and subsystem namespaces.
- `show_zns_properties(libnvme_ns_t n)` obtains a transport handle, allocates a 4 KiB zone report buffer, issues ZNS identify namespace/controller commands, prints fields, issues report zones, prints `nr_zones`, and frees the buffer.

APIs used:
- Tree traversal macros: `libnvme_for_each_host`, `libnvme_for_each_subsystem`, `libnvme_subsystem_for_each_ctrl`, `libnvme_ctrl_for_each_ns`, `libnvme_subsystem_for_each_ns`.
- ZNS command initializers: `nvme_init_zns_identify_ns()`, `nvme_init_zns_identify_ctrl()`, `nvme_init_zns_report_zones()`.
- Passthrough executors: `libnvme_exec_admin_passthru()`, `libnvme_exec_io_passthru()`.
- Endian conversion helpers for ZNS fields.

Integration:
- Meson builds `test-zns`; it is not a pure unit test because it depends on system topology and permissions.

Risk and maintenance notes:
- The zone report allocation size is fixed at `0x1000`, enough for a small report but not exhaustive.
- Failures mostly print diagnostics and return from the per-namespace function rather than failing the program.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/test/zns.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/check-public-headers.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/tools/check-public-headers.py

This Python tool validates that every symbol exported in libnvme version scripts has a declaration/prototype in an installed public header.

Inputs:
- Preferred Meson mode: repeated `--ld FILE` and `--header FILE` arguments.
- Standalone mode: optional source root; auto-discovers `src/*.ld` and `src/nvme/*.h` excluding headers with `private` in the filename.

Algorithm:
- Parses `.ld` files line by line with `^\s+([a-z]\w+);` to collect exported symbol names.
- Parses headers with regex `\b([a-z_]\w+)\s*\(` to collect function-like identifiers.
- Reports any exported symbol missing from all installed headers.
- Exits 1 on errors; otherwise prints an OK count.

Integration:
- `libnvme/test/meson.build` registers it as `libnvme - check-public-headers`.
- Complements `check-public-symbols.py`: this tool checks ABI exports are declared for users.

Risk and maintenance notes:
- Regex parsing is intentionally lightweight. It may count macro invocations or comment text as declarations, though the libnvme/libnvmf namespace reduces practical false positives.
- Symbols not beginning with lowercase letters are ignored by the `.ld` parser.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/check-public-headers.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/check-public-symbols.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/tools/check-public-symbols.py

This Python tool checks consistency between `__libnvme_public` annotations in C sources and exported symbols in libnvme version scripts.

Inputs:
- Optional libnvme source root, defaulting to the parent of the script directory.
- Fixed version scripts: `libnvme.ld`, `libnvmf.ld`, `libnvme-mi.ld`, `accessors.ld`, and `accessors-fabrics.ld`.
- C sources from `src/nvme/*.c`.

Algorithm:
- Collects `.ld` entries using `^\s+([a-z]\w+);`.
- Collects public definitions using a multiline regex matching lines starting with `__libnvme_public` and extracting the last identifier before `(`.
- Reports:
  - public C definitions missing from all version scripts
  - version-script entries without a corresponding `__libnvme_public` definition
- Exits 1 on any mismatch.

Integration:
- Registered by Meson as `libnvme - check-public-symbols`.
- Protects against hidden ABI drift when compile-time visibility and linker version scripts disagree.

Risk and maintenance notes:
- Only scans top-level `src/nvme/*.c`; public definitions outside that glob would be missed.
- Requires `__libnvme_public` to appear at the start of a line.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/check-public-symbols.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/generator/generate-accessors.py -->
# File Research: sources/virtualization/nvme-cli/libnvme/tools/generator/generate-accessors.py

This is libnvme’s generator for struct accessors, lifecycle helpers, linker-script entries, SWIG fragments, and optional Python dict-field tables. It parses annotated C headers and emits committed generated files such as `accessors.h`, `accessors.c`, `accessors.ld`, `accessors.i`, and dict-table headers.

Annotation model:
- `// !generate-accessors[:read=MODE,write=MODE]` enables getter/setter generation for a struct. Modes are `generated`, `custom`, or `none`.
- `// !access:read=...,write=...` overrides member access modes.
- `const` members force `write=none`.
- `// !nested-accessors[:...]` marks helper structs whose fields can be flattened into parent accessors via `// !access:nested`.
- `// !generate-lifecycle` emits `struct_new()` and `struct_free()`.
- `// !lifecycle:none` excludes a member from destructor freeing.
- `// !default:VALUE` emits an init-defaults helper and default assignment logic.
- `// !generate-python[:alias=NAME]`, `// !python:none`, and `// !python:alias=NAME` drive SWIG output.
- `// !generate-dict-table` and `// !dict-table:none` drive field-offset table generation.

Parsing:
- Uses regexes for simple C struct bodies, char arrays, scalar arrays, generic members, and nested struct members.
- Supports:
  - dynamic `char *`
  - `char **` string arrays
  - fixed `char name[N]`
  - fixed scalar arrays
  - scalar value fields
  - selected integer/bool/string fields for dict tables
- Does not support typedef struct and is limited by `STRUCT_RE`, which matches `struct name { ... };` without nested braces.

Generated C/header behavior:
- Dynamic string setters free the old value and `strdup()` the new value or clear on NULL.
- Fixed char-array setters use `snprintf()` into the destination array.
- String-array setters deep-copy NULL-terminated arrays and free the previous array.
- Scalar setters assign directly.
- Scalar-array setters use `memcpy()`.
- Getters return stored values or pointers.
- Lifecycle constructors allocate zeroed structs, optionally call init-defaults, and return `-EINVAL`/`-ENOMEM` on setup errors.
- Destructors free owned `char *` and `char **` members, then free the struct.
- Linker output lists generated getters, setters, lifecycle functions, and default initializers under `LIBNVME_ACCESSORS_3`.

SWIG/Python behavior:
- Emits a `_nvme_guarded_setattr` helper to reject unknown Python attributes.
- Direct generated members appear as struct fields.
- Custom accessors are routed through `%extend` and `%rename` bridge macros.
- Read-only members emit `%immutable`.
- Nested flattened fields are excluded from SWIG direct struct output because SWIG cannot access dotted field paths as plain members.
- Detects Python alias collisions and invalid struct aliases before writing.

Dict-table behavior:
- Emits `struct fctx_field { const char *key; size_t off; }` arrays grouped by int, long, bool, and `char *`.
- Skips unsupported narrow scalars, arrays, const fields, structs, and complex pointers, warning unless explicitly silenced.

Main program:
- CLI options include `--h-out`, `--c-out`, `--ld-out`, `--swig-out`, `--dict-table-out`, `--nested-source`, `--prefix`, and `--verbose`.
- Expands globbed header inputs.
- Pass 1 collects nested-accessor structs across normal and nested-source headers.
- Pass 2 parses header structs and accumulates header/source/ld/SWIG fragments.
- Emits files with generated banners, include guards, forward declarations, and required includes.

Integration:
- `tools/generator/meson.build` invokes this through `update-accessors.sh`.
- Generated files are committed and checked for drift rather than regenerated during normal builds.

Risk and maintenance notes:
- Regex C parsing is adequate for the project’s annotated private headers but fragile for complicated declarations, preprocessor-heavy struct bodies, nested braces, function pointers, or unsupported pointer types.
- Fixed char-array setter generation does not guard NULL input; callers must not pass NULL for those setters.
- Dynamic string default initialization uses `strdup()` without checking allocation failure.
- The generator hardcodes the linker version section name `LIBNVME_ACCESSORS_3`; manual version-script policy is handled by the wrapper script.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/generator/generate-accessors.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/generator/meson.build -->
# File Research: sources/virtualization/nvme-cli/libnvme/tools/generator/meson.build

This Meson file defines developer-only targets for regenerating or checking generated accessor files.

Targets:
- `update-common-accessors` runs `update-accessors.sh` to generate common accessor outputs:
  - `src/nvme/accessors.h`
  - `src/nvme/accessors.c`
  - `src/accessors.ld`
  - SWIG output `libnvme/accessors.i`
  - dict table output `libnvme/fctx_field_tables.h`
  - input `src/nvme/private.h`
  - nested source `src/nvme/private-fabrics.h`
- `update-fabrics-accessors` does the same for fabrics-specific accessors:
  - `src/nvme/accessors-fabrics.h`
  - `src/nvme/accessors-fabrics.c`
  - `src/accessors-fabrics.ld`
  - SWIG output `libnvme/accessors-fabrics.i`
  - input `src/nvme/private-fabrics.h`
  - nested source `src/nvme/private.h`
- `alias_target('update-accessors', ...)` runs both.

Behavior:
- Uses `python3` and `generate-accessors.py`.
- Adds `--check` when Meson option `check-accessors` is enabled, making the wrapper read-only for CI drift checks.
- Targets are not build-by-default; developers run `meson compile -C <build-dir> update-accessors`.

Integration:
- Included from `libnvme/meson.build` before library source setup so generated code paths are known.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/generator/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/generator/update-accessors.sh -->
# File Research: sources/virtualization/nvme-cli/libnvme/tools/generator/update-accessors.sh

This shell wrapper runs `generate-accessors.py` and either updates generated source files or checks them for drift.

Inputs:
- Required positional args:
  - Python interpreter
  - generator script
  - output `.h`
  - output `.c`
  - output `.ld`
  - one or more input headers
- Optional:
  - `--check`
  - `--swig-out FILE`
  - `--dict-table-out FILE`

Workflow:
- Creates a temporary work directory and removes it on exit.
- Runs the Python generator into temporary `.h`, `.c`, `.ld`, optional `.i`, and optional dict-table files.
- In update mode:
  - `update_if_changed()` atomically replaces `.h`, `.c`, `.i`, and dict-table outputs only when content differs.
  - Does not update `.ld` automatically.
  - Calls `check_ld_drift()` and prints symbols to add/remove as maintainer guidance.
- In check mode:
  - `check_if_current()` compares generated temp files with committed outputs.
  - `check_ld_drift()` compares generated vs committed symbol lists.
  - Exits nonzero if any output is stale or `.ld` symbol list drift is detected.

Important helpers:
- `extract_syms()` extracts linker symbols with `grep`, `sed`, and `sort`.
- `check_ld_drift()` uses `comm` to report added/removed symbols.

Integration:
- Invoked by Meson run targets in `tools/generator/meson.build`.
- Supports CI via `-Dcheck-accessors=true`.

Risk and maintenance notes:
- `.ld` drift is intentionally manual because version-section labels require maintainer decisions.
- The script assumes common Unix tools including `realpath`, `grep`, `sed`, `sort`, and `comm`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/tools/generator/update-accessors.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/logging.c -->
# File Research: sources/virtualization/nvme-cli/logging.c

This file implements nvme-cli logging hooks for libnvme passthrough commands and NVMe-MI requests/responses.

Global state:
- `int log_level` controls verbosity.
- Static `struct submit_data sb` stores one command’s start/end timestamps.

Public functions:
- `is_printable_at_level(int level)` returns true when `log_level >= level` and CLI output format is `"normal"`.
- `map_log_level(int verbose, bool quiet)` maps CLI verbosity to libnvme levels: quiet or zero verbosity -> `LIBNVME_LOG_ERR`, one `-v` -> `LIBNVME_LOG_INFO`, higher -> `LIBNVME_LOG_DEBUG`.
- `nvme_submit_entry()` zeroes timing state and records start time at debug level.
- `nvme_submit_exit()` records end time and prints command fields, result, error, and latency at debug level.
- `nvme_decide_retry()` is intended as retry decision callback for passthrough errors.
- `nvme_mi_submit_entry()` prints NVMe-MI admin request fields and records timing at debug level.
- `nvme_mi_submit_exit()` prints NVMe-MI response result/status and latency at debug level.

Internal formatting:
- `nvme_show_common()` prints common `libnvme_passthru_cmd` fields.
- `nvme_show_command()` adds result and error.
- `nvme_show_latency()` prints elapsed microseconds.
- `nvme_show_req_admin()` converts an NVMe-MI admin request header into passthrough-like fields.
- `nvme_show_req()` and `nvme_show_resp()` switch on NVMe-MI message type and currently handle admin messages.

Integration:
- Includes `logging.h`, `util/sighdl.h`, and `nvme-print.h`.
- Uses global `nvme_args` for output format and retry settings.
- Uses libnvme and libnvme-mi callback signatures.

Risk and maintenance notes:
- `sb` is a single static object, so concurrent submissions would overwrite timing state.
- `nvme_decide_retry()` appears logically inconsistent: it returns false when retries are enabled (`!nvme_args.no_retries`) and its error condition cannot return true for either `-EAGAIN` or `-EINTR` as written. This deserves review if retry behavior matters.
- `nvme_log_retry(errno)` logs global `errno`, not necessarily the passed `err`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/logging.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/logging.h -->
# File Research: sources/virtualization/nvme-cli/logging.h

This header declares nvme-cli logging callbacks and verbosity helpers.

Exports:
- `extern int log_level;`
- `bool is_printable_at_level(int level);`
- `int map_log_level(int verbose, bool quiet);`
- libnvme passthrough callbacks:
  - `nvme_submit_entry()`
  - `nvme_submit_exit()`
  - `nvme_decide_retry()`
- NVMe-MI callbacks:
  - `nvme_mi_submit_entry()`
  - `nvme_mi_submit_exit()`

Macros:
- `print_info(...)` prints only when `LIBNVME_LOG_INFO` is printable.
- `print_debug(...)` prints only when `LIBNVME_LOG_DEBUG` is printable.

Integration:
- Forward declares libnvme transport and NVMe-MI types to avoid heavy includes.
- Includes `<nvme/lib.h>` for log-level constants and types such as `__u8`.

Risk and maintenance notes:
- The macros use `printf` but the header does not include `<stdio.h>` directly; users likely include it transitively.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/logging.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/meson.build -->
# File Research: sources/virtualization/nvme-cli/meson.build

This is the top-level Meson build definition for nvme-cli and bundled libnvme.

Project setup:
- Project name: `nvme-cli`, C language, Meson `>=0.62.0`.
- Version: `3.0-a.5`.
- Licenses: GPL-2.0-only for nvme-cli and LGPL-2.1-or-later for libnvme.
- Default options include GNU99, debugoptimized build, warning level 1, sysconfdir `etc`, and no fallback wraps.

Feature selection:
- Reads Meson options for `nvme`, `libnvme`, `fabrics`, `mi`, `python`, `tests`, `examples`, docs, and optional libraries.
- Disables fabrics/MI/tests/examples on Windows where needed.
- Python bindings require fabrics, libnvme, python dependency, SWIG, and `Python.h`; `-Dpython=enabled` forces libnvme enabled.

Version/config:
- Converts project version into a 2- or 3-component libnvme shared-object version.
- Uses major-only soname for PyPI builds.
- Generates `nvme-config.h` with feature and platform probes.
- Supports `version-tag` override or runs `scripts/meson-vcs-tag.sh`.

Dependency probing:
- json-c, liburing, libkmod, OpenSSL/LibreSSL compatibility, keyutils, dbus, threads, dl, bcrypt/kernel32 on Windows.
- Compiler/platform checks for endian, builtins, `typeof`, byteswap, `isblank`, `sys/random.h`, sed-opal headers, `tm_gmtoff`, fallthrough attribute, statement expressions, Linux MCTP, netdb, sendfile, mmap, reallocarray, and sigaction.

Build structure:
- Adds global C args: `-fomit-frame-pointer`, `-D_GNU_SOURCE`, and `-include <build>/nvme-config.h`.
- Adds special include path handling when nvme-cli links against a separately installed libnvme under a nonstandard prefix.
- Enters subdirs:
  - `ccan`
  - `libnvme`
  - `plugins` and `util` when building nvme executable
  - `unit`, optional `tests`, and `Documentation` under the executable path
- Builds `nvme` executable from core sources including `logging.c`, `nvme-cmds.c`, `nvme.c`, printing modules, plugin sources, util sources, optional `fabrics.c`, and optional JSON printer.

Install/configuration outputs:
- Configures and installs `discovery.conf`.
- Installs dracut rules, systemd units, udev rules, NetworkManager dispatcher scripts, shell completions, and generated spec file.
- Sets install directories from Meson options.

Testing:
- Adds `valgrind` and `asanubsan` test setups on non-Windows.
- `valgrind` setup uses project suppression file and optionally Python suppression file.

Summary:
- Prints paths, dependencies, selected features, and configuration values.

Integration with files in this group:
- Includes `logging.c` and `nvme-cmds.c` in the `nvme` executable source list.
- Enters `libnvme`, where accessor generator targets and libnvme tests are defined.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/meson_options.txt -->
# File Research: sources/virtualization/nvme-cli/meson_options.txt

This file defines configurable Meson options for nvme-cli/libnvme builds.

Feature options:
- `nvme`: build nvme executable, default enabled.
- `libnvme`: build libnvme library, default enabled.
- `fabrics`: NVMe-oF support, default enabled.
- `mi`: NVMe-MI support, default enabled.
- `python`: Python bindings, default auto.
- `json-c`, `libkmod`, `openssl`, `keyutils`, `liburing`, `libdbus`: optional dependency features.
- `tests`: build tests, default true.
- `nvme-tests`: run hardware tests, default false.
- `examples`: build examples, default true.

Documentation/install options:
- `docs`: combo of `false`, `html`, `man`, `rst`, `all`.
- `docs-build`: build documentation boolean.
- `htmldir`, `rstdir`, `dracutrulesdir`, `systemddir`, `udevrulesdir`, `nmdispatchdir`, `rundir`, and `systemctl`.

Behavioral/release options:
- `pdc-enabled`: default Persistent Discovery Controllers behavior.
- `version-tag`: override git version string.
- `pypi`: use short libnvme soname suitable for wheels.
- `check-accessors`: CI mode for accessor generator drift checks.

Plugin option:
- `plugins` is an array with a fixed list of vendor/feature plugins. If unset, all plugins are included; `[]` means no plugins.

Integration:
- Consumed throughout top-level and subdir Meson files to decide dependencies, sources, generated checks, tests, and install outputs.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/meson_options.txt -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-builtin.h -->
# File Research: sources/virtualization/nvme-cli/nvme-builtin.h

This header defines the nvme-cli built-in command table through the project’s command macro system.

Structure:
- Sets `CMD_INC_FILE nvme-builtin`.
- Includes `cmd.h`.
- Expands `COMMAND_LIST(...)` containing many `ENTRY(command-name, description, function[, alias])` declarations.
- Includes `define_cmd.h` after the list, allowing the command framework to generate declarations/dispatch structures depending on macro context.

Command categories represented:
- Device/topology: `list`, `list-subsys`, `show-topology`, `top`.
- Identify/list commands: controller, namespace, UUID, IOCS, domains, endurance groups, etc.
- Namespace management: create/delete/attach/detach/get ns id.
- Logs: telemetry, firmware, SMART, ANA, errors, effects, endurance, persistent event, reservation, boot partition, power, host discovery, AVE, and many newer log pages.
- Features/properties: get/set feature/property.
- Firmware and passthrough: fw commit/download, admin/io passthru, security send/recv.
- I/O commands: flush, compare, read, write, write zeroes, write uncorrectable, verify, copy, DSM.
- Maintenance: sanitize, reset, subsystem reset, rescan, registers.
- Fabrics commands under `CONFIG_FABRICS`: discover, connect, disconnect, config, DIM.
- Host/security key helpers: host NQN, DHCHAP, TLS key operations.
- Misc: directives, virtual management, RPMB, lockdown, I/O management.
- NVMe-MI commands under `CONFIG_MI`: `nvme-mi-recv`, `nvme-mi-send`.

Integration:
- Central registry for command dispatch and help generation.
- Conditional entries track build-time feature macros generated from Meson config.

Risk and maintenance notes:
- Adding a command requires consistency between this table, implementation function names, help text, and feature guards.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-builtin.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-cmds.c -->
# File Research: sources/virtualization/nvme-cli/nvme-cmds.c

This file provides small nvme-cli command helper wrappers for namespace attachment and detachment.

Core helper:
- `nvme_ns_attachment(struct libnvme_transport_handle *hdl, bool ish, __u32 nsid, __u16 num_ctrls, __u16 *ctrlist, bool attach)`
  - Creates `struct nvme_ctrl_list cntlist`.
  - Initializes it with `nvme_init_ctrl_list()`.
  - If `ish` and the handle is an MI handle, calls `nvme_init_mi_cmd_flags(&cmd, ish)`.
  - Initializes either attach or detach command:
    - `nvme_init_ns_attach_ctrls()`
    - `nvme_init_ns_detach_ctrls()`
  - Executes via `libnvme_exec_admin_passthru()`.

Public wrappers:
- `nvme_namespace_attach_ctrls(...)`
- `nvme_namespace_detach_ctrls(...)`

Integration:
- Included in the nvme executable source list.
- Declared by `nvme-cmds.h`.
- Bridges CLI code to libnvme command initializer/executor APIs.

Risk and maintenance notes:
- `cmd` is not explicitly zero-initialized before possible `nvme_init_mi_cmd_flags()` and attach/detach initializer calls. Correctness depends on those initializers fully setting required fields or tolerating prior state.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-cmds.c -->