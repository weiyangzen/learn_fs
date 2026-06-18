# subset-b-009521 Research

This grouped report covers the assigned syzkaller VM implementation files and unionmount testsuite files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/starnix/starnix.go -->
# sources/test-tools/syzkaller/vm/starnix/starnix.go

Purpose: implements the syzkaller VM backend for Fuchsia Starnix, registering `targets.Starnix` with `vmimpl` and exposing Starnix containers as SSH-driven test instances.

Important APIs/types/functions: `Config`, `Pool`, `instance`, `ctor`, `Pool.Create`, `Pool.Close`, `instance.boot`, `startFuchsiaVM`, `startFuchsiaLogs`, `startSshdAndConnect`, `connect`, `ffxCommand`, `runFfx`, `Copy`, `Forward`, `Run`, `Info`, `setFuchsiaVersion`, `getFuchsiaBuildDir`, and `GetToolPath`. The backend implements `vmimpl.Infoer`.

Control flow: `ctor` parses JSON config and creates an isolated temporary `ffx` directory. `Create` resolves `ffx`/`ffx-log` from Fuchsia `tool_paths.json`, copies selected default `ffx` config values into the isolate, discovers SSH keys, records the Fuchsia version, then boots. Boot stops any stale emulator by name, starts a headless emulator, runs Starnix Alpine and sshd components, copies the SSH authorized key into the component namespace, creates a host-local SSH bridge, and starts `ffx log` into an `OutputMerger`. `Run` starts host `ssh`, attaches stdout/stderr streams, and uses `vmimpl.Multiplex`.

State and persistence: runtime state is mostly process handles, pipes, ports, the `ffx` isolate directory, and output merger state. Persistent source-side reads are `.fx-build-dir` and `tool_paths.json`; guest copies go to `/tmp`. `Pool.Close` removes the isolate directory so `ffx` daemon state is discarded.

Dependencies and integration: depends on Fuchsia checkout layout, `ffx`, `ffx-log`, component URLs for `syzkaller_starnix`, host SSH/SCP, syzkaller `osutil`, `config`, `targets`, and `vmimpl` output/SSH helpers. It integrates with the generic `vm` monitor through the `vmimpl.Instance` contract.

Risks: heavily tied to Fuchsia tooling and component monikers; SSH bridge readiness is a fixed sleep; `Forward` allows only one reverse-forward port; `Diagnose` is empty, so crash triage relies on existing logs; `Close` ignores most command errors; `GetToolPath` assumes current Fuchsia build metadata.

Test signals: no direct test file is assigned. Practical coverage comes from VM integration runs that validate emulator boot, Starnix sshd startup, SCP, `Run`, and log merger behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/starnix/starnix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/virtualbox/virtualbox.go -->
# sources/test-tools/syzkaller/vm/virtualbox/virtualbox.go

Purpose: implements a VirtualBox-backed syzkaller VM pool that clones a named base VM, configures SSH NAT and a serial console, runs commands over SSH, and streams kernel output through the common VM monitor.

Important APIs/types/functions: `Config` (`base_vm_name`, `count`), `Pool`, `instance`, `ctor`, `Pool.Create`, `clone`, `boot`, `Forward`, `Close`, `Copy`, `Run`, and `Diagnose`.

Control flow: `ctor` parses config, validates count, base VM name, and `VBoxManage` availability. `Create` assigns a deterministic `syzkaller_vm_<index>` clone name, creates long pipes, calls `clone` and `boot`. `clone` runs `VBoxManage clonevm`, creates a random host NAT forwarding rule to guest port 22, and configures UART1 as a Unix socket. `boot` starts the VM headless, connects to the serial socket, starts an output merger, collects boot output while `WaitForSSH` probes the forwarded SSH port, and returns `BootError` with captured logs on failure. `Run` opens SSH stdout/stderr pipes, optionally adds reverse forwarding, and delegates lifecycle to `vmimpl.Multiplex`.

State and persistence: each instance creates a registered VirtualBox clone plus a serial socket under the workdir. `Close` powers off and unregisters/deletes the clone, closes pipes/sockets, and waits for merger goroutines. Guest copies land at `/`.

Dependencies and integration: depends on `VBoxManage`, host SSH/SCP, Unix domain sockets, syzkaller `osutil`, `vmimpl.SSHOptions`, `WaitForSSH`, `SCP`, and `Multiplex`.

Risks: clone names collide across concurrent pools with the same index; serial socket connection may race VM boot; cleanup ignores `VBoxManage` failures; NAT rule names derive from random ports but are not retried after modify failures; `Diagnose` is a stub.

Test signals: no direct unit tests are assigned. Validation is integration-level: clone, boot, SSH, serial console, command execution, and cleanup must all work on a host with VirtualBox.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/virtualbox/virtualbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vm.go -->
# sources/test-tools/syzkaller/vm/vm.go

Purpose: high-level VM abstraction used by syzkaller managers and tools. It wraps `vmimpl` backends with pool creation, per-instance workdirs, snapshot helpers, command execution monitoring, crash report extraction, diagnostics, output trimming, shutdown handling, and dispatcher integration.

Important APIs/types/functions: `Pool`, `Instance`, `ShutdownCtx`, `vmType`, `AllowsOvercommit`, `Create`, `Pool.Create`, `Pool.Close`, `SetupSnapshot`, `RunSnapshot`, `Copy`, `Forward`, `RunOptions`, `WithExitCondition`, `WithBeforeContext`, `WithInjectExecuting`, `WithEarlyFinishCb`, `Instance.Run`, `RunStream`, `Info`, `Close`, `NewDispatcher`, and the internal `monitor`.

Control flow: `Create` resolves the registered backend type, builds `vmimpl.Env`, invokes its constructor, applies debug count limiting, and records timeout/stat configuration. `Pool.Create` makes a process temp workdir, optionally copies a template, asks the backend to create an instance, and increments active count. `Instance.Run` calls backend `Run`, then `monitorExecution` multiplexes VM chunks, command errors, timeouts, injected execution heartbeats, and global shutdown. It converts normal/error/timeout/no-output outcomes into parsed reports or synthetic reports, calls backend diagnostics when needed, waits briefly for delayed output, and trims reports to configured context.

State and persistence: each instance owns a temp workdir removed on `Close`; pool state tracks active instance count and output byte stats. Snapshot state is a boolean guard enforcing `SetupSnapshot` before `RunSnapshot`.

Dependencies and integration: imports all backend packages for registration, plus manager config, target timeouts, report parsing, crash types, stats, dispatcher, and `vmimpl`. It is the main integration point between VM backends and syzkaller execution/reporting code.

Risks: `Pool.Close` panics if instances remain active; monitor assumes `extractErrors` is called once; `NoOutput` depends on either console output or explicit execution markers; report trimming can drop far-back context; default synthetic errors may race with late kernel crashes; global `Shutdown` is process-wide.

Test signals: `vm_test.go` covers monitor exit conditions, diagnostics, preemption, no-output detection, delayed crashes, output trimming, nil output channels, VM type parsing, and multiple-error extraction. `vm_full_test.go` covers repeated real command runs through `Multiplex`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vm_full_test.go -->
# sources/test-tools/syzkaller/vm/vm_full_test.go

Purpose: integration-style unit test for repeated `Instance.Run` calls through the real `vmimpl.Multiplex` path without requiring an external VM.

Important APIs/types/functions: `localInstancePool`, `localInstance`, `makeLocalInstance`, `localInstance.Run`, init-time `vmimpl.Register("test-local")`, and `TestMultipleRun`.

Control flow: the local backend creates an `OutputMerger`, splits the requested command into executable/args, runs it in the instance workdir with stdout/stderr pipes, and uses `vmimpl.Multiplex`. `TestMultipleRun` creates a Linux/AMD64 syzkaller VM wrapper using the local backend and runs `echo Hello` three times with `ExitNormal`, checking that each run returns exactly `Hello\n`.

State and persistence: test state is a temporary workdir, local process pipes, and merger goroutines. No guest or persistent external state is created.

Dependencies and integration: depends on `osutil.LongPipe`, `osutil.Command`, `vmimpl.OutputMerger`, `vmimpl.Multiplex`, generic `vm.Run`, and the helper `makeLinuxAMD64Futex` from `vm_test.go`.

Risks: command parsing uses `strings.Split`, so it is only suitable for simple test commands; `Copy` and `Forward` are stubs; this test exercises command lifecycle but not crash parsing.

Test signals: verifies that a single instance can be reused for multiple runs and that merger state remains usable across sequential command executions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vm_full_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vm_test.go -->
# sources/test-tools/syzkaller/vm/vm_test.go

Purpose: regression tests for the high-level VM monitor, synthetic crash conversion, diagnostics, output buffering, preemption handling, no-output detection, and VM type parsing.

Important APIs/types/functions: fake `testPool`, `testInstance`, registered `"test"` backend, `withTestRunOptionsDefaults`, table-driven `tests`, `TestMonitorExecution`, `TestNilChannelBlock`, `makeLinuxAMD64Futex`, `testMonitorExecution`, `TestVMType`, `TestExtractMultipleErrors`, and embedded Linux KASAN fixture constants.

Control flow: fake instances expose buffered output and error channels. Each table case drives those channels to model normal exit, unexpected exit, kernel crash, delayed crash, diagnostics producing crashes, direct diagnostic output, timeout, command error, no output, executed-program heartbeats, closed output channels, split lines, and preempted executor strings. `testMonitorExecution` runs the monitor with short tick periods and asserts expected reports, titles, output snippets, types, or errors.

State and persistence: all state is in memory plus temporary manager workdirs. The init function mutates global `vmimpl.WaitForOutputTimeout` to keep tests short.

Dependencies and integration: uses Linux/AMD64 target metadata, `report.NewReporter`, `crash` types, `testify`, and the real `vm.Create`/`Instance.Run` wrapper.

Risks: global timeout mutation can affect other tests in the same package; fake channels intentionally bypass real backend process behavior; expected output snippets are sensitive to report parser changes.

Test signals: strong coverage of monitor control-flow edge cases, including single early-finish callback invocation, avoiding nil-channel blocking, `proxyapp:*` type stripping, and returning two parsed reports from one output buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console.go

Purpose: non-Windows console helpers for VM implementations, covering direct TTY serial consoles and command-backed remote console streams.

Important APIs/types/functions: `OpenConsole`, `tty.Read`, `tty.Close`, `OpenRemoteKernelLog`, `OpenRemoteConsole`, `OpenAdbConsole`, `OpenConsoleByCmd`, `remoteCon.Read`, and `remoteCon.Close`.

Control flow: `OpenConsole` opens a console device with `O_NOCTTY|O_SYNC`, reads termios using platform constants, configures 115200 8N1 non-canonical mode, and returns a lock-protected `tty`. Remote helpers build SSH/ADB/dmesg commands and call `OpenConsoleByCmd`, which creates a long pipe, starts the command with stdout/stderr to the pipe, and returns a `remoteCon` that kills the process and closes the pipe on `Close`.

State and persistence: runtime state is file descriptors, command processes, and read/close locks. No persistent files are written.

Dependencies and integration: depends on `golang.org/x/sys/unix`, `syscall`, `osutil.LongPipe`, and platform-specific `console_*` constants. VM backends add returned readers to `OutputMerger`.

Risks: direct console setup depends on correct ioctl constants per host arch; `OpenRemoteKernelLog` hardcodes `vsoc-01@`; command close kills processes bluntly; direct TTY read serializes reads and returns EOF after close.

Test signals: no direct assigned test. Merger/backend integration validates readers indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_darwin.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_darwin.go

Purpose: Darwin-specific terminal ioctl constants used by `console.go`.

Important APIs/types/functions: constants `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS`; the latter two map to `syscall.TIOCGETA` and `syscall.TIOCSETA`.

Control flow: no runtime logic. The file supplies compile-time constants selected by Go build constraints through filename suffix.

State and persistence: none.

Dependencies and integration: imports `syscall` and integrates with `OpenConsole` termios get/set calls.

Risks: baud and flow-control masks are zero on Darwin, so Linux-style bit clearing is intentionally inert; real serial behavior depends on Darwin termios compatibility.

Test signals: build coverage on Darwin is the main signal; no direct unit test is assigned.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_freebsd.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_freebsd.go

Purpose: FreeBSD placeholder constants for shared console code.

Important APIs/types/functions: zero-valued `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS`.

Control flow: no runtime logic; it only satisfies symbols referenced by `console.go`.

State and persistence: none.

Dependencies and integration: no imports. It participates in cross-platform builds of `vmimpl`.

Risks: the comment says it is merely to fix build, so direct `OpenConsole` termios use on FreeBSD may not work correctly with zero ioctl request values.

Test signals: compile-only coverage; FreeBSD VM diagnosis is handled separately in `freebsd.go`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_386.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_linux_386.go

Purpose: Linux 386 constants for shared serial-console termios setup.

Important APIs/types/functions: maps `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` to `golang.org/x/sys/unix` constants, using `TCGETS2`/`TCSETS2`.

Control flow: no runtime logic. The file is selected by architecture-specific filename.

State and persistence: none.

Dependencies and integration: imported by build selection into the `vmimpl` package so `OpenConsole` can set baud, character size, parity, stop bits, and hardware flow control.

Risks: comment notes it builds but is not tested; ioctl support can vary by device/host kernel.

Test signals: compile and any host-side serial console use on linux/386.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_386.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_amd64.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_linux_amd64.go

Purpose: Linux AMD64 constants for `OpenConsole` termios manipulation.

Important APIs/types/functions: maps baud and flow-control masks plus `TCGETS2`/`TCSETS2` ioctl request constants from `golang.org/x/sys/unix`.

Control flow: no functions; build-system filename selection supplies constants.

State and persistence: none.

Dependencies and integration: used by `console.go` on common Linux hosts, including syzkaller development and CI environments.

Risks: assumes `TCGETS2`/`TCSETS2` are appropriate for the opened console device. Errors propagate from `OpenConsole` if unsupported.

Test signals: indirect coverage from Linux backend runs that open physical or emulated serial consoles.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_amd64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm.go

Purpose: Linux ARM constants for shared console setup.

Important APIs/types/functions: maps `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` to `unix.CBAUD`, `unix.CRTSCTS`, `unix.TCGETS2`, and `unix.TCSETS2`.

Control flow: compile-time constants only.

State and persistence: none.

Dependencies and integration: feeds `OpenConsole` on ARM Linux hosts.

Risks: file comment notes it compiles but was not tested; unsupported ioctl behavior appears as console-open failure.

Test signals: build coverage and any ARM host serial-console integration run.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm64.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm64.go

Purpose: Linux ARM64 constants for `vmimpl.OpenConsole`.

Important APIs/types/functions: provides `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` from `golang.org/x/sys/unix`.

Control flow: no executable logic; selected by filename.

State and persistence: none.

Dependencies and integration: supports serial console access on ARM64 Linux hosts.

Risks: comment says compile-only confidence; host/device termios support remains the runtime risk.

Test signals: compile and platform integration coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_arm64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_ppc64le.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_linux_ppc64le.go

Purpose: PPC64LE Linux placeholder constants for shared console code.

Important APIs/types/functions: zero-valued baud, flow-control, and ioctl constants.

Control flow: none.

State and persistence: none.

Dependencies and integration: exists so `vmimpl` builds on linux/ppc64le.

Risks: comment says PPC64LE host with adb VMs is not tested; direct console opening likely fails if ioctl constants are required.

Test signals: compile-only unless a PPC64LE host exercises `OpenConsole`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_ppc64le.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_riscv64.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_linux_riscv64.go

Purpose: Linux RISC-V 64 constants for serial console termios configuration.

Important APIs/types/functions: maps `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS` to `unix` package constants.

Control flow: no runtime behavior.

State and persistence: none.

Dependencies and integration: enables `OpenConsole` builds and runtime attempts on riscv64 Linux hosts.

Risks: no local behavioral tests; device/ioctl compatibility is discovered only at runtime.

Test signals: architecture build coverage and host-console integration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_riscv64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_s390x.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_linux_s390x.go

Purpose: Linux s390x constants for the common console opener.

Important APIs/types/functions: defines baud mask, hardware flow-control mask, and `TCGETS2`/`TCSETS2` constants from `golang.org/x/sys/unix`.

Control flow: constants only.

State and persistence: none.

Dependencies and integration: supports `OpenConsole` on s390x Linux builds.

Risks: lacks direct tests; the termios2 ioctl path may not match all console devices.

Test signals: compile and platform integration runs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_linux_s390x.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_netbsd.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_netbsd.go

Purpose: NetBSD placeholder constants for shared console code.

Important APIs/types/functions: zero-valued `unixCBAUD`, `unixCRTSCTS`, `syscallTCGETS`, and `syscallTCSETS`.

Control flow: none.

State and persistence: none.

Dependencies and integration: compile-time integration with `console.go`.

Risks: marked as build-only; direct console termios setup is unlikely to be functional without real NetBSD ioctl values.

Test signals: build coverage only.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_openbsd.go -->
# sources/test-tools/syzkaller/vm/vmimpl/console_openbsd.go

Purpose: OpenBSD placeholder constants for shared console code.

Important APIs/types/functions: zero-valued termios masks and ioctl constants.

Control flow: no executable logic.

State and persistence: none.

Dependencies and integration: keeps `vmimpl` compiling on OpenBSD-related builds; OpenBSD VM diagnosis itself is in `openbsd.go`.

Risks: direct `OpenConsole` use is build-satisfied but not behaviorally implemented.

Test signals: compile-only coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/console_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/freebsd.go -->
# sources/test-tools/syzkaller/vm/vmimpl/freebsd.go

Purpose: helper for collecting additional diagnostics from a panicked FreeBSD kernel through an interactive debugger console.

Important APIs/types/functions: `DiagnoseFreeBSD(w io.Writer)`.

Control flow: writes a blank line, disables debugger pagination and line wrapping, then sends `show registers`, `show proc`, `ps`, lock, malloc, UMA, and TCP control-block commands, sleeping one second between commands. It returns `nil, true`, meaning diagnostic output is expected to arrive asynchronously on the console stream.

State and persistence: no durable state; it only writes debugger commands to the provided writer.

Dependencies and integration: depends on an `io.Writer` connected to a FreeBSD DDB prompt. VM backends can call it from `Instance.Diagnose` when the parsed report suggests a FreeBSD panic.

Risks: if the console is not at DDB, commands may be typed into a login shell or lost; fixed sleeps make diagnosis slow; returned output is not captured directly.

Test signals: no direct unit test is assigned. Integration requires a FreeBSD VM panic path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/linux.go -->
# sources/test-tools/syzkaller/vm/vmimpl/linux.go

Purpose: Linux-specific post-crash diagnostic helper for reports that need extra VM-side state.

Important APIs/types/functions: `DiagnoseLinux(rep *report.Report, ssh func(args ...string) ([]byte, error))`.

Control flow: checks the report title for `MAX_LOCKDEP`; if absent, returns unhandled. For lockdep-capacity reports, it runs `cat /proc/lockdep_stats /proc/lockdep /proc/lockdep_chains` through the supplied SSH callback, records any command error as bytes, strips large pointer-like hex values with a regexp, and returns the output with `handled=true`.

State and persistence: no persistent state; only reads procfs from the guest through SSH.

Dependencies and integration: depends on `pkg/report` and a backend-provided SSH function. Integrated from VM backends that can diagnose Linux guests.

Risks: narrow trigger substring; proc files can be huge or unavailable; regexp may remove useful numeric context; command failures become text rather than errors.

Test signals: no direct assigned test. Monitor tests cover diagnostic plumbing generically, not this Linux-specific command.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/merger.go -->
# sources/test-tools/syzkaller/vm/vmimpl/merger.go

Purpose: merges multiple VM output streams, preserves output type metadata, optionally tees complete lines, and reports reader errors to command lifecycle code.

Important APIs/types/functions: `OutputType`, `Chunk`, `MergerError`, `OutputMerger`, `NewOutputMerger`, `Wait`, `Errors`, `Add`, `AddDecoder`, and `runDecoder`.

Control flow: each added reader gets a goroutine that reads 4 KiB chunks. If a protocol decoder is supplied, decoded payloads are emitted separately. Raw output is buffered until the last newline, then cloned and sent as a `Chunk`; incomplete trailing data is newline-terminated on read error. `Errors(ctx)` creates an errgroup waiting for active decoders to finish and returns the first non-nil `MergerError`. `Wait` waits for all decoders and closes the public output channel.

State and persistence: state is in memory: output channel, per-name decoder state, wait group, pending buffers, and optional tee writer lock. No files are written except through the caller-provided tee.

Dependencies and integration: used by VM backends to combine console, stdout, and stderr for the high-level monitor and by `vmimpl.Multiplex` to detect EOF/failure.

Risks: `Add` with an existing name replaces error state while old goroutine may still run; output sends are lossy under backpressure due to default case; error is always wrapped, including expected EOF; decoders must return valid slice indexes.

Test signals: `merger_test.go` covers incomplete-line buffering, tee ordering, EOF errors, persistent error reporting, replacing decoder state by name, and hanging background readers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/merger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/merger_test.go -->
# sources/test-tools/syzkaller/vm/vmimpl/merger_test.go

Purpose: unit tests for `OutputMerger` line buffering, tee output, error reporting, and decoder-state replacement.

Important APIs/types/functions: `TestMerger`, `brokenReader`, and `TestMergerErrors`.

Control flow: `TestMerger` creates two long pipes, writes partial data that must not emit until newline, verifies completed lines from each pipe, closes pipes to force EOF, checks `MergerError` fields, waits for merger shutdown, and compares tee content. `TestMergerErrors` adds a failing reader plus a hanging background pipe, verifies the first error, verifies the same error persists across `Errors` calls, re-adds the same decoder name with a new failure, and confirms the new error replaces the old state.

State and persistence: all state is in-memory pipes, a bytes buffer tee, and goroutines.

Dependencies and integration: uses `osutil.LongPipe`, `context`, `testify/assert`, and real `OutputMerger` APIs.

Risks: timing-dependent no-output checks use a short sleep; expected ordering matches current implementation rather than a fully robust interleaving model.

Test signals: direct coverage for line completeness, trailing newline insertion on close, tee serialization, EOF wrapping, and name replacement behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/merger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/openbsd.go -->
# sources/test-tools/syzkaller/vm/vmimpl/openbsd.go

Purpose: helper for retrieving OpenBSD DDB diagnostics after a panic or hang.

Important APIs/types/functions: `DiagnoseOpenBSD(w io.Writer)`.

Control flow: writes debugger commands to disable pagination/wrapping, show panic, trace, registers, process lists, locks, malloc/pools, and traces for CPU 0 and CPU 1. It sleeps one second after each command and returns `nil, true` to ask the caller to wait for console output.

State and persistence: no durable state; command text is sent to the provided console writer.

Dependencies and integration: depends only on `io` and `time`. The OpenBSD `vmm` backend calls it from `Diagnose`.

Risks: typo in comment aside, functionality assumes the console is at DDB; if not, commands may have side effects in a shell. Fixed sleeps slow triage.

Test signals: no direct unit test. Indirect coverage comes from OpenBSD VM crash integration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/util.go -->
# sources/test-tools/syzkaller/vm/vmimpl/util.go

Purpose: shared utility functions for VM implementations, especially interruptible sleep, SSH/SCP option construction, waiting for SSH boot readiness, random port allocation, and shell double-quote escaping.

Important APIs/types/functions: `SleepInterruptible`, `SSHOptions`, `WaitForSSH`, `ErrCantSSH`, `SSHArgs`, `SSHArgsForward`, `SCPOptions`, `SCP`, `RandomPort`, `UnusedTCPPort`, and `EscapeDoubleQuotes`.

Control flow: `WaitForSSH` sleeps briefly, then every five seconds runs `ssh user@addr pwd` or Windows `dir` until success, stop-channel error, global shutdown, or timeout. SSH/SCP argument helpers add isolated config, known-host suppression, identity options, timeouts, optional key, verbose mode, and reverse forwarding. `SCP` runs legacy-protocol `scp` with timeout and wraps failures. `UnusedTCPPort` samples random high ports until `net.Listen` succeeds or an unexpected listen error is fatal. `EscapeDoubleQuotes` walks bytes and re-escapes double quotes and quote-directed backslash sequences.

State and persistence: no durable state. Port allocation is inherently transient; SSH/SCP operate on guest/host files as requested by callers.

Dependencies and integration: used by most VM backends for boot readiness, file copy, command forwarding, and safe shell construction.

Risks: random free port can race later bind; `WaitForSSH` consumes only one stop error and can wait full intervals; `scp -O` assumes legacy protocol availability; escaping is byte-oriented and bash-specific.

Test signals: exercised indirectly by backend integration tests; no direct unit test is assigned here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/vmimpl.go -->
# sources/test-tools/syzkaller/vm/vmimpl/vmimpl.go

Purpose: defines the low-level VM backend interface and shared process/output lifecycle machinery used by all syzkaller VM implementations.

Important APIs/types/functions: `Pool`, `Instance`, `Infoer`, `Env`, `BootError`, `MakeBootError`, `InfraError`, `Register`, `Type`, global `Shutdown`, `ErrTimeout`, `ErrPreempted`, `Types`, `CmdCloser`, `MultiplexConfig`, `Multiplex`, `waitAndKill`, `RandomPort`, `UnusedTCPPort`, and `EscapeDoubleQuotes`.

Control flow: backends register a `Type` with constructor and capability flags. `Multiplex` starts a goroutine that waits for context timeout, instance close signal, or merger error. On stream error it waits briefly for the command, maps configured preemption errors, optionally sleeps for extra console output, closes controlled console readers, waits for the merger, and signals one final error. On timeout/close it kills the process and closes readers. Error types attach boot/infra output for higher-level reporting.

State and persistence: global backend registry and process-wide shutdown channel are persistent process state. Runtime state includes child processes, merger goroutines, channels, and optional console closers.

Dependencies and integration: central contract for all `vm/*` backends and the high-level `vm` package. Uses OS process control, random, networking, target timeouts, logging, and report types.

Risks: `Types` map is unsynchronized and assumes init-time registration; process killing is blunt; `CmdCloser.Close` assumes `Process` is non-nil; `Shutdown` cannot be reset; port allocation races are unavoidable.

Test signals: `vm_test.go`, `vm_full_test.go`, and `merger_test.go` cover key monitor/multiplex/merger paths. Backend integration tests cover interface compliance.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmimpl/vmimpl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmm/vmm.go -->
# sources/test-tools/syzkaller/vm/vmm/vmm.go

Purpose: OpenBSD `vmm`/`vmctl` backend for syzkaller, using OpenBSD virtualization to boot kernel/image pairs and run commands over SSH.

Important APIs/types/functions: `Config`, `Pool`, `instance`, `ctor`, `Pool.Create`, `Boot`, `lookupSSHAddress`, `Close`, `Forward`, `Copy`, `Run`, `Diagnose`, `vmctl`, and `vmctlStatusRegex`.

Control flow: `ctor` validates image, kernel, count, and memory config. `Create` prepares an instance disk with `vmctl create`, stops stale VMs by name, then calls `Boot`. `Boot` starts `vmctl start` with kernel, disk, local network, and console connection, adds console output to a merger, derives SSH address from `vmctl status` VM id as `100.64.<id>.3`, and waits for SSH. `Run` adds SSH stdout/stderr to the same merger and starts `ssh`; a custom goroutine handles context timeout or merger errors. `Diagnose` sends OpenBSD DDB commands.

State and persistence: creates a per-instance qcow2 image in the workdir, runs a `vmctl` process, and holds a console writer. `Close` stops the VM, closes console input, kills/waits the process, and waits for merger shutdown.

Dependencies and integration: depends on OpenBSD `vmctl`, SSH/SCP, syzkaller `vmimpl` helpers, and OpenBSD DDB diagnosis.

Risks: address derivation depends on `vmctl status` formatting and network convention; boot failure reads only one output chunk; stale stop is racy by comment; `Run` uses custom lifecycle rather than `Multiplex`; `Forward` assumes guest host-side address `.2`.

Test signals: no direct unit test. Integration requires OpenBSD host `vmm`, kernel/image artifacts, SSH, and console behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmm/vmm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmware/vmware.go -->
# sources/test-tools/syzkaller/vm/vmware/vmware.go

Purpose: VMware-backed syzkaller VM implementation using `vmrun` clone/start/IP discovery, SSH command execution, and a serial Unix socket for kernel output.

Important APIs/types/functions: `Config` (`base_vmx`, `count`), `Pool`, `instance`, `ctor`, `Pool.Create`, `clone`, `boot`, `Forward`, `Close`, `Copy`, `Run`, and `Diagnose`.

Control flow: `ctor` parses config and validates `vmrun`. `Create` creates a timestamped VMX path in the workdir, clones the base VMX, and boots it. `boot` starts the VM nogui, waits for guest IP via `vmrun getGuestIPAddress -wait`, and stores it. `Run` dials a `serial` Unix socket beside the VMX, creates SSH stdout/stderr pipes, builds SSH args with optional reverse forwarding, starts `ssh`, adds dmesg/stdout/stderr to a new `OutputMerger`, and uses `vmimpl.Multiplex`.

State and persistence: a full VMware clone is created under the workdir and deleted by `vmrun deleteVM` on `Close`. Runtime state includes guest IP, close channel, optional forward port, and command-local merger.

Dependencies and integration: depends on `vmrun`, host SSH/SCP, a serial socket created/configured by the VMX, `vmimpl` SSH/SCP and Multiplex helpers.

Risks: no `WaitForSSH` after IP discovery; serial socket absence fails each run; cleanup ignores `vmrun` errors; `Diagnose` is empty; timestamp path avoids most collisions but relies on full clone cost.

Test signals: no direct test assigned. Integration tests must validate clone, boot, IP discovery, serial socket, SSH, SCP, run, and cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/vm/vmware/vmware.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/Makefile -->
# sources/test-tools/unionmount-testsuite/Makefile

Purpose: minimal make entrypoint for the Python unionmount testsuite.

Important APIs/types/functions: `all` target prints `Nothing to do`; `clean` removes editor backup files in the root and `tests/`.

Control flow: there is no build. The suite is run through the `run` script, so make only provides a harmless default target and cleanup.

State and persistence: `clean` deletes `*~` and `tests/*~`; `all` writes only to stdout.

Dependencies and integration: depends on make and the shell `$(RM)` variable. Integrates with standard source-tree cleanup workflows.

Risks: cleanup is intentionally narrow and does not remove mounts, generated lower/upper trees, or Python caches.

Test signals: executing `make` should not alter the suite; `make clean` should remove only backup files.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/context.py -->
# sources/test-tools/unionmount-testsuite/context.py

Purpose: core state model and operation library for unionmount/overlayfs tests. It mirrors expected filesystem state as a dentry/inode tree, runs real VFS operations, and validates copy-up, layer, device, inode, content, and error behavior.

Important APIs/types/functions: `upper` enum, `inode`, `dentry`, and `test_context`. Public operation methods include `open_file`, `open_dir`, `chmod`, `link`, `mkdir`, `readlink`, `rename`, `rmdir`, `truncate`, `unlink`, `utimes`, `rmtree`, `check_layer`, path/name helpers, layer tracking, and device/inode checks.

Control flow: setup code records lower-layer fixtures into the shadow tree. Each test operation walks paths with symlink and terminal-slash semantics, derives expected errors, prints a reproducible `./run` command, checks current layer state, performs the OS call, updates the shadow dentry state on success or failed create, validates content/size when requested, and checks layer state again. Rename/link paths update hardlink/copy-up expectations and optionally remount/rotate upper layers for recycle tests.

State and persistence: shadow state tracks dentries, inodes, layers, upper/data/meta status, lower/upper device IDs, current layer count, generated file number, cwd, and test flags. Real operations mutate the mounted test filesystem.

Dependencies and integration: imports `tool_box`, `remount_union`, `os`, `errno`, stat helpers, and test configuration. `run` creates one context per test script and subtests call its methods.

Risks: direct mode bypasses shadow path semantics; pathwalk emulates kernel behavior and may diverge on edge cases; copy-up block checks are disabled; `errorf` calls global `error` instead of `self.error`; terminal slash overrides are complex.

Test signals: every unionmount test script exercises this file. Failures produce `TestError` diagnostics and a reproducible command line.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/context.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/direct.py -->
# sources/test-tools/unionmount-testsuite/direct.py

Purpose: command-line direct-operation dispatcher for replaying a single open or VFS operation without full suite setup.

Important APIs/types/functions: `parse_C_int`, `direct_open_file`, and `direct_fs_op`.

Control flow: `direct_open_file` parses `--open-file` options into `test_context.open_file` keyword arguments, resolves errno names, creates a direct-mode context, and performs the open. `direct_fs_op` parses `--chmod`, `--link`, `--mkdir`, `--readlink`, `--rename`, `--rmdir`, `--truncate`, `--unlink`, or `--utimes`, maps common flags (`-L`, `-l`, `-B`, `-E`, etc.), creates a direct-mode context, and dispatches to the matching context method.

State and persistence: no setup state is created; operations act directly on caller-supplied paths and can mutate the filesystem.

Dependencies and integration: used by `run` before normal cleanup/setup handling. Depends on `argparse`, `errno`, `ArgumentError`, and `test_context`.

Risks: `parse_C_int` slices octal/decimal strings with `s[2:]`, which misparses common values like `0755` and decimal strings; the `--link` dispatcher calls `ctx.rename` instead of `ctx.link`; direct mode omits layer validation.

Test signals: direct replay commands printed by context methods should exercise these paths.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/direct.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/mount_union.py -->
# sources/test-tools/unionmount-testsuite/mount_union.py

Purpose: constructs the union mount under test for either bind-mounted `--no` mode or overlay/fuse-overlay/nested overlay mode.

Important APIs/types/functions: `mount_union(ctx)`.

Control flow: for `--no`, it bind mounts the lower root onto the union mount and records upper-like device IDs. For overlay modes, it mounts or prepares the upper root, creates the current layer directory with `u` and `w`, optionally mounts a per-layer tmpfs, writes a pure upper file, optionally mounts a nested overlay as the lower layer, then mounts the tested overlay/fuse filesystem with lowerdir/upperdir/workdir and configured mount options. It records lower layers, upper layer path, and device IDs for later checks.

State and persistence: creates directories under upper/base roots, mounts tmpfs and overlay filesystems, and writes `upperdir/f` as a pure upper sample.

Dependencies and integration: depends on `tool_box.system`, `write_file`, `config`, and `test_context` note methods. Called by `run` after `set_up`.

Risks: shell command construction is string-based; leftover upper contents are removed with `rm -rf`; mount failures are fatal; nested mount option adjustments are policy-heavy.

Test signals: all non-direct suite runs depend on successful mount and correct recorded device/layer metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/mount_union.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/remount_union.py -->
# sources/test-tools/unionmount-testsuite/remount_union.py

Purpose: remounts the active union during tests, optionally rotating the current upper layer into lower layers for multi-layer/recycle scenarios.

Important APIs/types/functions: `remount_union(ctx, rotate_upper=False)`.

Control flow: only acts for overlayfs testing. It unmounts the union, drops caches, checks kernel taint, and either keeps the current lower/upper/work directories or, when `rotate_upper` and more layers are available, prepends the current upper layer to `lowerdir`, advances the context layer number, creates a new layer with `u`/`w`, optionally mounts a per-layer tmpfs, and writes a pure upper file. It mounts overlay again and records current device and layer metadata.

State and persistence: mutates mount state, creates new upper layer directories, may mount tmpfs layers, and updates context-recorded lower/upper paths.

Dependencies and integration: called from context `mkdir`, `rename`, and `link` paths when recycle/rotation checks are active. Depends on `tool_box.system`, `check_not_tainted`, and `write_file`.

Risks: assumes unmount/drop-caches privileges; layer rotation is string-concatenated lowerdir order; only overlayfs path is implemented; remount failures stop the suite.

Test signals: multi-layer runs such as `--ov=N` validate inode stability and copy-up behavior across remounts.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/remount_union.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/run -->
# sources/test-tools/unionmount-testsuite/run

Purpose: main Python CLI for configuring, setting up, running, cleaning, and directly replaying unionmount/overlayfs tests.

Important APIs/types/functions: `show_format`, top-level argument parser, direct `--open-file`/`--<fsop>` dispatch, cleanup/setup flow, test list construction, feature detection, and subtest discovery/execution.

Control flow: creates `config`, handles direct one-off operations, cleans old mounts, parses mode (`--no`, `--ov`, `--ovov[=layers]`), optional fuse/samefs/maxfs/squashfs/erofs/xdev/xino/meta/verify/terminal-slash flags, auto-detects overlay module and mount options, optionally performs setup-only, builds the test list, and for each test/recycle lane creates a `test_context`, calls `set_up` and `mount_union`, imports `tests.<name>`, finds `subtest_*` functions, sorts them by source line, runs them, checks taint, and unmounts. At the end it leaves a fresh union mounted for interactive use.

State and persistence: mutates system mounts, lower/upper/base directories, kernel drop-caches/taint checks, and test files. CLI direct mode can mutate arbitrary provided paths.

Dependencies and integration: depends on root-capable mount/umount, overlayfs/fuse-overlayfs/kernel feature files, `settings`, `context`, setup/mount/unmount/remount helpers, `tool_box`, and Python test modules.

Risks: string-built shell commands require trusted paths; imports execute test module top-level code; final remount leaves state behind by design; feature auto-enabling can change mount options from user input.

Test signals: the script is the suite driver; successful run means all selected subtests completed and the kernel remained untainted.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/run -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/set_up.py -->
# sources/test-tools/unionmount-testsuite/set_up.py

Purpose: cleans previous suite mounts and creates the reusable lower-layer fixture tree for unionmount tests.

Important APIs/types/functions: `create_file`, `clean_up`, and `set_up`.

Control flow: `clean_up` syncs and repeatedly unmounts old union, lower, upper, per-layer, and base mounts regardless of current config. `set_up` mounts/prepares base and lower roots as needed, creates the lower test directory, records path components in the context tree, sets cwd, and for file numbers 100-129 creates regular files, direct/indirect symlinks, dangling symlinks, populated directories, empty directories, dir symlinks, root-owned files, and missing path records. It optionally converts the lower tree into squashfs or erofs, or remounts lower read-only for overlay tests.

State and persistence: creates/mounts lower/base filesystems and populates the lower fixture tree; updates context shadow dentries and lower device ID.

Dependencies and integration: called before every test script by `run`. Depends on mount helpers from `tool_box`, `os`, `shutil`, and external `mksquashfs`/`mkfs.erofs` when requested.

Risks: aggressive cleanup unmounts broad globbed paths; fixture ownership assumes uid/gid 1 for `bin`; read-only image tooling must exist for squashfs/erofs modes; repeated setup removes existing lower testdir.

Test signals: all test scripts depend on the fixture names and contents created here.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/set_up.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/settings.py -->
# sources/test-tools/unionmount-testsuite/settings.py

Purpose: configuration object for unionmount tests, translating environment variables and CLI flags into mount roots, filesystem type/name, mount options, feature flags, and test mode.

Important APIs/types/functions: `config` methods for testing mode, base/lower/upper/union roots, mount decisions, lower image/testdir paths, verbosity/verify/maxfs/samefs/squashfs/erofs/xino/metacopy/nested/fuse flags, and mount options.

Control flow: constructor reads `UNIONMOUNT_BASEDIR`, `UNIONMOUNT_LOWERDIR`, `UNIONMOUNT_MNTPOINT`, and `UNIONMOUNT_MNTOPTIONS`, prints them, normalizes mount options to start with `-o`, derives default maxfs/samefs behavior, and initializes flags. Later setters are called by `run` as CLI parsing and feature detection proceeds.

State and persistence: configuration is in memory; constructor prints environment details to stdout. Paths point to `/base`, `/lower`, `/upper`, and `/mnt` by default unless overridden.

Dependencies and integration: used by setup, mount, remount, context, direct mode, and run driver.

Risks: environment values are passed to shell commands elsewhere without quoting; constructor prints every run; samefs inference from `UNIONMOUNT_BASEDIR` plus empty lowerdir is implicit; mount option string is mutable comma concatenation.

Test signals: coverage comes from running the suite under each mode/flag combination.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/settings.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-open-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-open-dir.py

Purpose: verifies opening existing populated directories with `O_DIRECTORY` across read and write access modes.

Important APIs/types/functions: six `subtest_*` functions calling `ctx.open_dir`.

Control flow: each subtest chooses `ctx.non_empty_dir()` with optional terminal slash, opens it read-only successfully, or attempts write-only, append, read/write, and append/read-write forms expecting `EISDIR`, then reopens read-only to confirm the directory remains accessible.

State and persistence: no intended mutation; all operations should preserve the lower directory and its contents.

Dependencies and integration: depends on setup-created populated directories and `context.open_dir` flag/error handling.

Risks: expected errno can vary for unusual filesystems, especially with terminal slashes or non-overlay direct mode.

Test signals: confirms directory opens do not copy up or corrupt directories and that write-like open modes are rejected.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-open-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-open.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-open.py

Purpose: tests opening existing populated directories without `O_DIRECTORY`.

Important APIs/types/functions: six `subtest_*` functions using `ctx.open_file`.

Control flow: read-only open of a directory is expected to succeed. Write-only, repeated write-only, append, read/write, and append/read-write variants expect `EISDIR`; each failed write-like operation is followed by successful read-only open.

State and persistence: should not mutate the directory tree or file contents.

Dependencies and integration: uses `ctx.non_empty_dir`, terminal-slash mode, and `open_file` error/layer checks.

Risks: some filesystems can differ on directory open permissions, but the suite encodes Linux VFS expectations.

Test signals: validates directory error behavior for non-`O_DIRECTORY` opens and post-failure stability.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym1-open.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-sym1-open.py

Purpose: verifies open behavior through a direct symlink to an existing directory.

Important APIs/types/functions: five `subtest_*` functions using `ctx.direct_dir_sym` and `ctx.open_file`.

Control flow: read-only open through the symlink succeeds. Write-only, append, read/write, and append/read-write opens through the symlink expect `EISDIR`, with successful read-only rechecks after each failure.

State and persistence: no intended mutation; symlink and target directory should remain lower-visible and readable.

Dependencies and integration: depends on setup-created direct directory symlink and context symlink pathwalk behavior.

Risks: terminal slash and symlink following semantics are subtle; the test assumes normal Linux following for final symlink in `open`.

Test signals: catches overlayfs regressions where directory symlink opens produce wrong errors or alter the target.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym1-open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym1-weird-open.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-sym1-weird-open.py

Purpose: exercises direct directory symlink opens with create, exclusive, and truncate flag combinations.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.direct_dir_sym` and `ctx.open_file`.

Control flow: `O_CREAT` and `O_TRUNC` combinations through the symlink to a directory generally expect `EISDIR`, while `O_CREAT|O_EXCL` combinations expect `EEXIST`. Each subtest reopens the symlink read-only to confirm the target directory is unchanged.

State and persistence: failed operations should not create files, truncate anything, or copy up directory data unexpectedly.

Dependencies and integration: depends on `context.open_file` create/truncate/exclusive error prediction and setup-created direct dir symlink.

Risks: errno behavior is kernel-sensitive for `O_EXCL` plus symlinks and terminal slash paths.

Test signals: validates symlink-to-directory error precedence and post-failure stability.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym1-weird-open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym2-open.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-sym2-open.py

Purpose: tests open behavior through an indirect symlink chain that resolves to an existing directory.

Important APIs/types/functions: five `subtest_*` functions using `ctx.indirect_dir_sym` and `ctx.open_file`.

Control flow: read-only open through the indirect symlink succeeds twice. Write-like modes (`O_WRONLY`, append, `O_RDWR`, append/read-write) expect `EISDIR`, then read-only open confirms the target remains accessible.

State and persistence: no intended mutation of either symlink or target directory.

Dependencies and integration: relies on setup-created direct and indirect directory symlinks and recursive symlink handling in `context.pathwalk`.

Risks: symlink-loop protection and terminal slash handling can alter expected errors if pathwalk diverges from kernel behavior.

Test signals: catches regressions in multi-hop symlink resolution over overlay layers.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym2-open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym2-weird-open.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-sym2-weird-open.py

Purpose: verifies indirect directory symlink error behavior with create, exclusive, and truncate flags.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.indirect_dir_sym` and `ctx.open_file`.

Control flow: combinations of read/write access with `O_CREAT`, `O_TRUNC`, and both generally expect `EISDIR`; combinations including `O_CREAT|O_EXCL` expect `EEXIST`. After each failed operation the symlink is opened read-only to confirm the directory still resolves.

State and persistence: no files should be created and no directory data should be copied up or changed by failed opens.

Dependencies and integration: depends on context symlink-chain tracking and open flag/error modeling.

Risks: error precedence for indirect symlinks plus terminal slashes is a frequent kernel compatibility edge.

Test signals: validates multi-hop symlink-to-directory behavior under unusual open flags.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-sym2-weird-open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-weird-open-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-weird-open-dir.py

Purpose: tests existing directory opens with `O_DIRECTORY` plus create/exclusive/truncate flag combinations.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.open_dir`.

Control flow: `O_DIRECTORY|O_CREAT` combinations expect `EINVAL`; `O_DIRECTORY|O_TRUNC` without create expects `EISDIR`; `O_CREAT|O_EXCL` variants also expect `EINVAL`. Every subtest reopens the directory read-only afterward.

State and persistence: no intended mutation; failed open attempts must not alter directory layer state or contents.

Dependencies and integration: relies on `context.open_dir` translating to `open_file(dir=1)` and Linux errno semantics.

Risks: exact errno ordering can differ across kernel versions or non-overlay filesystems.

Test signals: catches regressions in `O_DIRECTORY` validation and post-error directory accessibility.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-weird-open-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-weird-open.py -->
# sources/test-tools/unionmount-testsuite/tests/dir-weird-open.py

Purpose: tests existing directory opens without `O_DIRECTORY` when create, exclusive, and truncate flags are present.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.open_file`.

Control flow: create/truncate combinations on a directory expect `EISDIR`, while `O_CREAT|O_EXCL` variants expect `EEXIST`. Each subtest validates the directory remains readable after the failed operation.

State and persistence: should not mutate the existing directory or create replacement files.

Dependencies and integration: uses `ctx.non_empty_dir`, terminal-slash mode, and open flag modeling.

Risks: errno precedence around `O_CREAT|O_EXCL` on directories is subtle and kernel-dependent.

Test signals: validates Linux VFS directory-open behavior through overlayfs copy-up paths.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/dir-weird-open.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/hard-link-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/hard-link-dir.py

Purpose: verifies that hard-link operations involving directories fail correctly and leave directory state intact.

Important APIs/types/functions: eight `subtest_*` functions using `ctx.link`, `ctx.open_dir`, `ctx.open_file`, `ctx.rmdir`, `ctx.mkdir`, and `ctx.rename`.

Control flow: tests hard-linking a directory to a missing name (`EPERM`), linking files over dirs and dirs over files/dirs (`EEXIST`), linking a dir over itself or parent, linking removed directories (`ENOENT`), and linking renamed directories. Follow-up opens confirm original and target names.

State and persistence: some subtests create, rename, or remove directories before failed link attempts; expected state is maintained in the context tree.

Dependencies and integration: depends on `context.link` hardlink metadata checks and setup lower directories.

Risks: terminal slashes can change errors; overlayfs redirect_dir/xdev behavior can affect prior rename setup.

Test signals: validates directory hardlink prohibition and no accidental copy-up/name creation.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/hard-link-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/hard-link-sym.py -->
# sources/test-tools/unionmount-testsuite/tests/hard-link-sym.py

Purpose: tests hard-link behavior for symlinks, dangling symlinks, and symlinks after unlink/rename.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.link`, `ctx.open_file`, `ctx.unlink`, and `ctx.rename`.

Control flow: creates hard links to direct and dangling symlinks, verifies both names resolve the same way, rejects links over existing files/new files/symlinks with `EEXIST`, rejects missing sources with `ENOENT`, and validates unlinked/renamed symlink source behavior.

State and persistence: successful links add additional directory entries sharing the symlink inode metadata; later opens validate target content or dangling errors.

Dependencies and integration: depends on `context.link` no-follow/follow behavior, setup symlinks, and errno expectations.

Risks: POSIX hardlink symlink-following behavior differs by flags and platform; context defaults are Linux-oriented.

Test signals: validates overlayfs handling of symlink hardlinks and whiteout/copy-up state after rename/unlink.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/hard-link-sym.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/hard-link.py -->
# sources/test-tools/unionmount-testsuite/tests/hard-link.py

Purpose: tests hard links for regular files under lower, upper, missing, unlinked, and renamed states.

Important APIs/types/functions: eleven `subtest_*` functions using `ctx.link`, `ctx.open_file`, `ctx.unlink`, and `ctx.rename`.

Control flow: links a lower file to a new name, rejects missing sources and existing destinations, verifies links over itself fail, creates new upper files and rejects overwrites, unlinks sources before link attempts, and renames files before creating hardlinks back to old names. Follow-up reads verify content and missing names.

State and persistence: successful hardlinks create new dentries sharing inode state; failed operations should not alter source/destination contents. Some subtests create upper files or remove names.

Dependencies and integration: exercises `context.link`, copy-up metadata, inode/dev stability checks, and lower fixture files.

Risks: overlayfs index/nfs_export/xino settings can affect hardlink inode stability checks.

Test signals: important coverage for hardlink copy-up correctness across lower and upper layers.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/hard-link.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/impermissible.py -->
# sources/test-tools/unionmount-testsuite/tests/impermissible.py

Purpose: verifies permission-denied behavior for non-root user operations against root-owned lower files and confirms privileged operations still work afterward.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`, `ctx.truncate`, `ctx.utimes`, and direct metadata checks.

Control flow: switches effective uid/gid through `as_bin` in context operations. Tests denied write/truncate/append/utime attempts expecting `EACCES`, checks contents/timestamps are unchanged, then performs the same operation as root and validates new content, size, or timestamps.

State and persistence: mutates `rootfile` content, size, and timestamps only in privileged parts. Permission-failed parts must not copy up or alter data.

Dependencies and integration: setup creates root-owned files; context handles `seteuid`/`setegid` around operations.

Risks: assumes uid/gid 1 exists and lacks write permission; timestamp equality can be coarse on some filesystems; terminal slash mode skips some size/time checks.

Test signals: validates permission checks occur before copy-up/data mutation.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/impermissible.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/mkdir.py -->
# sources/test-tools/unionmount-testsuite/tests/mkdir.py

Purpose: tests directory creation over missing names, existing files/dirs, symlink paths, populated parents, and dangling symlinks.

Important APIs/types/functions: eleven `subtest_*` functions using `ctx.mkdir`, `ctx.open_file`, and symlink/path helpers.

Control flow: creates a new missing directory then rejects duplicate creation, rejects mkdir over files and existing dirs with `EEXIST`, creates subdirectories inside empty and populated lower dirs, rejects mkdir over direct/indirect symlinks to files or dirs, and rejects over dangling symlink paths. Follow-up opens confirm existing targets remain.

State and persistence: successful mkdir creates upper directories and may trigger remount/upper rotation in recycle mode. Failed operations mark failed creates but should not alter existing fixtures.

Dependencies and integration: exercises `context.mkdir`, terminal slash handling, symlink pathwalk, and remount-on-create behavior.

Risks: mkdir over symlink errno depends on terminal slash and follow semantics; recycled layer checks depend on overlay feature flags.

Test signals: coverage for directory creation/copy-up across lower and upper parents.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/mkdir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat-excl-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/noent-creat-excl-trunc.py

Purpose: verifies creation of missing files with `O_CREAT|O_EXCL|O_TRUNC` under different access modes.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: each subtest opens a missing path with create/exclusive/truncate and read-only, write-only, append, read-write, or append/read-write. First open creates an empty or one-byte file; second exclusive open expects `EEXIST`; final read confirms content.

State and persistence: creates one new upper file per subtest and writes `q` where applicable.

Dependencies and integration: depends on `context.open_file` create/exclusive/truncate state updates and content checking.

Risks: terminal slash mode can convert missing-file creation to directory-related errors through context overrides.

Test signals: validates exclusive creation and no unintended truncation after `EEXIST`.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat-excl-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat-excl.py -->
# sources/test-tools/unionmount-testsuite/tests/noent-creat-excl.py

Purpose: tests missing-file creation with `O_CREAT|O_EXCL` across read/write/append modes.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: creates a new file on first open, writes `q` for write-like modes, verifies content, then repeats the exclusive open expecting `EEXIST` and verifies content remains unchanged.

State and persistence: creates upper files and optional one-byte data.

Dependencies and integration: uses context creation tracking and open flag mapping.

Risks: exact behavior for `O_CREAT|O_EXCL|O_RDONLY` is Linux-specific but expected by the suite.

Test signals: catches overlayfs mistakes where exclusive create overwrites or alters existing upper files.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat-excl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/noent-creat-trunc.py

Purpose: verifies missing-file creation with `O_CREAT|O_TRUNC`, including repeated truncation and append behavior.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: first open creates the file. Repeated read-only create/truncate keeps it empty; write and read-write overwrite content from `q` to `p`; append mode appends `p` to existing `q` when the second open omits truncate in those subtests.

State and persistence: creates and mutates upper files with expected content transitions.

Dependencies and integration: exercises open/create/truncate/data-copy-up state in `context.py`.

Risks: append plus truncate sequencing is easy to misread; context expectations encode exact contents.

Test signals: validates creation/truncation data semantics on upper files.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat.py -->
# sources/test-tools/unionmount-testsuite/tests/noent-creat.py

Purpose: tests ordinary `O_CREAT` behavior for previously missing files.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only create makes an empty file. Write-only/read-write creates and overwrites first byte from `q` to `p`. Append creates with `q` then appends `p`, producing `qp`. Readbacks confirm each state.

State and persistence: creates upper files and mutates content through normal write/append semantics.

Dependencies and integration: uses setup missing path records, context open creation, write, and read validation.

Risks: terminal slash mode can force creation errors; append semantics assume file offset behavior from `O_APPEND`.

Test signals: baseline creation coverage for missing regular files.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-creat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-plain.py -->
# sources/test-tools/unionmount-testsuite/tests/noent-plain.py

Purpose: verifies opening absent files without create flags fails consistently.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only, write-only, append, read-write, and append/read-write opens are attempted twice against a missing path, each expecting `ENOENT`.

State and persistence: no intended mutation; missing dentry should remain absent after all attempts.

Dependencies and integration: depends on setup missing dentry records and context error handling.

Risks: terminal slash mode can alter missing path errors in some contexts, but expected result here is `ENOENT`.

Test signals: baseline negative-open behavior and failed-create state stability.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-plain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/noent-trunc.py

Purpose: verifies `O_TRUNC` without `O_CREAT` still fails on absent files.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only+truncate, write-only+truncate, append+truncate, read-write+truncate, and append/read-write+truncate are attempted twice and must return `ENOENT`.

State and persistence: no files should be created; shadow dentry remains negative.

Dependencies and integration: exercises context open flag composition and missing path handling.

Risks: filesystems must not treat truncate as implicit create; terminal slash handling can affect errno.

Test signals: catches accidental upper creation or wrong errno on truncating absent paths.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/noent-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat-excl-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/open-creat-excl-trunc.py

Purpose: tests opening existing lower files with `O_CREAT|O_EXCL|O_TRUNC`.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: all read/write/append variants expect `EEXIST` because the file exists. Each subtest then opens read-only and verifies original `:xxx:yyy:zzz` content remains.

State and persistence: no intended mutation; truncate must not occur after exclusive failure.

Dependencies and integration: lower regular file fixtures and context open/exclusive handling.

Risks: error precedence with terminal slash may differ if path is treated as directory-like.

Test signals: validates `O_EXCL` prevents copy-up/truncation of existing lower files.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat-excl-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat-excl.py -->
# sources/test-tools/unionmount-testsuite/tests/open-creat-excl.py

Purpose: verifies `O_CREAT|O_EXCL` fails on existing lower files without changing them.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: attempts read-only, write-only, append, read-write, and append/read-write exclusive opens, all expecting `EEXIST`, then reads original content.

State and persistence: no file content or layer state should change.

Dependencies and integration: context open flag handling and lower regular fixtures.

Risks: some paths with terminal slash can produce slash-related errors instead of `EEXIST`.

Test signals: baseline exclusive-open existing-file regression coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat-excl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/open-creat-trunc.py

Purpose: tests existing-file open behavior with `O_CREAT|O_TRUNC`.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only+truncate empties the file. Write-only/read-write truncates then writes `q`, then repeats and writes `p`. Append variants with truncate also produce exactly the newly written byte after each open. Readbacks validate content.

State and persistence: lower file is copied up with data and truncated/overwritten in upper layer.

Dependencies and integration: exercises data copy-up, truncation, create-no-op on existing files, and readback checks.

Risks: truncation through overlayfs must happen on upper copy; content expectations are sensitive to `O_APPEND|O_TRUNC` ordering.

Test signals: key data-copy-up/truncate coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat.py -->
# sources/test-tools/unionmount-testsuite/tests/open-creat.py

Purpose: tests `O_CREAT` on existing lower files without truncation.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only create reads original content. Write-only/read-write writes `q` then `p` at the start, preserving the rest of the file. Append variants append `q` then `p`, producing original content plus suffixes.

State and persistence: write-like opens copy data up and mutate content in upper layer; read-only does not.

Dependencies and integration: context open/write/read and lower regular fixture content.

Risks: assumes write starts at offset zero when not append; terminal slash can change error handling.

Test signals: validates create-as-open semantics and data preservation on existing files.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-creat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-plain.py -->
# sources/test-tools/unionmount-testsuite/tests/open-plain.py

Purpose: baseline tests for opening existing regular files without create/truncate/exclusive flags.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only opens verify original content twice. Write-only/read-write overwrites first byte from `q` to `p`. Append modes append `q` and `p`. Readbacks after each mutation validate expected content.

State and persistence: write-like operations copy up lower data to upper and mutate it; read-only operations should not.

Dependencies and integration: lower regular files created by setup and context content/layer validation.

Risks: repeated mutations mean each subtest assumes a fresh setup context from the runner.

Test signals: foundational regular-file open, write, append, and copy-up coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-plain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-trunc.py -->
# sources/test-tools/unionmount-testsuite/tests/open-trunc.py

Purpose: baseline tests for opening existing regular files with `O_TRUNC`.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only+truncate empties the file. Write-only/read-write+truncate writes `q` then truncates again and writes `p`. Append+truncate behaves similarly, leaving only the post-truncate byte.

State and persistence: lower file is data-copied to upper and truncated; content becomes empty or one-byte values depending on writes.

Dependencies and integration: context open/truncate/write/read logic and lower file fixtures.

Risks: Linux allows `O_RDONLY|O_TRUNC` behavior that may be surprising; non-Linux semantics could differ.

Test signals: direct coverage for truncation-triggered copy-up and upper data mutation.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/open-trunc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/readlink.py -->
# sources/test-tools/unionmount-testsuite/tests/readlink.py

Purpose: validates `readlink` on files, directories, direct/indirect symlinks, dangling symlinks, and absent paths.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.readlink`.

Control flow: regular files and directories expect `EINVAL`; direct and indirect symlinks to files or dirs return their stored symlink contents; absent files expect `ENOENT`; dangling symlinks return their link text rather than following to the missing target.

State and persistence: read-only; no filesystem mutation is intended.

Dependencies and integration: depends on setup symlink values and context `readlink` no-follow behavior.

Risks: terminal slash on symlinks can convert expected results to slash traversal errors through context override logic.

Test signals: covers symlink metadata preservation and no-follow lookup across overlay layers.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/readlink.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-dir.py

Purpose: tests moving populated lower directories and populated subdirectories to sibling locations.

Important APIs/types/functions: two `subtest_*` functions using `ctx.rename`, `ctx.open_dir`, and `ctx.open_file`.

Control flow: moves a populated directory into an empty directory child path, then verifies the old name is missing, the new directory exists, and contained files are readable. A second subtest moves the `pop` subdirectory and verifies child `b`.

State and persistence: successful renames copy up/redirect directory metadata and update context dentries. Repeated rename from the old source expects `ENOENT`.

Dependencies and integration: depends on overlayfs redirect_dir support unless xdev mode selects `rename-exdev` instead.

Risks: directory rename behavior differs when redirect_dir is disabled; terminal slash and nested paths affect errno.

Test signals: validates populated directory rename with contents preserved under new name.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-empty-dir.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-empty-dir.py

Purpose: broad coverage of empty directory rename, removal, overwrite, self-rename, and wrong-type targets.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.rename`, `ctx.rmdir`, `ctx.unlink`, `ctx.open_dir`, and `ctx.open_file`.

Control flow: renames empty dirs away and back, removes/unlinks old names, removes then tries rename, renames twice, rejects rename over populated dir with `ENOTEMPTY`, allows self-rename, rejects rename over files with `ENOTDIR`, and rejects over the parent test directory with `ENOTEMPTY`.

State and persistence: successful renames update directory dentries and may rotate upper layers in recycle mode; removals create whiteouts/negative dentries.

Dependencies and integration: context rename/rmdir/unlink state machine and overlayfs directory rename support.

Risks: errno behavior for empty dir over non-empty dir can be `ENOTEMPTY` or `EEXIST`; context tolerates some variants.

Test signals: dense coverage for directory whiteout/redirect/copy-up state.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-empty-dir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-exdev.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-exdev.py

Purpose: alternate directory rename tests for overlayfs configurations where `redirect_dir` is disabled and directory renames should fail with `EXDEV`.

Important APIs/types/functions: four `subtest_*` functions using `ctx.rename`, `ctx.open_dir`, and `ctx.open_file`.

Control flow: attempts to rename empty and populated directories within the same parent and into another parent. Each expects `EXDEV`, then verifies the destination remains absent and the original source and contents remain readable.

State and persistence: no successful rename should occur; source dentries remain in place.

Dependencies and integration: selected by `run` when overlayfs redirect_dir is off or `--xdev` is used.

Risks: if kernel auto-enables redirect_dir unexpectedly, these tests fail because rename succeeds instead of `EXDEV`.

Test signals: validates backward-compatible overlayfs behavior without directory redirects.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-exdev.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-file.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-file.py

Purpose: tests regular file rename behavior across missing names, removals, wrong-type targets, replacement, and self-rename.

Important APIs/types/functions: ten `subtest_*` functions using `ctx.rename`, `ctx.unlink`, `ctx.rmdir`, `ctx.open_file`, and `ctx.open_dir`.

Control flow: renames a file away and back, unlinks/rmdirs old names, rejects operations after source removal, renames twice, replaces another file, self-renames, rejects rename over directories with `EISDIR`, and rejects rename over the parent directory with `ENOTEMPTY`. Readbacks verify content and missing names.

State and persistence: successful renames copy up file metadata/data as needed, replace dentries, and create negative old names. Replacement over a file changes the destination content.

Dependencies and integration: context rename model, lower regular files, whiteout behavior, and content validation.

Risks: directory target errno can vary; each subtest depends on fresh fixture numbering.

Test signals: key regular-file rename and replacement coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-file.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-hard-link.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-hard-link.py

Purpose: verifies rename behavior for files that have hard links.

Important APIs/types/functions: single `subtest_1` using `ctx.link`, `ctx.rename`, and `ctx.open_file`.

Control flow: creates a hard link from a lower regular file to a new name, renames that linked name away and back, then renames the original source to a fourth name. Final checks ensure the original name is absent and the remaining linked names read the original content.

State and persistence: creates shared-inode dentries, then moves names while preserving content/inode association.

Dependencies and integration: relies on hardlink copy-up/index behavior and context rename/link inode tracking.

Risks: overlayfs without index support can have hardlink verification limitations in multi-layer modes.

Test signals: targets link-count/name preservation through rename operations.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-hard-link.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-2.py -->
# sources/test-tools/unionmount-testsuite/tests/rename-mass-2.py

Purpose: stress test for repeated mass renames of a small range of lower regular files through sequential suffix generations.

Important APIs/types/functions: constants `file_count = 104`, `iter_count = 3`, `subtest_1`, and `subtest_2`.

Control flow: `subtest_1` derives the base `foo` path, renames files `foo100` through `foo103` to `_0`, then for three iterations renames each file in reverse order from suffix `_j` to `_j+1`. `subtest_2` unlinks the final `_3` names.

State and persistence: repeatedly moves lower-file names into upper/whiteout state and then deletes them. Context tracks each rename/unlink.

Dependencies and integration: uses `ctx.rename` and `ctx.unlink` with setup regular files.

Risks: small file range limits stress; reverse iteration avoids name collisions but still exercises dense rename metadata updates.

Test signals: catches rename scalability/state leaks across repeated file moves.
<!-- END_FILE_RESEARCH: sources/test-tools/unionmount-testsuite/tests/rename-mass-2.py -->
