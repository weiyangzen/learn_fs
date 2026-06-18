# sources/distributed-fs/ceph-client/net/dcb/Kconfig

## Purpose

This Kconfig entry exposes `CONFIG_DCB`, the build-time option for Data Center Bridging rtnetlink support. It describes DCB as Ethernet enhancements for mixed traffic requirements and lists Enhanced Transmission Selection and Priority-based Flow Control as key features.

## Important APIs, Types, and Functions

There are no runtime APIs in this file. The important symbol is `DCB`, a boolean option defaulting to `n`. Enabling it causes the DCB net subsystem objects from this directory to be built according to the parent networking Makefiles.

## Control Flow

The file participates only in Kconfig resolution. When selected by a user or another config dependency, code guarded by `CONFIG_DCB` becomes available and the `net/dcb` objects can provide rtnetlink handling and notifier APIs.

## State and Persistence Behavior

The only state is the kernel build configuration. It persists in `.config` and determines whether DCB code is compiled into the kernel image.

## Dependencies and Integration Points

The option is presented to networking configuration users and is consumed by the kernel build system. Its help text targets DCB-capable Ethernet adapters and switches.

## Risks

Because the option defaults off, driver or distribution configs that expect DCB must explicitly enable it or select it. The help text is descriptive but does not encode dependencies, so dependency correctness must be maintained outside this file.

## Test Signals

Build tests should cover `CONFIG_DCB=y` and `CONFIG_DCB=n`, confirming that DCB rtnetlink handlers and exported notifier/app APIs appear only when expected.
