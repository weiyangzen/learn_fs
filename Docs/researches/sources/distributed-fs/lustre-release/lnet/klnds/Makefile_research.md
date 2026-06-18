# sources/distributed-fs/lustre-release/lnet/klnds/Makefile

## Purpose
This Kbuild makefile selects which kernel LNet Network Driver subdirectories participate in the build.

## Important APIs, Types, And Functions
Config-gated entries are `CONFIG_LNET_GNILND`, `CONFIG_LNET_O2IBLND`, `BUILD_EXT_O2IB`, `CONFIG_LNET_KFILND`, and `CONFIG_LNET_EFALND`. `socklnd/` is always included as an external module entry.

## Control Flow
Kbuild evaluates config symbols and optional `BUILD_EXT_O2IB` to decide which child directories to visit. In-kernel O2IB and external O2IB are mutually represented by separate entries.

## State, Persistence, And Dependencies
No runtime state exists. Build output depends on kernel config, Lustre build variables, and child makefiles.

## Integration Points
This file connects the top-level LNet build to GNILND, O2IBLND, KFILND, EFALND, and SOCKLND module builds.

## Risks
Incorrect config symbols can silently omit an LND. Always building `socklnd/` means its child makefile must handle unsupported configurations correctly. External O2IB selection depends on the build environment variable being set consistently.

## Test Signals
Matrix builds should verify each LND config independently, all enabled together, external O2IB mode, and absence of unexpected modules when configs are disabled.
