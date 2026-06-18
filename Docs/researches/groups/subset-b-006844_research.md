# subset-b-006844 grouped research

This grouped report covers the requested KVM selftest utility and test sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/kvm`. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/sparsebit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/sparsebit.c

## Purpose
`sparsebit.c` implements a memory-efficient sparse bitset for 64-bit indexes. KVM selftests use it to track large guest physical and virtual page spaces without allocating dense bitmaps. It supports single-bit and range set/clear queries, iteration over set or clear ranges, copy/free/dump helpers, and an internal validator.

## Important APIs, Types, and Functions
The public API is centered on `struct sparsebit`, `sparsebit_alloc()`, `sparsebit_free()`, `sparsebit_copy()`, `sparsebit_is_set()`, `sparsebit_is_set_num()`, `sparsebit_is_clear()`, `sparsebit_is_clear_num()`, `sparsebit_num_set()`, `sparsebit_any_set()`, `sparsebit_all_set()`, `sparsebit_first_set()`, `sparsebit_next_set()`, `sparsebit_next_set_num()`, `sparsebit_next_clear()`, `sparsebit_next_clear_num()`, `sparsebit_set_num()`, `sparsebit_clear_num()`, `sparsebit_set_all()`, `sparsebit_clear_all()`, `sparsebit_dump()`, and `sparsebit_validate_internal()`. Internally, `struct node` stores a binary-search-tree node with `idx`, a 32-bit `mask`, and `num_after` for a contiguous run following the mask.

## Control Flow
Lookup walks the BST by node start index, then checks whether the target bit falls in the mask or in `num_after`. Mutations first use `node_split()` and `node_add()` to ensure the affected range has mask-addressable boundaries, update the mask or run count, and then call `node_reduce()` to merge adjacent runs or remove empty nodes. Range operations handle unaligned leading/trailing bits with single-bit helpers and whole-mask middle ranges with splits, node deletion, and `num_after` expansion. Iterators use `node_first()`, `node_next()`, `node_prev()`, and `node_first_set()/node_first_clear()` to find the next requested bit or range.

## State and Persistence
All state is heap resident in a `struct sparsebit` tree. `num_set` is a redundant total used for O(1) counting and for all-set overflow semantics: zero means either none set or every possible bit set, so callers must use `sparsebit_any_set()`/`sparsebit_all_set()` for boolean tests. No filesystem or kernel state is persisted.

## Dependencies and Integration Points
The file depends on `sparsebit.h`, `test_util.h`, standard allocation/assert APIs, and compiler builtins such as `__builtin_popcount()` and `__builtin_ctz()`. KVM VM helpers integrate this structure with guest page allocation, valid-page tracking, protected-page tracking, and page table mapping decisions.

## Risks and Test Signals
The main risks are off-by-one errors near `UINT64_MAX`, wraparound in `idx + num - 1`, tree imbalance, stale parent pointers, incorrect `num_set` accounting, and invalid reductions that overlap adjacent nodes. Test signals include `sparsebit_validate_internal()` invariant checks, diagnostic dumps, assertions in all public operations, and the optional `FUZZ` driver that compares sparsebit behavior against a simple range log under random operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/sparsebit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/string_override.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/string_override.c

## Purpose
`string_override.c` supplies minimal `memcmp()`, `memcpy()`, `memset()`, and `strnlen()` implementations that can be linked into KVM guest code. This prevents compiler-generated calls to out-of-line libc or PLT entries, which are not available inside selftest guests.

## Important APIs, Types, and Functions
The file defines standard C string/memory entry points with simple byte loops. `memcmp()` returns the first unsigned-byte difference, `memcpy()` copies forward and returns `dest`, `memset()` fills bytes and returns `s`, and `strnlen()` counts until NUL or the supplied limit.

## Control Flow
All functions are straight-line loops with no helper calls. They intentionally avoid optimized library dispatch, dynamic loading, vector routines, and platform-specific code.

## State and Persistence
There is no persistent state. The only side effects are writes to caller-provided memory in `memcpy()` and `memset()`.

## Dependencies and Integration Points
The only include is `<stddef.h>`. These symbols override basic built-ins when guest payloads are linked, integrating with any guest C code that the compiler lowers to standard memory/string functions.

## Risks and Test Signals
The risk is semantic drift from standard functions, especially overlapping `memcpy()` behavior, signedness in `memcmp()`, and bounded termination in `strnlen()`. Test signals are indirect: guest code that uses these helpers should execute without jumping to unresolved host/runtime text and should preserve expected C-library behavior for simple byte operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/string_override.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/test_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/test_util.c

## Purpose
`test_util.c` provides shared host and guest utility functions for KVM selftests. It covers SIGBUS handling, deterministic guest random numbers, size and integer parsing, `timespec` arithmetic, skip reporting, host backing-memory discovery, sysfs/procfs probing, and small string/clocksource helpers.

## Important APIs, Types, and Functions
Key APIs include `expect_sigbus_handler()`, `new_guest_random_state()`, `guest_random_u32()`, `parse_size()`, `timespec_to_ns()`, `timespec_add_ns()`, `timespec_add()`, `timespec_sub()`, `timespec_elapsed()`, `timespec_div()`, `print_skip()`, `thp_configured()`, `get_trans_hugepagesz()`, `is_numa_balancing_enabled()`, `get_def_hugetlb_pagesz()`, `vm_mem_backing_src_alias()`, `get_backing_src_pagesz()`, `is_backing_src_hugetlb()`, `backing_src_help()`, `parse_backing_src_type()`, `get_run_delay()`, `atoi_paranoid()`, `strdup_printf()`, and `sys_get_cur_clocksource()`. The backing source table maps `enum vm_mem_backing_src_type` values to names and mmap flags.

## Control Flow
Parsing functions validate input eagerly through `TEST_ASSERT()` and fail fast on overflow or trailing characters. Sysfs/procfs helpers stat or read files, returning booleans for optional kernel features and skipping when hugetlb is unavailable. Backing-source helpers centralize selection of anonymous, THP, hugetlb, shared memory, and explicit hugepage sizes. Time helpers convert through nanoseconds for consistent arithmetic.

## State and Persistence
State is limited to `expect_sigbus_jmpbuf` and transient heap allocations such as `strdup_printf()` and `sys_get_cur_clocksource()` results. The file reads host state from `/sys`, `/proc`, and clocksource files but does not persist changes.

## Dependencies and Integration Points
It depends on `test_util.h`, `linux/kernel.h`, libc file/stat/time APIs, `linux/mman.h`, and KVM selftest assertion/skip conventions. The backing source helpers are used by VM memory region creation and stress tests, while the time helpers are used by performance and timer tests.

## Risks and Test Signals
Risks include misparsing large sizes, assuming sysfs/procfs file formats, using default hugepage size when no pool exists, and returning stale or malformed clocksource strings. Test signals are `TEST_ASSERT()` failures, `KSFT_SKIP` exits for unavailable host features, and performance output that depends on sane `timespec` arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/test_util.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/userfaultfd_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/userfaultfd_util.c

## Purpose
`userfaultfd_util.c` provides demand-paging infrastructure for KVM memory tests. It registers a host virtual range with userfaultfd, starts reader threads, dispatches page-fault events to a caller-provided handler, and tears the setup down cleanly.

## Important APIs, Types, and Functions
When `__NR_userfaultfd` is available, the file defines `uffd_setup_demand_paging()` and `uffd_stop_demand_paging()`. The worker `uffd_handler_thread_fn()` monitors both the userfaultfd and a stop pipe through epoll. It consumes `struct uffd_msg` records and invokes an `uffd_handler_t` with the mode, fd, and message.

## Control Flow
Setup allocates an `uffd_desc`, creates a nonblocking userfaultfd, negotiates `UFFD_API`, registers the range in missing or minor mode, verifies required ioctls (`UFFDIO_COPY` or `UFFDIO_CONTINUE`), creates one pipe per reader, and launches reader threads. Each reader waits for userfaultfd events or a pipe wakeup, optionally delays, handles page faults, counts handled pages, and exits when signaled. Stop writes to every pipe, joins readers, closes fds, and frees arrays.

## State and Persistence
State lives in `struct uffd_desc`, reader thread ids, pipe fds, and per-reader arguments. No state is persisted after `uffd_stop_demand_paging()`, but registered userfaultfd ranges affect live VM memory behavior while active.

## Dependencies and Integration Points
The file depends on Linux userfaultfd ioctls, epoll, pthreads, `kvm_util.h`, `test_util.h`, `memstress.h`, and `userfaultfd_util.h`. It integrates with demand paging and memory stress tests that resolve faults by copying or continuing pages.

## Risks and Test Signals
Risks include missing kernel userfaultfd support, unsupported minor/missing mode ioctls, lost wakeups, handler failures, incorrect nonblocking `EAGAIN` handling, and resource leaks on teardown. Test signals include `TEST_ASSERT()` checks around fd creation, registration, epoll events, handler return values, and debug output reporting handled page counts and rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/userfaultfd_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/apic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/apic.c

## Purpose
`apic.c` contains guest-side x86 APIC mode helpers for KVM selftests. It can disable the local APIC, enable xAPIC, and enable x2APIC while ensuring the software-enable bit is set in the spurious interrupt vector register.

## Important APIs, Types, and Functions
The public functions are `apic_disable()`, `xapic_enable()`, and `x2apic_enable()`. They operate on `MSR_IA32_APICBASE`, `MSR_IA32_APICBASE_ENABLE`, `MSR_IA32_APICBASE_EXTD`, `APIC_SPIV`, and `APIC_SPIV_APIC_ENABLED` through `rdmsr()`, `wrmsr()`, `xapic_read_reg()`, `xapic_write_reg()`, `x2apic_read_reg()`, and `x2apic_write_reg()`.

## Control Flow
`xapic_enable()` follows SDM sequencing: if already in x2APIC, it first disables APIC, then enables xAPIC; if APIC is disabled, it sets the enable bit. Both enable helpers then set the APIC software-enable bit in SPIV.

## State and Persistence
The functions mutate guest CPU MSR and local APIC state. The state persists for the running vCPU until reset or explicit reconfiguration.

## Dependencies and Integration Points
The file depends on `apic.h` and x86 guest register/MSR helpers. It integrates with tests that need deterministic local interrupt controller state before injecting or receiving timer, IPI, or APIC-related events.

## Risks and Test Signals
Risks include invalid APIC mode transitions, failing to set SPIV software enable, and writing xAPIC registers while still in x2APIC. Test signals are indirect: interrupt delivery tests should receive expected vectors and should not fail due to a disabled local APIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/apic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/handlers.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/handlers.S

## Purpose
`handlers.S` builds the x86 guest IDT entry stubs used by KVM selftests. Each vector wrapper normalizes the exception frame, saves general-purpose registers, calls C exception routing, restores registers, discards vector/error-code slots, and returns with `iretq`.

## Important APIs, Types, and Functions
The assembly exports `idt_handlers`, an array of stub addresses in `.rodata`, and `idt_handler_code`, the block containing generated wrappers. The shared target `handle_exception` calls the C function `route_exception()` with `%rsp` as a pointer to the saved `struct ex_regs` layout. The `HANDLERS` macro emits stubs for vectors 0 through 255 and accounts for exceptions that already push an error code.

## Control Flow
For vectors without hardware error codes, the stub pushes a synthetic zero. Every stub pushes the vector number and jumps to `handle_exception`. The common handler pushes registers in a fixed order, calls `route_exception`, restores the registers, adjusts the stack by 16 bytes for vector and error code, and executes `iretq`.

## State and Persistence
No persistent data is mutated except for the generated `idt_handlers` address table. Runtime state is the guest stack and register frame during exception dispatch.

## Dependencies and Integration Points
The file integrates with `processor.c`, which installs IDT descriptors pointing at `idt_handlers` and provides `route_exception()`. It depends on x86-64 calling conventions and the expected `struct ex_regs` memory layout.

## Risks and Test Signals
Risks include mismatched stack layout, forgetting synthetic error codes, corrupting callee state, or returning to the wrong RIP/RFLAGS. Test signals are successful guest exception handling, `GUEST_ASSERT` failures with accurate vector metadata, and no unexpected triple faults during selftests that deliberately raise exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/handlers.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/hyperv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/hyperv.c

## Purpose
`hyperv.c` provides x86 Hyper-V enlightenment helpers for KVM selftests. It queries supported Hyper-V CPUID leaves, installs merged CPUID into vCPUs, allocates shared Hyper-V test pages, and enables the guest VP assist page.

## Important APIs, Types, and Functions
Key functions are `kvm_get_supported_hv_cpuid()`, `vcpu_set_hv_cpuid()`, `vcpu_get_supported_hv_cpuid()`, `kvm_hv_cpu_has()`, `vcpu_alloc_hyperv_test_pages()`, and `enable_vp_assist()`. The page allocator fills `struct hyperv_test_pages` with guest, host, and GPA addresses for VP assist, partition assist, and enlightened VMCS pages.

## Control Flow
Supported Hyper-V CPUID is cached after `KVM_GET_SUPPORTED_HV_CPUID`. `vcpu_set_hv_cpuid()` merges normal KVM CPUID with Hyper-V leaves while dropping conflicting KVM 0x400000xx leaves, then calls `vcpu_init_cpuid()`. VP assist enabling writes `HV_X64_MSR_VP_ASSIST_PAGE` and updates `current_vp_assist`.

## State and Persistence
Static CPUID caches persist process-wide. Allocated pages live in guest memory for the VM lifetime. `current_vp_assist` is guest-visible state used by VMX/Hyper-V paths.

## Dependencies and Integration Points
The file depends on `processor.h`, `hyperv.h`, KVM ioctls, CPUID helpers, and Hyper-V MSR definitions. It integrates with enlightened VMCS tests, nested VMX paths, and feature probes guarded by `KVM_CAP_SYS_HYPERV_CPUID`.

## Risks and Test Signals
Risks include stale CPUID caching, duplicate or conflicting hypervisor leaves, unsupported KVM caps, and mismatched guest physical addresses for assist pages. Test signals include successful `KVM_GET_SUPPORTED_HV_CPUID`, vCPU CPUID installation, feature checks via `kvm_hv_cpu_has()`, and Hyper-V tests observing valid assist page state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/hyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/memstress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/memstress.c

## Purpose
`memstress.c` adds x86 nested-virtualization support to the generic KVM memstress framework. It lets memstress run in L2 by preparing either VMX or SVM state in an L1 guest and then entering nested guest code.

## Important APIs, Types, and Functions
Public functions include `memstress_l2_guest_code()`, `memstress_nested_pages()`, and `memstress_setup_nested()`. Internal paths include the assembly entry `memstress_l2_guest_entry`, `l1_vmx_code()`, `l1_svm_code()`, `memstress_l1_guest_code()`, and `memstress_setup_ept_mappings()`.

## Control Flow
L1 setup chooses VMX when `X86_FEATURE_VMX` is available, otherwise SVM. VMX setup enables VMX operation, loads a VMCS, requires 1G EPT support, prepares the VMCS with an L2 stack containing the vCPU id, launches L2, and expects a `VMCALL` exit. SVM setup builds a VMCB and expects `SVM_EXIT_VMMCALL`. Host setup enables TDP, identity maps low memory and the memstress region with 1G mappings, allocates per-vCPU nested state, rewrites the vCPU RIP to L1 code, and passes nested data plus vCPU id.

## State and Persistence
State includes per-vCPU VMX/SVM pages, nested page tables, the L2 stack, and the global `memstress_args`. It persists for the life of the memstress VM and is cleaned up with the VM.

## Dependencies and Integration Points
The file depends on `memstress.h`, `processor.h`, `svm_util.h`, `vmx.h`, TDP helpers, and generic memstress guest code. It integrates with tests that request nested memstress and need KVM to shadow EPT12/NPT efficiently.

## Risks and Test Signals
Risks include missing TDP, missing 1G EPT support, wrong nested entry stack ABI, VMX/SVM feature mismatch, and failure to map the tested GPA range in L2. Test signals are `GUEST_ASSERT()` checks, expected `EXIT_REASON_VMCALL` or `SVM_EXIT_VMMCALL`, and normal memstress completion from L2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/memstress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/pmu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/pmu.c

## Purpose
`pmu.c` centralizes x86 PMU event lists and host errata detection for KVM selftests. It supplies canonical Intel architectural event encodings, AMD Zen event encodings, and an errata mask for CPUs that overcount certain retired events.

## Important APIs, Types, and Functions
The file exports `intel_pmu_arch_events[]`, `amd_pmu_zen_events[]`, `pmu_errata_mask`, and `kvm_init_pmu_errata()`. Internal `get_pmu_errata()` checks vendor, family, and model to set `INSTRUCTIONS_RETIRED_OVERCOUNT` and `BRANCHES_RETIRED_OVERCOUNT` bits.

## Control Flow
Static assertions ensure event arrays match `NR_INTEL_ARCH_EVENTS` and `NR_AMD_ZEN_EVENTS`. Initialization runs once through architecture setup and records model-specific errata for later guest-visible synchronization.

## State and Persistence
`pmu_errata_mask` is global process state and is synchronized into guests by x86 VM setup. There is no external persistence.

## Dependencies and Integration Points
The file depends on `pmu.h`, `processor.h`, `linux/kernel.h`, and CPU vendor/model helpers. It integrates with PMU selftests that need to suppress or adjust expectations for known Intel Atom event-counting errata.

## Risks and Test Signals
Risks include incomplete model coverage, incorrect event-array ordering, or failing to sync errata state to guests. Test signals are compile-time array-size assertions and PMU tests that account for `pmu_errata_mask` when validating retired instruction or branch counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/processor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/processor.c

## Purpose
`processor.c` is the main x86 architecture backend for KVM selftests. It provides guest page table construction, nested TDP mapping, descriptor table setup, exception routing, vCPU creation and register initialization, CPUID/MSR utilities, save/restore of x86 vCPU state, hypercall helpers, address-space limits, SEV address properties, SMM setup, and architecture-wide initialization.

## Important APIs, Types, and Functions
Major APIs include `virt_arch_pgd_alloc()`, `__virt_pg_map()`, `virt_arch_pg_map()`, `virt_map_level()`, `vm_get_pte()`, `tdp_get_pte()`, `addr_arch_gva2gpa()`, `vm_enable_tdp()`, `tdp_mmu_init()`, `tdp_map()`, `tdp_identity_map_default_memslots()`, `tdp_identity_map_1g()`, `vm_install_exception_handler()`, `route_exception()`, `kvm_arch_vm_post_create()`, `vm_arch_vcpu_add()`, `vcpu_arch_set_entry_point()`, `vcpu_args_set()`, `kvm_get_supported_cpuid()`, `vcpu_init_cpuid()`, `vcpu_set_cpuid_property()`, `vcpu_set_or_clear_cpuid_feature()`, `vcpu_get_msr()`, `_vcpu_set_msr()`, `vcpu_save_state()`, `vcpu_load_state()`, `kvm_get_cpu_address_width()`, `kvm_init_vm_address_properties()`, `kvm_hypercall()`, `xen_hypercall()`, `vm_compute_max_gfn()`, `kvm_selftest_arch_init()`, `setup_smram()`, and `inject_smi()`.

## Control Flow
VM creation allocates page tables, an IRQ chip, GDT/IDT/TSS pages, exception handler arrays, CPUID, XCR0, SREGS, stack, and initial registers. Page mapping walks or creates multi-level PTEs, supports huge leaves, checks alignment and canonicality, and applies SEV/TDX C/S bits only to final stage-1 leaves. Exception stubs from `handlers.S` enter `route_exception()`, which dispatches installed handlers, fixes expected exception probes, or reports guest failure. State migration first completes pending I/O, then captures events, MP state, regs, XSAVE/XCRS, SREGS, nested state, MSRs, and debug regs; loading restores the same classes in KVM-compatible order.

## State and Persistence
The file maintains global host CPU vendor flags, forced-emulation state, guest TSC frequency, PMU errata, supported CPUID cache, and guest exception handler pointer. Per-VM state includes page-table roots, architecture bit masks, descriptor-table pages, TSS, handlers page, SEV fd and C/S-bit tags, and maximum GFN. Per-vCPU state includes CPUID caches and KVM register state.

## Dependencies and Integration Points
Dependencies include `kvm_util.h`, `processor.h`, `pmu.h`, `smm.h`, `svm_util.h`, `sev.h`, `vmx.h`, sparsebit tracking, KVM ioctls, x86 CPUID/MSR definitions, and the assembly IDT stubs. It is the integration layer between generic selftest VM APIs and x86-specific KVM ABI details.

## Risks and Test Signals
Risks are broad: incorrect PTE masks, mapping protected guests' page tables, stale CPUID after XCR/SREG changes, wrong descriptor entries, incomplete save/restore ordering, AMD HyperTransport address-hole mistakes, and SEV C-bit mishandling. Test signals include `TEST_ASSERT()`s on mapping validity, KVM ioctl return checks, guest exception reports, CPUID/MSR sanity checks, successful migration/save-restore tests, and architecture setup failures when required caps such as `KVM_GET_TSC_KHZ` are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/sev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/sev.c

## Purpose
`sev.c` provides AMD SEV, SEV-ES, and SEV-SNP VM launch helpers for x86 KVM selftests. It initializes encrypted-guest state, encrypts registered memory regions, performs launch update/measure/finish flows, and creates launched VMs for tests.

## Important APIs, Types, and Functions
Key functions are `sev_vm_init()`, `sev_es_vm_init()`, `snp_vm_init()`, `sev_vm_launch()`, `sev_vm_launch_measure()`, `sev_vm_launch_finish()`, `snp_vm_launch_start()`, `snp_vm_launch_update()`, `snp_vm_launch_finish()`, `vm_sev_create_with_one_vcpu()`, and `vm_sev_launch()`. Internal `encrypt_region()` iterates `region->protected_phy_pages` with sparsebit range macros and calls SEV or SNP update helpers.

## Control Flow
SEV and SEV-ES initialization uses legacy init ioctls for default VM type or `KVM_SEV_INIT2` for explicit VM types. Launch begins with policy setup, verifies guest status, encrypts all protected pages across memslots, optionally updates VMSA for SEV-ES, measures, and finishes. SNP launch enables hypercall exits for GPA range mapping, starts launch, updates all private pages with SNP page type normal, and finishes without the SEV measurement step.

## State and Persistence
State persists in `vm->arch.sev_fd`, `vm->arch.is_pt_protected`, protected-page sparsebits per memory region, private/shared page attributes, and firmware-side launch state. Measurements are returned through caller-provided buffers.

## Dependencies and Integration Points
The file depends on `sev.h`, sparsebit helpers, KVM SEV ioctls, memory attribute helpers, `vm_mem_set_private()`, `sev_launch_update_data()`, and `snp_launch_update_data()`. It integrates with x86 VM creation, protected guest tests, and page-table code that must not walk protected page tables after launch.

## Risks and Test Signals
Risks include encrypting the wrong page ranges, missing protected pages, using the wrong init ioctl for VM type, failing to update VMSA for SEV-ES, and mishandling SNP private memory. Test signals are guest status state checks, policy equality checks, successful launch measure/finish transitions, and protected guest tests that run only after `vm->arch.is_pt_protected` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/sev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/svm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/svm.c

## Purpose
`svm.c` implements nested AMD SVM support helpers for KVM selftests. It allocates VMCB-related pages, configures nested paging, builds a runnable VMCB from current guest state, runs nested guests with `vmrun`, and opens `/dev/sev` for SEV tests.

## Important APIs, Types, and Functions
Public functions include `vcpu_alloc_svm()`, `vm_enable_npt()`, `generic_svm_setup()`, `run_guest()`, and `open_sev_dev_path_or_exit()`. The file also defines global `guest_regs` and `rflags`, plus `vmcb_set_seg()` and assembly register save/restore macros.

## Control Flow
Allocation reserves pages for `struct svm_test_data`, VMCB, host-save area, and MSR permission map, then records GPAs/HVAs. `vm_enable_npt()` clones the VM's PTE masks but clears the C-bit and marks NPT walks as user accesses before initializing the stage-2 MMU. `generic_svm_setup()` enables EFER.SVME, writes `MSR_VM_HSAVE_PA`, snapshots current segment/control/debug state into the VMCB, sets intercepts for VMRUN and VMMCALL, sets the nested RIP/RSP, and enables nested paging when an NCR3 is present. `run_guest()` uses inline assembly to vmload/vmrun/vmsave while exchanging GPRs with the global save area.

## State and Persistence
Per-nested-vCPU state lives in allocated VMCB, save-area, MSRPM, and optional NPT root pages. Global register save state is process/guest global and is overwritten for each nested run.

## Dependencies and Integration Points
The file depends on `svm_util.h`, `processor.h`, KVM VM allocation helpers, x86 MSRs, and SVM instructions. It integrates with nested SVM tests and x86 memstress nested execution.

## Risks and Test Signals
Risks include incorrect VMCB segment attributes, stale global GPR save state across concurrent runs, missing SVME/HSAVE setup, C-bit leakage into NPT entries, and incorrect exit-code expectations. Test signals are `TEST_ASSERT()`s for NPT support, guest `GUEST_ASSERT()`s after `run_guest()`, and expected SVM exits such as `SVM_EXIT_VMMCALL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/svm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/ucall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/ucall.c

## Purpose
`ucall.c` is the x86 backend for KVM selftest ucalls. It implements the guest exit mechanism using PIO from a fixed port and extracts the guest-provided ucall pointer from vCPU registers on the host.

## Important APIs, Types, and Functions
The file defines `UCALL_PIO_PORT` as `0x1000`, `ucall_arch_do_ucall()`, and `ucall_arch_get_ucall()`. The guest path passes the ucall pointer in RDI and executes `in` from the port. The host path checks `KVM_EXIT_IO` and the port, then reads RDI via `vcpu_regs_get()`.

## Control Flow
Guest code saves nonvolatile registers plus RDX/RDI, performs the PIO instruction, and restores registers. The extra save/restore is a nested-VMX workaround because L2 ucalls may exit to L1, which can clobber registers before returning. Host code returns NULL for non-ucall exits.

## State and Persistence
No persistent state is stored. The PIO exit and RDI pointer are transient communication state between guest and host.

## Dependencies and Integration Points
The file depends on `kvm_util.h`, x86 PIO behavior, and common ucall code in `ucall_common.c`. It integrates with every x86 guest selftest using `GUEST_SYNC`, `GUEST_DONE`, `GUEST_PRINTF`, or `GUEST_ASSERT`.

## Risks and Test Signals
Risks include port conflicts, register clobbering in nested guests, missing KVM I/O completion, and returning an invalid guest pointer. Test signals are host `get_ucall()` receiving expected commands and nested tests preserving guest registers across ucalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/ucall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/vmx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/vmx.c

## Purpose
`vmx.c` provides nested Intel VMX support helpers for KVM selftests. It allocates VMX control pages, enables EPT/TDP mappings, enters VMX root operation, loads VMCS state, initializes control/host/guest VMCS fields, checks EPT capability, and prepares APIC-access virtualization memory.

## Important APIs, Types, and Functions
Important APIs include `vcpu_enable_evmcs()`, `vm_enable_ept()`, `vcpu_alloc_vmx()`, `prepare_for_vmx_operation()`, `load_vmcs()`, `ept_1g_pages_supported()`, `prepare_vmcs()`, `kvm_cpu_has_ept()`, and `prepare_virtualize_apic_accesses()`. Globals include `enable_evmcs`, `current_evmcs`, and `current_vp_assist`.

## Control Flow
VMX allocation reserves guest pages for VMXON, VMCS, MSR bitmap, shadow VMCS, VMREAD bitmap, VMWRITE bitmap, and optional EPTP root. VMX preparation adjusts CR0/CR4 according to fixed MSRs, enables CR4.VMXE, locks/enables feature control when possible, writes VMCS revisions, and executes `vmxon`, `vmclear`, and `vmptrld`. VMCS preparation initializes controls, optionally enables EPT with write-back memory type and A/D bits, records host state from current registers/MSRs, and initializes guest state mostly as a clone with caller-provided RIP/RSP.

## State and Persistence
State lives in allocated VMX pages, VMCS fields, VMX root mode, global enlightened-VMCS pointers, and stage-2 EPT page tables. It persists until VM teardown or explicit VMX operation changes.

## Dependencies and Integration Points
The file depends on `vmx.h`, `processor.h`, `kvm_util.h`, `test_util.h`, x86 VMX MSRs, Hyper-V EVMCS support, and TDP mapping helpers. It integrates with nested VMX tests, Hyper-V enlightened VMCS tests, and x86 memstress nested execution.

## Risks and Test Signals
Risks include illegal CR0/CR4 fixed-bit handling, feature-control writes that still leave VMXON unavailable, invalid EPTP construction, missing secondary controls, mismatched host/guest segment state, and unsupported 5-level EPT. Test signals are VMX instruction return values, `TEST_ASSERT()` and `GUEST_ASSERT()` checks, expected VM exits from nested guests, and feature probes via `kvm_cpu_has_ept()`/`ept_1g_pages_supported()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/vmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/arch_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/arch_timer.c

## Purpose
`loongarch/arch_timer.c` tests LoongArch KVM timer virtualization. It validates time counter monotonicity, periodic timer interrupts, one-shot timer interrupts, and idle wakeup/emulated timer behavior through CSR timer registers.

## Important APIs, Types, and Functions
Key functions are `guest_irq_handler()`, `guest_test_period_timer()`, `guest_test_oneshot_timer()`, `guest_test_emulate_timer()`, `guest_time_count_test()`, `guest_code()`, `test_vm_create()`, and `test_vm_cleanup()`. The test uses `timer_get_cycles()`, `timer_get_cfg()`, `timer_get_val()`, `timer_set_next_cmp_ms()`, `disable_timer()`, `timer_irq_enable()`, `csr_read()`, and `csr_write()`.

## Control Flow
The guest first verifies the counter starts within an expected early window and monotonically increases. It enables timer interrupts, runs periodic mode until the shared iteration counter reaches zero, runs repeated one-shot timers while checking each IRQ increments `nr_iter`, and tests idle wakeup with local IRQs disabled around `idle 0`. The IRQ handler validates timer interrupt identity, clears TI, and either decrements periodic remaining count or validates one-shot TVAL/cycle timing.

## State and Persistence
State is shared through `vcpu_shared_data[]` and `test_args`, synchronized into the guest before execution. Timer CSR state persists in the vCPU during the test and is explicitly cleared or disabled by handlers.

## Dependencies and Integration Points
The file depends on LoongArch `processor.h`, `arch_timer.h`, common `timer_test.h`, `kvm_util.h`, and `ucall_common.h`. It integrates with the generic timer test harness through `test_vm_create()` and `test_vm_cleanup()`.

## Risks and Test Signals
Risks include timer IRQ delivery latency, wrong CSR emulation, nonmonotonic virtual counters, timer clear failures, and too-small error margins on loaded hosts. Test signals are guest assertions on interrupt id, iteration counts, TVAL/cfg relationship, elapsed cycles, and final `GUEST_DONE()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/arch_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/pmu_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/pmu_test.c

## Purpose
`loongarch/pmu_test.c` validates LoongArch KVM PMU virtualization. It checks PMU availability, basic event counting for cycles/instructions/branches/branch misses, and delivery of a PMU overflow interrupt.

## Important APIs, Types, and Functions
Important functions are `has_pmu_support()`, `dump_pmu_caps()`, `guest_pmu_base_test()`, `guest_irq_handler()`, `guest_pmu_interrupt_test()`, `guest_code()`, and `main()`. The guest manipulates `LOONGARCH_CSR_PERFCNTR0-3` and `LOONGARCH_CSR_PERFCTRL0-3`, uses event constants from `pmu.h`, and handles `INT_PMI`.

## Control Flow
Host setup skips if CPUCFG6 says no PMU or no counters, dumps capabilities, creates a VM/vCPU, installs the interrupt handler, checks `KVM_LOONGARCH_VM_FEAT_PMU`, and runs the guest. Guest base test clears counters, configures four events, executes a relaxation loop, reads counters, and asserts ranges. The interrupt test preloads counter 0 near overflow, enables PMIE for cycles, spins, and expects one interrupt.

## State and Persistence
State includes guest PMU CSRs and global `pmu_irq_count`, which is synchronized into the guest. Host state is limited to VM feature discovery and ucall handling.

## Dependencies and Integration Points
The file depends on LoongArch processor helpers, `kvm_util.h`, `ucall_common.h`, PMU constants, `KVM_HAS_DEVICE_ATTR`, and exception table initialization. It integrates with KVM's LoongArch VM feature control ABI.

## Risks and Test Signals
Risks include hardware PMU absence, VM PMU feature disabled, counter-width mismatches, imprecise event ranges on different cores, and missing PMI delivery. Test signals include skip output for unsupported hosts, PMU capability prints, guest counter range assertions, `pmu_irq_count == 1`, and host handling of `UCALL_DONE` versus `UCALL_ABORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/loongarch/pmu_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_modification_stress_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_modification_stress_test.c

## Purpose
`memslot_modification_stress_test.c` stresses KVM behavior while memslots are repeatedly added and removed as guest vCPUs actively access memory. It targets memslot update/zap races and the x86 slot-zap-all quirk.

## Important APIs, Types, and Functions
Key functions are `vcpu_worker()`, `add_remove_memslot()`, `run_test()`, `help()`, and `main()`. Parameters are carried in `struct test_params`, including delay, iteration count, memory partitioning, and optional x86 quirk disabling.

## Control Flow
The test creates a memstress VM for each selected guest mode, optionally disables `KVM_X86_QUIRK_SLOT_ZAP_ALL`, starts memstress vCPU threads, repeatedly adds and deletes a dummy memslot just below the memstress GPA range, then joins vCPUs and destroys the VM. Guest workers run until `memstress_args.stop_vcpus` is set and only accept expected `UCALL_SYNC` exits.

## State and Persistence
State includes global vCPU count, per-vCPU memory size, memstress global arguments, and transient dummy memslot state at slot 7. No state persists after VM destruction.

## Dependencies and Integration Points
The file depends on generic `memstress.h`, `guest_modes.h`, KVM memory region helpers, `ucall_common.h`, and optional x86 `KVM_CAP_DISABLE_QUIRKS2`. It integrates with the memstress framework's vCPU thread lifecycle.

## Risks and Test Signals
Risks include memslot invalidation races, incorrect GPA placement for the dummy slot, unsupported vCPU counts, and quirk-capability mismatches. Test signals are absence of unexpected exits, successful memslot add/delete loops, worker joins, and explicit assertions on invalid guest sync status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/memslot_modification_stress_test.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/mmu_stress_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/mmu_stress_test.c

## Purpose
`mmu_stress_test.c` stresses KVM MMU and mmu-notifier behavior across large numbers of memslots and vCPUs. It exercises guest writes/reads, MMU context reset, host `mprotect(PROT_READ)` faults, writable restoration, slot deletion, and backing unmap cleanup.

## Important APIs, Types, and Functions
Important functions are `guest_code()`, `rendezvous_with_boss()`, `assert_sync_stage()`, `run_vcpu()`, `vcpu_worker()`, `spawn_workers()`, `rendezvous_with_vcpus()`, `calc_default_nr_vcpus()`, and `main()`. Host state uses `struct vcpu_info`, atomic rendezvous counters, `mprotect_ro_done`, `all_vcpus_hit_ro_fault`, and `nr_ro_faults`.

## Control Flow
The host creates a large VM, maps many memslots backed by one mmap, identity maps guest memory, partitions GPA ranges across worker threads, and synchronizes phases. Guests write all pages, sync, optionally have CR0.WP toggled on x86 to reset MMU context, rewrite, read read-only memory, then repeatedly write while the host changes the backing VMA to read-only. Workers expect `-EFAULT` on writes, optionally advance PC on x86/arm64 to validate all writes fault, then resume after writable protection is restored. The host later deletes even slots and unmaps half the backing to test cleanup.

## State and Persistence
State spans many KVM memslots, one shared backing mapping, per-vCPU KVM state, atomic phase counters, and guest-visible booleans synchronized into the VM. The test intentionally exits without fully deleting all memslots or closing KVM fd to exercise cleanup paths.

## Dependencies and Integration Points
The file depends on `kvm_util.h`, `guest_modes.h`, `processor.h`, `ucall_common.h`, pthreads, atomics, Linux sizes, and architecture-specific guest store instruction handling. It integrates with KVM MMU invalidation, dirty/write fault handling, memslot deletion, and mmu_notifier release.

## Risks and Test Signals
Risks include deadlocked rendezvous, failure to convert host faults to `-EFAULT`, incorrect PC advancement for fixed instruction sizes, slot limits below test size, and untested cleanup if vCPUs never run. Test signals are staged `UCALL_SYNC` values, expected `EFAULT`, all-vCPU fault accounting, timing output for run/reset/RO/RW phases, and successful worker joins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/mmu_stress_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/pre_fault_memory_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/pre_fault_memory_test.c

## Purpose
`pre_fault_memory_test.c` validates the `KVM_PRE_FAULT_MEMORY` vCPU ioctl. It checks successful prefaulting, partial failure at unmapped tails, racing memslot deletion/recreation, and private-memory behavior for supported x86 protected VM types.

## Important APIs, Types, and Functions
Key functions are `guest_code()`, `delete_slot_worker()`, `pre_fault_memory()`, `__test_pre_fault_memory()`, `test_pre_fault_memory()`, and `main()`. The race state is held in `struct slot_worker_data`. The ioctl payload is `struct kvm_pre_fault_memory`.

## Control Flow
The test creates a VM, places a test slot near the top of GPA space, maps it into guest VA space, optionally marks it private, and calls `pre_fault_memory()` for three ranges. Each prefault attempt starts a worker that deletes the slot once prefaulting begins, then recreates it when requested. The host retries after `EINTR` or after slot recreation, asserts expected remaining size, and checks success or `ENOENT`. Finally, the guest reads all mapped pages and exits with `GUEST_DONE()`.

## State and Persistence
State includes the test memslot, optional guest_memfd/private memory attribute, the racing worker flags, and the mutable `range.size` field returned by KVM. All state is freed with the VM.

## Dependencies and Integration Points
The file depends on `KVM_CAP_PRE_FAULT_MEMORY`, KVM VM type caps, pthreads, `kvm_util.h`, `processor.h`, and protected memory helpers. It integrates with x86 software-protected VM tests and generic KVM vCPU ioctl wrappers.

## Risks and Test Signals
Risks include misinterpreting partial progress, treating racing deletion `EAGAIN` as stable, accepting size-zero retries, and failing private-memory prefaults. Test signals are `range.size` decreasing only on success, expected zero or `PAGE_SIZE` bytes left, success for complete ranges, `ENOENT` for unmapped portions, and final guest read completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/pre_fault_memory_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/arch_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/arch_timer.c

## Purpose
`riscv/arch_timer.c` tests RISC-V KVM SSTC timer interrupt virtualization. It validates that guest writes to `vstimecmp` cause supervisor timer interrupts at the expected virtual time.

## Important APIs, Types, and Functions
Important functions are `guest_irq_handler()`, `guest_run()`, `guest_code()`, `test_vm_create()`, and `test_vm_cleanup()`. It uses `timer_set_next_cmp_ms()`, `timer_get_cycles()`, `timer_get_cmp()`, `timer_irq_enable()`, `timer_irq_disable()`, vector table helpers, and `vcpu_get_reg(... RISCV_TIMER_REG(frequency))`.

## Control Flow
Host setup creates vCPUs, requires `KVM_RISCV_ISA_EXT_SSTC`, installs interrupt handlers, initializes vector tables, reads and syncs timer frequency, and syncs test arguments. Guest code disables timer IRQs, enables local IRQs, then loops setting the next compare value, recording start cycles, enabling timer IRQs, delaying for period plus margin, and checking the interrupt count. The IRQ handler disables timer IRQs, verifies the cause is supervisor timer, and asserts current cycles are at or beyond compare.

## State and Persistence
State is shared through `timer_freq`, `test_args`, and per-vCPU `vcpu_shared_data`. Timer compare and interrupt-enable state is vCPU-local and reset by the handler/test loop.

## Dependencies and Integration Points
The file depends on RISC-V processor helpers, common timer test infrastructure, `kvm_util.h`, `ucall_common.h`, and KVM ISA extension discovery. It integrates with the generic architecture timer harness through `test_vm_create()`.

## Risks and Test Signals
Risks include SSTC absence, wrong interrupt cause decoding, timer frequency mismatch, late interrupt delivery under load, and not disabling IRQs between iterations. Test signals are the SSTC require skip, guest assertions on interrupt id and `xcnt >= cmp`, iteration count checks, and final `GUEST_DONE()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/arch_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/ebreak_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/ebreak_test.c

## Purpose
`riscv/ebreak_test.c` verifies RISC-V KVM guest-debug handling for software breakpoints. It checks that `ebreak` exits to userspace while guest debug is enabled and is handled inside the guest after debug controls are disabled.

## Important APIs, Types, and Functions
Key elements are `guest_code()`, `guest_breakpoint_handler()`, and `main()`. The test labels two non-compressed `ebreak` instructions as `sw_bp_1` and `sw_bp_2`, stores the handled breakpoint address in `sw_bp_addr`, and uses `struct kvm_guest_debug`.

## Control Flow
Host setup requires `KVM_CAP_SET_GUEST_DEBUG`, creates one vCPU, initializes vector tables, installs an exception handler for `EXC_BREAKPOINT`, enables guest debug, and runs until `KVM_EXIT_DEBUG`. It verifies the PC equals `sw_bp_1`, advances PC by 4 to skip it, disables debug controls, and resumes. The second `ebreak` is then handled by the guest exception handler, which records EPC and advances it by 4. Guest code asserts that the handled address is `sw_bp_2` and reports done.

## State and Persistence
State is limited to guest global `sw_bp_addr`, host guest-debug control state, and the vCPU PC. No state persists after VM cleanup.

## Dependencies and Integration Points
The file depends on RISC-V KVM register access, vector table setup, exception installation, `ucall_common.h`, and the guest debug capability. It integrates with KVM's `KVM_SET_GUEST_DEBUG` and `KVM_EXIT_DEBUG` ABI.

## Risks and Test Signals
Risks include compressed instruction encoding changing breakpoint length, not advancing PC correctly, debug controls leaking after disable, and exception handler registration failure. Test signals are `KVM_EXIT_DEBUG` at `sw_bp_1`, final guest assertion that `sw_bp_2` was handled internally, and `UCALL_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/riscv/ebreak_test.c -->
