# sources/distributed-fs/ceph-client/scripts/generate_rust_target.rs

## Purpose
Creates the custom Rust target specification JSON consumed by kernel Rust builds for architectures that cannot rely solely on rustc built-in targets.

## APIs, Control Flow, and State
The file implements a tiny JSON emitter with `Value`, `Object`, `TargetSpec`, and `Display` impls, intentionally avoiding a serde dependency in the build host tool. `KernelConfig::from_stdin()` parses `include/config/auto.conf` from stdin into a `HashMap`. `KernelConfig::has()` checks `CONFIG_` options while avoiding literal config names in comments that would confuse `fixdep`, and `rustc_version_atleast()` compares `CONFIG_RUSTC_VERSION`. `main()` selects architecture behavior: ARM, ARM64, 64-bit RISC-V, and LoongArch panic because they use built-in targets; 32-bit RISC-V and non-UML i386 panic as unsupported; x86_64 and UML i386 emit architecture, data-layout, target features, LLVM target, sanitizer, pointer-width, endian, frame-pointer, stack-probe, and debug-script settings.

## Dependencies and Integration
The tool depends only on Rust stdlib and kbuild piping `auto.conf` to stdin. It integrates with Rust compilation flags and must track rustc target-spec schema changes.

## Risks and Test Signals
The hand-written JSON generator does not escape strings, which is acceptable for fixed internal keys but risky if arbitrary values are added. Version-gated pointer-width typing and x86 ABI features are brittle across rustc releases. Test signals include rustc accepting the generated target file, architecture build coverage, and negative tests for unsupported architectures.
