# sources/distributed-fs/lustre-release/lnet/Makefile

## Purpose
This Kbuild makefile declares the top-level LNet module subdirectories to build: core LNet, kernel LNDs, and selftest.

## Important APIs, Types, And Functions
The only build rules are `obj-m += lnet/`, `obj-m += klnds/`, and `obj-m += selftest/`.

## Control Flow
During an out-of-tree Lustre kernel-module build, Kbuild descends into each listed subdirectory and evaluates its own makefile. This file does not apply config gating itself; the subdirectories contain their own object selection.

## State, Persistence, And Dependencies
No runtime state exists. The persistent behavior is build graph inclusion: omitting a directory here prevents its child makefiles from contributing modules.

## Integration Points
It connects the Lustre build system to core LNet code, LND modules, and the selftest module tree.

## Risks
Accidental removal or reordering can omit modules from builds or affect build diagnostics. Because all entries are `obj-m`, downstream config gates must be correct in child makefiles.

## Test Signals
Build tests should verify that `lnet/`, `klnds/`, and `selftest/` are entered and that expected modules appear under representative configs.
