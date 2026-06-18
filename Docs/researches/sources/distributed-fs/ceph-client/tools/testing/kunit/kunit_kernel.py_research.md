# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_kernel.py

## Purpose

This module owns the low-level KUnit kernel configuration, build, and execution operations for both UML and QEMU-backed architectures. It abstracts make invocation, Kconfig merging/validation, process startup, output capture, timeout enforcement, and interrupt cleanup behind `LinuxSourceTree`.

## Important APIs, Types, And Data

Constants define KUnit paths such as `.config`, `.kunitconfig`, `last_used_kunitconfig`, default/all-tests/UML config fragments, `test.log`, and QEMU config directories. Exceptions are `ConfigError` and `BuildError`. Operation classes are `LinuxSourceTreeOperations`, `LinuxSourceTreeOperationsQemu`, and `LinuxSourceTreeOperationsUml`; the public orchestrator is `LinuxSourceTree`. Helpers include `get_kconfig_path()`, `get_kunitconfig_path()`, `get_old_kunitconfig_path()`, `get_parsed_kunitconfig()`, `get_outfile_path()`, `_default_qemu_config_path()`, and `_get_qemu_ops()`.

## Control Flow

`LinuxSourceTree.__init__()` chooses UML by default or loads a QEMU config module for non-UML architectures, parses and merges requested kunitconfig fragments, and adds `--kconfig_add` entries. `build_reconfig()` reuses an existing `.config` only if it contains the requested KUnit options and the remembered `last_used_kunitconfig` matches; otherwise it removes and regenerates `.config`. `build_kernel()` runs olddefconfig and `make all compile_commands.json scripts_gdb`. `run_kernel()` builds kernel command-line KUnit filters, starts UML or QEMU, tees output to `test.log`, yields lines to the parser, and uses a background waiter to terminate on timeout.

## State And Persistence Behavior

Persistent state lives in the build directory: `.kunitconfig`, `.config`, `last_used_kunitconfig`, `test.log`, `linux`/kernel images, build products, and generated compile/debug artifacts. The class also keeps in-memory `_process` state while the kernel is running and restores terminal settings after process completion or SIGINT.

## Dependencies And Integration Points

It depends on `subprocess`, `os`, `shlex`, `shutil`, `signal`, `threading`, dynamic import machinery, `kunit_config`, and `qemu_config`. It integrates with make, UML binaries, `qemu-system-*`, architecture-specific `tools/testing/kunit/qemu_configs/*.py`, Linux Kbuild `O=`, KUnit kernel command-line flags, and `kunit.py` request handling.

## Risks And Edge Cases

QEMU config loading mutates `extra_qemu_params` on the imported `QEMU_ARCH` object, so repeated construction with extra args can accumulate if the same module object is reused. `run_kernel()` writes leftover stdout in `finally`, which is good for logs but depends on callers consuming the generator or closing it. Timeout handling terminates the process from a background thread and prints generic exceptions. `build_config()` uses append-mode Kconfig writes and relies on prior file removal for clean replacement. Non-UML QEMU assumes acceleration fallbacks and kernel paths are valid for the selected arch.

## Test Signals

Unit tests should mock `subprocess` for make/UML/QEMU command construction, verify kunitconfig merge/conflict/validation paths, ensure repeated `run_kernel()` calls do not mutate caller args, and test timeout cleanup. Integration tests are `kunit.py config`, `build`, `exec --raw_output=all`, architecture listing with `--arch=help`, and validation that `test.log` captures the same kernel output sent to the parser.
