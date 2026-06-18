# sources/distributed-fs/lustre-release/lustre/mdt/Makefile

## Purpose

This `Makefile` defines the Lustre Metadata Target (`mdt`) kernel module composition. It tells kbuild to build `mdt.o` as a module and lists the object files that make up the MDT implementation.

## Important APIs, Types, And Functions

There are no C APIs or runtime functions in this file. The important build variables are `obj-m += mdt.o`, which declares the module, and `mdt-objs`, which accumulates all object files linked into it. The object list includes handler, library, reintegration, xattr, recovery, open, identity, procfs, filesystem, size-on-MDS, LVB, HSM, MDS integration, IO, restripe, HSM coordinator/action/request/client/agent pieces, coordinator support, and batch support.

## Control Flow

Build control is linear kbuild variable evaluation. `mdt-objs` is initialized with core MDT objects and then extended over several lines with HSM and coordinator-related objects. If `CONFIG_GCOV_PROFILE_LUSTRE` is set, `GCOV_PROFILE := y` enables coverage instrumentation for the module.

## State And Persistence Behavior

The Makefile itself has no runtime state or persistence. It controls which source files become part of the MDT module binary. Changing the object list changes available runtime functionality and can introduce unresolved symbols or remove feature entry points.

## Dependencies And Integration Points

It integrates with the Linux kernel module build system and Lustre's build configuration. The object list is the build-time counterpart to source files under `lustre/mdt/`; those objects implement the server side that MDC client files in this subset talk to through MDS/MDT RPCs.

## Risks

The main risks are build omissions and instrumentation mismatch. Removing or misordering objects can break link-time symbol resolution or silently omit feature support. GCOV enablement depends on the `CONFIG_GCOV_PROFILE_LUSTRE` configuration and may affect build outputs and performance in test kernels.

## Test Signals

Signals are compile and link success for `mdt.o`, module load availability, and feature tests that exercise each listed component. Coverage builds should confirm `GCOV_PROFILE` is applied when `CONFIG_GCOV_PROFILE_LUSTRE` is enabled.
