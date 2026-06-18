# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/efivarfs.sh

## Purpose
Main efivarfs behavior suite. It validates variable creation, empty create rejection, helper-based create/read, deletion, zero-size delete semantics, unlink of open variables, valid/invalid filename parsing, truncation protection, and multi-open close semantics.

## Important APIs, Types, And Functions
Uses `/sys/firmware/efi/efivars`, EFI attribute bytes `\x07\x00\x00\x00`, `chattr -i`, `rm`, `stat`, shell redirections, `mknod` FIFO synchronization, and helpers `create-read` and `open-unlink`. Functions include `file_cleanup()`, `check_prereqs()`, `run_test()`, individual `test_*` functions, `setup_test_multiple()`, `waitstart()`, `waitpipe()`, and `endjob()`.

## Control Flow
After root/mount checks, it runs each test in a subshell and records pass/fail. Single-variable tests create/delete a variable with a fixed GUID. Filename tests try accepted and rejected names. Multi-open tests use named pipes to hold one writer and two readers open, closing them in controlled order to validate create/delete only occurs on final close.

## State And Persistence
It writes real EFI variables under efivarfs and uses `/tmp/efivarfs_pipe*` FIFOs. Cleanup removes immutable flags and files when possible.

## Dependencies And Integration Points
Requires root, EFI firmware, efivarfs mounted, `chattr`, helper binaries, and safe firmware variable write capacity.

## Risks
EFI variable writes are invasive and can be limited by firmware storage. The cleanup trap is local to multi-test setup and uses shared `/tmp` pipe names that may collide. Incorrect cleanup can leave test variables.

## Test Signals
Signals are per-test `[PASS]`/`[FAIL]`, correct file size/existence changes, failed invalid filename creation, refused zero truncation, and final-close deletion/creation behavior.
