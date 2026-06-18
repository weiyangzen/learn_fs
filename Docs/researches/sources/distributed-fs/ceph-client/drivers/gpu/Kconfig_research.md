# sources/distributed-fs/ceph-client/drivers/gpu/Kconfig

Purpose: declares the common GPU buddy allocator option and its KUnit test option for the GPU driver subtree.

Important APIs/types/functions: defines hidden `GPU_BUDDY` and `GPU_BUDDY_KUNIT_TEST`, a tristate test option depending on `GPU_BUDDY && KUNIT` and defaulting to `KUNIT_ALL_TESTS`.

Control flow: GPU/DRM memory managers select `GPU_BUDDY`; KUnit builds allocator tests when the test option is enabled.

State/persistence: no runtime state; choices persist in kernel `.config`.

Dependencies/integration: selected by DRM buddy users and consumed by the top-level GPU Makefile and GPU tests.

Risks: hidden allocator users must select it correctly; missing selects cause unresolved `gpu_buddy` symbols.

Test signals: Kconfig dependency checks, allmodconfig, and `GPU_BUDDY_KUNIT_TEST` builds/runs.
