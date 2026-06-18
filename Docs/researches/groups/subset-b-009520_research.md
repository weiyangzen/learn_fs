# Research Group subset-b-009520

This grouped report covers syzkaller trace conversion tools and VM backends under `sources/test-tools/syzkaller`. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/fuzz.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/fuzz.go

## Purpose

`fuzz.go` adds a libFuzzer-style entry point for the `proggen` package. It feeds arbitrary strace-like bytes into `ParseData` using a preinitialized Linux/amd64 syzkaller target, so parser and program-generation crashes can be found without running the command-line tool.

## Important APIs, Types, and Functions

The file defines package-level `linuxTarget`, `Fuzz(data []byte) int`, and `init`. `linuxTarget` calls `prog.GetTarget(targets.Linux, targets.AMD64)`, imports the syscall descriptions through a blank `sys` import, and builds `target.ConstMap` from target constants. `Fuzz` calls `ParseData` and returns zero on parse errors or the number of generated programs on success. `runtime.KeepAlive(Fuzz)` marks the entry as live for dead-code tooling.

## Control Flow

Initialization happens once at package load. Each fuzz input is parsed into the trace tree by `ParseData`, converted into one or more `prog.Prog` values by the rest of `proggen`, and collapsed to a simple coverage signal. Errors are intentionally not treated as fuzzing failures.

## State and Persistence Behavior

The only persistent state is the shared `linuxTarget` pointer and its constant map. Inputs, parsed traces, and generated programs are transient. There is no filesystem or network state.

## Dependencies and Integration Points

It depends on `prog`, `sys/targets`, the imported syscall descriptions, and `proggen.ParseData`. It integrates with Go fuzzing or syzkaller's dead-code analysis as a package-level fuzz harness.

## Risks and Test Signals

The fixed Linux/amd64 target means target-specific parser bugs for other OS/arch pairs are not covered. Because parse errors return zero, only panics, fatal exits, and unexpected internal failures are strong fuzz signals. Useful signals are fuzz corpora containing malformed strace syntax, nested groups, weird constants, and syscalls with union or resource arguments.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/generate_unions.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/generate_unions.go

## Purpose

`generate_unions.go` contains special-case union selection for strace arguments whose syzkaller descriptions cannot be inferred by a simple first-field fallback. It primarily maps socket address and interface request traces into the correct syzkaller union arm.

## Important APIs, Types, and Functions

The methods are `(*context).genSockaddrStorage`, `(*context).genSockaddrNetlink`, and `(*context).genIfrIfru`. They use `prog.UnionType`, `prog.MakeUnionArg`, `parser.GroupType`, `parser.Constant`, `ctx.target.ConstMap`, and recursive `ctx.genArg`.

## Control Flow

`genUnionArg` in `proggen.go` dispatches here for union type names `sockaddr_storage`, `sockaddr_nl`, and `ifr_ifru`. `genSockaddrStorage` reads the first parsed group element as an address family and chooses arms such as `in6`, `in`, `un`, `nl`, `nfc`, or `ll`. `genSockaddrNetlink` inspects the netlink PID to choose user, kernel, or unspecified arms. `genIfrIfru` chooses an alternate field when strace produced a plain constant.

## State and Persistence Behavior

The functions build local field-name-to-index maps on each call and do not persist state. They depend on the context's target constant map and current conversion context.

## Dependencies and Integration Points

They integrate tightly with Linux syscall descriptions and `tools/syz-trace2syz/parser` IR shapes. They are called only from `proggen` union generation and must track syzkaller union field names.

## Risks and Test Signals

The logic assumes parsed groups are non-empty and the first element is a constant; malformed or unexpected traces can trigger fatal logging. Field-name drift in syscall descriptions would silently select the zero arm or panic through bad assumptions. Test signals include socket connect/bind/sendto traces for IPv4, IPv6, UNIX, netlink, NFC, packet sockets, and ioctl ifreq variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/generate_unions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen.go

## Purpose

`proggen.go` is the core trace-to-syzkaller-program converter. It reads parsed strace traces, selects matching syzkaller syscall descriptions, translates parser IR values into `prog.Arg` trees, tracks returned resources, and emits validated `prog.Prog` programs.

## Important APIs, Types, and Functions

Public entry points are `ParseFile` and `ParseData`. Main internals are `parseTree`, `genProg`, `context`, `(*context).genCall`, `Select`, `genResult`, `genArg`, `genVma`, `genArray`, `genStruct`, `recurseStructs`, `genUnionArg`, `genBuffer`, `genPtr`, `genConst`, `genResource`, `parseProc`, `addr`, and `shouldSkip`. It depends on `prog.Builder`, `prog.Type` implementations, `parser.TraceTree`, `parser.Syscall`, and call selectors from the same package.

## Control Flow

`ParseFile` reads bytes from disk and delegates to `ParseData`. `ParseData` parses strace bytes into a trace tree, then `parseTree` recursively walks the process hierarchy from `RootPid`, generating one syzkaller program per traced process. `genProg` skips paused and unsupported calls, sets current trace context, generates calls, appends them to a `prog.Builder`, and finalizes the program. `genCall` selects a syscall variant, creates a `prog.Call`, generates each argument from syzkaller type metadata and parsed IR, and caches positive resource returns.

## State and Persistence Behavior

`context` owns the mutable program builder, target, call selectors, return cache, and current source/destination call. Builder allocations provide stable virtual addresses for pointer/VMA arguments. The return cache links later resource arguments to earlier returned `prog.ResultArg` values using resource kind and trace expression. No state persists beyond one generated program.

## Dependencies and Integration Points

It integrates with `parser.ParseData`, syzkaller syscall descriptions, `prog.MakeProgGen`, `prog.Make*Arg` constructors, resource typing, and selector logic in companion files. The command-line `trace2syz.go`, tests, and fuzz harness are the direct callers.

## Risks and Test Signals

Many unexpected IR/type combinations call `log.Fatalf`, so malformed traces can terminate conversion instead of producing partial output. Buffer endian conversion, omitted struct fields, out-direction defaults, recursive struct wrapping, and resource reuse are correctness-sensitive. `proggen_test.go` supplies strong regression signals for open/write, pipe, socket variants, ioctl, sockaddr unions, device opens, xattrs, IPv4/IPv6 byte ordering, and unsupported or skipped calls.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen_test.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen_test.go

## Purpose

`proggen_test.go` is the main regression suite for trace-to-program conversion. It verifies that representative strace snippets serialize to stable syzkaller programs.

## Important APIs, Types, and Functions

The file defines `TestParse`, a table of input/output cases, and uses `parser.ParseData`, `genProg`, `prog.GetTarget`, `targets.Linux`, `targets.AMD64`, and `prog.Prog.Serialize`. The blank `sys` import registers syscall descriptions needed by `prog.GetTarget`.

## Control Flow

The test initializes a Linux/amd64 target and fills its `ConstMap`. Each case trims the input trace, parses it into a trace tree, generates a program from the root PID trace, serializes the program, trims whitespace, and compares it to the expected text.

## State and Persistence Behavior

All state is test-local except for target description registration through the blank import. The test does not touch files, devices, or network resources.

## Dependencies and Integration Points

It exercises the parser, syscall target metadata, selector logic, resource cache, union generation, pointer allocation, and serialization format. It is the primary integration signal for `proggen` behavior.

## Risks and Test Signals

The suite is broad but example-driven; it does not cover all syscall descriptions or fatal error paths. Expected strings are sensitive to syscall description changes and allocator layout. High-value signals include resource reuse across `open`, `pipe`, and `inotify`, sockaddr family selection, ioctl selector choice, device-specific `openat` rewrites, endian parsing of network buffers, and default generation for omitted fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/proggen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/return_cache.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/return_cache.go

## Purpose

`return_cache.go` implements the resource-return cache used during trace conversion. It lets later syscall arguments reference earlier returned resources instead of hard-coding raw numeric values.

## Important APIs, Types, and Functions

The main type is `returnCache map[string]prog.Arg`. Functions are `newRCache`, `returnCacheKey`, `returnCache.cache`, and `returnCache.get`. Keys combine the first resource kind from `prog.ResourceType.Desc.Kind` with the parser IR string representation.

## Control Flow

When `genResult` or an out resource argument sees a returned resource, it calls `cache`. When `genResource` handles an input constant, it calls `get`; a hit creates a `prog.ResultArg` linked to the original result, while a miss falls back to a raw value.

## State and Persistence Behavior

The cache is per-generated program through `context.returnCache`. It is an in-memory map with no eviction because traces are processed once and then discarded.

## Dependencies and Integration Points

It depends on `prog.ResourceType`, `prog.Arg`, and parser IR stringification. It is coupled to `proggen.go` resource generation and result handling.

## Risks and Test Signals

`returnCacheKey` fatals on non-resource types and assumes `Desc.Kind` is non-empty. String-based keys can collide if distinct parser IR values stringify identically in a relevant context. Tests in `proggen_test.go` cover file descriptor and pipe/inotify resource reuse; additional stress should cover reused numeric values across different resource kinds.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/return_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/unsupported_calls.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/unsupported_calls.go

## Purpose

`unsupported_calls.go` centralizes syscall names that `syz-trace2syz` intentionally skips. These calls are unsupported, unsafe, too environment-dependent, or not useful for seed generation.

## Important APIs, Types, and Functions

The file exports package-level `unsupportedCalls`, a `map[string]bool` consumed by `shouldSkip` in `proggen.go`. Entries include `execve`, `arch_prctl`, wait/futex/clone calls, memory mapping calls, selected signal calls, `getcwd`, `getcpu`, `rt_sigaction`, `set_robust_list`, and `set_tid_address`.

## Control Flow

During `genProg`, each parsed syscall is checked with `shouldSkip`. If its name is in this map, conversion logs a skip and does not append a syzkaller call.

## State and Persistence Behavior

The map is immutable after package initialization by convention. It has no persistence or side effects.

## Dependencies and Integration Points

It is coupled to parser syscall naming and syzkaller syscall descriptions. The list documents policy for trace conversion rather than runtime execution.

## Risks and Test Signals

Skipping may remove context needed by later calls, especially resource creation, memory setup, or signal state. Not skipping unsafe calls can produce programs that hang, fork away coverage, corrupt summaries, or depend on unrecoverable function pointers. Test signals are traces containing skipped calls followed by useful calls and ensuring conversion still produces valid programs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/unsupported_calls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/trace2syz.go -->
# sources/test-tools/syzkaller/tools/syz-trace2syz/trace2syz.go

## Purpose

`trace2syz.go` is the command-line tool that converts one strace file or a directory of strace files into a syzkaller `corpus.db`. It can also write serialized programs for inspection.

## Important APIs, Types, and Functions

The tool defines flags `-file`, `-dir`, and `-deserialize`, constants for Linux/amd64 target selection, and functions `main`, `initializeTarget`, `parseTraces`, `getTraceFiles`, and `pack`. It uses `proggen.ParseFile`, `db.Create`, `osutil.WriteFile`, and `prog.Target`.

## Control Flow

`main` parses flags, initializes the target and constant map, parses traces, and packs generated programs into `corpus.db`. `parseTraces` chooses either the single file or all directory entries, converts each file with `proggen.ParseFile`, optionally writes each serialized program into the deserialize directory, and returns all programs. `pack` serializes records into a syzkaller database.

## State and Persistence Behavior

It reads trace files and writes `corpus.db` in the current working directory. With `-deserialize`, it writes per-program text files named from the trace basename plus an index. It does not filter directory entries by type.

## Dependencies and Integration Points

The tool integrates strace output, `proggen`, syzkaller target descriptions, and corpus database creation. It is intended for seed selection and debugging, not as a general live tracer.

## Risks and Test Signals

Hard-coded Linux/amd64 support limits portability. Fatal errors stop the whole batch on one bad trace. Directory mode includes every entry and does not sort explicitly, so corpus generation order depends on `os.ReadDir` names. Tests should cover missing flags, unreadable files, parse failures, deserialize output, and database creation with multiple traces.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-trace2syz/trace2syz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-tty/syz-tty.go -->
# sources/test-tools/syzkaller/tools/syz-tty/syz-tty.go

## Purpose

`syz-tty.go` is a small diagnostic utility for testing syzkaller USB console reading. It opens a TTY-like console path and copies all output to stdout.

## Important APIs, Types, and Functions

The only function is `main`. It uses `vmimpl.OpenConsole`, `io.Copy`, `fmt.Fprintf`, and `os.Exit`.

## Control Flow

The program expects exactly one argument. It opens that console, defers close, and streams bytes to stdout until EOF or copy error.

## State and Persistence Behavior

It reads from the specified device and writes to stdout. There is no persistent state, but it holds the console device open while running.

## Dependencies and Integration Points

The utility reuses the same console-opening helper as VM backends, making it a manual integration check for USB serial console support.

## Risks and Test Signals

Errors from `io.Copy` are ignored, so abrupt disconnects are not reported distinctly after open succeeds. It can block indefinitely by design. Test signals are mostly manual: invalid usage exits nonzero, missing devices report open errors, and valid consoles stream kernel output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-tty/syz-tty.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-upgrade/upgrade.go -->
# sources/test-tools/syzkaller/tools/syz-upgrade/upgrade.go

## Purpose

`upgrade.go` rewrites a syzkaller corpus directory from an older program serialization format to the current one. It is a manual migration helper used while changing `prog.Serialize` and `prog.Deserialize`.

## Important APIs, Types, and Functions

The file defines `main` and `fatalf`. `main` uses `prog.GetTarget(runtime.GOOS, runtime.GOARCH)`, `target.Deserialize(data, prog.NonStrict)`, `p.Serialize`, SHA-1 hashing, `osutil.WriteFile`, and `os.Remove`.

## Control Flow

The tool expects a single corpus directory. It reads each directory entry, deserializes the program non-strictly, serializes it with current code, and compares bytes. Changed programs are printed, written under the SHA-1 hash of the new serialization, and the old file is removed.

## State and Persistence Behavior

This tool mutates the corpus directory in place and can delete original files after successful replacement. It does not recurse into subdirectories and stops on the first fatal error.

## Dependencies and Integration Points

It depends on local runtime GOOS/GOARCH target descriptions and syzkaller program serialization semantics. It is part of developer workflow around corpus format changes.

## Risks and Test Signals

The operation is destructive and assumes the current runtime target matches the corpus target. Hash-based filenames can collide only cryptographically improbably, but existing files with the same hash may be overwritten by `osutil.WriteFile` semantics. Tests should use a temporary corpus, verify unchanged files remain, changed files are renamed to content hash, and malformed programs abort.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-upgrade/upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-usbgen/usbgen.go -->
# sources/test-tools/syzkaller/tools/syz-usbgen/usbgen.go

## Purpose

`usbgen.go` parses kernel syslog lines containing generated USB and HID IDs and emits a Go source file with driver-to-ID maps for Linux virtual USB initialization.

## Important APIs, Types, and Functions

Functions are `main`, `extractIds`, `generateIdsVar`, and `usage`. The tool uses regular expressions for `USBID` and `HIDID` lines, `hex.DecodeString`, `maps.Keys`, `slices.Sorted`, `slices.Sort`, `osutil.WriteFile`, and `tool.Failf`.

## Control Flow

`main` requires input and output paths, reads syslog bytes, extracts 34-character USB IDs and 24-character HID IDs, generates a Go file header, appends `usbIds` and `hidIds` variables plus aggregate strings, and writes the output. `extractIds` deduplicates identical matching log lines and groups IDs by driver. `generateIdsVar` sorts drivers and IDs for stable output and formats decoded byte strings as concatenated Go string literals.

## State and Persistence Behavior

It reads one syslog file and overwrites one generated Go file. It prints counts to stdout but does not persist metadata beyond the generated source.

## Dependencies and Integration Points

The generated file targets `package linux` and is referenced by Linux USB external fuzzing setup. The input format is tied to kernel log prefixes emitted by USB/HID ID discovery code.

## Risks and Test Signals

The driver capture regex is greedy and trusts log formatting. Invalid hex is fatal despite the regex restricting lowercase hex. Empty input generates empty aggregate strings. Tests should cover duplicate log lines, multiple drivers, sort stability, no-match output, malformed sizes, and generated Go compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-usbgen/usbgen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/version.mk -->
# sources/test-tools/syzkaller/tools/version.mk

## Purpose

`version.mk` is a Makefile fragment that builds version metadata flags for syzkaller tools. It embeds the current git revision and optional build commit metadata into Go linker flags.

## Important APIs, Types, and Functions

The fragment defines `GITREV`, `VERSION`, appends to `GOFLAGS`, and optionally appends `-X github.com/google/syzkaller/pkg/build.Commit=$(BUILD_COMMIT)`. It invokes `git rev-parse HEAD` through `$(shell ...)`.

## Control Flow

Make evaluates `GITREV`, constructs `VERSION` as a linker `-X` assignment to `pkg/build.gitRevision`, appends it to `GOFLAGS`, and conditionally appends the build commit assignment when `BUILD_COMMIT` is non-empty.

## State and Persistence Behavior

It does not write files; it affects build command state through Make variables and Go linker flags. The resulting binaries persist the selected revision strings.

## Dependencies and Integration Points

It integrates Make-based tool builds with `pkg/build` variables in Go code and depends on being run inside a git checkout.

## Risks and Test Signals

Outside a git repository, `GITREV` may be empty or contain command diagnostics depending on shell behavior. Quoting is minimal, so values should remain simple commit identifiers. Test signals are built binaries reporting expected revision metadata with and without `BUILD_COMMIT`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/version.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/adb/adb.go -->
# sources/test-tools/syzkaller/vm/adb/adb.go

## Purpose

`adb.go` implements the syzkaller VM backend for Android devices reachable through ADB. It manages configured devices, repair and reboot, console association, battery checks, binary copy, adb reverse forwarding, and merged runtime output.

## Important APIs, Types, and Functions

Key types are `Device`, `Config`, `Pool`, and `instance`. The backend registers as `adb`. Important functions include `loadDevice`, `ctor`, `Pool.Count`, `Pool.Create`, `parseAdbOutToInt`, `findConsole`, `findConsoleImpl`, `Forward`, `adb`, `adbWithTimeout`, `waitForBootCompletion`, `markBootSuccessful`, `repair`, `runScript`, `waitForSSH`, `checkBatteryLevel`, `getBatteryLevel`, `Close`, `Copy`, `isRemoteCuttlefish`, `Run`, and `Diagnose`.

## Control Flow

`ctor` loads defaults and validates ADB binary and device identifiers. `Create` loads the indexed device, repairs it, discovers or configures console access, checks battery level, clears stale `/data/syzkaller*` files, and lowers `kptr_restrict`. `repair` optionally runs a repair script, waits for ADB, reboots, roots the device, waits for boot-service completion, marks the boot successful, mounts debugfs, and runs startup script. `Run` opens a console source, starts `adb shell cd /data; command`, merges console/stdout/stderr streams, and returns `vmimpl.Multiplex` channels.

## State and Persistence Behavior

Per-instance state stores adb binary, serial, console path/command, a close channel, debug flag, and timeout scale. Package-level console caches map devices to consoles. It mutates target device state by rebooting, rooting, mounting debugfs, deleting `/data/syzkaller*`, pushing binaries to `/data`, changing permissions, and changing kernel printk/kptr settings.

## Dependencies and Integration Points

It depends on Android ADB, `vmimpl` console/multiplex helpers, `osutil`, target timeouts, and optional remote Cuttlefish kernel-log helpers. It implements the `vmimpl.Pool` and `vmimpl.Instance` contracts consumed by syz-manager.

## Risks and Test Signals

Runtime behavior is environment-heavy: ADB hangs, reboot semantics, boot service names, root availability, battery service, console discovery races, and remote Cuttlefish IP handling can all fail. `Close` closes a channel without guarding double close. Tests currently cover config and device parsing; integration tests need real or simulated ADB devices for repair, console discovery, forwarding, copy, and merged output behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/adb/adb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/adb/adb_ppc64le.go -->
# sources/test-tools/syzkaller/vm/adb/adb_ppc64le.go

## Purpose

`adb_ppc64le.go` disables the ADB backend implementation on ppc64le while keeping package builds successful.

## Important APIs, Types, and Functions

The file contains only the `package adb` declaration under normal Go source syntax. There are no exported functions or types.

## Control Flow

There is no runtime control flow. Build selection excludes `adb.go` on ppc64le and includes this placeholder instead.

## State and Persistence Behavior

No state is created or persisted.

## Dependencies and Integration Points

The comment explains that ppc64le lacks a `golang.org/x/sys/unix.TCGETS2` constant required by console code, so the backend is turned off on that platform.

## Risks and Test Signals

The risk is silent absence of ADB VM registration on ppc64le. Build tests for ppc64le should verify the package compiles and syzkaller reports unsupported backend behavior cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/adb/adb_ppc64le.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/adb/adb_test.go -->
# sources/test-tools/syzkaller/vm/adb/adb_test.go

## Purpose

`adb_test.go` verifies JSON config loading and per-device config parsing for the ADB VM backend.

## Important APIs, Types, and Functions

Tests are `TestConfigParseBootService`, `TestConfigParseAllFields`, and `TestDeviceParse`. They use `config.LoadData`, `loadDevice`, `Config`, and `Device`.

## Control Flow

Each test builds raw JSON, initializes defaults where needed, loads data into config structs, and asserts expected field values. Device parsing tests cover legacy string serials and object form with `serial`, `console`, or `console_cmd`.

## State and Persistence Behavior

The tests are pure in-memory JSON parsing checks. They do not invoke ADB or mutate devices.

## Dependencies and Integration Points

They protect compatibility between manager JSON config and `adb.go` defaults, especially the newer `boot_service` option and flexible device representation.

## Risks and Test Signals

Coverage is limited to config parsing. It does not validate serial regex checks in `ctor`, ADB binary lookup, repair flow, battery parsing, or console discovery. Strong signals are default boot service preservation, explicit empty boot service behavior, all-field parsing, and legacy device string compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/adb/adb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/bhyve/bhyve.go -->
# sources/test-tools/syzkaller/vm/bhyve/bhyve.go

## Purpose

`bhyve.go` implements a FreeBSD bhyve VM backend. It creates per-instance disk clones or copies, sets up networking, boots VMs, waits for SSH, and runs commands with merged console and SSH output.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`; the backend registers as `bhyve` with overcommit. Important functions are `ctor`, `Pool.Count`, `Pool.Create`, `Boot`, `Close`, `Forward`, `Copy`, `Run`, `Diagnose`, and `parseIP`.

## Control Flow

`Create` prepares an instance name and SSH options, creates a ZFS snapshot/clone when `Dataset` is configured or copies the image into workdir otherwise, optionally creates and bridges a tap device, then calls `Boot`. `Boot` destroys any old VM, selects tap or slirp networking, optionally runs `bhyveload`, starts `bhyve`, captures console output, waits for an IP in DHCP output or uses localhost for slirp, and waits for SSH. `Run` starts an SSH command with optional port forwarding and adds its streams to the existing console merger.

## State and Persistence Behavior

Instance state tracks image copy/clone path, ZFS snapshot, tap device, forward port, bhyve process, console writer, and output merger. It mutates host state through ZFS snapshots/clones, copied images, tap interfaces, bridge membership, bhyve VMs, and SSH/SCP transfers. `Close` kills the VM and cleans these resources best-effort.

## Dependencies and Integration Points

It depends on FreeBSD host tooling (`bhyve`, `bhyveload`, `bhyvectl`, `ifconfig`, optional `zfs`), SSH helpers, and `vmimpl` multiplex/diagnose helpers. It implements the syzkaller VM instance interface.

## Risks and Test Signals

Boot success depends on DHCP/IP log parsing, host network setup, ZFS layout, image compatibility, and bhyve process cleanup. `Forward` supports only one slirp forward. Unit coverage is absent here, so useful tests are integration boot/SSH/copy/run/diagnose cycles, ZFS cleanup failure handling, tap bridge cleanup, and `parseIP` samples.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/bhyve/bhyve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/cuttlefish/cuttlefish.go -->
# sources/test-tools/syzkaller/vm/cuttlefish/cuttlefish.go

## Purpose

`cuttlefish.go` layers Android Cuttlefish device management on top of the GCE VM backend. It creates a GCE worker, launches a Cuttlefish Android instance inside it, and proxies syzkaller operations through host SSH and device ADB.

## Important APIs, Types, and Functions

Types are `Pool` and `instance`; constants are `deviceRoot` and `consoleReadCmd`. Important functions are `ctor`, `Pool.Count`, `Pool.Create`, `sshArgs`, `runOnHost`, `Copy`, `Forward`, `Close`, `Run`, and `Diagnose`.

## Control Flow

`ctor` creates an underlying `gce.Pool` configured to read Cuttlefish kernel logs. `Create` creates a GCE instance, starts `launch_cvd`, waits for ADB, roots the Android device, mounts debugfs, and creates `/data/fuzz`. `Copy` copies to the GCE host then `adb push`es into the device. `Forward` sets up host forwarding through the GCE backend, starts `socat` on the host, then repeatedly tries `adb reverse` to expose a device-local port. `Run` executes the command through `adb shell` inside `deviceRoot`.

## State and Persistence Behavior

The wrapper stores the underlying GCE instance and host SSH metadata. It creates Cuttlefish runtime state on the GCE VM, pushes files under `/data/fuzz`, and starts background forwarding processes on the host.

## Dependencies and Integration Points

It depends on the `gce` backend, host SSH, Cuttlefish binaries/images (`launch_cvd`, `bzImage`, `initramfs.img`), ADB, `socat`, and `vmimpl.Instance` methods.

## Risks and Test Signals

The flow assumes a specific Cuttlefish host layout and command syntax. Quoting in `sshArgs`/`runOnHost` is simple and command-string based. `socat` background lifetime is not explicitly tracked. Integration tests should cover launch failure, ADB wait/root failure, debugfs setup, copy/push, forward/reverse retries, and cleanup through underlying GCE close.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/cuttlefish/cuttlefish.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/dispatcher/pool.go -->
# sources/test-tools/syzkaller/vm/dispatcher/pool.go

## Purpose

`pool.go` implements a generic, concurrent pool scheduler for bootable instances. It keeps a default runner active on unreserved instances while allowing a dynamically sized sub-pool for custom one-shot runners.

## Important APIs, Types, and Functions

Core abstractions are `Instance`, `UpdateInfo`, `Runner[T]`, `CreateInstance[T]`, `Pool[T]`, `Info`, `poolInstance[T]`, and `InstanceState`. Public methods include `NewPool`, `SetDefault`, `TogglePause`, `Loop`, `ReserveForRun`, `Run`, `Total`, and `State`. Internal helpers include `kickDefault`, `waitUnpaused`, `runInstance`, `reportBootError`, `reset`, `updateInfo`, `status`, `reserved`, `getInfo`, `reserve`, `free`, and `mergeContextCancel`.

## Control Flow

`Loop` starts one goroutine per slot. Each slot waits for the pool to be unpaused, creates an instance through `creator`, records boot time, then runs either its default job or a job received from the reserved job channel. When a job returns or creation fails, the loop recreates the instance. `ReserveForRun` stops and converts slots between default and custom-job modes. `Run` sends a wrapped job to the reserved job channel and waits for completion or context cancellation.

## State and Persistence Behavior

State is in memory: per-instance status, reservation flags, stop callbacks, job channels, boot average, and boot-error channel. `poolInstance.reset` preserves the reservation bit across restarts. No filesystem or external VM state is owned directly; the supplied creator and instance close functions manage that.

## Dependencies and Integration Points

It depends on Go generics, contexts, sync primitives, `pkg/stat`, and syzkaller logging. It is reusable infrastructure for managers that need a stable default workload plus reserved lanes.

## Risks and Test Signals

Concurrency correctness is the main risk: reservation changes race with booting/waiting instances, default replacement must restart active jobs, and boot errors must not deadlock when no reader drains the channel. `pool_test.go` exercises default restarts, split reserved pools, stress with pause/reserve/run, default replacement, pause behavior, run cancellation, and full boot-error channels.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/dispatcher/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/dispatcher/pool_test.go -->
# sources/test-tools/syzkaller/vm/dispatcher/pool_test.go

## Purpose

`pool_test.go` verifies scheduler behavior for the generic dispatcher pool, especially restart, reservation, cancellation, pause, and race-prone state transitions.

## Important APIs, Types, and Functions

Tests include `TestPoolDefault`, `TestPoolSplit`, `TestPoolStress`, `TestPoolNewDefault`, `TestPoolPause`, `TestPoolCancelRun`, and `TestPoolBootErrors`. Helpers and fixtures include `makePool`, `testInstance`, `nilInstance`, `reset`, `run`, `waitRun`, `stopRun`, `Index`, and `Close`.

## Control Flow

The tests construct pools with fake instance creators and runner callbacks, start `Loop` in a goroutine, manipulate reservations and contexts, and use channels/atomics to assert expected scheduling. The stress tests intentionally interleave `TogglePause`, `Run`, and `ReserveForRun` to help the race detector.

## State and Persistence Behavior

All state is in-memory test fixture state. Fake instances expose stop channels and atomics so tests can observe job lifecycle without external VMs.

## Dependencies and Integration Points

It uses `testing`, `context`, `sync`, `atomic`, `runtime.Gosched`, and `testify/assert`. It is the main automated signal for `dispatcher.Pool`.

## Risks and Test Signals

The tests use polling sleeps, so pathological scheduler delays could cause slowness but not fixed timeouts in most cases. They do not verify `Info` callback contents or boot-time averages. Strong signals include all default slots restarting after job stop, custom jobs using only reserved slots, cancellation unblocking queued jobs, pause preventing start, and boot-error channel saturation not blocking shutdown.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/dispatcher/pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gce/gce.go -->
# sources/test-tools/syzkaller/vm/gce/gce.go

## Purpose

`gce.go` implements the Google Compute Engine VM backend. It prepares or reuses GCE images, creates instances with per-instance SSH keys, copies binaries, runs commands with serial console capture, detects preemption, and gathers diagnostics.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`. Public constructors are `ctor` and `Ctor`. Important functions include `initGCE`, `Pool.Count`, `Pool.Create`, `Close`, `Forward`, `Copy`, `Run`, `waitForConsoleConnect`, `hasBeenPreempted`, `Diagnose`, `ssh`, `sshArgs`, `serialPortArgs`, `getSerialPortOutput`, and `uploadImageToGCS`.

## Control Flow

`Ctor` validates config, initializes GCE context with retries, optionally uploads a raw disk image as a tar.gz to GCS and creates a GCE image, then returns a pool. `Create` generates an SSH key, builds instance config, deletes stale instances when appropriate, creates the instance, handles conflict by deleting/recreating, selects SSH credentials, and waits for SSH. `Run` starts a serial-console SSH connection, waits for it to attach, starts the workload SSH command, merges console/stdout/stderr, and uses `vmimpl.Multiplex` with preemption detection.

## State and Persistence Behavior

Pool state includes GCE context, config, optional console command, and an `alreadyCreated` map to avoid repeated cross-zone deletion. Instance state includes instance name/zone, per-instance key path, close channel, console writer, timeout scale, and preempted flag. The backend creates/deletes cloud instances, images, GCS objects during image upload, and local SSH key files.

## Dependencies and Integration Points

It depends on `pkg/gce`, `pkg/gcs`, Google API errors, SSH/SCP helpers, serial-port SSH service, crash diagnosis helpers, and target OS metadata. Cuttlefish reuses this backend with a custom console-read command.

## Risks and Test Signals

Risks include cloud quota/transient failures, stale instance conflicts, serial-port permission failures, missed early crash logs before console connect, preemption misclassification, and destructive image deletion by configured name. Tests are mostly integration-level: create/delete instances, upload images, SSH boot, serial console replay, copy failure under preemption, and diagnostics for Linux/FreeBSD/OpenBSD.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gce/gce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gce/tar_go1.10.go -->
# sources/test-tools/syzkaller/vm/gce/tar_go1.10.go

## Purpose

`tar_go1.10.go` provides the Go 1.10+ implementation of tar header formatting for GCE image uploads.

## Important APIs, Types, and Functions

It defines `setGNUFormat(hdr *tar.Header)`, which sets `hdr.Format = tar.FormatGNU`.

## Control Flow

`uploadImageToGCS` in `gce.go` calls `setGNUFormat` before writing the disk image tar header. On Go versions matching the build tag, this direct format assignment is used.

## State and Persistence Behavior

The function mutates only the provided tar header before it is written to the gzip/tar stream. The persisted effect is a GNU-format tar member in the uploaded image archive.

## Dependencies and Integration Points

It depends on the standard `archive/tar` package and Go build tags. It pairs with `tar_go1.9.go` for older toolchains.

## Risks and Test Signals

Risk is low; the main compatibility requirement is that GCE accepts the uploaded tar format. Tests should verify generated image archives contain a GNU-format `disk.raw` header under supported Go versions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gce/tar_go1.10.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gce/tar_go1.9.go -->
# sources/test-tools/syzkaller/vm/gce/tar_go1.9.go

## Purpose

`tar_go1.9.go` provides a pre-Go-1.10 fallback for forcing GNU tar format in GCE image uploads.

## Important APIs, Types, and Functions

It defines `setGNUFormat(hdr *tar.Header)`, assigning large `Uid` and `Gid` values to force the older `archive/tar` package to select GNU format.

## Control Flow

The build tag selects this file when Go 1.10 APIs are unavailable. `uploadImageToGCS` calls the same function name and receives GNU-compatible tar output indirectly.

## State and Persistence Behavior

Only the tar header is mutated. The resulting tar stream contains synthetic large owner IDs used solely as a format-selection hack.

## Dependencies and Integration Points

It depends on `archive/tar` behavior in old Go releases and GCE's expectation for old GNU tar format.

## Risks and Test Signals

This is intentionally hacky and relies on historical standard-library behavior. Tests on old toolchains should verify GCE accepts generated archives and that the `disk.raw` member remains readable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gce/tar_go1.9.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gvisor/gvisor.go -->
# sources/test-tools/syzkaller/vm/gvisor/gvisor.go

## Purpose

`gvisor.go` implements a VM backend for testing gVisor/runsc as the target kernel-like environment. It creates an OCI bundle, launches a runsc sandbox, copies test binaries into the root, executes commands inside the sandbox, and exposes a stdin-based proxy path for manager connections.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`; the backend registers under `targets.GVisor`. Important functions include `ctor`, `Pool.Count`, `Pool.Create`, `waitBoot`, `args`, `Info`, `runscCmd`, `Close`, `Forward`, `Copy`, `Run`, `guestProxy`, `Diagnose`, the proxy `init`, and constants/templates `initStartMsg`, `configTempl`, and `sandboxCaps`.

## Control Flow

`Create` builds root/image/bundle directories, writes `config.json`, copies the current binary as `/init`, creates a panic FIFO, starts `runsc run`, and waits for `SYZKALLER INIT STARTED` from the init path. `Run` builds `runsc exec` with root capabilities, wires stdout/stderr into the merger, optionally passes a Unix socketpair endpoint as stdin for manager proxying, starts the command, and kills the sandbox command on context timeout. `guestProxy` bridges the host TCP manager port to a Unix socket passed into the guest.

## State and Persistence Behavior

Instance state tracks the runsc root, image directory, sandbox name, command process, output merger, and one forwarded port. It writes bundle config and copied binaries under workdir, creates a FIFO, and manages a runsc container name in the runsc root. `Close` deletes the container forcefully and waits for merger/process cleanup.

## Dependencies and Integration Points

It depends on a runsc binary supplied as `env.Image`, OCI runtime config semantics, cgroup resource fields, Linux FIFOs/socketpairs, `vmimpl` output merging, and syzkaller's host-fuzzer forwarding expectations.

## Risks and Test Signals

Command splitting uses whitespace and cannot preserve complex shell quoting. `Close` assumes `inst.cmd` exists after successful create. Memory/cpu limit validation must match host resources. Integration tests should cover boot success/failure messages, panic-log capture, copy permissions, single-forward enforcement, proxy data flow, timeout killing, and diagnosis stack/dmesg collection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/gvisor/gvisor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/isolated/isolated.go -->
# sources/test-tools/syzkaller/vm/isolated/isolated.go

## Purpose

`isolated.go` implements a VM backend for externally managed physical or virtual machines reachable over SSH. It repairs/reboots targets, copies binaries to a target directory, runs commands remotely, captures remote console output, and optionally reads pstore crash logs.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`; the backend registers as `isolated`. Important functions include `ctor`, `Pool.Count`, `Pool.Create`, `Forward`, `ssh`, `waitRebootAndSSH`, `repair`, `waitForSSH`, `waitForReboot`, `Close`, `Copy`, `Run`, `readPstoreContents`, `Diagnose`, and `splitTargetPort`.

## Control Flow

`ctor` loads config, defaults host to localhost, validates targets and optional USB device counts. `Create` parses target host/port, repairs the target, remounts root writable, creates and cleans the target directory, and clears pstore when enabled. `repair` waits for SSH, optionally reboots through USB authorization toggling or SSH, then runs a startup script by reading it locally and executing its contents remotely. `Run` opens remote console output, starts SSH command execution in the target directory with optional port forwarding, and multiplexes dmesg/stdout/stderr.

## State and Persistence Behavior

Instance state tracks SSH options, target index, close channel, forward port, OS, and timeout scale. It mutates remote machines by rebooting, remounting `/`, deleting target directory contents, killing old binaries before copy, running startup scripts, and optionally deleting pstore files. USB reboot mutates host sysfs authorization files.

## Dependencies and Integration Points

It depends on SSH/SCP, `vmimpl.OpenRemoteConsole`, `vmimpl.Multiplex`, target OS metadata, optional pstore support, and `vmimpl.EscapeDoubleQuotes` for startup script execution.

## Risks and Test Signals

String-built shell commands make quoting important. `ssh` has a hard 30-second command wait outside some longer boot waits. USB power toggling requires exact sysfs device numbers. Tests cover double-quote escaping and target:port parsing; integration coverage should include repair paths, startup scripts, copy/run, forwarding, pstore diagnosis, and system SSH config behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/isolated/isolated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/isolated/isolated_test.go -->
# sources/test-tools/syzkaller/vm/isolated/isolated_test.go

## Purpose

`isolated_test.go` covers pure helper behavior for the isolated backend: shell quote escaping used for startup scripts and target address parsing.

## Important APIs, Types, and Functions

Tests are `TestEscapeDoubleQuotes` and `TestSplitTargetPort`. They call `vmimpl.EscapeDoubleQuotes` and `splitTargetPort`.

## Control Flow

The escaping test runs a table of strings containing plain text, backslashes, existing escapes, quotes, and a multi-line shell snippet. The split test checks host with explicit port, host with default port, empty target, and malformed port cases.

## State and Persistence Behavior

The tests are pure and create no external state.

## Dependencies and Integration Points

They protect helper behavior used by `isolated.repair` and config validation in `ctor`.

## Risks and Test Signals

They do not cover actual SSH execution, reboot, pstore, or copy/run flows. Strong signals are preserving non-quote escapes, re-escaping double quotes correctly for `bash -c`, defaulting missing port to 22, and rejecting empty targets or invalid ports.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/isolated/isolated_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/init.go -->
# sources/test-tools/syzkaller/vm/proxyapp/init.go

## Purpose

`init.go` defines configuration parsing and backend registration for the experimental proxyapp VM backend, which delegates VM operations to an external plugin over JSON-RPC.

## Important APIs, Types, and Functions

Key pieces are `makeDefaultParams`, `init`, `proxyAppParams`, `osutilCommandContext`, `subProcessCmd`, `Config`, `parseConfig`, and `URIParseErr`. Config fields include command, RPC server URI, security mode, server TLS certificate, transfer-file-content mode, and opaque plugin config.

## Control Flow

Registration wires `proxyapp` to `ctor(makeDefaultParams(), env)`. `parseConfig` loads JSON, requires either `cmd` or `rpc_server_uri`, validates URI shape when supplied, and returns config. `URIParseErr` prepends `http://` for parsing, then requires host:port without scheme decorations.

## State and Persistence Behavior

The file itself creates no persistent state. `proxyAppParams` allows tests to inject command runners, retry delay, and log output.

## Dependencies and Integration Points

It depends on `config.LoadData`, `osutil.CommandContext`, `vmimpl.Register`, and the client implementation in `proxyappclient.go`.

## Risks and Test Signals

URI validation permits only simple host:port strings. Mutual TLS is accepted at config level but implemented as an error in client setup. `init_test.go` covers command/URI combinations, bad URI formats, and opaque config preservation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/init_test.go -->
# sources/test-tools/syzkaller/vm/proxyapp/init_test.go

## Purpose

`init_test.go` verifies proxyapp configuration parsing and URI validation.

## Important APIs, Types, and Functions

Tests are `TestParseConfig` and `TestURIParseErr`. They use `parseConfig`, `URIParseErr`, `Config`, and `testify/assert`.

## Control Flow

The parse-config table checks command plus URI, command-only, URI-only, missing both, valid and invalid URI shapes, and optional remote plugin config. The URI test directly checks accepted host:port forms and rejected scheme/no-port inputs.

## State and Persistence Behavior

The tests are in-memory only.

## Dependencies and Integration Points

They protect the config contract consumed by `proxyappclient.ctor`.

## Risks and Test Signals

They do not exercise TLS setup, subprocess launch, reconnection, or RPC calls. Strong signals are rejecting empty plugin configuration and preserving `json.RawMessage` plugin config without semantic interpretation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/init_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/mocks/ProxyAppInterface.go -->
# sources/test-tools/syzkaller/vm/proxyapp/mocks/ProxyAppInterface.go

## Purpose

`ProxyAppInterface.go` is generated testify/mock code for the proxyapp RPC service interface. It supports unit tests that assert RPC method calls and inject replies/errors.

## Important APIs, Types, and Functions

The main type is `mocks.ProxyAppInterface` with constructor `NewProxyAppInterface`. It implements methods from `proxyrpc.ProxyAppInterface`: `CreatePool`, `CreateInstance`, `Diagnose`, `Copy`, `Forward`, `RunStart`, `RunStop`, `RunReadProgress`, `Close`, and `PoolLogs`, plus typed expectation helper structs.

## Control Flow

Each method delegates to `_mock.Called`, extracts configured return behavior, supports function-valued returns for custom logic, and panics if no return value was specified. The constructor registers cleanup to assert expectations.

## State and Persistence Behavior

State is held in the embedded `mock.Mock`: expected calls, actual calls, and return values. There is no external persistence.

## Dependencies and Integration Points

It depends on `github.com/stretchr/testify/mock` and `vm/proxyapp/proxyrpc` request/reply structs. Tests in the proxyapp package use similar local mocks and can use this generated package for typed expectations.

## Risks and Test Signals

Generated mocks can drift from `proxyrpc.ProxyAppInterface` if not regenerated after interface changes. Because missing returns panic, tests must configure all expected RPC calls. Test signal is successful compilation after RPC interface changes and expectation assertions during unit tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/mocks/ProxyAppInterface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/mocks/subProcessCmd.go -->
# sources/test-tools/syzkaller/vm/proxyapp/mocks/subProcessCmd.go

## Purpose

`subProcessCmd.go` is generated testify/mock code for the proxyapp subprocess command abstraction. It lets tests simulate stdin/stdout/stderr pipes, process start, and process wait behavior.

## Important APIs, Types, and Functions

The main type is `mocks.SubProcessCmd` with constructor `NewSubProcessCmd`. It implements `Start`, `StdinPipe`, `StdoutPipe`, `StderrPipe`, and `Wait`, each with typed expectation helper structs.

## Control Flow

Methods call into the embedded mock, return configured values or function-return results, and panic when no return is configured. Cleanup assertions are registered by the constructor.

## State and Persistence Behavior

All state is mock expectation and call history. The mock may hold in-memory pipe objects supplied by tests but creates no external process state itself.

## Dependencies and Integration Points

It depends on `io` and `testify/mock`, and mirrors the `subProcessCmd` interface in `proxyapp/init.go`. It supports tests for `runProxyApp`, pipe initialization failures, subprocess launch, and close behavior.

## Risks and Test Signals

Generated code must be refreshed when `subProcessCmd` changes. Test setup must provide realistic pipe closure behavior to avoid blocked goroutines. Compilation and proxyapp client tests are the main signals.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/mocks/subProcessCmd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient.go -->
# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient.go

## Purpose

`proxyappclient.go` implements the proxyapp VM backend client. It launches or connects to an external JSON-RPC plugin, supervises reconnection, forwards VM pool/instance operations over RPC, streams plugin logs, and adapts run progress into syzkaller output chunks.

## Important APIs, Types, and Functions

Key functions and types include `ctor`, `pool`, `pool.init`, `closeProxy`, `Count`, `Create`, `Close`, `ProxyApp`, `initPipedRPCClient`, `initNetworkRPCClient`, `runProxyApp`, `signalLostConnection`, `ProxyApp.Call`, `doLogPooling`, `CreatePool`, `CreateInstance`, `instance`, `Copy`, `Forward`, `buildMerger`, `Run`, `runStop`, `Diagnose`, `Close`, `stdInOutCloser`, and `clientErrorf`.

## Control Flow

`ctor` parses config, initializes a proxy connection, and starts a supervisor goroutine that reacts to pool close, subprocess termination, lost connection, or retry timers by closing and reinitializing the proxy. `pool.init` either launches a subprocess with piped JSON-RPC or dials TCP/TLS, starts log polling, and calls `ProxyVM.CreatePool`, enforcing a stable pool size. Instance methods translate syzkaller `Copy`, `Forward`, `Run`, `Diagnose`, and `Close` calls to `ProxyVM.*` RPC methods. `Run` starts a remote run, repeatedly issues `RunReadProgress`, writes stdout/stderr/console chunks into an output merger, stops on context cancellation, and emits `SYZFAIL` text on plugin errors.

## State and Persistence Behavior

Pool state includes current proxy pointer, fixed pool count, mutex, close channel, and close result channel. `ProxyApp` stores the RPC client, transfer-content mode, subprocess cancel function, lifecycle channels, and log-polling channels. Transfer-content mode reads image, workdir files, or copied files into RPC request payloads. No durable state is stored locally beyond spawned subprocess lifetime and network connections.

## Dependencies and Integration Points

It depends on `net/rpc/jsonrpc`, TLS/x509, subprocess pipes, `proxyrpc` contracts, syzkaller logging, `vmimpl` interfaces, and `report.Report`. External plugins must implement service name `ProxyVM`.

## Risks and Test Signals

The supervisor must avoid races between close, lost connection, and reinit. Log polling can turn RPC errors into reconnect triggers. File-content transfer may be expensive and uses `WalkDir` path trimming that can produce leading separators. Mutual TLS is unimplemented. Tests cover constructor success/failures, create/copy/forward/diagnose/run RPC behavior, timeout stop, progress errors, TCP/TLS connection setup, lost connection reinit, and subprocess pipe failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_mocks_test.go -->
# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_mocks_test.go

## Purpose

`proxyappclient_mocks_test.go` contains test-local mock and fixture support for proxyapp client tests.

## Important APIs, Types, and Functions

The file defines helper mock command runner/process fixtures used by `proxyappclient_test.go`, including mock command runner setup, subprocess pipe behavior, and server fixture initialization around `proxyrpc.ProxyAppInterface`.

## Control Flow

Fixtures create in-memory pipes, a JSON-RPC server registered as `ProxyVM`, a fake subprocess command exposing those pipes, and default mock expectations for `CreatePool` and log polling. Tests customize returned errors or RPC replies per scenario.

## State and Persistence Behavior

All state is in memory: pipes, mock expectations, channels for wait/log notifications, and RPC server goroutines. No filesystem or network state is required for piped-mode tests.

## Dependencies and Integration Points

It depends on `net/rpc/jsonrpc`, `io.Pipe`, `testify/mock`, `proxyrpc`, and proxyapp's `subProcessCmd` abstraction. It is a support layer rather than production code.

## Risks and Test Signals

Fixture correctness is important because dead pipes or missing expectations can hang tests. The main signal is the broader proxyapp client test suite passing without leaked goroutines or unmet mock expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_mocks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_tcp_test.go -->
# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_tcp_test.go

## Purpose

`proxyappclient_tcp_test.go` tests proxyapp's TCP and TLS JSON-RPC connection modes and reconnection behavior when server connections are closed.

## Important APIs, Types, and Functions

Key helpers are `testTCPEnv`, `testTCPEnvTLS`, `proxyAppServerTCPFixture`, `proxyAppServerTCPFixtureTLS`, `makeMockProxyAppServerWithListener`, `makeMockProxyAppServer`, and `makeMockProxyAppServerTLS`. Tests include successful TCP construction, successful TLS construction with generated certs, and lost-connection reinitialization scenarios.

## Control Flow

The tests create a loopback listener, register a mock `ProxyVM` service over JSON-RPC, build a proxyapp environment pointing at the listener, and call `ctor`. TLS tests generate a self-signed localhost certificate and pass it through `server_tls_cert`. Lost-connection tests close accepted connections and assert the client reconnects or remains unable to initialize depending on server behavior.

## State and Persistence Behavior

The tests create local listeners, accepted TCP/TLS connections, generated certificate files where needed, and in-memory mock state. Cleanup is coordinated by the test context and connection close helper.

## Dependencies and Integration Points

They exercise `initNetworkRPCClient`, TLS root pool handling, URI parsing, log polling, supervisor reconnect behavior, and `pool.proxy` state transitions.

## Risks and Test Signals

The listener goroutine panics on accept errors, so cleanup ordering matters. Generated cert validity and DNS name must match `localhost`. Strong signals are successful non-TLS and TLS pool creation, reconnect after closed connections, and nil proxy state while reinit cannot complete.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_tcp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_test.go -->
# sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_test.go

## Purpose

`proxyappclient_test.go` is the main unit suite for piped proxyapp client behavior. It verifies constructor failures, pool creation, close behavior, and instance method RPC translations.

## Important APIs, Types, and Functions

Tests cover `ctor`, `pool.Create`, `pool.Close`, `instance.Close`, `Diagnose`, `Copy`, `Forward`, and `Run`. Helpers include `makeTestParams`, `makeMockProxyAppProcess`, `poolFixture`, `proxyAppServerFixture`, `createInstanceFixture`, and `contextWithTimeout`.

## Control Flow

Fixtures run an in-memory JSON-RPC server over pipes exposed by a mocked subprocess command. Tests set mock expectations for RPC calls, invoke the proxyapp pool or instance methods, and assert return values, errors, output chunks, and timeout behavior. Run tests simulate `RunStart`, repeated `RunReadProgress`, plugin errors, RPC errors, finished replies, and cancellation.

## State and Persistence Behavior

The tests use in-memory pipes, goroutines, mock state, and contexts. They do not launch real subprocesses or VMs.

## Dependencies and Integration Points

They exercise piped JSON-RPC setup, log polling, pool-size enforcement, instance ID propagation, error-to-output conversion through `clientErrorf`, and `vmimpl.ErrTimeout` behavior.

## Risks and Test Signals

Some TODOs remain for periodic subprocess crash handling and pool close plugin API behavior. Strong signals include constructor errors for bad config or broken pipes, create failures surfacing, copy/forward/diagnose RPC mapping, run timeout calling `RunStop`, plugin progress errors producing `SYZFAIL`, and finished progress returning nil error.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyappclient_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyrpc/proxyrpc.go -->
# sources/test-tools/syzkaller/vm/proxyapp/proxyrpc/proxyrpc.go

## Purpose

`proxyrpc.go` defines the JSON-RPC service contract between syzkaller's proxyapp VM backend and external proxy VM plugins.

## Important APIs, Types, and Functions

The main interface is `ProxyAppInterface` with methods `CreatePool`, `CreateInstance`, `Diagnose`, `Copy`, `Forward`, `RunStart`, `RunStop`, `RunReadProgress`, `Close`, and `PoolLogs`. Request/reply structs include `CreatePoolParams/Result`, `CreateInstanceParams/Result`, `CopyParams/Result`, `ForwardParams/Result`, `RunStartParams/Reply`, `RunStopParams/Reply`, `RunReadProgressParams/Reply`, `CloseParams/Reply`, `DiagnoseParams/Reply`, and `PoolLogsParam/Reply`.

## Control Flow

There is no executable control flow. The client calls these methods under service name `ProxyVM`; plugins implement the interface and fill reply structs. Run execution is split into start, progress polling, stop, and close operations.

## State and Persistence Behavior

The structs carry state across RPC boundaries: pool config, image/workdir/file byte payloads, instance IDs, run IDs, output chunks, errors, finish flags, and log messages. Persistence is plugin-defined.

## Dependencies and Integration Points

It is imported by the proxyapp client, tests, generated mocks, and external plugin implementations. It intentionally carries simple JSON-serializable fields.

## Risks and Test Signals

Interface changes are wire-contract changes for plugins and require mock regeneration. Large byte fields can be expensive when transfer-content mode is enabled. Tests should verify backward-compatible plugin behavior, run progress sequencing, error propagation, and pool log verbosity handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/proxyapp/proxyrpc/proxyrpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/qemu.go -->
# sources/test-tools/syzkaller/vm/qemu/qemu.go

## Purpose

`qemu.go` implements syzkaller's QEMU VM backend. It builds architecture-specific QEMU command lines, boots images or injected kernels, waits for SSH, copies and runs binaries, forwards manager ports, gathers diagnostics, and supports optional snapshot acceleration hooks.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, `instance`, and `archConfig`; `archConfigs` maps OS/arch pairs to defaults. Important functions include `ctor`, `Pool.Count`, `Pool.Create`, `Pool.ctor`, `Close`, `boot`, `buildQemuArgs`, `handleVfioPciArg`, `splitArgs`, `Forward`, `targetDir`, `Copy`, `Run`, `Info`, `Diagnose`, `needsRegisterInfo`, `ssh`, and `sshArgs`. The file also contains the 9p `initScript`.

## Control Flow

`ctor` validates config, image/kernel requirements, CPU/memory limits, QEMU binary presence, and captures QEMU version. `Create` prepares special 9p SSH/init files when needed, then retries `Pool.ctor` on transient host-forwarding conflicts. `boot` creates a monitor port, builds args, starts QEMU, starts console merging, optionally performs snapshot handshake, and waits for SSH. `Run` either runs `syz-execprog` on host for host-fuzzer targets or starts an SSH command in the guest target directory and multiplexes output.

## State and Persistence Behavior

Instance state includes QEMU args, image path, workdir, SSH options, monitor connection, pipes, process, output merger, copied host-fuzzer file map, forward port, and optional snapshot state. The backend starts/kills QEMU processes, may write 9p init/key files, copies binaries by SCP, and uses QEMU `-snapshot` to avoid modifying disk images when configured.

## Dependencies and Integration Points

It depends on QEMU system binaries, SSH/SCP, syzkaller target metadata, `vmimpl` multiplex and diagnostics, QMP/HMP helpers in `qmp.go`, and snapshot helpers in platform-specific files. It is the broadest default VM backend used by syz-manager.

## Risks and Test Signals

Command-line construction is complex and architecture-sensitive. Simple whitespace splitting for `QemuArgs` cannot preserve quoted arguments. Port allocation is race-prone but retried for known errors. Diagnosis uses QMP register collection only for selected crash types. Integration signals include boot across all supported OS/arch configs, 9p boot, host-fuzzer mode, VFIO placeholder expansion, forwarding conflicts, copy/run timeout behavior, and register diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/qemu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/qmp.go -->
# sources/test-tools/syzkaller/vm/qemu/qmp.go

## Purpose

`qmp.go` implements QEMU Machine Protocol support used by the QEMU backend for monitor commands and HMP passthrough diagnostics.

## Important APIs, Types, and Functions

Types are `qmpVersion`, `qmpBanner`, `qmpCommand`, `hmpCommand`, and `qmpResponse`. Methods are `qmpConnCheck`, `qmpRecv`, `doQmp`, `qmp`, and `hmp`.

## Control Flow

`qmpConnCheck` lazily dials the monitor TCP port, decodes the QMP banner, initializes JSON encoder/decoder, sends `qmp_capabilities`, and stores the connection. `qmpRecv` skips asynchronous event messages until it gets a command response. `qmp` sends a command, validates error/return fields, and treats HMP textual `Error:` or `unknown command:` replies as errors. `hmp` wraps a human monitor command in `human-monitor-command` with CPU index and returns the string output.

## State and Persistence Behavior

The monitor connection, encoder, and decoder are stored on the QEMU instance and reused. No external state is persisted beyond QEMU monitor side effects from commands.

## Dependencies and Integration Points

It depends on `net`, `encoding/json`, QEMU QMP/HMP protocols, and `qemu.go` instance fields. `Diagnose` uses `hmp("info registers", cpu)` to collect register dumps.

## Risks and Test Signals

The code assumes one outstanding synchronous command at a time and skips all events. A failed capability negotiation clears encoder/decoder but leaves the raw conn for GC/close only through caller state. Type assertions assume HMP returns a string. Tests should use a fake QMP server to cover banner decode, capability failure, event skipping, error responses, missing returns, and HMP error text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/qmp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/snapshot_linux.go -->
# sources/test-tools/syzkaller/vm/qemu/snapshot_linux.go

## Purpose

`snapshot_linux.go` implements Linux-only QEMU snapshot acceleration support using ivshmem shared memory, an eventfd doorbell, and syzkaller flatrpc snapshot headers.

## Important APIs, Types, and Functions

The `snapshot` struct stores ivshmem listener/connection, doorbell/event/shmem file descriptors, mapped shared memory, input slice, and `flatrpc.SnapshotHeaderT`. Methods include `snapshotClose`, `snapshotEnable`, `snapshotHandshake`, `SetupSnapshot`, and `RunSnapshot`.

## Control Flow

`snapshotEnable` creates memfds for shared memory and doorbell, sizes and mmaps shared memory, maps input/header regions, creates an eventfd, listens on a Unix socket for ivshmem setup, and returns QEMU args enabling migration/snapshot-compatible ivshmem devices. `snapshotHandshake` accepts the ivshmem connection and sends protocol/version, VM id, doorbell, and eventfd descriptors. `SetupSnapshot` writes initial input, coordinates executor handshake state through the shared header, enables QMP `x-ignore-shared`, and saves the `syz` VM snapshot. `RunSnapshot` writes new input, restores the VM snapshot with `loadvm syz`, waits for completion notification via eventfd/header state, and returns result/output.

## State and Persistence Behavior

State is held in file descriptors, a Unix socket, and a shared mmap region. It persists for the lifetime of the QEMU instance and is cleaned by `snapshotClose`. Input and execution status are communicated through shared memory rather than files.

## Dependencies and Integration Points

It depends on Linux `memfd_create`, `eventfd`, Unix sockets with file-descriptor passing, `syscall.Mmap`, `flatrpc` snapshot constants/header layout, QEMU ivshmem, and QMP snapshot/migration commands. `qemu.go` calls these hooks when `env.Snapshot` enables snapshot mode.

## Risks and Test Signals

This code is tightly coupled to QEMU ivshmem behavior and the executor snapshot protocol. Descriptor leaks, mmap lifetime bugs, endian/header mismatches, restore timeouts, and shared-memory races are high-risk. Tests require Linux integration with QEMU snapshot support, fd-passing validation, repeated `RunSnapshot` cycles, timeout/error handling, and cleanup after failed handshake.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/snapshot_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/snapshot_unimpl.go -->
# sources/test-tools/syzkaller/vm/qemu/snapshot_unimpl.go

## Purpose

`snapshot_unimpl.go` provides non-Linux stubs for QEMU snapshot acceleration so the qemu package compiles on platforms without the Linux-specific ivshmem/eventfd implementation.

## Important APIs, Types, and Functions

It defines empty `snapshot`, package-level `errNotImplemented`, and methods `snapshotClose`, `snapshotEnable`, `snapshotHandshake`, `SetupSnapshot`, and `RunSnapshot`.

## Control Flow

All snapshot operations except close return `errNotImplemented`; close is a no-op. Build tags select this file for `!linux`.

## State and Persistence Behavior

No state is stored or persisted.

## Dependencies and Integration Points

It integrates with `qemu.go` by satisfying the same method set as the Linux implementation. If snapshot mode is requested on non-Linux, QEMU argument construction or setup fails with the not-implemented error.

## Risks and Test Signals

The error message contains a spelling mistake but is otherwise straightforward. Build tests on non-Linux should verify qemu package compilation and clear failure when snapshots are enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/qemu/snapshot_unimpl.go -->
