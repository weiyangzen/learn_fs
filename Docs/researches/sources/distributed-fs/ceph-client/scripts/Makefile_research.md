# sources/distributed-fs/ceph-client/scripts/Makefile

## Purpose
`scripts/Makefile` defines host tools, generated targets, subdirectories, and build flags for Linux kernel build helper programs.

## APIs, Types, And Functions
It uses kbuild variables such as `hostprogs-always-*`, `hostprogs`, `targets`, `subdir-*`, object lists, `HOSTCFLAGS_*`, and `HOSTLDLIBS_*`. It defines a `filechk_rust_target` rule to generate `target.json`.

## Control Flow
Kbuild evaluates configuration-dependent host programs: `kallsyms`, `recordmcount`, `sorttable`, `asn1_compiler`, `sign-file`, Rust doctest helpers, and tracepoint tools. It adds include paths and libraries as needed, generates Rust target data on x86 when Rust is enabled, and descends into plugin, genksyms, SELinux, IPE, and core script subdirs.

## State And Persistence
Generated host binaries, `target.json`, and `module.lds` are build artifacts. No runtime state is held by the Makefile.

## Dependencies And Integration Points
It integrates deeply with kbuild, host compiler/linker rules, libcrypto via `pkg-config`, Rust host tool support, ORC unwind metadata, and architecture-specific include paths.

## Risks And Test Signals
Risks include stale config gating, missing host libraries, incorrect architecture include selection, or Rust target regeneration drift. Test signals are successful kernel host-tool builds under relevant configs and correct incremental rebuilds when dependencies change.
