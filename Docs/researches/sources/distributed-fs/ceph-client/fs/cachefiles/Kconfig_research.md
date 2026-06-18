# sources/distributed-fs/ceph-client/fs/cachefiles/Kconfig

## Purpose
This Kconfig file defines the build-time feature switches for CacheFiles, the FS-Cache backend that stores network filesystem cache objects as files on a mounted local filesystem.

## Important APIs, Types, and Functions
It declares `CONFIG_CACHEFILES`, `CONFIG_CACHEFILES_DEBUG`, `CONFIG_CACHEFILES_ERROR_INJECTION`, and `CONFIG_CACHEFILES_ONDEMAND`. `CACHEFILES` is a tristate depending on `NETFS_SUPPORT`, `FSCACHE`, and `BLOCK`. Debug, error injection, and on-demand mode are optional booleans layered on top.

## Control Flow
There is no runtime control flow. Build configuration selects whether `fs/cachefiles` is compiled and which optional source files and internal code paths are enabled.

## State and Persistence Behavior
The state is compile-time configuration. Enabling `CACHEFILES` creates the module/built-in backend and its `/dev/cachefiles` daemon interface. `CACHEFILES_ERROR_INJECTION` exposes sysctl-driven test state. `CACHEFILES_ONDEMAND` enables the userspace delegated cache-miss protocol.

## Dependencies and Integration Points
The options integrate with the netfs library, FS-Cache core, block layer, sysctl for error injection, module parameter debug support, and userspace cachefilesd configuration.

## Risks and Edge Cases
Incorrect dependency changes can produce build combinations where CacheFiles lacks the netfs/FSCache/block primitives it assumes. On-demand mode is default off and materially changes read-miss behavior, so tests must cover both compiled-in and compiled-out stubs.

## Test Signals
Build `CACHEFILES` as built-in and module, with and without debug, error injection, and on-demand mode. Confirm `make oldconfig` prompts are sensible and that disabled optional features leave stubbed internal helpers link-clean.
