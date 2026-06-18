# sources/distributed-fs/ceph-client/rust/bindings/bindings_helper.h

## Purpose
Provides the curated C include surface that bindgen uses to generate the Rust `bindings` crate, plus constant helper declarations for C macros and configuration-specific subsystem exposure.

## APIs, Types, and Functions
The header includes many kernel subsystem headers: ACPI, DRM, KUnit, auxiliary bus, block, clock, completion, CPU, cpumask, credentials, device core internals, DMA, file/firmware/fs, I/O, jump labels, memory management, OF/platform/PCI, PID namespaces, poll, property, PWM, refcount, regulator, scheduler, security, slab, task work, USB, wait queues, workqueues, xarray, and trace events. It defines `RUST_CONST_HELPER_*` constants for values bindgen cannot read as Rust constants, including GFP flags, page and slab alignment, block/file flags, xarray flags, vm flags, and optional GPU buddy flags. Conditional includes expose DRM panic QR and Android Binder Rust support when configured.

## Control Flow, State, and Persistence
There is no runtime control flow. During build, bindgen parses this translation unit and emits Rust declarations in `bindings_generated.rs`; the Makefile then renames helper constants by stripping `RUST_CONST_HELPER_`. Persistent outputs are generated Rust bindings under the object tree, not this source file.

## Dependencies and Integration
Depends on exact C header availability and config gates. It is integrated with `rust/Makefile`, the `bindings` crate, and Rust abstractions that rely on generated types and constants rather than handwritten FFI.

## Risks and Test Signals
Risks include exposing unstable private C layout, bindgen enum forward-reference behavior, architecture/config-specific header parse failures, constants accidentally using the wrong source expression, and the likely typo assigning `VM_MAYSHARE` from `VM_MAYEXEC`. Test signals are successful bindgen across broad configs, Rust compilation of generated constants, diff review of generated bindings after header changes, and targeted builds with DRM, Binder, GPU buddy, and security options toggled.
