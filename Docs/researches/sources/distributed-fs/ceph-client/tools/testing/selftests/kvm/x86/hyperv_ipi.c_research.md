# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_ipi.c

Purpose: Tests Hyper-V synthetic cluster IPI hypercalls, including `HvCallSendSyntheticClusterIpi` and `HvCallSendSyntheticClusterIpiEx` in slow, fast, and XMM-fast forms.

Important APIs/types/functions: `struct hv_vpset`, `struct hv_send_ipi`, and `struct hv_send_ipi_ex` model hypercall inputs; `ipis_rcvd[]` records per-VP interrupt counts; `receiver_code()` halts receiver vCPUs; `guest_ipi_handler()` increments counters and writes Hyper-V EOI; `sender_guest_code()` runs the hypercall matrix; pthread helpers run and cancel receiver vCPUs.

Control flow: The host creates one sender vCPU and two receiver vCPUs with sparse VP IDs 2 and 65 to cover multiple VP-set banks. Receiver threads enable x2APIC/Hyper-V and wait in `safe_halt()`. Sender waits for readiness, then sends IPIs to each receiver and both receivers using simple masks, sparse VP sets, and `HV_GENERIC_SET_ALL`, validating counts after each stage.

State and persistence behavior: `ipis_rcvd[]` is volatile guest global state shared by vCPUs. Hypercall input pages are reused and cleared between calls. Receiver threads run until host cancellation.

Dependencies and integration points: Requires `KVM_CAP_HYPERV_SEND_IPI`, Hyper-V CPUID setup, x2APIC, synthetic interrupt delivery, Hyper-V EOI MSR handling, XMM fast input helpers, and pthread scheduling.

Risks and maintenance notes: Busy-wait readiness and nop delays can be sensitive to scheduling. Sparse VP IDs intentionally test bank indexing; changing IDs without updating masks would weaken coverage.

Test signals: Passing means KVM routes Hyper-V synthetic IPIs to the requested vCPUs for all tested input formats and leaves untargeted vCPUs unchanged. Failures implicate VP-set parsing, fast hypercall input handling, or interrupt delivery.
