# sources/distributed-fs/ceph-client/arch/s390/kvm/diag.c

## Purpose
Implements in-kernel handling for selected s390 DIAGNOSE instructions intercepted by SIE. The handled diagnose codes cover page discard, time-slice yield, directed yield, page-reference services for pfault, IPL reset requests, and virtio-ccw hypercalls.

## Important APIs, Types, And Functions
The public entry point is `kvm_s390_handle_diag`. Internal handlers are `diag_release_pages`, `__diag_page_ref_service`, `__diag_time_slice_end`, `__diag_time_slice_end_directed`, `__diag_ipl_functions`, and `__diag_virtio_hypercall`. `do_discard_gfn_range` walks memslots and calls `gmap_helper_discard`. `diag9c_forwarding_overrun` rate-limits directed-yield forwarding through `diag9c_forwarding_hz`.

## Control Flow
`kvm_s390_handle_diag` rejects problem-state diagnose instructions, extracts the diagnose code, traces it, and dispatches by code. DIAG 0x10 validates a page-aligned real range, accounts for prefix-page remapping, locks the VM mmap for read, and discards matching host virtual ranges. DIAG 0x258 reads a real-address parameter block, validates version/length/masks, and either registers or cancels pfault token state. DIAG 0x44 yields the current vCPU. DIAG 0x9c attempts directed yield to a target vCPU or forwards to a preempted host CPU within a rate limit. DIAG 0x308 prepares reset flags and exits to userspace. DIAG 0x500 writes a virtio-ccw notification to the KVM I/O bus and returns the cookie/result in GPR2 when handled in-kernel.

## State And Persistence
State changes are runtime-only. The file updates vCPU statistics, trace events, `vcpu->arch.pfault_token/select/compare`, `run->s390_reset_flags`, `run->exit_reason`, and GPR return values. Static `forward_cnt` and `cur_slice` rate-limit DIAG 0x9c forwarding. Page discard affects host memory backing and guest page cache residency, not durable storage.

## Dependencies And Integration Points
Integrates with KVM memslot iteration, `gmap_helper_discard`, guest real-memory access helpers from `gaccess.h`, pfault state in `kvm-s390.h`, scheduler yield helpers, reset exit ABI (`KVM_EXIT_S390_RESET`), virtio-ccw notification bus, and s390 tracing/statistics. It is reached from the instruction-intercept dispatcher in `intercept.c`.

## Risks And Edge Cases
DIAG 0x10 must split ranges that overlap the two prefix pages or it can discard the wrong guest frames. The pfault token path must refuse token changes while a handshake is active and must distinguish specification from addressing exceptions. Directed yield has concurrency races with target vCPU scheduling and deliberately treats invalid/self/running targets as ignored. Reset handling returns `-EREMOTE` to force userspace action. Virtio hypercalls must not overwrite GPR2 if userspace will handle the diagnose.

## Test Signals
Exercise diagnose instruction emulation in s390 KVM selftests or guest workloads: page-release ranges including prefix overlap, pfault token/cancel return codes, spin/yield behavior, DIAG 0x308 reset exits and flags, virtio-ccw notifications with and without CSS support, problem-state privilege exceptions, and unknown diagnose fallback to userspace.
