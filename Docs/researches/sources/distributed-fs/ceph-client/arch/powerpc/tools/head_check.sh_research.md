# sources/distributed-fs/ceph-client/arch/powerpc/tools/head_check.sh

## Purpose
`head_check.sh` validates that 64-bit PowerPC head code remains at fixed expected locations and has not been displaced by linker-inserted branch stubs.

## Important APIs, Types, And Functions
It accepts paths to `nm` and `vmlinux`, extracts `_stext`, `start_first_256B`, `text_start`, and `start_text` into `.tmp_symbols.txt`, compares expected and actual addresses, and emits guidance about `LD_HEAD_STUB_CATCH` on failure.

## Control Flow
The script validates arguments, captures relevant symbols, checks that `start_first_256B` equals `_stext`, derives the top VMA prefix, checks that `start_text` equals the relocated `text_start`, then removes the temporary symbol file.

## State And Persistence
It temporarily creates `.tmp_symbols.txt` in the current working directory and deletes it on the success path. It has no intended persistent output.

## Dependencies And Integration Points
It depends on POSIX shell, `nm`, `grep`, `cut`, and `sed`, and integrates with the PowerPC post-link checks that protect early boot and interrupt-vector placement.

## Risks
Failure before cleanup can leave `.tmp_symbols.txt`. Address derivation with `cut -d'0' -f1` assumes the expected kernel VMA string shape. The check is sensitive to symbol names and types emitted by different toolchains.

## Test Signals
Passing output is silent with zero exit. Failures report the mismatched symbol address and point maintainers to branch-stub placement comments in the script.
