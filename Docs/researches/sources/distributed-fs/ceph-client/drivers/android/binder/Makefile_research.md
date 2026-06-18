# sources/distributed-fs/ceph-client/drivers/android/binder/Makefile

## Purpose

This Makefile builds the Rust Binder driver objects when `CONFIG_ANDROID_BINDER_IPC_RUST` is enabled. It is the build glue for the Rust implementation living under `drivers/android/binder/`, not for the legacy C `binder.c` driver.

## Important APIs, types, and functions

The file has no functions or types. Its build-facing API is:

- `ccflags-y += -I$(src)` so generated or local C trace/event headers can be found.
- `obj-$(CONFIG_ANDROID_BINDER_IPC_RUST) += rust_binder.o` to conditionally build the Rust Binder aggregate object.
- `rust_binder-y := rust_binder_main.o rust_binderfs.o rust_binder_events.o` to compose the aggregate from the Rust module object plus C shims for binderfs and events.

## Control flow

There is no runtime control flow. Kbuild reads this file during kernel build evaluation. If the Rust Binder config option is disabled, none of the listed objects are linked. If enabled, Kbuild links `rust_binder.o` from the three component objects.

## State and persistence behavior

The file persists no runtime state. It controls object inclusion in the kernel build output. The important state is the build-time configuration value of `CONFIG_ANDROID_BINDER_IPC_RUST` and the source directory include path.

## Dependencies and integration points

This Makefile depends on the kernel Kbuild object syntax and the surrounding Android driver Kconfig. It integrates Rust Binder code with C helper files `rust_binderfs.c` and `rust_binder_events.c`, plus local trace/event headers reachable through `-I$(src)`.

## Risks

The risk is build composition drift. Adding a Rust Binder source without updating this file can compile locally only under partial configs or fail at link time. Removing `-I$(src)` can break trace-event includes. Misnaming component objects can silently disable the Rust Binder implementation for enabled configs.

## Test signals

Build with `CONFIG_ANDROID_BINDER_IPC_RUST=y` or `m`, build with it disabled, and run a clean incremental rebuild after touching trace/event headers. Link-time presence of `rust_binder.o` and absence of unresolved Rust Binder/binderfs/event symbols are the main signals.
