# sources/distributed-fs/ceph-client/tools/Makefile

## Purpose
Top-level Linux tools Makefile. It advertises available tool targets and dispatches build, install, and clean commands into subdirectories.

## Important APIs, Types, And Functions
- Exports empty `srctree` and `objtree` for tools using kernel-like variables.
- Includes `scripts/Makefile.include` for `descend` and common Kbuild helpers.
- Defines individual targets such as `perf`, `selftests`, `cpupower`, `objtool`, `ynl`, and many others.
- Defines aggregate `all`, `install`, and `clean` targets.

## Control Flow
Most targets call `$(call descend,<dir>[,<target>])`. `perf` is special and invokes `make -C perf O=$(PERF_O) subdir=`. Install and clean targets mirror build targets with `_install` and `_clean` suffixes.

## State And Persistence
No runtime state. Build artifacts are produced in tool subdirectories and optionally under `O=` output trees; `PERF_O` maps `O` to `$(O)/tools/perf`.

## Dependencies And Integration Points
Integrates all kernel userspace tools and relies on each subdirectory Makefile. The accounting tools in this subset are not directly listed here, so they are built by entering `tools/accounting` explicitly or through external packaging.

## Risks
Aggregate targets can be broad and expensive. Target names must stay synchronized with available subdirectories. `clean` dispatch can remove many generated outputs.

## Test Signals
Run `make -C tools help`, selected targets, install targets with `DESTDIR`, and clean targets. Verify `O=` handling for `perf`.
