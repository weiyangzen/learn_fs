# sources/distributed-fs/ceph-client/scripts/basic/Makefile

## Purpose
`scripts/basic/Makefile` builds the essential `fixdep` host tool and defines early generated-file rules needed by the kernel build.

## APIs, Types, And Functions
It uses `hostprogs-always-y += fixdep`, defines `gen-randstruct-seed`, and creates rules for `randstruct.seed` and `include/generated/integer-wrap.h`.

## Control Flow
Kbuild always builds `fixdep`. When `CONFIG_RANDSTRUCT` is enabled, it runs `gen-randstruct-seed.sh`. When `CONFIG_UBSAN_INTEGER_WRAP` is enabled, it touches `integer-wrap.h` whenever the ignore list changes to force rebuilds.

## State And Persistence
Persistent build artifacts are the `fixdep` host binary, `randstruct.seed`, and generated integer-wrap header timestamp.

## Dependencies And Integration Points
It integrates with the earliest kbuild dependency-generation stage, GCC plugin/randomized layout support, and UBSAN integer-wrap build invalidation.

## Risks And Test Signals
Risks include incorrect early dependency ordering and stale generated headers. Test signals are successful clean builds, `fixdep` availability before normal dependency processing, and rebuilds when randomization or integer-wrap inputs change.
