# sources/distributed-fs/ceph-client/lib/kunit/user_alloc.c

Purpose: provides KUnit helpers for tests that need a user address space or user mappings from kernel test threads.

Important APIs/types/functions: `struct kunit_vm_mmap_resource`, `struct kunit_vm_mmap_params`, `kunit_attach_mm()`, `kunit_vm_mmap_init()`, `kunit_vm_mmap_free()`, and `kunit_vm_mmap()`.

Control flow: `kunit_attach_mm()` returns if the task already has an `mm`, rejects non-MMU configs, allocates an `mm_struct`, sets `task_size`, chooses mmap layout, and attaches it to the current kthread via `kthread_use_mm()`. `kunit_vm_mmap()` wraps `vm_mmap()` in a KUnit resource, storing address and size for cleanup bookkeeping.

State/persistence: attaches an mm to the current kthread until the process dies. The resource stores mapping metadata, but the free function only frees metadata because the test monitor runs after the test mm is gone.

Dependencies/integration: depends on MMU memory-management APIs, `vm_mmap()`, `kthread_use_mm()`, KUnit resources, and exported-for-KUnit symbols.

Risks: `vm_mmap()` returns encoded errors in normal kernel API style; this code only checks zero as failure and may propagate error values as addresses. It intentionally does not unmap during resource free.

Test signals: no direct tests in this subset; callers should validate successful nonzero mapping and run under MMU configs.
