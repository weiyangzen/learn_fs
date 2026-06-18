# Research: sources/distributed-fs/ceph-client/include/asm-generic/mshyperv.h

## Purpose
Defines architecture-independent Hyper-V integration state, hypercall helpers, VP-set conversion, and root partition hooks. In the Ceph client source snapshot this is kernel-derived architecture infrastructure, so its behavior matters indirectly through the generic Linux APIs consumed by filesystem, networking, memory-management, driver, and concurrency code rather than through Ceph-specific business logic.

## Important APIs, Types, And Macros
Source size: 396 lines. Important visible surface detected in this header: `VTPM_BASE_ADDRESS, VP_INVAL, _hv_status_fmt, hv_status_printk, hv_status_err, hv_status_debug, hv_do_hypercall, hv_do_fast_hypercall8, hv_do_fast_hypercall16, hv_isolation_type_snp, hv_isolation_type_tdx, AEOI, hv_recommend_using_aeoi, hv_numa_node_to_pxm_info, hv_result, hv_result_success, hv_repcomp, hv_do_rep_hypercall_ex, hv_do_rep_hypercall, hv_generate_guest_id, hv_get_hypervisor_version, hv_setup_vmbus_handler, hv_remove_vmbus_handler, hv_setup_stimer0_handler`. Direct dependencies: linux/types.h, linux/atomic.h, linux/bitops.h, acpi/acpi_numa.h, linux/cpumask.h, linux/nmi.h, asm/ptrace.h, hyperv/hvhdk.h. The header is part of the asm-generic fallback layer; architectures can replace or predefine pieces before including it, so the API contract is as important as the inline implementation.

## Control Flow
Control flow wraps raw hypercalls, fast hypercalls, repeated hypercalls with rep completion loops, guest ID generation, Hyper-V initialization hooks, CPU-to-VP conversion, cpumask-to-VPset packing, status formatting, panic reporting, isolation hooks, and root-partition memory/processor calls. Most branches are compile-time branches selected by CONFIG_* options, word size, endian mode, or architecture-provided override macros. Runtime branches, where present, are narrow checks for fast paths, unsupported sizes, feature availability, or fault/error returns.

## State And Persistence
State lives in the global ms_hyperv structure, hv_vp_index, partition IDs, per-CPU hypercall pages, and root/isolation feature flags. Risks include stale VP mappings on CPU hotplug, invalid sparse bank masks for large VP counts, not touching the NMI watchdog in long rep hypercalls, and using root-only calls when CONFIG_MSHV_ROOT is off. The header itself does not perform durable persistence. Effects are immediate kernel memory/register/page-table/I/O side effects governed by the caller's locking, interrupt, preemption, or MMU context.

## Dependencies And Integration Points
Integrated through architecture <asm/...> wrapper headers, generic kernel subsystems, and configuration-specific include selection during kernel builds. It depends on the surrounding kernel include environment for types such as `struct mm_struct`, `struct page`, `pte_t`, `atomic_t`, `pt_regs`, endian helpers, barriers, and configuration symbols. Consumers should include the public subsystem header rather than this generic fallback directly unless the file explicitly documents otherwise.

## Risks And Edge Cases
State lives in the global ms_hyperv structure, hv_vp_index, partition IDs, per-CPU hypercall pages, and root/isolation feature flags. Risks include stale VP mappings on CPU hotplug, invalid sparse bank masks for large VP counts, not touching the NMI watchdog in long rep hypercalls, and using root-only calls when CONFIG_MSHV_ROOT is off. Additional edge cases include unsupported CONFIG combinations, hidden assumptions about BITS_PER_LONG or endian layout, side effects in macro arguments, address-space annotation misuse, and compile-only paths that are rarely exercised on mainstream architectures.

## Test Signals
Useful test signals include configuration matrix builds, subsystem selftests that exercise the exported API, fault-injection where applicable, and runtime stress on SMP/preemption/debug configurations. For this repository, the practical signal is whether code importing the Ceph client headers still builds under representative kernel-style configuration matrices and whether static analysis catches misuse of the generated fallback API.
