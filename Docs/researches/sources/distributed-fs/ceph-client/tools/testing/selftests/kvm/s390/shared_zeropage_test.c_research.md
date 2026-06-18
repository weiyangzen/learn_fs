# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/shared_zeropage_test.c

## Purpose
This s390x test verifies that executing storage-key instructions disables shared zeropage usage for the process and unshares existing shared zeropages.

## Important APIs, Types, And Functions
It uses `mmap()`, `madvise(MADV_NOHUGEPAGE)`, `/proc/self/pagemap`, `PAGEMAP_SCAN`, and page-category flags `PAGE_IS_PFNZERO` and `PAGE_IS_PRESENT`. The guest runs one `sske` through `set_storage_key()` and returns `GUEST_DONE`.

## Control Flow
`main()` maps three anonymous read-only pages, verifies page 0 can be detected as a shared zeropage, creates a one-vCPU VM, and checks page 1 still maps the shared zeropage after VM creation. It then runs guest storage-key code, confirms page 1 is no longer shared, touches page 2, and confirms no new shared zeropage is created.

## State, Dependencies, And Integration
The state is process memory mapping behavior, not guest memory: the mapped pages are intentionally outside the VM. It depends on pagemap scan support, shared zeropage availability, storage-key support, and selftest KVM VM creation.

## Risks And Test Signals
Risks include kernel configurations that do not expose or use shared zeropages, pagemap permission issues, and THP masking the behavior. Test signals are one prerequisite check plus three planned assertions: shared zeropages enabled after VM creation, gone after `sske`, and disabled for later faults.
