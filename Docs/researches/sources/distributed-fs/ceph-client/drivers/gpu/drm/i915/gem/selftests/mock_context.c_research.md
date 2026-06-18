# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.c

## Purpose
Creates lightweight mock, live, and kernel GEM contexts for selftests without normal userspace ioctl setup.

## APIs And Control Flow
Provides `mock_context()`, `mock_context_close()`, `mock_init_contexts()`, `live_context()`, `kernel_context()`, and `kernel_context_close()`. Mock context allocation initializes refs, mutexes, stale engine lists, persistence, optional mock PPGTT, default engines, and handle/VMA lookup structures. Live contexts are created from proto-contexts, registered in the file-private xarray, and configured for no error capture. Kernel contexts are non-bannable, persistent, and optionally bound to a supplied VM.

## State, Dependencies, Integration, Risks, And Tests
State persists for the returned context lifetime and referenced VM/engine set. Dependencies include file-private data, mock DRM/GTT, proto-context creation, default engines, xarray registration, and common close paths. Used by many GEM selftests. Risks are partial-init cleanup, VM ref leaks, and file-private ID leaks. Signals are context creation errors and downstream request allocation failures.
