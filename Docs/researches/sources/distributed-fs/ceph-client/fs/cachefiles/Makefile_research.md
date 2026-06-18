# sources/distributed-fs/ceph-client/fs/cachefiles/Makefile

## Purpose
This Makefile composes the CacheFiles module object from its core implementation files and conditionally adds optional error-injection and on-demand sources.

## Important APIs, Types, and Functions
`cachefiles-y` includes `cache.o`, `daemon.o`, `interface.o`, `io.o`, `key.o`, `main.o`, `namei.o`, `security.o`, `volume.o`, and `xattr.o`. `cachefiles-$(CONFIG_CACHEFILES_ERROR_INJECTION)` adds `error_inject.o`; `cachefiles-$(CONFIG_CACHEFILES_ONDEMAND)` adds `ondemand.o`; `obj-$(CONFIG_CACHEFILES)` emits `cachefiles.o`.

## Control Flow
There is no runtime flow. Kbuild turns the selected objects into the CacheFiles module or built-in object, matching the internal header's conditional stubs.

## State and Persistence Behavior
Build selection determines which runtime features exist. The object list also defines link availability for exported internal symbols such as daemon fops, cache ops, netfs I/O ops, xattr helpers, volume acquisition, and on-demand request handlers.

## Dependencies and Integration Points
The Makefile integrates with the Kconfig symbols in the same directory and with core kernel Kbuild. Its ordering must keep `main.o` linked with all helpers it registers or references.

## Risks and Edge Cases
Missing an object causes link failures or feature stubs to diverge from actual compiled implementations. Adding on-demand calls outside `#ifdef CONFIG_CACHEFILES_ONDEMAND` without updating the Makefile and stubs would break non-on-demand builds.

## Test Signals
Run kernel builds for `CONFIG_CACHEFILES=n`, `m`, and `y`, and matrix builds for `CONFIG_CACHEFILES_ERROR_INJECTION` and `CONFIG_CACHEFILES_ONDEMAND`. Link failures are the primary test signal.
