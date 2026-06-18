# File Research: sources/cow-pools/nilfs-utils/sbin/mount/sundries.c

## Scope

Legacy support utilities shared by mount and umount helpers.

## APIs And Behavior

- `xstrndup()`, `xstrconcat3()`, and `xstrconcat4()` provide fatal-on-OOM string allocation/concatenation helpers.
- `block_signals()` blocks or unblocks all signals except SIGTRAP and SIGSEGV.
- `error()` prints nonfatal diagnostics unless quiet mode is active.
- `matching_type()` matches filesystem type filters with `no` negation and excludes swap.
- `matching_opts()` checks whether a full option string satisfies requested option/nooption filters.
- `canonicalize()` returns stable strings for pseudo sources like `none`, `proc`, and `devpts`, otherwise tries `myrealpath()` and falls back to the original path.

## State And Dependencies

Uses external `mount_quiet`, NLS, `xmalloc`, `xrealloc`, and local realpath helper. It is derived from util-linux mount support code.

## Risks And Invariants

`matching_opts()` uses stack allocation proportional to the test option string length. `canonicalize()` deliberately returns the input path unchanged when realpath fails, so callers must not treat it as proof of existence.
