# subset-b-000192 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default-old-format.json -->
# sources/cloud-native/moby/daemon/pkg/oci/fixtures/default-old-format.json

## Purpose
Provides a legacy Docker seccomp fixture for validating that the seccomp loader still accepts the old per-syscall profile format. It defaults to `SCMP_ACT_ERRNO`, declares an `architectures` array instead of the newer `archMap`, and lists 311 individual syscall entries with `name`, `action`, and optional `args`.

## Important APIs, Types, And Functions
The file is data-only but its schema is consumed by `github.com/moby/profiles/seccomp.LoadProfile`. The most important fields are `defaultAction`, `architectures`, and `syscalls[].name/action/args`.

## Control Flow
Runtime code reads this JSON as a string and passes it into the seccomp profile parser. The parser expands each syscall entry into OCI Linux seccomp rules for a default Linux spec.

## State, Dependencies, And Integration Points
No state is persisted. It depends on the historical Docker seccomp JSON shape and integrates with `seccomp_test.go` to prevent compatibility regressions.

## Risks And Test Signals
The risk is silent removal of old-profile support. `TestSeccompLoadProfile` is the direct signal: this fixture must parse without error on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default-old-format.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default.json -->
# sources/cloud-native/moby/daemon/pkg/oci/fixtures/default.json

## Purpose
Provides the current default seccomp fixture used to verify profile loading. It defaults to `SCMP_ACT_ERRNO`, uses the newer `archMap` form with seven architecture mappings, and groups allowed syscalls into 26 rule blocks with include/exclude conditions.

## Important APIs, Types, And Functions
This is data consumed by `seccomp.LoadProfile`. Its important fields are `defaultAction`, `archMap`, `syscalls[].names`, `syscalls[].action`, `syscalls[].args`, and optional `includes`/`excludes` filters such as kernel-version or architecture gates.

## Control Flow
The test reads the full file from `fixtures/default.json`, initializes `DefaultLinuxSpec()`, and asks the profile loader to transform the JSON into the spec's seccomp configuration.

## State, Dependencies, And Integration Points
No local state. It depends on libseccomp action/operator naming and the Moby profiles package. It is the realistic fixture for daemon default seccomp behavior.

## Risks And Test Signals
Large grouped syscall lists make accidental syntax or schema drift easy. `TestSeccompLoadProfile` confirms parser compatibility but does not assert individual syscall semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/example.json -->
# sources/cloud-native/moby/daemon/pkg/oci/fixtures/example.json

## Purpose
Provides a minimal seccomp fixture for parser coverage. It denies by default and allows only `clone` with a masked argument comparison plus `open` and `close`.

## Important APIs, Types, And Functions
The relevant fields are `defaultAction`, `syscalls[].name`, `syscalls[].action`, and `syscalls[].args[]` with `SCMP_CMP_MASKED_EQ`.

## Control Flow
`seccomp_test.go` loads the file into a default OCI Linux spec through `seccomp.LoadProfile`. The short profile validates the older single-`name` syscall schema and argument comparator parsing.

## State, Dependencies, And Integration Points
No state is changed. The fixture integrates with Moby's seccomp loader tests and complements the large default fixtures by making comparator coverage easy to inspect.

## Risks And Test Signals
It is intentionally too small to represent production policy. Passing `TestSeccompLoadProfile/example.json` signals only that the minimal schema and masked comparator are accepted.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/example.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fuzz_test.go -->
# sources/cloud-native/moby/daemon/pkg/oci/fuzz_test.go

## Purpose
Fuzzes `AppendDevicePermissionsFromCgroupRules` so arbitrary pre-existing OCI device cgroup entries and arbitrary rule strings cannot panic the parser.

## Important APIs, Types, And Functions
`FuzzAppendDevicePermissionsFromCgroupRules` uses `github.com/AdaLogics/go-fuzz-headers` to generate up to 40 `specs.LinuxDeviceCgroup` records and a string slice of rules before invoking the target function.

## Control Flow
The fuzz function consumes bytes into a count, generated structs, and generated rule strings. If generation fails it returns early; otherwise it discards the target function's output and error.

## State, Dependencies, And Integration Points
No persisted state. It depends on Go fuzzing, `go-fuzz-headers`, and the OCI runtime-spec type definitions. It directly protects daemon device-cgroup rule parsing.

## Risks And Test Signals
The fuzz target checks crash safety, not semantic correctness. Unit tests in `oci_test.go` provide deterministic validation; fuzzing adds malformed aggregate input coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/namespaces.go -->
# sources/cloud-native/moby/daemon/pkg/oci/namespaces.go

## Purpose
Provides small helpers for editing and querying namespace entries in an OCI runtime spec.

## Important APIs, Types, And Functions
`RemoveNamespace(*specs.Spec, specs.LinuxNamespaceType)` removes the first namespace of a requested type if `s.Linux` exists. `NamespacePath(*specs.Spec, specs.LinuxNamespaceType)` returns the first matching namespace path and a boolean.

## Control Flow
Both functions linearly scan `s.Linux.Namespaces`. Removal rewrites the slice with `append(slice[:i], slice[i+1:]...)` and stops after the first match.

## State, Dependencies, And Integration Points
They mutate only the provided spec in memory and depend on `github.com/opencontainers/runtime-spec/specs-go`. Plugin spec generation uses `RemoveNamespace` when plugins request host network, PID, or IPC namespaces.

## Risks And Test Signals
`NamespacePath` assumes `s.Linux` is non-nil and would panic otherwise, unlike `RemoveNamespace`. No direct tests are in this subset; integration coverage comes through plugin spec creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/namespaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci.go -->
# sources/cloud-native/moby/daemon/pkg/oci/oci.go

## Purpose
Parses Docker daemon device-cgroup rule strings into OCI `LinuxDeviceCgroup` entries and appends them to an existing permission list.

## Important APIs, Types, And Functions
`deviceCgroupRuleRegex` accepts exact strings of form `([acb]) ([0-9]+|*):([0-9]+|*) ([rwm]{1,3})`. `AppendDevicePermissionsFromCgroupRules` returns a new slice or a format/parse error.

## Control Flow
For each rule, the regex must produce five groups. The function creates an allow entry, maps wildcard major/minor to `-1` pointers, parses numeric values as signed 64-bit integers, sets access bits from the rule, and appends to the input slice.

## State, Dependencies, And Integration Points
No persistence. It depends on Moby's lazy regexp helper, `strconv`, and OCI runtime-spec types. It feeds OCI specs used by container runtimes.

## Risks And Test Signals
The regex is strict about single spaces and does not deduplicate or sort permission letters. The TODO notes uncertainty around `a` all-device syntax. `oci_test.go` and the fuzz target cover syntax, overflow, wildcard, and permission cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci_test.go -->
# sources/cloud-native/moby/daemon/pkg/oci/oci_test.go

## Purpose
Provides deterministic unit coverage for device-cgroup rule parsing.

## Important APIs, Types, And Functions
`TestAppendDevicePermissionsFromCgroupRules` table-drives calls to `AppendDevicePermissionsFromCgroupRules`. It uses `gotest.tools/v3/assert` and compares full `specs.LinuxDeviceCgroup` structs, including major/minor pointers.

## Control Flow
Each subtest calls the parser with one rule. Error cases assert exact error messages; success cases assert a one-entry result slice.

## State, Dependencies, And Integration Points
No state. It depends on the OCI runtime spec package and forms the main regression suite for daemon `--device-cgroup-rule` conversion.

## Risks And Test Signals
The test exercises invalid whitespace, unknown device types, missing colon, non-numeric and negative numbers, overflow, wildcards, all/char/block types, and access strings. It does not cover multiple rules in one call or all permutations of repeated access letters.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/seccomp_test.go -->
# sources/cloud-native/moby/daemon/pkg/oci/seccomp_test.go

## Purpose
Linux-only test coverage for loading bundled seccomp profiles into a default OCI Linux spec.

## Important APIs, Types, And Functions
`TestSeccompLoadProfile` reads `default.json`, `default-old-format.json`, and `example.json` and calls `seccomp.LoadProfile`. `TestSeccompLoadDefaultProfile` marshals `seccomp.DefaultProfile()` and loads it the same way.

## Control Flow
Each test creates `rs := DefaultLinuxSpec()` and treats any read, marshal, or load error as fatal.

## State, Dependencies, And Integration Points
No persisted state. It depends on Linux build tags, local fixture files, Moby's profiles/seccomp package, and OCI default-spec creation.

## Risks And Test Signals
The tests validate parse/load compatibility but not the exact generated syscall allowlist. They catch schema regressions, fixture syntax errors, and mismatches between default-profile generation and the loader.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/seccomp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools.go -->
# sources/cloud-native/moby/daemon/pkg/opts/address_pools.go

## Purpose
Implements a flag/JSON value for daemon default address pools used by libnetwork IPAM.

## Important APIs, Types, And Functions
`PoolsOpt` holds `[]*ipamutils.NetworkToSplit`. `UnmarshalJSON` decodes directly into `Values`. `Set` parses CSV fields with keys `base` and `size`; `Type`, `String`, `Value`, and `Name` support flag/config plumbing.

## Control Flow
`Set` reads one CSV record, lowercases each field, splits on `=`, parses `base` as `netip.Prefix` and `size` as integer, rejects unknown keys, and appends a `NetworkToSplit`.

## State, Dependencies, And Integration Points
State is in-memory `Values`. It depends on `encoding/csv`, `net/netip`, and daemon libnetwork `ipamutils`. The daemon config layer consumes the parsed pools.

## Risks And Test Signals
Case-insensitive keys are a documented TODO. `Set` permits missing base or size until later consumers validate semantics. The test covers one valid definition and an invalid combined string.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/address_pools_test.go

## Purpose
Exercises basic `PoolsOpt.Set` behavior for daemon default address-pool flag input.

## Important APIs, Types, And Functions
`TestAddressPoolOpt` instantiates `PoolsOpt`, calls `Set` with `base=175.30.0.0/16,size=16`, then verifies a malformed multi-pool string returns an error.

## Control Flow
The test fails immediately on unexpected error from valid input and fails if invalid input is accepted.

## State, Dependencies, And Integration Points
No external state. It targets the address-pool parser used by daemon config and libnetwork setup.

## Risks And Test Signals
Coverage is shallow: it does not inspect parsed `Base`/`Size`, JSON decoding, missing keys, unknown keys, IPv6, or String/Value output. Its signal is mainly that CSV parsing rejects a common malformed comma-separated pair sequence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/env.go -->
# sources/cloud-native/moby/daemon/pkg/opts/env.go

## Purpose
Validates and normalizes environment-variable flag entries while intentionally leaving variable-name syntax mostly to the container workload.

## Important APIs, Types, And Functions
`ValidateEnv(val string) (string, error)` is the exported validator. It uses `strings.Cut` to detect `KEY=VALUE` and `os.LookupEnv` to fill values for bare names.

## Control Flow
If the key before `=` is empty, the function returns an invalid-variable error. If `=` is present, it returns the original string. If no `=`, it looks up the key in the current process environment and returns `KEY=value` only when present; otherwise it returns the original bare key.

## State, Dependencies, And Integration Points
Reads process environment but persists nothing. It integrates with Docker CLI/daemon option parsing for `--env`-style values.

## Risks And Test Signals
Host environment affects bare-key normalization. The intentionally permissive name policy accepts spaces, digits, and punctuation. `env_test.go` covers explicit empty-name failures and PATH lookup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/env_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/env_test.go

## Purpose
Tests `ValidateEnv` compatibility with Docker's permissive environment-variable handling.

## Important APIs, Types, And Functions
`TestValidateEnv` table-drives values through `ValidateEnv`, using `gotest.tools/v3/assert` for exact output and error matching.

## Control Flow
The test enumerates bare names, explicit assignments, values containing `=`, spaces, unusual names, empty-name inputs, and PATH lookup. On Windows it adds a case-insensitive environment lookup case for `PaTh`.

## State, Dependencies, And Integration Points
The test reads the actual test-process `PATH`; this makes the expected result environment-dependent but deterministic within the process. It validates daemon option behavior rather than container runtime behavior.

## Risks And Test Signals
It confirms empty keys are rejected and nearly everything else is preserved. It does not isolate environment mutations, so future tests changing PATH could affect expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/env_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts.go

## Purpose
Parses, validates, and normalizes daemon listener host addresses and extra-host entries.

## Important APIs, Types, And Functions
Constants define default ports, sockets, named pipe, and `HostGatewayName`. `ValidateHost`, `ParseDaemonHost`, `ParseTCPAddr`, `parseTCPAddr`, `parseSimpleProtoAddr`, and `ValidateExtraHost` are the core functions.

## Control Flow
`ParseDaemonHost` infers `tcp` when no scheme is present, dispatches to protocol-specific parsing, accepts `fd://` as-is, and rejects unknown protocols. TCP parsing validates URL scheme/path/port and fills missing host or port from a strict default. Extra-host validation splits on the first colon and validates IP unless the value is `host-gateway`.

## State, Dependencies, And Integration Points
No persistence. It depends on `net`, `net/url`, and the broader `opts.ValidateIPAddress`. It feeds daemon `-H` listener configuration and container host aliases.

## Risks And Test Signals
`ValidateHost` returns the original untrimmed value for later TLS handling. TCP ports are only parsed for numeric syntax and zero, so very large integers may pass. `hosts_test.go` provides broad edge-case coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts_test.go

## Purpose
Regression-tests daemon host parsing and `--add-host` validation.

## Important APIs, Types, And Functions
`TestParseDockerDaemonHost` covers full protocol dispatch. `TestParseTCP` isolates TCP default filling and validation. `TestValidateExtraHosts` checks host-to-IP strings.

## Control Flow
Tests are map/table-driven: invalid inputs assert exact error strings and empty address output; valid inputs assert normalized address strings. Extra-host tests verify valid IPv4/IPv6 examples and error substrings for invalid forms.

## State, Dependencies, And Integration Points
No external state. Expected outputs depend on platform constants such as `DefaultHTTPHost`, so Unix and Windows builds differ through companion files.

## Risks And Test Signals
Map iteration order is irrelevant but exact error strings are brittle against Go URL parser wording. Coverage is strong for common daemon bind address confusion, IPv6 brackets, paths, unsupported schemes, and host-gateway-adjacent validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_unix.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts_unix.go

## Purpose
Provides Unix/non-Windows defaults for daemon host parsing.

## Important APIs, Types, And Functions
`DefaultHTTPHost` is `localhost`. `DefaultHost` is `unix://` plus `DefaultUnixSocket`.

## Control Flow
There is no executable flow; build tags select this file on non-Windows platforms.

## State, Dependencies, And Integration Points
No state. The constants are consumed by `hosts.go`, daemon defaults, and tests that normalize TCP and Unix listener addresses.

## Risks And Test Signals
The behavior differs from Windows, especially default listener transport and TCP host. `hosts_test.go` indirectly validates the constants in expected output strings under non-Windows builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_windows.go -->
# sources/cloud-native/moby/daemon/pkg/opts/hosts_windows.go

## Purpose
Provides Windows-specific daemon host defaults and documents the historical reason for using `127.0.0.1` instead of `localhost` for TCP defaults.

## Important APIs, Types, And Functions
`DefaultHTTPHost` is `127.0.0.1`. `DefaultHost` is `npipe://` plus `DefaultNamedPipe`.

## Control Flow
No functions execute. The Go build selects this file on Windows.

## State, Dependencies, And Integration Points
No state. These constants affect `ParseDaemonHost`, daemon startup defaults, and Windows client/daemon local connection behavior.

## Risks And Test Signals
The long comment records a DNS delay workaround; changing the constant can reintroduce local Windows connection latency. Host parser tests validate expected normalization under Windows builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/hosts_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts.go -->
# sources/cloud-native/moby/daemon/pkg/opts/nri_opts.go

## Purpose
Parses daemon NRI configuration from JSON and command-line flag values.

## Important APIs, Types, And Functions
`NRIOpts` contains `Enable`, `PluginPath`, `PluginConfigPath`, and `SocketPath`. `UnmarshalJSON` rejects unknown fields. `NamedNRIOpts` implements `Set`, `Type`, `String`, and `Name`.

## Control Flow
JSON decoding uses `DisallowUnknownFields`. CLI parsing reads one CSV record, splits each field at `=`, treats bare `enable` as `enable=true`, parses booleans with `strconv.ParseBool`, stores path strings, and rejects unknown keys.

## State, Dependencies, And Integration Points
State is the referenced `NRIOpts` struct. It integrates with daemon config/flags for Node Resource Interface support.

## Risks And Test Signals
Path values are accepted without filesystem validation. CSV parsing supports quoted commas but a missing `=` for path keys silently sets an empty path. Tests cover JSON strictness, CLI booleans, path serialization, and unknown keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/nri_opts_test.go

## Purpose
Verifies JSON and command-line parsing for daemon NRI options.

## Important APIs, Types, And Functions
`TestNRIOptsJSON` directly invokes `NRIOpts.UnmarshalJSON`. `TestNRIOptsCmd` uses `NewNamedNRIOptsRef`, `Set`, and `String`.

## Control Flow
JSON tests compare decoded structs and assert unknown-field errors. Command tests set CLI strings and compare expected struct fields plus serialized output; bare `enable` is expected to mean true.

## State, Dependencies, And Integration Points
No external state. The tests protect daemon config parsing for NRI enablement and path settings.

## Risks And Test Signals
They do not cover invalid boolean strings, quoted CSV, duplicate keys, or empty path semantics. They strongly signal that unknown JSON and CLI keys must be rejected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/nri_opts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts.go -->
# sources/cloud-native/moby/daemon/pkg/opts/opts.go

## Purpose
Centralizes generic flag value containers and validators used by Docker daemon configuration.

## Important APIs, Types, And Functions
`ListOpts`, `MapOpts`, `MapMapOpts`, and named wrappers implement pflag-style behavior. Validators include `ValidateIPAddress`, `ValidateDNSSearch`, `ValidateLabel`, `ValidateSingleGenericResource`, `ParseLink`, and `MemBytes` JSON/flag parsing.

## Control Flow
List and map setters optionally call validators before appending or storing values. DNS validation trims spaces and uses lazy regexps. Label validation requires `=` and blocks reserved Docker namespaces. `ParseLink` handles `name:alias`, short format, and legacy `/container:/path/alias`. `MemBytes` delegates to `go-units`.

## State, Dependencies, And Integration Points
State is held in referenced slices/maps. It depends on `netip`, regex helpers, `go-units`, and standard string/path utilities. Many daemon flags compose these primitives.

## Risks And Test Signals
Map iteration makes String output order unstable. Validators are intentionally permissive in some places. `opts_test.go` covers major value-container behavior and validator edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/opts_test.go

## Purpose
Tests generic option containers and validators in `opts.go`.

## Important APIs, Types, And Functions
Tests cover `ValidateIPAddress`, `MapOpts`, `ListOpts`, `ValidateDNSSearch`, `ValidateLabel`, named wrappers, `ParseLink`, and `MapMapOpts`.

## Control Flow
Table-driven validators assert normalized output or exact errors. Container tests mutate shared slices/maps and inspect length, lookup, deletion, and nested key assignment.

## State, Dependencies, And Integration Points
No persistent state. It depends on `gotest.tools` assertions and protects shared daemon flag infrastructure.

## Risks And Test Signals
The tests explicitly allow duplicate list values and check map de-duplication through `GetMap`. They cover reserved label namespaces, IPv6 normalization, DNS length/shape, legacy link parsing, validator invocation, and nested map syntax. `MemBytes` is not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/opts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/runtime.go -->
# sources/cloud-native/moby/daemon/pkg/opts/runtime.go

## Purpose
Parses named OCI runtime definitions from daemon configuration.

## Important APIs, Types, And Functions
`RuntimeOpt` stores an option name, stock runtime name, and `map[string]system.Runtime`. `NewNamedRuntimeOpt`, `Set`, `String`, `GetMap`, `Type`, and `Name` implement option behavior.

## Control Flow
`Set` requires `name=path`, trims spaces, rejects empty name/path, lowercases the name, rejects the reserved stock runtime name, rejects duplicates, and stores `system.Runtime{Path: path}`.

## State, Dependencies, And Integration Points
State is the referenced runtime map. It depends on Docker API `system.Runtime`. The daemon runtime selection path consumes this map.

## Risks And Test Signals
Lowercasing and trimming are TODO-marked compatibility behaviors that may accept surprising input. No direct test in this subset covers runtime parsing, so regressions rely on broader daemon config tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/runtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit.go -->
# sources/cloud-native/moby/daemon/pkg/opts/ulimit.go

## Purpose
Implements pflag/config parsing for default container ulimit settings.

## Important APIs, Types, And Functions
`UlimitOpt` wraps `map[string]*container.Ulimit`; `Set` uses `units.ParseUlimit`; `String` and `GetList` expose values. `NamedUlimitOpt` adds a config field name.

## Control Flow
Setting a value parses the `name=soft:hard` string, then stores it by ulimit name, replacing any prior entry. Listing and stringification iterate the map.

## State, Dependencies, And Integration Points
State is an in-memory map referenced from daemon config. Dependencies are Docker API container types and `docker/go-units`. Defaults are later applied to container host config/resource limits.

## Risks And Test Signals
Map iteration order is unstable; tests allow two expected string orders. Pointer-valued map entries can be mutated by callers. `ulimit_test.go` covers valid append, invalid type rejection, String, and GetList.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/ulimit_test.go

## Purpose
Verifies `UlimitOpt` parsing and exported views.

## Important APIs, Types, And Functions
`TestUlimitOpt` initializes a map with `nofile`, constructs `NewUlimitOpt`, calls `Set`, `String`, and `GetList`.

## Control Flow
The test checks initial stringification, adds a valid `core=1024:1024`, verifies an invalid ulimit type errors, accepts either map iteration order in String output, and expects two list entries.

## State, Dependencies, And Integration Points
No external state. It depends on `container.Ulimit` and `go-units` validation behavior.

## Risks And Test Signals
It does not assert the contents of `GetList` beyond length, but it catches common regressions in parsing, map replacement, and invalid ulimit-name validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/backend_linux.go

## Purpose
Implements the Linux plugin backend exposed to daemon API operations: enable/disable, inspect, privileges, pull, upgrade, list, push, remove, set, and create-from-context.

## Important APIs, Types, And Functions
Key functions include `Disable`, `Enable`, `Inspect`, `computePrivileges`, `Privileges`, `Upgrade`, `Pull`, `List`, `Push`, `buildManifest`, `getManifestDescriptor`, `writeManifest`, `Remove`, `Set`, `CreateFromContext`, `splitConfigRootFSFromTar`, and `atomicRemoveAll`.

## Control Flow
Remote install flows fetch plugin content into the content store, apply rootfs layers to a temp directory, validate required privileges, and create or upgrade an on-disk plugin directory. Push builds or reuses a Docker schema2-style manifest, streams progress, and retries HTTP fallback. Create-from-context splits `config.json` and `rootfs/` from an uploaded tar, stores blobs, writes a manifest, and creates the plugin.

## State, Dependencies, And Integration Points
Persists plugin rootfs/config under manager root and blobs under the content store. It integrates with registry auth/resolvers, daemon filters, progress streams, pubsub events, authorization middleware, containerfs cleanup, and mount unmounting.

## Risks And Test Signals
Privilege validation is central to security. TODOs note incomplete config validation and layer media-type assumptions. Removal uses rename-to-`-removing` for crash recovery. Tests cover atomic removal; broader plugin integration tests cover lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/backend_linux_test.go

## Purpose
Tests `atomicRemoveAll`, the plugin directory removal helper used by Linux backend removal and cleanup recovery.

## Important APIs, Types, And Functions
`TestAtomicRemoveAllNormal`, `TestAtomicRemoveAllAlreadyExists`, and `TestAtomicRemoveAllNotExist` exercise rename-and-remove behavior.

## Control Flow
Each test creates temporary directories, calls `atomicRemoveAll`, then asserts both the original directory and `-removing` path are absent.

## State, Dependencies, And Integration Points
State is limited to temporary directories. It validates the cleanup pattern used by plugin removal and daemon reload cleanup of interrupted removals.

## Risks And Test Signals
The tests do not simulate permission errors, mount points, or rollback on failed `EnsureRemoveAll`, but they cover normal, pre-existing marker, and missing-origin cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_unsupported.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/backend_unsupported.go

## Purpose
Provides non-Linux stubs for plugin backend API methods on platforms that do not support managed plugins.

## Important APIs, Types, And Functions
Defines `errNotSupported` and stubs for `Disable`, `Enable`, `Inspect`, `Privileges`, `Pull`, `Upgrade`, `List`, `Push`, `Remove`, `Set`, and `CreateFromContext`.

## Control Flow
Every method immediately returns `errNotSupported` or nil result plus that error.

## State, Dependencies, And Integration Points
No state. Build tags select this file for `!linux`, preserving API compatibility for daemon builds while disabling functionality.

## Risks And Test Signals
Callers must handle unsupported errors consistently. The file prevents accidental Linux-only dependency leakage into unsupported builds; platform compile tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/defs.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/defs.go

## Purpose
Defines shared plugin store state and option hooks used by the plugin manager and daemon subsystems.

## Important APIs, Types, And Functions
`Store` holds plugins, runtime spec modifiers, and legacy handlers under an RW mutex. `NewStore` initializes maps. `SpecOpt`, `CreateOpt`, `WithSwarmService`, `WithEnv`, and `WithSpecMounts` provide extension points.

## Control Flow
`WithEnv` builds effective environment values from configured defaults and user-provided `key=value` entries, then stores de-duplicated settings. `WithSpecMounts` appends mounts to an OCI spec when invoked.

## State, Dependencies, And Integration Points
Store is the in-memory plugin inventory; plugin config persists elsewhere through manager save. Hooks integrate managed plugins with swarm, env overrides, runtime spec customization, and legacy plugin handlers.

## Risks And Test Signals
`WithEnv` uses map iteration, so environment order is unstable. Invalid env lines are ignored. Store concurrency relies on callers using the provided locks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/defs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/errors.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/errors.go

## Purpose
Defines typed plugin errors that map to Docker API error classes.

## Important APIs, Types, And Functions
Error types include `errNotFound`, `errAmbiguous`, `errDisabled`, `inUseError`, `enabledError`, and `alreadyExistsError`. Marker methods implement `NotFound`, `InvalidParameter`, or `Conflict`.

## Control Flow
Each type formats an error string and marker methods are no-op interfaces used by error classification.

## State, Dependencies, And Integration Points
No state. These errors flow through plugin manager operations and API handlers for correct HTTP/status classification.

## Risks And Test Signals
String wording can affect tests or clients that compare messages, but the main contract is marker-interface behavior. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/events.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/events.go

## Purpose
Provides structured plugin manager events and subscription filtering for create, remove, disable, and enable operations.

## Important APIs, Types, And Functions
`Event` requires `matches`. Event types are `EventCreate`, `EventRemove`, `EventDisable`, and `EventEnable`. `Manager.SubscribeEvents` returns a channel and cancellation function.

## Control Flow
Event matchers compare event type and plugin ID; create events optionally filter by capability interface using OR logic. Subscription builds a pubsub topic function that panics on non-Event payloads and evicts the channel on cancel.

## State, Dependencies, And Integration Points
State lives in the manager's pubsub publisher. Events are published by backend lifecycle methods and consumed by subsystems waiting for plugin availability/removal.

## Risks And Test Signals
Subscribers must call cancel to avoid leaks. The type panic enforces internal publisher discipline. No direct tests in this subset cover event matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/fetch_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/fetch_linux.go

## Purpose
Implements Linux plugin image fetch, metadata capture, layer extraction, and progress reporting.

## Important APIs, Types, And Functions
Key pieces are `setupProgressOutput`, `Manager.fetch`, `applyLayer`, `childrenHandler`, `fetchMeta`, `storeFetchMetadata`, `validateFetchedMetadata`, and `withFetchProgress`.

## Control Flow
Fetch normalizes the reference, sets plugin-specific auth scope and media-type prefix, resolves and fetches content through containerd handlers, and falls back to older Accept headers when resolution fails. Handlers record config/manifest/layer digests, skip plugin config children, apply layers to rootfs, and stream layer status from the content store.

## State, Dependencies, And Integration Points
Writes fetched blobs to `pm.blobStore` and extracts rootfs files into caller-provided directories. It depends on containerd remotes/content/images, Moby progress utilities, chrootarchive, registry auth, and OCI descriptors.

## Risks And Test Signals
A TODO notes multi-layer extraction order risk. Progress goroutines use context cancellation carefully but are timing-sensitive. Backend pull/upgrade/create flows are integration signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/fetch_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager.go

## Purpose
Defines the core plugin manager: configuration, executor abstraction, persisted plugin reload, event handling, saving, garbage collection, logging streams, and privilege comparison.

## Important APIs, Types, And Functions
Important items are `Executor`, `EndpointResolver`, `ManagerConfig`, `Manager`, `controller`, `NewManager`, `HandleExitEvent`, `reload`, `loadPlugin`, `save`, `GC`, `makeLoggerStreams`, `validatePrivileges`, and `normalizePrivileges`.

## Control Flow
`NewManager` creates root/exec/tmp directories, creates an executor and local content store, reloads saved plugin directories, and initializes pubsub. Reload scans full 64-character IDs, loads `config.json`, restores enabled plugins, migrates propagated mounts, saves updated state, and may re-enable when live restore is off. Exit events remove exec bundles, close exit channels, restart or unmount, and GC removes unused blobs.

## State, Dependencies, And Integration Points
Persists plugin JSON under manager root and blob content under `storage`. Integrates with containerd local content store, runtime executors, Docker events, authorization, pubsub, and atomic writer.

## Risks And Test Signals
Reload and exit handling are concurrency-sensitive. Privilege comparison sorts names and values for order-insensitivity. Tests cover privilege comparison and Linux restore/remove paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_linux.go

## Purpose
Implements Linux-specific plugin lifecycle operations around OCI spec creation, executor start/restore/signal, propagated mounts, rootfs setup, shutdown, upgrade, and creation.

## Important APIs, Types, And Functions
Key functions are `enable`, `pluginPostStart`, `restore`, `shutdownPlugin`, `disable`, `Shutdown`, `upgradePlugin`, `setupNewPlugin`, `createPlugin`, and `recursiveUnmount`.

## Control Flow
Enable sets rootfs, builds the plugin OCI spec, records restart control, prepares propagated mount and init layer, invokes the executor, then dials the plugin socket before marking it enabled and calling handlers. Restore either reattaches or restarts depending on live-restore state. Shutdown sends SIGTERM then SIGKILL after timeout. Upgrade backs up rootfs, installs new rootfs/config, and rolls back on failure.

## State, Dependencies, And Integration Points
Mutates persisted plugin JSON and rootfs directories. Depends on OCI spec generation, init layer setup, mount propagation, container executor, Unix signals, plugin clients, and content-store config blobs.

## Risks And Test Signals
Socket readiness uses sleeps/retries. Forced disable with live mounts requires careful unmounting before upgrade/remove. Linux tests cover mount isolation, create failure cleanup, and live-restore startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_linux_test.go

## Purpose
Tests Linux plugin manager behavior around mounts, failed create cleanup, and already-running plugin restore.

## Important APIs, Types, And Functions
Tests use `TestManagerWithPluginMounts`, `newTestPlugin`, `simpleExecutor`, `TestCreateFailed`, `executorWithRunning`, `TestPluginAlreadyRunningOnStartup`, and `listenTestPlugin`.

## Control Flow
Root-only tests create temporary manager roots and fake plugins. One test mounts tmpfs under an enabled plugin and verifies removing another plugin does not unmount it. Create-failure test uses an executor returning an error. Startup test simulates an already-listening Unix socket and checks client setup with live-restore on/off.

## State, Dependencies, And Integration Points
Uses temp directories, real mounts, Unix sockets, and fake executors. It integrates manager reload/enable/remove paths with filesystem and mount behavior.

## Risks And Test Signals
Root requirements skip some coverage for unprivileged runs. Unix socket path length is explicitly managed. These tests are high-value lifecycle signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_test.go

## Purpose
Tests plugin privilege validation semantics.

## Important APIs, Types, And Functions
`TestValidatePrivileges` exercises `validatePrivileges` and implicitly `normalizePrivileges` using `plugin.Privileges`.

## Control Flow
The table compares required privileges against provided privileges and expects success only when lengths, names, and value sets match. One case confirms privilege and value ordering does not matter.

## State, Dependencies, And Integration Points
No external state. This protects the install/upgrade privilege gate used by Linux plugin pull and upgrade.

## Risks And Test Signals
Descriptions are ignored by validation, while names and values are strict and case-sensitive. The test covers empty, mismatched length, mismatched values, order-insensitive success, and single-privilege behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_windows.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_windows.go

## Purpose
Provides Windows stubs for manager lifecycle internals.

## Important APIs, Types, And Functions
Stubbed functions include `enable`, `initSpec`, `disable`, `restore`, `Shutdown`, and `recursiveUnmount`.

## Control Flow
Lifecycle methods return `fmt.Errorf("Not implemented")`, `Shutdown` is a no-op, and `recursiveUnmount` returns nil.

## State, Dependencies, And Integration Points
No state is mutated. This file preserves package shape for Windows builds where the Linux managed-plugin runtime is unavailable.

## Risks And Test Signals
The error text is capitalized and generic. Backend unsupported stubs are the public surface; these internal stubs guard compile compatibility. Windows build tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/progress.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/progress.go

## Purpose
Tracks plugin push jobs and converts containerd upload tracker state into Docker progress messages.

## Important APIs, Types, And Functions
`newPushJobs`, `pushJobs.add`, `pushJobs.status`, and `contentStatus` are the main items.

## Control Flow
`add` de-duplicates upload job IDs and stores a display name. `status` locks the job list, queries `docker.StatusTracker`, maps missing status to `Waiting`, and reports uploading or upload-complete state based on `UploadUUID`.

## State, Dependencies, And Integration Points
State is an in-memory job list and ID-to-name map protected by a mutex. It integrates with `backend_linux.go` push progress goroutines and containerd's Docker remotes tracker.

## Risks And Test Signals
Status polling depends on tracker keys matching `remotes.MakeRefKey`. No direct tests exist; plugin push integration output is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/registry.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/registry.go

## Purpose
Builds registry resolver configuration for plugin pull and push operations.

## Important APIs, Types, And Functions
`scope` builds `repository(plugin):...` auth scopes. `Manager.newResolver`, `registryHTTPClient`, and `Manager.registryHostsFn` configure containerd Docker resolvers and hosts.

## Control Flow
Resolver creation adds Docker user-agent headers and delegates host selection to `registryHostsFn`. Host resolution asks the daemon registry service for endpoints, optionally filters to HTTP fallback, assigns pull/resolve/referrers and push capabilities, builds TLS-aware HTTP clients, and installs an authorizer using username/password or identity token.

## State, Dependencies, And Integration Points
No persistence. It depends on containerd remotes/docker, daemon registry service endpoint lookup, Docker version user-agent, TLS config, and registry auth config.

## Risks And Test Signals
Push fallback only uses HTTP endpoints when requested because containerd push tries the first host. Auth scope must include the plugin classifier or registry authorization fails. Integration tests around pull/push are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/store.go

## Purpose
Implements the in-memory managed plugin inventory plus compatibility lookups for legacy v1 plugins.

## Important APIs, Types, And Functions
Key methods include `GetV2Plugin`, `validateName`, `GetAll`, `SetAll`, `SetState`, `Add`, `Remove`, `Get`, `GetAllManagedPluginsByCap`, `GetAllByCap`, `Handle`, `CallHandler`, and plugin ID/name resolution helpers. `pluginType` formats Docker capability identifiers.

## Control Flow
Lookups resolve name, full ID, or partial ID, then filter by capability and enabled state. `Get` increments refcount only after an enabled plugin passes capability filtering, and falls back to legacy plugins when allowed. Handlers are registered by capability and called when matching plugins become available.

## State, Dependencies, And Integration Points
State is protected by `Store`'s RW mutex and includes managed plugins, spec options, and legacy callbacks. It integrates with `plugingetter`, legacy `pkg/plugins`, and manager lifecycle.

## Risks And Test Signals
Partial ID/name ambiguity is a user-facing risk. Reference counts must not change on failed capability checks; `store_test.go` covers that.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/store_test.go

## Purpose
Tests plugin capability filtering and reference-count behavior.

## Important APIs, Types, And Functions
`TestFilterByCapNeg`, `TestFilterByCapPos`, and `TestStoreGetPluginNotMatchCapRefs` use `v2.Plugin.FilterByCap`, `Store.Add`, and `Store.Get`.

## Control Flow
The tests build fake plugins with interface capability IDs, assert mismatched capability errors, assert matched capability success, and confirm store lookup does not increment refs when capability filtering fails, both disabled and enabled.

## State, Dependencies, And Integration Points
State is an in-memory `Store` and plugin structs. It validates behavior consumed by daemon subsystems that acquire plugins by capability.

## Risks And Test Signals
The tests do not cover ambiguous names, partial IDs, legacy fallback, or handler callbacks. They strongly protect refcount correctness on failed lookups.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin.go

## Purpose
Defines the managed v2 plugin model and its concurrency-safe accessors, settings mutation, capability filtering, reference counts, timeout/address, and protocol behavior.

## Important APIs, Types, And Functions
`Plugin`, `ErrInadequateCapability`, `ScopedPath`, `Client`, `SetPClient`, `IsV1`, `Name`, `FilterByCap`, `InitEmptySettings`, `Set`, enabled/ID/socket/type/refcount accessors, `Acquire`, `Release`, `SetSpecOptModifier`, timeout/address methods, and `Protocol`.

## Control Flow
`InitEmptySettings` copies configurable defaults into runtime settings. `Set` rejects active plugins, parses user assignments, finds matching env/mount/device/args config entries, checks allowed settable fields, and mutates settings. Accessors lock around shared mutable fields.

## State, Dependencies, And Integration Points
State is the plugin object, persisted digest metadata, rootfs path, refcount, runtime spec modifier, swarm service ID, client, timeout, and socket address. Manager/store/backend code consumes these methods.

## Risks And Test Signals
`Set` mutates range-loop copies for mounts/devices rather than settings slices in some paths, which is a subtle area to inspect when changing. Tests cover settable parsing helpers and capability filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_linux.go

## Purpose
Builds an OCI runtime spec for a managed plugin on Linux.

## Important APIs, Types, And Functions
`Plugin.InitSpec(execRoot string)` is the exported behavior. It uses `oci.DefaultSpec`, `oci.RemoveNamespace`, `oci.DevicesFromPath`, rootless mount option helpers, and optional runtime spec modifiers.

## Control Flow
The function sets rootfs, prepares plugin runtime bind mounts, handles propagated mount storage, applies host network/PID/IPC namespace requests, adds configured mounts and devices, removes default `/dev` mounts overridden by user mounts, builds env and process args, adds Linux capabilities, applies spec modifiers, and adjusts bind mount flags/rootless spec conversion when running in user namespaces.

## State, Dependencies, And Integration Points
Creates the plugin exec root directory and returns an in-memory spec. It depends on rootless detection, mount flag introspection, OCI helpers, and plugin settings from `PluginObj`.

## Risks And Test Signals
Mount source nil values error out. Device paths are dereferenced and must be present. User-namespace mount flags are subtle. Linux manager tests exercise spec use indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_unsupported.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_unsupported.go

## Purpose
Provides non-Linux `Plugin.InitSpec` behavior for unsupported platforms.

## Important APIs, Types, And Functions
`InitSpec(execRoot string) (*specs.Spec, error)` returns an error.

## Control Flow
The function immediately returns `nil` and `errors.New("not supported")`.

## State, Dependencies, And Integration Points
No state. Build tags select this for `!linux`, keeping package APIs compilable while disabling Linux-specific OCI spec construction.

## Risks And Test Signals
Callers must not assume managed plugin runtime support on non-Linux. Compile tests and backend unsupported behavior are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/settable.go

## Purpose
Parses and validates plugin setting assignment syntax used by `Plugin.Set`.

## Important APIs, Types, And Functions
`settable` holds `name`, `field`, and `value`. Helpers include `newSettables`, `newSettable`, `prettyName`, `isSettable`, and `updateSettingsEnv`. Allowed fields are defined for env, args, devices, and mounts.

## Control Flow
Assignments must be `<name>[.<field>][=<value>]`; leading `=` is invalid. Field is parsed from the last dot before `=`, with defaulting only when exactly one field is declared settable. `updateSettingsEnv` replaces an existing `NAME=` entry or appends a new one.

## State, Dependencies, And Integration Points
State changes are limited to env slices passed by pointer. It integrates with v2 plugin configuration mutation before save.

## Risks And Test Signals
Names containing dots may be interpreted as field syntax. Multiple settable fields require explicit field selection. Tests cover parsing, allowed-field checks, and env update ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/settable_test.go

## Purpose
Tests parsing and validation helpers for plugin settable options.

## Important APIs, Types, And Functions
`TestNewSettable`, `TestIsSettable`, and `TestUpdateSettingsEnv` cover `newSettable`, `isSettable`, and `updateSettingsEnv`.

## Control Flow
Parsing tests verify name/value, bare name, field syntax, empty value, and invalid leading equals. Validation tests check allowed and configured field combinations, including multiple-field ambiguity. Env tests check replace or append behavior.

## State, Dependencies, And Integration Points
No external state. It protects the lower-level parser used by `Plugin.Set` and daemon plugin setting persistence.

## Risks And Test Signals
The tests do not cover full `Plugin.Set` across mounts/devices/args, but they strongly signal syntax and env mutation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth.go -->
# sources/cloud-native/moby/daemon/pkg/registry/auth.go

## Purpose
Implements registry credential stores, v2 login validation, authenticated HTTP client construction, credential-key normalization, and v2 registry ping/challenge discovery.

## Important APIs, Types, And Functions
`AuthClientID`, `loginCredentialStore`, `staticCredentialStore`, `NewStaticCredentialStore`, `loginV2`, `v2AuthHTTPClient`, `ConvertToHostname`, `resolveAuthConfig`, `PingResponseError`, and `PingV2Registry`.

## Control Flow
Login pings `/v2/`, builds token/basic auth handlers from challenges, sends a GET, and returns a captured identity token on 200. Auth resolution first checks the canonical config key, then scans legacy URL keys normalized to host. `PingV2Registry` records auth challenges from a registry response.

## State, Dependencies, And Integration Points
`loginCredentialStore` mutates a copy of auth config to capture refresh tokens; static store is read-only. Depends on Docker distribution auth/transport, registry API types, and transport headers.

## Risks And Test Signals
Authentication errors are translated for API classification. Legacy credential matching is compatibility-sensitive. `auth_test.go` covers official/private and full-URL credential resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/auth_test.go

## Purpose
Tests registry auth-config resolution for official and private indexes, including legacy full-URL keys.

## Important APIs, Types, And Functions
`buildAuthConfigs`, `TestResolveAuthConfigIndexServer`, and `TestResolveAuthConfigFullURL` exercise `resolveAuthConfig`.

## Control Flow
The first test checks that official indexes use `IndexServer` credentials while private indexes do not. The second injects auth entries using `https://`, `http://`, bare host, and `/v1/` forms, verifying they resolve only while present.

## State, Dependencies, And Integration Points
State is an in-memory map of `registry.AuthConfig`. It protects daemon credential lookup compatibility with old Docker config formats.

## Risks And Test Signals
The tests do not cover unknown schemes or username-less token auth, but they strongly cover host normalization and official-index special-casing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config.go -->
# sources/cloud-native/moby/daemon/pkg/registry/config.go

## Purpose
Defines registry service configuration parsing and validation for Docker Hub defaults, mirrors, insecure registries, certificate locations, and index-name handling.

## Important APIs, Types, And Functions
Key items are `ServiceOptions`, `serviceConfig`, Docker Hub constants, `DefaultV2Registry`, `CertsDir`, `newServiceConfig`, `copy`, `loadMirrors`, `loadInsecureRegistries`, `isSecureIndex`, `isCIDRMatch`, `ValidateMirror`, `ValidateIndexName`, `validateHostPort`, and `getAuthConfigKey`.

## Control Flow
Mirror loading normalizes URLs and removes duplicates. Insecure registry loading adds localhost CIDRs, strips allowed schemes with warnings, stores CIDRs or insecure index configs, and always configures the official index. Security checks prefer explicit index config, then CIDR matching with DNS resolution. Validation rejects mirror credentials, query, fragment, unsupported schemes, invalid hosts, and out-of-range ports.

## State, Dependencies, And Integration Points
State is the daemon registry service config. Depends on `netip`, `reference.DomainRegexp`, rootless config dir detection, and Docker API registry types.

## Risks And Test Signals
DNS lookup affects CIDR matching. Some validation is intentionally legacy-compatible. `config_test.go` covers mirror, insecure registry, service config, and index-name behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/config_test.go

## Purpose
Tests daemon registry configuration validation for mirrors, insecure registries, service options, and index names.

## Important APIs, Types, And Functions
`TestValidateMirror`, `TestLoadInsecureRegistries`, `TestNewServiceConfig`, `TestValidateIndexName`, and `TestValidateIndexNameWithError` cover the major public/internal validation paths.

## Control Flow
The mirror table checks normalization and exact invalid-URI errors. Insecure registry tests call `loadInsecureRegistries` and inspect index config entries or invalid-argument classification. Service config tests combine mirror and insecure options. Index-name tests cover normalization and hyphen rejection.

## State, Dependencies, And Integration Points
No external state. It depends on containerd errdefs classification and protects daemon startup config validation.

## Risks And Test Signals
Exact URL parser error strings may be brittle. The suite has good coverage for schemes, credentials, fragments, ports, IPv6 forms, and Docker Hub normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/errors.go -->
# sources/cloud-native/moby/daemon/pkg/registry/errors.go

## Purpose
Provides registry-specific error wrappers with Docker API classification markers.

## Important APIs, Types, And Functions
`translateV2AuthError`, `invalidParam`, `invalidParamf`, `invalidParamWrapf`, and wrapper types `unauthorizedErr`, `invalidParameterErr`, `systemErr`, and `errUnknown`.

## Control Flow
`translateV2AuthError` unwraps URL and distribution errcode errors and maps unauthorized responses to `unauthorizedErr`. Invalid parameter helpers wrap errors while preserving unwrap behavior.

## State, Dependencies, And Integration Points
No state. Error wrappers integrate registry/auth/config code with daemon API error classification.

## Risks And Test Signals
Correct behavior depends on `errors.As`/`errors.Is` through nested distribution errors. Config tests assert invalid-argument classification; auth error translation has less direct coverage in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry.go -->
# sources/cloud-native/moby/daemon/pkg/registry/registry.go

## Purpose
Implements registry client TLS configuration, certificate directory loading, request headers, and HTTP transport creation.

## Important APIs, Types, And Functions
`hostCertsDir`, `newTLSConfig`, `hasFile`, `loadTLSConfig`, `Headers`, and `newTransport` are the key functions.

## Control Flow
TLS config starts from Docker server defaults and toggles `InsecureSkipVerify` for insecure endpoints. Secure endpoints load `.crt` CA files and `.cert`/`.key` client pairs from host-specific cert dirs, validating matching pairs. Headers returns transport request modifiers for user-agent and meta headers. Transport creation uses proxy, dial timeout, TLS handshake timeout, idle timeout, and OpenTelemetry instrumentation.

## State, Dependencies, And Integration Points
Reads certificate files from `CertsDir()` but persists nothing. Integrates with registry service endpoints, auth clients, plugin resolvers, and image distribution code.

## Risks And Test Signals
Malformed cert directories become invalid-parameter errors. Windows strips colons from host cert dirs. Direct tests are not in this subset; registry integration tests and mock registry helpers exercise transports.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry_mock_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/registry_mock_test.go

## Purpose
Defines reusable HTTP/HTTPS mock registry servers and helpers for registry package tests.

## Important APIs, Types, And Functions
Global `testHTTPServer` and `testHTTPSServer` are initialized in `init`. Helpers include `handlerAccessLog`, `makeURL`, `makeHTTPSURL`, `makeIndex`, `makeHTTPSIndex`, `makePublicIndex`, `writeHeaders`, `writeResponse`, `handlerGetPing`, `handlerSearch`, and `TestPing`.

## Control Flow
`init` registers v1 ping/search and v2 version handlers on an HTTP mux, then starts test servers. Handlers validate GET methods and return JSON. `TestPing` sends a GET to `/v1/_ping` and checks status/header.

## State, Dependencies, And Integration Points
The servers are process-global test state. They support registry tests needing endpoints without external network access and integrate with `registry.IndexInfo` construction helpers.

## Risks And Test Signals
Global servers live for the test process and may affect parallel tests if handlers mutate state in the future. The mock covers basic success responses, not auth challenges or registry error bodies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/registry_mock_test.go -->
