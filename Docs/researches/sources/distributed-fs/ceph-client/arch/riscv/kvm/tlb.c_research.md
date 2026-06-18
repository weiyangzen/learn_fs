# sources/distributed-fs/ceph-client/arch/riscv/kvm/tlb.c

Purpose: This file implements local and remote RISC-V KVM instruction-cache and TLB invalidation. It emits HFENCE/HINVAL sequences for G-stage and VS-stage translations, sanitizes stale VMID mappings on CPU migration, processes vCPU fence requests, queues bounded HFENCE work, and broadcasts requests to selected vCPUs.

Important APIs/types/functions: Local flush APIs include `kvm_riscv_local_hfence_gvma_vmid_gpa/all`, `kvm_riscv_local_hfence_gvma_gpa/all`, `kvm_riscv_local_hfence_vvma_asid_gva/all`, `kvm_riscv_local_hfence_vvma_gva/all`, and `kvm_riscv_local_tlb_sanitize`. Request processors include `kvm_riscv_fence_i_process`, `kvm_riscv_tlb_flush_process`, `kvm_riscv_hfence_vvma_all_process`, and `kvm_riscv_hfence_process`. Broadcast APIs include `kvm_riscv_fence_i`, all `kvm_riscv_hfence_*` variants, and `kvm_arch_flush_remote_tlbs_range`.

Control flow: Local range flushes fall back to whole-scope flushes when the requested range spans too many pages, otherwise use Svinval sequences if available or legacy HFENCE instructions. VS-stage flushes temporarily swap `HGATP` to the target VMID before issuing VVMA operations, then restore it. Remote requests select vCPUs by hart base/mask, enqueue detailed HFENCE data into a per-vCPU ring, and fall back to broader requests when the ring is full. vCPU request processing drains the queue and dispatches either NACL accelerated HFENCEs or local instructions.

State and persistence: Each vCPU has a bounded `hfence_queue` with head/tail protected by `hfence_lock`. `last_exit_cpu` and the VMID static/vendor quirk state control migration sanitization. Firmware-event PMU counters are incremented for received fence operations.

Dependencies and integration points: It depends on RISC-V instruction-definition macros, Svinval extension detection, KVM request bits, NACL HFENCE helpers, VMID state, and PMU firmware counters. G-stage mapping code uses these APIs after PTE changes.

Risks and test signals: Incorrect VMID/HGATP swapping can flush the wrong address space or leave host state corrupted. Queue overflow deliberately broadens invalidation and must remain conservative. Tests should cover Svinval and non-Svinval hosts, no-VMID hosts, vendor VS-stage TLB quirk, hart-mask selection, queue-full fallback, NACL and direct paths, instruction-cache flush requests, and range flushes crossing fallback thresholds.
