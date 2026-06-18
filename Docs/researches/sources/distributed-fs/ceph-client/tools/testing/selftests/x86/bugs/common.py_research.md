# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/common.py

## Purpose

`common.py` centralizes helper routines for Python x86 bug mitigation kselftests. It reads CPU/sysfs/cmdline state, reports kselftest results, parses vmlinux patch-site sections, disassembles x86 instructions, opens the live kernel through drgn, and skips tests when optional Python dependencies are absent.

## Important APIs, Types, and Functions

File readers include `read_file()`, `cpuinfo_has()`, `cmdline_has*()`, `get_sysfs()`, and `sysfs_has*()`. Result helpers are `bug_check_pass()`, `bug_check_fail()`, `bug_status_unknown()`, and `basic_checks_sufficient()`. Binary/kernel helpers are `get_section_info()`, `get_patch_sites()`, `get_instruction_from_vmlinux()`, `init_capstone()`, `get_runtime_kernel()`, and `check_dependencies_or_skip()`.

## Control Flow

Individual tests import this module, run basic vulnerability/status checks, and then use these helpers to inspect either text state or binary/runtime patch state. `get_patch_sites()` reads 32-bit relative offsets from a section such as `.return_sites` or `.retpoline_sites`. `get_instruction_from_vmlinux()` maps a virtual address into the `.text` section and returns the capstone instruction at that address. `check_dependencies_or_skip()` imports each required module and exits through `ksft.finished()` after a skip if a dependency is missing.

## State and Persistence Behavior

The module reads `/proc/cpuinfo`, `/proc/cmdline`, `/sys/devices/system/cpu/vulnerabilities/*`, vmlinux files, and live kernel memory through drgn. It does not persist state itself.

## Dependencies and Integration Points

It depends on Python kselftest `ksft`, optional `elftools`, `capstone`, and `drgn`, and kernel debug/vulnerability interfaces. It is shared by ITS sysfs, permutation, indirect alignment, and return alignment tests.

## Risks and Edge Cases

`sysfs_has()` assumes `get_sysfs()` returns a string; a missing vulnerability file can lead to membership tests on `None`. Section and symbol assumptions are x86_64-specific. drgn access to the live kernel requires permissions and debug symbols.

## Test Signals

Useful signals are clean dependency skips for missing modules, accurate pass/fail messages with found/expected mitigation text, successful section lookup with offsets, and valid capstone disassembly for runtime patch-site comparisons.
