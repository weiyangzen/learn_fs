<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_perf_test.c

## Purpose
`memslot_perf_test.c` is a configurable benchmark for KVM memslot performance. It measures slot setup time and runtime cost for map, unmap, chunked unmap, active move, inactive move, and guest/host read-write patterns under many memslots.

## Important APIs, Types, and Functions
Core structures are `struct vm_data`, `struct sync_area`, `struct test_data`, `struct test_args`, and `struct test_result`. Major functions include `prepare_vm()`, `launch_vm()`, `vcpu_worker()`, `host_perform_sync()`, `guest_perform_sync()`, guest code variants for map/unmap/move/RW, `test_memslot_map_loop()`, `test_memslot_unmap_loop_common()`, `test_memslot_move_loop()`, `test_memslot_rw_loop()`, `test_execute()`, `test_loop()`, `parse_args()`, and `main()`.

## Control Flow
Setup creates a VM with one vCPU, divides memory across requested memslots, allocates and maps all pages, initializes a shared synchronization page, and starts a vCPU thread. Guest code spins until start, then alternates memory touches with atomic sync handshakes or continuous move-area writes. Host loops run for the configured duration, performing `madvise(MADV_DONTNEED)`, memslot moves, or host writes/verification. Results track slot setup duration, total guest runtime, loop count, average iteration time, and best runs.

## State and Persistence
State is in anonymous VM memory slots, `hva_slots[]`, the atomic `sync_area`, semaphores, vCPU thread state, and global options `map_unmap_verify`, `verbose`, and optional `disable_slot_zap_quirk`. The benchmark does not persist results beyond stdout.

## Dependencies and Integration Points
The file depends on KVM VM/memslot helpers, pthreads, semaphores, atomics, `processor.h`, `ucall_common.h`, `test_util.h`, and Linux memory constants. On x86 it can disable the slot zap quirk to compare behavior.

## Risks and Test Signals
Risks include slot/page alignment rejection, timeout waiting for guest sync, MMIO exits during active move tests, benchmark noise, unsupported host/guest page sizes, and duplicate variable declarations that rely on compiler diagnostics. Test signals include successful `UCALL_SYNC`/`UCALL_DONE`, optional map/unmap value verification, expected MMIO address checks, printed loop counts and average times, and clear messages when slot count is too high.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_perf_test.c -->
