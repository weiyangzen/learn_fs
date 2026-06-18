# sources/distributed-fs/ceph-client/rust/helpers/helpers.c

## Purpose
Aggregates all Rust C helper fragments into one translation unit for bindgen and object/bitcode builds.

## APIs, Types, and Functions
Defines a bindgen-only `__rust_helper` attribute shape to expose correct C prototypes, otherwise maps helpers as exportable symbols. It includes every helper fragment from `atomic.c` through `xarray.c` in a fixed list.

## Control Flow, State, and Persistence
There is no direct runtime logic beyond the included helper functions. Build state differs depending on whether the file is parsed by bindgen, compiled into `helpers.o`, or emitted as LLVM bitcode for inline helper linking.

## Dependencies and Integration
Depends on `linux/compiler_types.h`, every included helper source, `rust/Makefile` bindgen rules, and optional `CONFIG_RUST_INLINE_HELPERS`.

## Risks and Test Signals
Risks include include-order conflicts, duplicate helper symbol names, bindgen seeing a different prototype than the compiler, and forgetting to add new helper files here. Test signals are bindgen helper generation, full Rust builds, symbol export generation, and inline/non-inline helper config builds.
