# sources/distributed-fs/ceph-client/arch/x86/kernel/ibt_selftest.S

## Purpose
Provides a tiny Indirect Branch Tracking selftest target that intentionally jumps indirectly to a function without ENDBR annotation.

## Important APIs And Labels
Defines `ibt_selftest_noendbr` with `ANNOTATE_NOENDBR` and `ibt_selftest`, which loads the no-ENDBR target address and performs an indirect jump marked retpoline-safe.

## Control Flow And State
The no-ENDBR target returns normally only if IBT is not enforcing or the #CP handler has made the expected adjustment; the comment notes the #CP handler sets `%ax` to zero. There is no persistent state in this file.

## Dependencies And Integration Points
Depends on objtool annotations, IBT/#CP exception handling, and nospec branch annotations. It is consumed by x86 CET/IBT selftest code elsewhere.

## Risks And Test Signals
Risks are annotation drift, jumping to a symbol that accidentally gets ENDBR, or #CP handler behavior changing. Test signals include CET/IBT boot selftests, expected control-protection exception handling, and objtool validation of unwind/no-ENDBR metadata.
