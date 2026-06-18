# sources/distributed-fs/ceph-client/kernel/rcu/Makefile

## Purpose
`kernel/rcu/Makefile` selects the RCU subsystem objects built for the active configuration and adjusts instrumentation flags for RCU code.

## Important APIs, types, and functions
The Makefile always builds `update.o` and `sync.o`. It conditionally builds `srcutree.o`, `srcutiny.o`, `rcutorture.o`, `rcuscale.o`, `refscale.o`, `tree.o`, `tiny.o`, and `rcu_segcblist.o` according to Kconfig symbols.

## Control flow
Kbuild evaluates configuration variables and appends objects to `obj-y` or `obj-$(CONFIG_...)`. KCOV instrumentation is disabled for this directory because coverage is non-deterministic and generally not syscall-input-driven. When KCSAN is enabled, the file adds debug-friendly flags `-g -fno-omit-frame-pointer`.

## State and persistence behavior
This file has no runtime state. It controls which object files become part of the kernel or module build.

## Dependencies and integration points
It integrates with Kbuild, Kconfig symbols from `kernel/rcu/Kconfig`, KCOV, KCSAN, and the RCU source files. `CONFIG_RCU_NEED_SEGCBLIST` is the build gate for segmented callback list support used by tree RCU, tree SRCU, and generic Tasks RCU.

## Risks and invariants
Object selection must match Kconfig semantics. Missing `rcu_segcblist.o` for a configuration that references segmented callback lists would cause link failures; building incompatible tree/tiny files would create duplicate or missing symbols. Instrumentation choices matter because RCU internals are sensitive to recursion, timing, and data-race observation.

## Test signals
Build matrix coverage across tiny, tree, SRCU, torture, scale, refscale, KCOV, and KCSAN configurations is the main signal. Link errors and unexpected instrumentation recursion are the likely regressions.
