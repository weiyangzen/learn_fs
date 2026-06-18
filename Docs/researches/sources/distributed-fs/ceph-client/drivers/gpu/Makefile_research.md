# sources/distributed-fs/ceph-client/drivers/gpu/Makefile

Purpose: orders common GPU objects and major GPU-related subdirectories.

Important APIs/types/functions: builds `buddy.o` under `CONFIG_GPU_BUDDY`, always descends into `host1x/`, `drm/`, `vga/`, and `tests/`, and conditionally includes `ipu-v3/`, `trace/`, and `nova-core/`.

Control flow: Kbuild link order places `buddy.o` before consumers and `host1x/` before `drm/` for built-in Tegra initialization ordering.

State/persistence: build-time composition only.

Dependencies/integration: integrates the common buddy allocator with DRM/host1x consumers and GPU memory tracing/tests.

Risks: link-order changes can break built-in initialization or symbol resolution.

Test signals: built-in and module builds for GPU buddy, host1x plus DRM, and GPU buddy KUnit tests.
