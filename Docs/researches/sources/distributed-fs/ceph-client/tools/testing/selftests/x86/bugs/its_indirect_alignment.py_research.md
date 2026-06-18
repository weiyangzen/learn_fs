# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_indirect_alignment.py

## Purpose

`its_indirect_alignment.py` validates indirect branch/call patch sites under the x86 indirect target selection mitigation. It compares `.retpoline_sites` from vmlinux with live instructions read from `/proc/kcore` via drgn, checking that unsafe sites are patched to aligned ITS thunks or otherwise safe direct branches.

## Important APIs, Types, and Functions

The script imports `ksft` and `common` helpers, uses pyelftools `ELFFile`, drgn `program_from_kernel()`, `identify_address()`, and capstone disassembly. It consumes the sysfs vulnerability `indirect_target_selection`, skips if aligned thunks are not active or Spectre v2 retpolines are deployed, optionally copies a user-supplied vmlinux into `/usr/lib/debug/lib/modules/$(uname -r)/vmlinux`, and reads symbols `__retpoline_sites` and `__x86_indirect_its_thunk_r15`.

## Control Flow

After skip/dependency checks, the script locates `.retpoline_sites`, reads its relative patch-site offsets, maps the vmlinux section base to the live kernel `__retpoline_sites` address, and iterates over each site. For each site it prints vmlinux and kcore instructions, computes whether the instruction end is in a safe half of the 64-byte region, and passes safe sites immediately. Unsafe sites pass if their immediate target resolves to an ITS thunk at a safe address or to a direct branch that does not require an ITS thunk; otherwise they are failed or marked unknown on unexpected operands/exceptions.

## State and Persistence Behavior

The script may copy a supplied vmlinux into `/usr/lib/debug/lib/modules/<release>/vmlinux`. Otherwise it only reads sysfs, vmlinux, and live kernel memory and prints kselftest output.

## Dependencies and Integration Points

It depends on aligned ITS mitigation being active, no retpoline deployment for this path, drgn, pyelftools, capstone, accessible kernel debug symbols, and readable live kernel memory.

## Risks and Edge Cases

The script assumes `.retpoline_sites`, `__retpoline_sites`, and ITS thunk symbols exist and match the running kernel. Operand parsing is narrow, and some unexpected instruction forms are classified unknown. Copying vmlinux via `os.system()` does not shell-quote the supplied path.

## Test Signals

Pass signals include zero failed sites, per-site diagnostics showing safe address alignment or acceptable thunk/direct branch targets, and a final kselftest pass when `tests_failed == 0`.
