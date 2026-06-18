<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/ucall_common.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/ucall_common.c

## Purpose
`ucall_common.c` implements architecture-neutral guest-to-host "ucall" support. It lets guest code report sync points, done/abort status, formatted output, and assertion metadata through an architecture-specific exit mechanism.

## Important APIs, Types, and Functions
`struct ucall_header` owns an `in_use` bitmap and one `struct ucall` per possible vCPU. Public functions include `ucall_nr_pages_required()`, `ucall_init()`, `ucall_assert()`, `ucall_fmt()`, `ucall()`, and `get_ucall()`. Internal helpers `ucall_alloc()` and `ucall_free()` manage per-vCPU slots using `test_and_set_bit()` and `clear_bit()`.

## Control Flow
Host setup allocates shared guest memory, initializes each ucall slot's host virtual address, writes the guest-visible `ucall_pool` pointer, and calls `ucall_arch_init()`. Guest calls allocate a free slot, fill command, arguments, and optional formatted text, then invoke `ucall_arch_do_ucall()` with the slot HVA. Host `get_ucall()` asks the architecture layer for the ucall address, copies the structure, and completes pending KVM I/O when needed.

## State and Persistence
State is per VM in shared memory. `ucall_pool` is deliberately guest-global data and must not be accessed directly as a host pointer. Slot allocation state is transient and protected only by atomic bitmap operations suitable for selftest guests.

## Dependencies and Integration Points
The file depends on `kvm_util.h`, `ucall_common.h`, Linux bitmap/atomic helpers, `guest_vsnprintf()`, and architecture hooks `ucall_arch_init()`, `ucall_arch_do_ucall()`, and `ucall_arch_get_ucall()`. It integrates with `GUEST_SYNC`, `GUEST_DONE`, `GUEST_ASSERT`, and host-side `REPORT_GUEST_ASSERT()`.

## Risks and Test Signals
Risks include exhausting ucall slots, freeing the wrong slot via pointer arithmetic, stale shared-memory addresses, and races when many vCPUs call concurrently. A special `GUEST_UCALL_FAILED` sentinel detects allocation failure without using `GUEST_ASSERT()`. Test signals are correct `UCALL_*` commands, completed I/O exits, and assertion metadata containing expression, file, line, and formatted buffer text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/ucall_common.c -->
