# Group Research: subset-b-006842

This grouped report covers KVM selftest headers and two KVM selftest programs from `sources/distributed-fs/ceph-client/tools/testing/selftests/kvm`. Each file section is source-tree aligned and bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/processor.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/processor.h

Purpose: arm64 processor support contract for KVM selftests. It defines KVM one-reg encodings for core and system registers, default MAIR/TCR/PTE constants, exception-vector metadata, MMIO accessors, interrupt masking helpers, SMCCC call wrappers, EL2-aware register aliasing, and vCPU setup hooks.

Important APIs/types/functions: `ARM64_CORE_REG`, `KVM_ARM64_SYS_REG`, `struct ex_regs`, `handler_fn`, `aarch64_vcpu_setup`, `aarch64_vcpu_add`, `vm_install_exception_handler`, `vm_install_sync_handler`, `virt_get_pte_hva_at_level`, `smccc_hvc`, `smccc_smc`, `wfi`, `test_wants_mte`, `test_disable_default_vgic`, `vm_supports_el2`, `ctxt_reg_alias`, and `kvm_get_default_vcpu_target`. Inline helpers expose `cpu_relax`, `isb`, `dsb`, `dmb`, `readl/writeq` families, IRQ/SERROR DAIF toggles, and current EL detection.

Control flow and state: the file is header-only except for external declarations. Tests create VMs/vCPUs through common `kvm_util.h`, then arm64 setup code initializes target features, descriptor tables, exception handlers, and page tables. `ctxt_reg_alias()` rewrites selected EL1 sysreg IDs to EL2 IDs when a vCPU has `KVM_ARM_VCPU_HAS_EL2`, so callers can use context-sensitive register access without duplicating EL checks.

Dependencies and integration: depends on Linux arm64 headers (`asm/sysreg.h`, `asm/esr.h`, `asm/brk-imm.h`), KVM uAPI IDs, `kvm_util.h`, and `ucall_common.h`. It integrates with arm64 KVM selftest libraries that implement VM creation, descriptor table setup, interrupt routing, and guest exception dispatch.

Risks: the register-alias switch intentionally build-fails for unsupported encodings, which is useful but brittle when new EL1/EL2 aliases are needed. MAIR/TCR/PTE constants must track architectural and kernel uAPI behavior, especially LPA2 address-bit packing. The raw MMIO helpers assume correct endian conversions and barrier placement; misuse can hide ordering bugs.

Test signals: selftests that install guest exception handlers, use VGIC/MMIO, exercise MTE, run EL2 guests, or perform SMCCC calls validate this header indirectly. Compile failures around missing sysreg names or KVM one-reg IDs are early signals of kernel/uapi drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/spinlock.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/spinlock.h

Purpose: minimal arm64 guest spinlock interface for KVM selftests. It exposes a one-word `struct spinlock` and external `spin_lock`/`spin_unlock` routines implemented elsewhere, typically in guest-support assembly or library code.

Important APIs/types/functions: `struct spinlock { uint32_t v; }`, `spin_lock(struct spinlock *)`, and `spin_unlock(struct spinlock *)`.

Control flow and state: all state is contained in the lock word. The header does not specify memory ordering directly; the implementation must provide atomic acquire/release behavior suitable for concurrent guest vCPUs.

Dependencies and integration: consumed by arm64 guest test code that needs in-guest synchronization. It relies on an architecture implementation being linked into the selftest binary.

Risks: since the header provides no inline semantics, callers depend completely on the linked implementation. ABI changes to `struct spinlock` would break guest code compiled against this header.

Test signals: multi-vCPU arm64 guest tests that share guest memory and use spinlocks are the meaningful validation path; linker failures catch missing implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/ucall.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/ucall.h

Purpose: arm64 architecture adapter for the common selftest ucall mechanism. It defines ucalls as MMIO exits and performs the guest-side write that causes KVM to exit to userspace.

Important APIs/types/functions: `UCALL_EXIT_REASON` is `KVM_EXIT_MMIO`, `ucall_exit_mmio_addr` is the shared target address, and `ucall_arch_do_ucall(gva_t uc)` stores the ucall payload pointer through the MMIO address.

Control flow and state: common ucall code builds a `struct ucall` in guest memory and calls `ucall_arch_do_ucall`; the arm64 helper writes the guest virtual address of the payload to a configured MMIO page. Userspace observes the MMIO exit and decodes the pointer through common helpers.

Dependencies and integration: includes `kvm_util.h` and is included by `ucall_common.h`. It depends on VM setup mapping `ucall_exit_mmio_addr` to an exit-producing MMIO region.

Risks: if the MMIO address is not initialized or not mapped as expected, guest notification will either fault or not reach userspace. Pointer-size and endian assumptions must remain aligned with arm64 guest code.

Test signals: any arm64 selftest using `GUEST_SYNC`, `GUEST_DONE`, `GUEST_ASSERT`, or guest printf exercises this adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/ucall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/vgic.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/vgic.h

Purpose: arm64 VGIC helper declarations for KVM selftests. It packages VGICv3 setup, IRQ line manipulation, device attribute access, and ITS creation behind test-friendly APIs.

Important APIs/types/functions: `REDIST_REGION_ATTR_ADDR`, `kvm_supports_vgic_v3`, `__vgic_v3_setup`, `__vgic_v3_init`, `vgic_v3_setup`, `kvm_irq_set_level_info`, `_kvm_irq_set_level_info`, `kvm_arm_irq_line`, `_kvm_arm_irq_line`, `kvm_irq_write_ispendr`, `kvm_irq_write_isactiver`, `KVM_IRQCHIP_NUM_PINS`, and `vgic_its_setup`.

Control flow and state: tests create a VM, initialize the virtual interrupt controller, optionally configure redistributor regions and ITS state, then inject interrupts either through irq-line ioctls or direct VGIC device attributes. The underscore-prefixed helpers return errors for negative tests; the non-underscore forms assert success.

Dependencies and integration: depends on `<linux/kvm.h>` device attributes and `kvm_util.h` device/ioctl wrappers. It integrates with arm64 interrupt and timer selftests, and with common IRQFD or KVM interrupt routing helpers where arm64 support is needed.

Risks: GIC redistributor layout, reserved interrupt ranges, and ITS capabilities vary by kernel and host support. Tests must avoid assuming VGICv3 availability without `kvm_supports_vgic_v3()`.

Test signals: VGIC setup tests, timer interrupt tests, IRQ injection tests, and ITS-specific selftests validate the helper surface. Return-code helpers enable negative-path validation for unsupported attributes or invalid interrupt IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/vgic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/guest_modes.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/guest_modes.h

Purpose: common registry for guest address-size/page-size modes supported by KVM selftests. It lets tests append defaults, iterate selected modes, print help, and parse mode-related command-line arguments.

Important APIs/types/functions: `struct guest_mode { bool enabled; bool supported; }`, global `guest_modes[NUM_VM_MODES]`, `guest_mode_append(mode, enabled)`, `guest_modes_append_default`, `for_each_guest_mode`, `guest_modes_help`, and `guest_modes_cmdline`.

Control flow and state: process-global `guest_modes` stores which `enum vm_guest_mode` values are available and enabled. Tests populate defaults, allow CLI overrides, then call `for_each_guest_mode()` to run mode-parametrized test bodies.

Dependencies and integration: depends on `kvm_util.h` for `enum vm_guest_mode` and mode parameters. It integrates with architecture-specific mode defaults and tests that need coverage across page sizes or address widths.

Risks: mode state is global and mutable, so tests must initialize it predictably before iteration. Unsupported modes need to be filtered or skipped to avoid false failures on host-specific limitations.

Test signals: command-line selftest runs with guest-mode options, plus multi-mode memory-management tests, validate parsing and iteration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/guest_modes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_syscalls.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_syscalls.h

Purpose: syscall wrapper macros for KVM selftests. It standardizes direct syscall invocation, assertion behavior, and mmap/dup helpers without repeating boilerplate.

Important APIs/types/functions: `MAP_ARGS*`, `DECLARE_ARGS`, `UNPACK_ARGS`, `__KVM_SYSCALL_ERROR`, `__KVM_SYSCALL_DEFINE`, `KVM_SYSCALL_DEFINE`, `__kvm_mmap`, `kvm_mmap`, and `kvm_dup`.

Control flow and state: generated wrappers call the raw syscall, either returning the result for negative testing or asserting that failure did not occur. `kvm_mmap` maps anonymous/file memory and asserts the result is not `MAP_FAILED`; `kvm_dup` asserts `dup` succeeded.

Dependencies and integration: depends on `<sys/syscall.h>` and `test_util.h` assertion macros through inclusion chains. It is used by `kvm_util.h` and lower-level helpers that need consistent error text.

Risks: variadic macro machinery is limited to the supported argument count and can be hard to debug when misused. Assertion wrappers are inappropriate for tests that intentionally provoke syscall failures; those need the underscore/raw variants.

Test signals: broad selftest compilation validates macro expansion. Runtime failures are surfaced as standardized `TEST_ASSERT` messages with syscall name and errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_test_harness.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_test_harness.h

Purpose: convenience macros that bind kselftest harness tests to common one-vCPU KVM VM setup and cleanup.

Important APIs/types/functions: `KVM_ONE_VCPU_TEST_SUITE(name)` defines fixture setup/teardown and `KVM_ONE_VCPU_TEST(suite, test, guestcode)` defines a harness test body receiving a prepared `struct kvm_vcpu *`.

Control flow and state: the fixture creates a VM with one vCPU running the supplied guest code before each test and frees it afterward. The macro-generated test invokes an internal `__suite_test(struct kvm_vcpu *)` helper so test authors can focus on vCPU behavior.

Dependencies and integration: includes `kselftest_harness.h` and uses common KVM VM creation from `kvm_util.h` through the fixture implementation.

Risks: the abstraction is intentionally narrow: one VM, one vCPU, default shape. Tests needing custom memory, protected VM types, multiple vCPUs, or custom setup should not force-fit into these macros.

Test signals: compile-time macro expansion and harness execution of one-vCPU tests validate fixture lifecycle and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_test_harness.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util.h

Purpose: central KVM selftest utility API. It defines the in-process model for VMs, vCPUs, memory regions, guest modes, binary stats, ioctl wrappers, memory allocation/mapping, vCPU execution, device attributes, IRQ routing, VM creation, CPU pinning, guest-global synchronization, and architecture hooks.

Important APIs/types/functions: key state types are `struct userspace_mem_region`, `struct kvm_binary_stats`, `struct kvm_vcpu`, `struct userspace_mem_regions`, `struct kvm_mmu`, `struct kvm_vm`, `struct vcpu_reg_sublist`, `struct vcpu_reg_list`, `enum vm_guest_mode`, `struct vm_shape`, and `struct vm_guest_mode_params`. Major APIs include `kvm_check_cap`, `vm_ioctl`/`vcpu_ioctl`, `vm_enable_cap`, `vm_set_memory_attributes`, `vm_guest_mem_fallocate`, dirty-log/ring helpers, `vm_get_stats_fd`, IRQFD helpers, stats descriptor/data readers, `vm_create_irqchip`, guest memfd helpers, memory-region add/move/delete/reload, guest virtual/physical allocators, `virt_map`, address conversion helpers, `vcpu_run`, register/device-attribute wrappers, device creation, IRQ routing, VM creation families, CPU pinning, page-count conversion, `sync_global_to_guest`, `write_guest_global`, `vm_vcpu_add`, arch page-table hooks, `kvm_selftest_arch_init`, and release/finalize hooks.

Control flow and state: tests open `/dev/kvm`, create a VM shape, add memory regions tracked by GPA/HVA trees and slot hash, create vCPUs tracked on the VM, map guest virtual pages using arch hooks, run vCPUs through `KVM_RUN`, and interpret exits through common utilities. State persistence is process-local and fd-backed: VM/vCPU fds, mmaped `kvm_run`, sparsebit allocation maps, dirty-ring buffers, binary stats fds/descriptors, memfd-backed guest memory, and per-VM mode/type fields.

Dependencies and integration: depends on Linux KVM uAPI, local kernel-style list/rbtree/hashtable headers, `test_util.h`, `kvm_syscalls.h`, `kvm_util_arch.h`, `kvm_util_types.h`, and `sparsebit.h`. It is the primary integration point for all architecture headers and almost every KVM selftest.

Risks: ioctl wrappers assert by default, so negative tests must use raw underscore forms. Memory-region state must stay synchronized with KVM memslot ioctls and host mappings. Protected-memory flows currently assert that only private/no attributes are used. VM-killed detection relies on probing `KVM_CAP_USER_MEMORY` after `-EIO`. Architecture hooks must preserve common invariants for page size, address tagging, vCPU init, and IRQ chip support.

Test signals: almost all KVM selftests compile through this header. Direct signals include VM creation tests, memory-mapping tests, dirty-log/ring tests, IRQFD/routing tests, binary stats tests, guest memfd/private memory tests, vCPU state save/restore tests, and arch page-table tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util_types.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util_types.h

Purpose: shared scalar type aliases for KVM selftest guest and host addresses. It avoids repeating Linux/uapi integer choices across utility headers.

Important APIs/types/functions: the header defines address-sized aliases such as `gpa_t`, `gva_t`, `hva_t`, and related guest frame/page-number types used throughout `kvm_util.h` and architecture helpers.

Control flow and state: no control flow; it is a type contract. State behavior is indirect: these aliases determine how VM memory metadata, page-table helpers, and ucall pointers are represented.

Dependencies and integration: included by `kvm_util.h` and architecture code. It must match KVM selftest assumptions about 64-bit guest physical and virtual addresses even when host userspace types vary.

Risks: changing alias widths or signedness would affect address arithmetic, sparsebit indexes, ioctl payloads, and pointer conversions. Tests that cast between guest virtual addresses and host pointers rely on explicit use of these types.

Test signals: compile-time warnings/errors in memory helpers and runtime failures in address translation or ucall decoding are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/arch_timer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/arch_timer.h

Purpose: LoongArch architectural timer helper definitions for KVM selftests. It provides CSR-level timer access and constants used by guest timer interrupt tests.

Important APIs/types/functions: important pieces include LoongArch timer CSR constants from `processor.h`, timer configuration values, interrupt bit definitions, and inline functions/macros for reading and writing timer CSRs.

Control flow and state: guest code configures timer CSR state, enables timer interrupts, waits for delivery, and clears pending timer status. Persistent state is guest CPU CSR state virtualized by KVM.

Dependencies and integration: depends on LoongArch CSR definitions in `loongarch/processor.h` and common KVM timer test scaffolding. It integrates with `timer_test.h` style cross-architecture timer validation.

Risks: timer frequency, interrupt pending semantics, and CSR bit definitions must match the LoongArch KVM uAPI and architecture manuals. Incorrect clear/enable ordering can produce flaky tests.

Test signals: LoongArch timer interrupt selftests validate that guest timer programming exits or interrupts as expected and that KVM virtualizes timer CSRs correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/arch_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/kvm_util_arch.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/kvm_util_arch.h

Purpose: LoongArch architecture extension point for `kvm_util.h`. This small header supplies the arch-specific struct definitions required by the common VM/MMU structs.

Important APIs/types/functions: defines `struct kvm_vm_arch` and `struct kvm_mmu_arch` for LoongArch builds, currently as minimal/empty architecture state placeholders.

Control flow and state: no runtime control flow. It fixes the shape of common KVM utility structures for LoongArch compilation.

Dependencies and integration: included by `kvm_util.h` when building LoongArch selftests. Architecture-specific implementation files fill behavior through hooks declared in `kvm_util.h`.

Risks: if LoongArch gains common per-VM or per-MMU state, these placeholders need to expand without breaking existing utility code. Empty structs can hide assumptions that the generic code does not require arch metadata.

Test signals: successful LoongArch selftest compilation and VM/page-table tests validate that no missing arch state is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/kvm_util_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/pmu.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/pmu.h

Purpose: LoongArch PMU helper definitions for KVM selftests. It defines PMU event, counter, CSR, and interrupt constants used to validate virtual PMU behavior.

Important APIs/types/functions: includes LoongArch PMU CSR/event constants, counter selectors, overflow/interrupt bits, and helper declarations used by PMU tests.

Control flow and state: guest PMU tests program event counters through LoongArch CSRs, enable PMU interrupts, execute workload, then inspect counter and interrupt state. Persistent state is per-vCPU virtual PMU state maintained by KVM.

Dependencies and integration: depends on `loongarch/processor.h` CSR access macros and common KVM test assertion infrastructure. It integrates with PMU selftests and timer/interrupt helpers for PMI delivery.

Risks: PMU event encodings and interrupt bits are architecture-specific and host-capability-sensitive. Tests must gate on PMU availability and avoid assuming exact counter increments for events with implementation-defined behavior.

Test signals: LoongArch PMU selftests should catch wrong counter virtualization, missing PMU interrupt delivery, or stale CSR definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/processor.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/processor.h

Purpose: LoongArch processor support header for KVM selftests. It defines register names for assembly, page-table/PTE bits, CSR IDs, exception register save layout, exception handler registration, vCPU setup, and local interrupt helpers.

Important APIs/types/functions: assembly register aliases (`a0`-`a7`, `t0`-`t8`, `s0`-`s8`), PTE bits (`_PAGE_VALID`, `_PAGE_PRESENT`, `_PAGE_WRITE`, `_PAGE_USER`), CSR constants (`LOONGARCH_CSR_CRMD`, `ESTAT`, `ERA`, `TCFG`, `TINTCLR`, etc.), `read_cpucfg`, `csr_read`, `csr_write`, `struct ex_regs`, `struct handlers`, `handle_tlb_refill`, `handle_exception`, `loongarch_vcpu_setup`, `vm_init_descriptor_tables`, `vm_install_exception_handler`, `cpu_relax`, `local_irq_enable`, and `local_irq_disable`.

Control flow and state: guest exception entry code saves general registers and CSR state into `struct ex_regs`, dispatches to handlers installed in a guest handler table, and returns according to architecture exception flow. VM setup initializes descriptor/exception tables and vCPU state. CSR helpers mutate virtual CPU state and interrupt enable bits.

Dependencies and integration: includes `ucall_common.h` for guest assertion/ucall behavior and integrates with `kvm_util.h` architecture hooks. Timer and PMU headers build on its CSR definitions.

Risks: save-area offsets are shared with assembly and must remain exact. CSR constants and PTE bit layouts must track LoongArch architecture and kernel headers. Interrupt enable/disable uses fixed temporary register constraints and can break if compiler/assembler expectations change.

Test signals: LoongArch exception, page-table, timer, PMU, and ucall tests exercise this header. Offset mismatches usually appear as bad exception reports or crashes very early in guest execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/ucall.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/ucall.h

Purpose: LoongArch adapter for common ucall guest-to-userspace notifications.

Important APIs/types/functions: defines the LoongArch `UCALL_EXIT_REASON` and `ucall_arch_do_ucall(gva_t uc)` implementation used by `ucall_common.h`.

Control flow and state: common guest code prepares a ucall record and invokes the architecture adapter. The adapter triggers a KVM exit in the LoongArch-supported way so host userspace can retrieve the ucall payload.

Dependencies and integration: includes `kvm_util.h` and participates in `ucall_common.h`. It integrates with all LoongArch tests using `GUEST_SYNC`, `GUEST_DONE`, assertions, or guest printf.

Risks: ucall transport is architecture-specific; incorrect exit reason or payload register/address convention will make every guest notification fail. The common side must agree with the host-side decoder.

Test signals: any LoongArch selftest using guest assertions validates this adapter. Failures usually manifest as unexpected exit reason or missing ucall payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/ucall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/lru_gen_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/lru_gen_util.h

Purpose: helper declarations for selftests involving multi-generation LRU (`lru_gen`) behavior under KVM workloads.

Important APIs/types/functions: exposes utility routines and constants used to inspect or manipulate kernel LRU generation controls and stats from tests.

Control flow and state: tests use these helpers to read sysfs/debugfs state, configure LRU generation knobs, run memory workloads, and compare before/after reclaim signals. Persistent state is external kernel MM configuration, not local process-only data.

Dependencies and integration: depends on generic `test_util.h` file-reading and assertion helpers and on kernel VM interfaces available on the host. It integrates with memory stress tests that create guest memory pressure.

Risks: host kernel configuration may omit or restrict LRU generation interfaces. Tests must skip cleanly when the feature is unavailable and avoid leaving host VM knobs changed.

Test signals: lru_gen-focused memory selftests validate successful parsing, feature detection, and cleanup. Skip paths are important signals on kernels without support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/lru_gen_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/memstress.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/memstress.h

Purpose: shared memory-stress workload interface for KVM selftests. It defines guest/host data structures and setup helpers for tests that fault, write, or verify large guest memory ranges with multiple vCPUs.

Important APIs/types/functions: declares memory stress argument structures, guest workload entry points, per-vCPU setup helpers, VM creation/setup routines, argument parsing/help helpers, and synchronization helpers used by dirty-log, page-fault, demand-paging, and memory-attribute tests.

Control flow and state: host code configures a `memstress` workload, creates a VM with requested memory backing and vCPU count, places per-vCPU arguments in guest memory, runs workers, and collects progress through ucalls or shared state. Guest state includes working-set addresses, page counts, stride/randomization policy, and write/read verification data.

Dependencies and integration: depends on `kvm_util.h`, `test_util.h`, guest modes, memory backing source parsing, and ucall synchronization. It integrates with userfaultfd, dirty logging, private memory, and NUMA-sensitive tests.

Risks: stress tests are sensitive to host memory availability, backing source page size, vCPU scheduling, and NUMA balancing. Incorrect page-count conversion or guest address placement can produce false memory corruption or mapping failures.

Test signals: memory stress consumers validate this header by running workload loops under different backing sources, vCPU counts, and access patterns. Failures usually appear as guest assertion failures, unexpected exits, or data mismatch reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/memstress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/numaif.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/numaif.h

Purpose: local NUMA policy syscall declarations/constants for selftests that cannot rely on a system `numaif.h` being available.

Important APIs/types/functions: provides NUMA policy constants, mode/flag definitions, and prototypes or syscall wrappers for operations such as `mbind`, `get_mempolicy`, `set_mempolicy`, and page-node queries.

Control flow and state: tests use these wrappers to bind guest memory or host helper allocations to NUMA nodes, then observe placement or migration behavior. Persistent state is host process memory policy until changed or process exit.

Dependencies and integration: relies on Linux NUMA syscalls and `test_util.h` style assertions in users. It integrates with memory backing, memstress, demand paging, and NUMA balancing tests.

Risks: NUMA availability is host-specific. Tests must skip if the system has one node, lacks permissions, or disables NUMA policy support. Incorrect nodemask sizing can make syscalls fail with `EINVAL`.

Test signals: NUMA-aware KVM memory tests validate that policy calls succeed, memory placement is observable, and skip paths work on non-NUMA hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/numaif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/arch_timer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/arch_timer.h

Purpose: RISC-V architectural timer helpers for KVM selftests. It defines timer register access, interrupt expectations, and timer setup primitives for guest tests.

Important APIs/types/functions: uses RISC-V timer KVM one-reg IDs from `processor.h`, CSR interrupt controls, timer frequency/value helpers, and declarations used by cross-architecture timer tests.

Control flow and state: host/vCPU setup configures timer state through KVM one-regs, guest code enables supervisor timer interrupts, waits for delivery, and checks timer CSR effects. Persistent state is per-vCPU virtual timer state in KVM.

Dependencies and integration: depends on `riscv/processor.h`, KVM RISC-V timer register IDs, and common `timer_test.h`. It integrates with SBI/interrupt handling when guests interact with virtual timers.

Risks: RISC-V timer behavior depends on ISA extensions, SBI support, and KVM timer implementation. Tests must distinguish unsupported timer features from failures.

Test signals: RISC-V timer selftests validate interrupt delivery, timer state get/set, and guest CSR behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/arch_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/kvm_util_arch.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/kvm_util_arch.h

Purpose: RISC-V architecture placeholder types for the common KVM utility layer.

Important APIs/types/functions: defines `struct kvm_vm_arch` and `struct kvm_mmu_arch` for RISC-V builds, currently minimal/empty.

Control flow and state: no runtime behavior. The types reserve architecture slots inside `struct kvm_vm` and `struct kvm_mmu`.

Dependencies and integration: included by `kvm_util.h`; RISC-V-specific implementation files provide the actual VM and page-table hook behavior.

Risks: future RISC-V state such as SATP mode, extension capability caches, or page-table metadata may need to be added here. Empty arch structs require the generic layer to avoid assumptions about state availability.

Test signals: RISC-V KVM selftest compilation and VM/page-table creation tests are the validation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/kvm_util_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/processor.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/processor.h

Purpose: RISC-V processor support header for KVM selftests. It defines KVM register ID builders, ISA/SBI extension checks, saved exception register layout, vector/exception handler APIs, page-table bit geometry, local interrupt helpers, and SATP mode discovery.

Important APIs/types/functions: `__kvm_reg_id`, `RISCV_CONFIG_REG`, `RISCV_CORE_REG`, `RISCV_GENERAL_CSR_REG`, `RISCV_TIMER_REG`, `RISCV_ISA_EXT_REG`, `RISCV_SBI_EXT_REG`, `__vcpu_has_ext`, `__vcpu_has_isa_ext`, `__vcpu_has_sbi_ext`, `struct pt_regs`, `vm_init_vector_tables`, `vcpu_init_vector_tables`, `vm_install_exception_handler`, `vm_install_interrupt_handler`, page-table masks/shifts, `local_irq_enable`, `local_irq_disable`, and `riscv64_get_satp_mode`.

Control flow and state: tests query or set vCPU registers using composed KVM one-reg IDs, initialize guest vector tables, install handlers, then execute guest code that reports traps through `struct pt_regs`. Page-table helpers use the defined masks to map guest memory. Interrupt enable/disable mutates supervisor status CSR bits.

Dependencies and integration: depends on Linux RISC-V CSR and KVM uAPI headers plus common `kvm_util.h`. It integrates with RISC-V timer, SBI, ucall, page-table, and extension capability tests.

Risks: register ID composition must match KVM RISC-V uAPI exactly. Page-table constants assume supported 64-bit RISC-V modes and may need updates for new address modes. Extension checks should be used before tests depend on optional ISA/SBI features.

Test signals: RISC-V exception tests, SATP/page-table tests, timer tests, and extension-gated SBI tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/sbi.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/sbi.h

Purpose: RISC-V SBI constants for KVM selftests. It records SBI version fields, standard error codes, and extension ID ranges used when testing virtual SBI exposure.

Important APIs/types/functions: `SBI_SPEC_VERSION_DEFAULT`, major/minor masks and shifts, `SBI_SUCCESS`, `SBI_ERR_*`, and experimental extension range constants.

Control flow and state: no executable control flow. Guest and host tests use these constants to interpret SBI call results and validate extension metadata.

Dependencies and integration: included by RISC-V SBI selftests and works with `riscv/processor.h` extension probing. It does not depend on common KVM helpers directly.

Risks: SBI constants must track the SBI specification version supported by KVM. Error-code mismatches would cause tests to misclassify unsupported or invalid calls.

Test signals: SBI extension and error-path tests validate these definitions by comparing guest-observed return values with expected codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/sbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/ucall.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/ucall.h

Purpose: RISC-V architecture adapter for common ucall notifications.

Important APIs/types/functions: defines RISC-V `UCALL_EXIT_REASON` and `ucall_arch_do_ucall(gva_t uc)`, using the architecture's supported guest-to-host exit path.

Control flow and state: common ucall code places a payload in guest memory and calls the RISC-V adapter, which triggers an exit that host userspace decodes as a ucall. The state is the guest payload address and KVM exit metadata.

Dependencies and integration: includes `kvm_util.h` and is pulled into `ucall_common.h`. It integrates with all RISC-V guest assertions, sync points, and completion notifications.

Risks: an incorrect exit reason or payload transport convention breaks all common guest communication. Tests must keep host-side ucall decoding synchronized with this adapter.

Test signals: any RISC-V selftest using `GUEST_SYNC`, `GUEST_DONE`, or `GUEST_ASSERT` validates this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/ucall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/debug_print.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/debug_print.h

Purpose: s390 guest debug-print support for KVM selftests. It provides low-level routines/macros to emit guest-visible diagnostic text, typically through s390-specific debug facilities.

Important APIs/types/functions: exposes debug printing helpers and formatting entry points used from guest code, backed by s390 diagnose or console-like mechanisms.

Control flow and state: guest code calls the debug print helper when it needs diagnostic output. The helper formats or copies data to an s390-specific output path. State is transient output data; no durable test state is owned by the header.

Dependencies and integration: integrates with s390 processor/facility helpers and common guest assertion/ucall code. It may depend on s390 diagnose behavior provided by KVM.

Risks: debug output paths are often best-effort and may be unavailable depending on host/KVM setup. Tests should not rely on debug text for pass/fail state.

Test signals: s390 guest tests that print diagnostics validate compilation and basic output delivery; failures should not normally affect test correctness unless the helper is part of the tested facility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/debug_print.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/diag318_test_handler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/diag318_test_handler.h

Purpose: s390 DIAG 0x318 test handler declaration for KVM selftests. DIAG 318 reports control-program information and is exposed to guests through KVM.

Important APIs/types/functions: declares the guest handler or entry points used by DIAG 318 tests to trigger and validate diagnostic behavior.

Control flow and state: tests install or invoke the handler, execute the DIAG instruction path, and check that expected guest-visible state or interception occurs. Persistent state is the virtual CPU diagnostic state maintained by KVM.

Dependencies and integration: integrates with s390 processor exception/interrupt handling and KVM DIAG-related selftests.

Risks: DIAG 318 behavior is s390-specific and dependent on KVM facility availability. Tests must gate on support and avoid confusing unsupported diagnostics with failures.

Test signals: DIAG 318 selftests validate handler invocation, expected return/intercept behavior, and correct KVM exposure of diagnostic state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/diag318_test_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/facility.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/facility.h

Purpose: s390 facility-list helper definitions. It lets selftests query and reason about architecture facilities exposed to the guest.

Important APIs/types/functions: includes facility bit constants, storage layout helpers, and functions/macros for testing whether a facility bit is present.

Control flow and state: guest or host code loads facility information, checks individual bits, and uses the result to skip or run feature-specific tests. The state is the facility bitmap reported by hardware/KVM.

Dependencies and integration: integrates with s390 processor helpers and tests for instruction/facility-specific behavior. It depends on s390 architectural definitions and KVM-exposed CPU model state.

Risks: facility numbering and bit ordering must be exact. Tests should avoid hard failing when optional facilities are absent and should clearly distinguish host absence from KVM bugs.

Test signals: s390 feature-gated tests validate that facility probing returns expected availability and skip decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/facility.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/kvm_util_arch.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/kvm_util_arch.h

Purpose: s390 architecture placeholder/state definitions for the common KVM utility layer.

Important APIs/types/functions: defines `struct kvm_vm_arch` and `struct kvm_mmu_arch` for s390 builds, currently minimal.

Control flow and state: no runtime control flow; the header shapes `struct kvm_vm` and `struct kvm_mmu` for s390 compilation.

Dependencies and integration: included by `kvm_util.h` and paired with s390-specific implementation files for VM setup, page tables, and vCPU initialization.

Risks: s390 has distinct memory-management and CPU-model behavior; if common utilities need cached arch state, this header must evolve in lockstep with implementations.

Test signals: s390 selftest compilation and VM creation/page mapping tests validate that the common layer has enough arch state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/kvm_util_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/processor.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/processor.h

Purpose: s390 processor support header for KVM selftests. It defines CPU/register helper declarations and architecture constants needed by s390 guest and host test code.

Important APIs/types/functions: includes s390 processor state helpers, guest entry/setup declarations, interrupt/exception-related types, and low-level instruction helper prototypes used by s390 tests.

Control flow and state: s390 tests use these declarations to initialize vCPU state, execute guest instructions, and inspect architecture-specific CPU state. Persistent state lives in KVM vCPU registers and s390-specific control blocks.

Dependencies and integration: integrates with `kvm_util.h`, `s390/sie.h`, facility helpers, debug printing, and ucall support.

Risks: s390 CPU model and facility exposure are highly architecture-specific. Register layout mismatches or missing facility gates can make tests fail on otherwise valid hosts.

Test signals: s390 KVM selftests that create vCPUs, run guest code, inspect registers, or handle exceptions validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/sie.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/sie.h

Purpose: s390 SIE (Start Interpretive Execution) control-block definitions for nested/low-level KVM selftests. It models the packed architecture data structures and intercept fields used by s390 virtualization.

Important APIs/types/functions: defines SIE control-block structs, prefix/state/intercept fields, bit constants, and layout helpers for interpreting or constructing SIE state.

Control flow and state: tests allocate or inspect SIE-related structures, set control bits, run guest/nested guest code, and examine intercept/exit fields after execution. Persistent state is the SIE control block and virtual CPU architecture state.

Dependencies and integration: integrates with s390 processor helpers, KVM vCPU state ioctls, and nested virtualization tests. Layout must match s390 architecture and kernel ABI expectations.

Risks: packed-structure layout is the main risk. Padding, alignment, or field-width mistakes can corrupt nested execution state or misinterpret intercept causes. Architecture updates may add fields or redefine bits.

Test signals: s390 nested/SIE selftests validate layout by successfully entering/exiting interpretive execution and matching expected intercept codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/sie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/ucall.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/ucall.h

Purpose: s390 adapter for common KVM selftest ucalls.

Important APIs/types/functions: defines s390 `UCALL_EXIT_REASON` and `ucall_arch_do_ucall(gva_t uc)` to transport guest notifications to host userspace.

Control flow and state: common guest code writes a ucall payload and invokes the s390 architecture adapter. The adapter triggers the architecture-specific KVM exit used by host-side ucall decoding.

Dependencies and integration: includes `kvm_util.h` and participates in `ucall_common.h`. All s390 tests using guest sync, done, abort, or printf depend on it.

Risks: the exit reason and payload convention must match host decoding. A broken adapter causes broad test failures with unexpected exits or missing ucall data.

Test signals: s390 guest assertion and synchronization tests are the primary validation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/ucall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/sparsebit.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/sparsebit.h

Purpose: public API for a sparse 64-bit-index bitmap library used by KVM selftests to track guest virtual/physical page availability and memory-region state efficiently.

Important APIs/types/functions: opaque `struct sparsebit`, `sparsebit_idx_t`, `sparsebit_num_t`, allocation/free/copy, single/range set and clear operations, set/clear queries, `sparsebit_num_set`, any/all tests, first/next set/clear searches, contiguous range search helpers, `sparsebit_dump`, `sparsebit_validate_internal`, and `sparsebit_for_each_set_range`.

Control flow and state: callers allocate a sparsebit object, update ranges as pages become allocated/mapped/protected/unused, and search for free or used ranges. The internal representation is hidden and optimized for mostly contiguous ranges over a huge 64-bit index space.

Dependencies and integration: used by `kvm_util.h` for VM virtual page maps, physical page availability, and protected page tracking. It is independent C API with C++ guards.

Risks: callers must check `sparsebit_any_set()` before using the range iteration macro because first-set aborts on empty input. Off-by-one errors are easy because range APIs use start plus count while the iteration macro exposes inclusive ends.

Test signals: VM memory allocator tests, page mapping tests, and sparsebit-specific unit tests validate range operations, dumps, and internal consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/sparsebit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/test_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/test_util.h

Purpose: generic KVM selftest utility header. It provides logging, skip/assertion macros, robust I/O helpers, SIGBUS expectation support, time math, guest random generation, memory backing-source metadata, alignment helpers, paranoid numeric parsing, guest snprintf, and clocksource lookup.

Important APIs/types/functions: `pr_debug`, `pr_info`, `print_skip`, `TEST_REQUIRE`, `TEST_ASSERT`, `TEST_ASSERT_EQ`, `TEST_ASSERT_KVM_EXIT_REASON`, `TEST_FAIL`, `TEST_EXPECT_SIGBUS`, `parse_size`, timespec helpers, `struct guest_random_state`, guest RNG helpers, `enum vm_mem_backing_src_type`, `struct vm_mem_backing_src_alias`, backing-source helpers, `align_up`, `align_down`, `align_ptr_up`, `atoi_paranoid`, `atoi_positive`, `atoi_non_negative`, `guest_vsnprintf`, `guest_snprintf`, `strdup_printf`, and `sys_get_cur_clocksource`.

Control flow and state: assertion macros terminate failing tests through kselftest mechanisms; `TEST_REQUIRE` skips. SIGBUS expectation temporarily installs a signal handler and uses `sigjmp_buf`. Memory backing helpers map CLI strings to mmap flags/page sizes. Guest RNG maintains deterministic seed/state for repeatable guest workloads.

Dependencies and integration: depends on `kselftest.h`, POSIX headers, Linux types, and is included by most KVM selftest headers. It is the base for `kvm_util.h` error handling and memory-source parsing.

Risks: assertion macros evaluate arguments with local temporaries but still terminate the process, so negative-path tests need non-asserting helpers. Host sysfs/proc feature probes can be environment-dependent. SIGBUS handler use must restore old handlers to avoid affecting later checks.

Test signals: every selftest using assertions, memory backing CLI, time helpers, or guest RNG validates this header. Failures are usually clear because macros include expression, file, line, and formatted diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/test_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/timer_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/timer_test.h

Purpose: cross-architecture timer selftest interface. It defines common timer-test parameters, guest/host synchronization points, and arch hooks so timer behavior can be validated consistently.

Important APIs/types/functions: timer-test constants, guest timer workload declarations, host setup helpers, and architecture hook declarations for enabling, programming, and checking virtual timer interrupts.

Control flow and state: host code creates vCPUs and shared timer test state, guest code programs an architecture timer, waits for interrupts or exits, and reports results. State includes per-vCPU timer configuration, interrupt counters, and synchronization flags.

Dependencies and integration: included by architecture timer implementations such as arm64, RISC-V, and LoongArch timer tests. Depends on `kvm_util.h`, guest interrupt helpers, and `test_util.h`.

Risks: timer tests are scheduling-sensitive and can be flaky if host load is high. Architecture timer frequency and interrupt controller setup must be correct before interpreting guest failures as KVM bugs.

Test signals: architecture timer selftests validate interrupt delivery timing, timer state migration or get/set behavior, and expected skips on unsupported hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/timer_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/ucall_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/ucall_common.h

Purpose: architecture-neutral guest-to-host ucall framework. It defines common ucall commands, payload layout, guest assertion/printf/done/sync helpers, and host-side retrieval APIs.

Important APIs/types/functions: commands `UCALL_NONE`, `UCALL_SYNC`, `UCALL_ABORT`, `UCALL_PRINTF`, `UCALL_DONE`, `UCALL_UNHANDLED`, `UCALL_MAX_ARGS`, `UCALL_BUFFER_LEN`, `struct ucall`, and common macros/functions for `GUEST_SYNC`, `GUEST_DONE`, `GUEST_ASSERT`, guest abort/printf, ucall initialization, and host-side ucall retrieval.

Control flow and state: guest code fills a `struct ucall` with command, args, and optional text, then calls the architecture adapter from `ucall.h`. Host code observes the configured exit reason, maps the guest payload, and dispatches on `cmd`. State is transient per ucall plus architecture-specific transport setup such as MMIO address.

Dependencies and integration: includes `test_util.h` and architecture `ucall.h`. It is used by nearly all guest-running KVM selftests as the common control channel.

Risks: payload layout is shared across guest and host; changing it requires synchronized decoder updates. Buffer length caps can truncate guest printf. Tests must handle `UCALL_ABORT` and `UCALL_UNHANDLED` distinctly from normal completion.

Test signals: every guest assertion, sync, printf, and done event validates this layer. Unexpected exit reason, invalid command, or malformed payload is the typical failure mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/ucall_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/userfaultfd_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/userfaultfd_util.h

Purpose: shared userfaultfd helper interface for KVM demand-paging and memory-fault selftests.

Important APIs/types/functions: declarations for creating/configuring userfaultfd, registering memory ranges, spawning fault-handler threads, resolving page faults, and collecting handler statistics.

Control flow and state: host registers guest memory ranges with userfaultfd, starts a handler thread, runs vCPUs that fault on demand, and the handler resolves faults by copying/zeroing pages or coordinating with test policy. Persistent state includes uffd fd, registered ranges, thread state, and counters.

Dependencies and integration: depends on Linux userfaultfd ioctls, pthreads, `kvm_util.h`, `test_util.h`, and memory stress helpers. It integrates with demand paging, dirty logging, private memory, and memslot tests.

Risks: userfaultfd availability is kernel-config and permission dependent. Races between vCPU faults, handler shutdown, and memory unregistration can be subtle. Tests must skip when unprivileged userfaultfd is unavailable.

Test signals: demand-paging KVM selftests validate successful registration, fault resolution, statistics, and clean handler shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/userfaultfd_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/apic.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/apic.h

Purpose: x86 APIC/x2APIC helper definitions for KVM selftests. It exposes APIC MSRs, MMIO register offsets, bit masks, and guest helpers to enable/disable APIC modes and read/write APIC registers.

Important APIs/types/functions: `APIC_DEFAULT_GPA`, `MSR_IA32_APICBASE` fields, xAPIC/x2APIC register offsets, ICR/LVT masks, `apic_disable`, `xapic_enable`, `x2apic_enable`, `get_bsp_flag`, `xapic_read_reg`, `xapic_write_reg`, `x2apic_read_reg`, `x2apic_write_reg_safe`, `x2apic_write_reg`, and `x2apic_write_reg_fault`.

Control flow and state: guest tests manipulate APIC base MSR and APIC registers either through MMIO at the default APIC GPA or through x2APIC MSRs. Safe write helpers capture fault vectors to validate negative cases.

Dependencies and integration: depends on `x86/processor.h` for MSR/fault helpers and `ucall_common.h` for guest assertions. It integrates with interrupt, APIC virtualization, x2APIC, and nested APIC tests.

Risks: APIC mode transitions are stateful and can affect later guest code. x2APIC MSR access must be feature-gated. Fault expectations rely on `wrmsr_safe` exception fixup working correctly.

Test signals: APIC/x2APIC selftests validate register access, interrupt delivery, faulting writes, and APIC base transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/apic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/evmcs.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/evmcs.h

Purpose: Hyper-V enlightened VMCS support layer for x86 nested VMX selftests. It defines the packed `hv_enlightened_vmcs` layout, clean-field bits, global eVMCS state, and inline replacements for VMCS pointer/read/write/launch/resume operations when eVMCS is enabled.

Important APIs/types/functions: `EVMCS_VERSION`, `enable_evmcs`, `struct hv_enlightened_vmcs`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_*`, `HV_VMX_SYNTHETIC_EXIT_REASON_TRAP_AFTER_FLUSH`, `current_evmcs`, `vcpu_enable_evmcs`, `evmcs_enable`, `evmcs_vmptrld`, `load_evmcs`, `evmcs_vmptrst`, `evmcs_vmread`, `evmcs_vmwrite`, `evmcs_vmlaunch`, and `evmcs_vmresume`.

Control flow and state: tests allocate Hyper-V assist pages, call `load_evmcs`, then VMX helpers in `vmx.h` delegate `vmread`, `vmwrite`, launch, and resume to this layer when `enable_evmcs` is true. `evmcs_vmwrite` updates the matching field and clears the correct clean-field group so Hyper-V/KVM knows what changed. Launch/resume assembly stores host RSP/RIP into eVMCS and returns a status flag after VM-entry failure or VM-exit.

Dependencies and integration: includes `hyperv.h` and `vmx.h`, and depends on VMCS field encodings from `x86/vmx.h`. It integrates with nested VMX tests running with Hyper-V enlightenments.

Risks: the packed layout and field mapping must match Hyper-V's eVMCS version exactly. Missing a VMCS field in read/write switches returns failure and can break nested tests. Clean-field bookkeeping is subtle; wrong groups can make KVM use stale state.

Test signals: Hyper-V eVMCS nested tests validate field translation, clean-field invalidation, VP assist page state, and successful nested launch/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/evmcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/hyperv.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/hyperv.h

Purpose: x86 Hyper-V enlightenment definitions for KVM selftests. It records Hyper-V CPUID leaves, synthetic MSRs, feature bits, hypercall numbers/status codes, VP assist page layout, and helper APIs for Hyper-V CPUID and test-page setup.

Important APIs/types/functions: `HYPERV_CPUID_*`, `HV_X64_MSR_*`, `HV_*` feature descriptors, `HVCALL_*`, `HV_STATUS_*`, `HV_HYPERCALL_*`, `__hyperv_hypercall`, `hyperv_hypercall`, `hyperv_write_xmm_input`, `HYPERV_LINUX_OS_ID`, `struct hv_nested_enlightenments_control`, `struct hv_vp_assist_page`, `current_vp_assist`, `enable_vp_assist`, `struct hyperv_test_pages`, `vcpu_alloc_hyperv_test_pages`, `kvm_get_supported_hv_cpuid`, `vcpu_get_supported_hv_cpuid`, `vcpu_set_hv_cpuid`, and `kvm_hv_cpu_has`.

Control flow and state: tests configure Hyper-V CPUID/MSRs on a vCPU, optionally allocate VP/partition assist pages and eVMCS storage, issue hypercalls through `vmcall`, and assert status/vector outcomes. State persists in vCPU CPUID, synthetic MSRs, assist-page memory, and nested enlightenment fields.

Dependencies and integration: depends on `x86/processor.h` for CPUID feature descriptors, safe assembly, SSE writes, and guest assertions. It integrates with eVMCS, nested Hyper-V, SynIC, synthetic timer, and hypercall tests.

Risks: Hyper-V ABI fields are dense and version-sensitive. Hypercall helpers clobber registers and rely on exception-fixup machinery. Feature bits must be checked before using optional MSRs/hypercalls.

Test signals: Hyper-V CPUID/MSR tests, hypercall tests, VP assist/eVMCS tests, and synthetic timer/SynIC tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/hyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/kvm_util_arch.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/kvm_util_arch.h

Purpose: x86 architecture state definitions for the common KVM utility layer. It stores x86-specific VM/MMU metadata needed by page-table and protected-memory helpers.

Important APIs/types/functions: defines x86 `struct kvm_vm_arch`, `struct kvm_mmu_arch`, PTE mask storage, and arch-specific fields used by `kvm_util.h` and `x86/processor.h`.

Control flow and state: no direct runtime control flow. The structs persist page-table mode, PTE masks, encryption/shared-bit metadata, and other x86-only state across VM setup and mapping operations.

Dependencies and integration: included by `kvm_util.h` for x86 builds and consumed by x86 page-table helpers, SEV/SNP code, TDP/EPT mapping, and VM creation hooks.

Risks: PTE mask correctness is critical for guest page-table and EPT predicates. SEV/SNP state must align with encryption C-bit and shared-bit handling or protected-memory tests can map pages incorrectly.

Test signals: x86 memory-management, EPT/TDP, SEV/SNP, and page-table inspection tests validate the struct fields indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/kvm_util_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/mce.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/mce.h

Purpose: x86 Machine Check Exception helper declarations/constants for KVM selftests.

Important APIs/types/functions: includes MCE-related MSR/register constants, helper declarations for injecting or checking machine-check state, and integration points for guest exception handlers.

Control flow and state: tests configure MCE capability/state through KVM vCPU ioctls or MSRs, inject machine-check conditions, run the vCPU, and validate guest exception or KVM exit behavior. Persistent state is vCPU MCE bank/register state.

Dependencies and integration: depends on `x86/processor.h` MSR and exception helpers and common KVM utility ioctls.

Risks: MCE behavior is CPU-model and KVM-capability dependent. Tests must gate on MCE support and avoid assuming host-specific bank counts or status bits.

Test signals: x86 MCE selftests validate injection, state get/set, guest handler dispatch, and expected KVM error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/mce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/pmu.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/pmu.h

Purpose: x86 PMU constants and helper declarations for KVM selftests. It encodes Intel/AMD event selectors, architectural PMU control bits, RDPMC flags, fixed counter controls, PMU capability bits, event indexes, and errata tracking.

Important APIs/types/functions: `KVM_PMU_EVENT_FILTER_MAX_EVENTS`, `RAW_EVENT`, `ARCH_PERFMON_EVENTSEL_*`, `INTEL_RDPMC_*`, `FIXED_PMC_*`, `PMU_CAP_*`, Intel and AMD event constants, `enum intel_pmu_architectural_events`, `enum amd_pmu_zen_events`, external event arrays, `enum pmu_errata`, `pmu_errata_mask`, `kvm_init_pmu_errata`, and `this_pmu_has_errata`.

Control flow and state: tests initialize errata state, query CPUID PMU features from `processor.h`, program event select MSRs/counters, run workloads, and validate counts or filter behavior. Persistent state includes vCPU PMU MSRs, global PMU errata mask, and host/KVM CPUID feature exposure.

Dependencies and integration: depends on Linux bit macros and x86 processor CPUID helpers. It integrates with PMU event-filter, RDPMC, fixed-counter, and migration tests.

Risks: PMU event behavior is CPU-vendor and model specific. The header explicitly tracks errata because exact counts can be unreliable. Event index ordering must stay aligned with CPUID architectural PMU enumeration.

Test signals: PMU selftests validate event encoding, supported-feature gating, counter increments, RDPMC paths, event filters, and errata handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/processor.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/processor.h

Purpose: broad x86 processor support header for KVM selftests. It defines CPUID feature/property descriptors, CPU/PMU feature probes, x86 state structs, low-level instruction helpers, MSR/XSAVE/CPUID ioctl wrappers, exception handling/fixup machinery, KVM module parameter probes, hypercall helpers, interrupt helpers, and page-table/TDP utilities.

Important APIs/types/functions: host globals `host_cpu_is_*`, `guest_tsc_khz`; `struct xstate`, `struct kvm_x86_cpu_feature`, `struct kvm_x86_cpu_property`, `struct kvm_x86_pmu_feature`, many `X86_FEATURE_*` and `X86_PROPERTY_*` constants, `struct gpr64_regs`, `struct desc64`, `struct desc_ptr`, `struct kvm_x86_state`, register/MSR helpers (`rdtsc`, `rdmsr`, `wrmsr`, CR getters/setters, `xgetbv`, `xsetbv`, `wrpkru`), CPUID helpers, SSE read/write helpers, `udelay`, state save/load/cleanup, MSR list helpers, vCPU MSR/debug/xsave/xcrs wrappers, CPUID mutation helpers, exception structs and `vm_install_exception_handler`, `KVM_ASM_SAFE` families, safe `rdmsr/rdpmc/xgetbv/wrmsr/xsetbv`, KVM module parameter probes, `kvm_hypercall`, `xen_hypercall`, `safe_halt`, STI/CLI helpers, `vm_xsave_require_permission`, page-level/PTE predicates, TDP/EPT mapping declarations, CR0/PFERR constants, and `sys_clocksource_is_based_on_tsc`.

Control flow and state: host-side tests query KVM-supported CPUID/MSRs, configure vCPUs, save/load x86 state, and install guest exception handlers. Guest-side inline assembly reads/writes CPU state, executes fault-safe instructions through register-based fixup, and triggers hypercalls. Page-table helpers inspect and build guest and TDP/EPT mappings using masks stored in `kvm_mmu_arch`.

Dependencies and integration: depends on Linux MSR/KVM para headers, `kvm_util.h`, and `ucall_common.h`. It is the root dependency for x86 APIC, Hyper-V, VMX, SVM, SEV, PMU, MCE, and SMM helpers.

Risks: this header is dense and ABI-sensitive. CPUID descriptor packing, safe-assembly register conventions, MSR durability checks, XSAVE sizing, and page-table masks must all match KVM and CPU behavior. Tests must use feature/property probes before executing optional instructions.

Test signals: almost all x86 KVM selftests validate this header. Strong signals include CPUID/MSR tests, xsave tests, exception-fixup tests, nested VMX/SVM tests, hypercall tests, TDP/EPT mapping tests, APIC/interrupt tests, and PMU tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/sev.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/sev.h

Purpose: x86 AMD SEV/SEV-ES/SNP helper interface for KVM selftests. It defines guest state classification, policy bits, launch helpers, VM creation wrappers, SEV ioctls, VM init hooks, VMGEXIT, encrypted-memory registration, and launch-update helpers.

Important APIs/types/functions: `enum sev_guest_state`, `SEV_POLICY_*`, `SNP_POLICY_*`, `GHCB_MSR_TERM_REQ`, `is_sev_snp_vm`, `is_sev_es_vm`, `is_sev_vm`, `sev_vm_launch`, `sev_vm_launch_measure`, `sev_vm_launch_finish`, `snp_vm_launch_start`, `snp_vm_launch_update`, `snp_vm_launch_finish`, `vm_sev_create_with_one_vcpu`, `vm_sev_launch`, `snp_default_policy`, `__vm_sev_ioctl`, `vm_sev_ioctl`, `sev_vm_init`, `sev_es_vm_init`, `snp_vm_init`, `vmgexit`, `sev_register_encrypted_memory`, `sev_launch_update_data`, and `snp_launch_update_data`.

Control flow and state: tests create a protected VM type, initialize SEV/ES/SNP state, register encrypted regions, perform launch-update over guest memory, measure/finish launch, then run encrypted guests. State persists in VM type, SEV launch state, guest memory attributes, encryption registration, and firmware/KVM-managed handles.

Dependencies and integration: depends on `linux/psp-sev.h`, `kvm_util.h`, `svm_util.h`, and `processor.h`. It integrates with guest memfd/private memory, SNP memory attributes, and AMD nested/SVM helpers.

Risks: SEV firmware availability, kernel capabilities, memory encryption C-bit handling, and policy compatibility are environment-sensitive. SEV ioctls must be routed to the right fd and negative tests need raw helpers.

Test signals: SEV, SEV-ES, and SNP launch tests validate policy setup, encrypted-memory registration, launch measurement/update, VMGEXIT behavior, and private/shared memory transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/sev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/smm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/smm.h

Purpose: x86 System Management Mode helper declarations for KVM selftests.

Important APIs/types/functions: `SMRAM_SIZE`, `SMRAM_MEMSLOT`, `SMRAM_PAGES`, `setup_smram`, and `inject_smi`.

Control flow and state: host tests reserve/map SMRAM, configure a vCPU for SMM testing, inject SMI, run the vCPU, and check SMM entry/exit behavior. State includes SMRAM memslot content and vCPU SMM/MP state.

Dependencies and integration: depends on `kvm_util.h` and x86 vCPU/register helpers from `processor.h` through implementation files.

Risks: SMM state is special and interacts with memory slots, hidden CPU state, and nested virtualization. SMRAM slot numbers must avoid collisions with normal test memory.

Test signals: x86 SMM selftests validate SMRAM setup, SMI injection, and guest transitions into/out of SMM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/smm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm.h

Purpose: AMD SVM architecture definitions for nested virtualization selftests. It defines intercept indexes, Hyper-V VMCB enlightenments, VMCB control/save layouts, bit masks for virtual interrupt control, event injection, IOIO intercept decoding, selector attributes, and intercept constants.

Important APIs/types/functions: intercept enum values, `struct hv_vmcb_enlightenments`, `HV_VMCB_NESTED_ENLIGHTENMENTS`, `HV_SVM_EXITCODE_ENL`, packed `struct vmcb_control_area`, `struct vmcb_seg`, `struct vmcb_save_area`, `struct vmcb`, TLB/interrupt masks, `SVM_IOIO_*`, `SVM_VM_CR_*`, `SVM_MISC*`, `SVM_SELECTOR_*`, CR/DR intercept constants, `SVM_EVTINJ_*`, and `SVM_EXITINTINFO_*`.

Control flow and state: nested SVM tests allocate and initialize a VMCB, set intercept and control bits, enter guest mode with `vmrun` via `svm_util.h`, then inspect exit code, exit info, event injection, and save-area state. State persists in the VMCB and guest physical pages shared with KVM.

Dependencies and integration: consumed by `svm_util.h`, SEV helpers, and nested SVM tests. It relies on exact AMD architecture layout and KVM's nested SVM interpretation.

Risks: packed VMCB layout correctness is critical. Bit definitions must match hardware, and nested tests can silently validate the wrong behavior if intercept bits or event-info masks are wrong.

Test signals: nested SVM tests validate VMRUN/VMEXIT behavior, intercept decoding, event injection, virtual interrupt masking, and Hyper-V enlightenment support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm_util.h

Purpose: helper API for constructing and running nested AMD SVM guests in KVM selftests.

Important APIs/types/functions: `struct svm_test_data`, `vmmcall`, `stgi`, `clgi`, `vcpu_alloc_svm`, `generic_svm_setup`, `run_guest`, `kvm_cpu_has_npt`, `vm_enable_npt`, and `open_sev_dev_path_or_exit`.

Control flow and state: host allocates SVM test pages and VMCB data, guest setup fills VMCB control/save fields, `run_guest` executes VMRUN against the VMCB GPA, and tests inspect resulting VMCB exit state. `stgi/clgi` and `vmmcall` provide guest instruction helpers for intercept tests.

Dependencies and integration: includes `<asm/svm.h>`, `svm.h`, and `processor.h`. It integrates with nested SVM and SEV tests, and uses common VM memory allocation/mapping.

Risks: VMCB physical/virtual address pairing must be correct. NPT support and SEV device availability are host-dependent. Inline instruction helpers require SVM-enabled guest context.

Test signals: nested SVM selftests validate allocation, setup, VMRUN execution, NPT enablement, and expected intercepts from `vmmcall`, `stgi`, or `clgi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/ucall.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/ucall.h

Purpose: x86 adapter for common ucall notifications. It uses port I/O exits rather than MMIO.

Important APIs/types/functions: `UCALL_EXIT_REASON` is `KVM_EXIT_IO`; `ucall_arch_init(struct kvm_vm *vm, gpa_t mmio_gpa)` is a no-op for x86 because port I/O does not need the MMIO setup used by other architectures.

Control flow and state: common guest ucall code triggers an I/O exit carrying the ucall payload convention expected by host-side decoding. There is no per-VM MMIO address state in this adapter.

Dependencies and integration: includes `kvm_util.h` and is included by `ucall_common.h`. It integrates with every x86 selftest using guest sync, done, abort, assertions, or printf.

Risks: the x86 transport depends on KVM I/O exit decoding and common ucall register/port conventions. Unlike MMIO adapters, initialization cannot repair a mismatched host decoder.

Test signals: almost every x86 guest-running selftest validates this path through `GUEST_SYNC` or `GUEST_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/ucall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/vmx.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/vmx.h

Purpose: Intel VMX nested virtualization helper definitions for KVM selftests. It defines VM-execution/control bits, VMCS field encodings, VMX instruction wrappers, VMX page allocations, VMX capability structs, and setup helpers for VMX/EPT/APIC-virtualization tests.

Important APIs/types/functions: VMX control masks (`CPU_BASED_*`, `SECONDARY_EXEC_*`, `PIN_BASED_*`, `VM_EXIT_*`, `VM_ENTRY_*`), `enum vmcs_field`, `struct vmx_msr_entry`, VMX instruction helpers (`vmxon`, `vmxoff`, `vmclear`, `vmptrld`, `vmptrst`, `vmptrstz`, `vmlaunch`, `vmresume`, `vmcall`, `vmread`, `vmreadz`, `vmwrite`, `vmcs_revision`), `struct vmx_pages`, `union vmx_basic`, `union vmx_ctrl_msr`, `vcpu_alloc_vmx`, `prepare_for_vmx_operation`, `prepare_vmcs`, `load_vmcs`, `ept_1g_pages_supported`, `kvm_cpu_has_ept`, `vm_enable_ept`, and `prepare_virtualize_apic_accesses`.

Control flow and state: nested VMX tests allocate VMXON/VMCS/MSR bitmap/APIC/EPT pages, enable VMX operation, load a VMCS, write control/guest/host fields, launch or resume L2, and inspect VM-exit fields. If `enable_evmcs` is set, VMCS read/write/launch/resume delegate to `evmcs.h`.

Dependencies and integration: depends on `<asm/vmx.h>`, `x86/processor.h`, `x86/apic.h`, and `x86/evmcs.h`. It integrates with x86 nested VMX, EPT, APIC virtualization, Hyper-V eVMCS, and VM-entry failure tests.

Risks: VMCS field encodings and control bit masks are architecture ABI. Assembly wrappers clobber many registers and deliberately do not establish guest GPR state. eVMCS conditional behavior means tests must understand whether raw VMCS or enlightened VMCS is active.

Test signals: nested VMX tests validate VMXON/VMCS setup, VM-entry/exit, VMREAD/VMWRITE, EPT setup, APIC access virtualization, and eVMCS delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/vmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/irqfd_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/irqfd_test.c

Purpose: executable KVM selftest for IRQFD assignment semantics and races. It verifies that KVM rejects assigning one eventfd to multiple GSIs/VMs while allowing deassign operations for valid fds, then stress-tests assignment/deassignment while another thread races close/recreate.

Important APIs/types/functions: globals `vm1`, `vm2`, `__eventfd`, `done`; constants `GSI_BASE_PRIMARY` and `GSI_BASE_SECONDARY`; `juggle_eventfd_secondary`, `secondary_irqfd_juggler`, `juggle_eventfd_primary`, and `main`.

Control flow and state: `main` requires a default irqchip, creates two full VMs with one unused vCPU each, assigns an eventfd to one GSI, asserts duplicate assignment returns `EBUSY`, deassigns valid fds, then starts a secondary thread. The primary loop creates 10,000 eventfds, attempts conflicting assignments on both VMs, deassigns, and closes the fd. The secondary thread repeatedly attempts assign/deassign on the current fd and accepts `EBUSY` or `EBADF` because the primary may close/recreate concurrently.

Dependencies and integration: depends on pthreads, eventfd helpers, IRQFD wrappers, VM creation, default irqchip support, and `READ_ONCE`/`WRITE_ONCE` style concurrency macros from included utility headers.

Risks: intentionally racy close/recreate behavior can expose timing-dependent failures. The test assumes KVM's asymmetric IRQFD ABI: assignment requires unique eventfd, deassignment keys on eventfd plus GSI and may succeed for never-assigned GSIs if fd is valid.

Test signals: pass means duplicate IRQFD assignment returns `EBUSY`, deassignment remains permissive for valid fds, and concurrent close/reassign does not crash or corrupt KVM state. Failures include unexpected success, wrong errno, or thread-race assertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/irqfd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_binary_stats_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_binary_stats_test.c

Purpose: executable selftest for KVM's fd-based binary statistics ABI. It validates header layout, descriptor layout, data layout, descriptor flags, exponent rules, data reads, and stats fd cleanup for KVM, VM, and vCPU stats.

Important APIs/types/functions: `stats_test(int stats_fd)`, `DEFAULT_NUM_VM`, `DEFAULT_NUM_VCPU`, and `main`. It uses `read_stats_header`, `get_stats_descriptor_size`, `read_stats_descriptors`, `get_stats_descriptor`, `read_stat_data`, VM/vCPU creation, and stats-fd helpers from `kvm_util.h`.

Control flow and state: `stats_test` reads the stats header, validates the ID string starts with `kvm`, checks descriptor/data offsets do not overlap invalidly, reads all descriptors, validates descriptor names, type/unit/base ranges, exponent rules, nonzero sizes, histogram bucket constraints, computes required data size, reads the bulk data block, then reads each stat individually. It frees allocations, closes the stats fd, and verifies the fd is closed. `main` parses optional VM/vCPU counts and runs the same validation for KVM-level, VM-level, and vCPU-level stats fds.

Dependencies and integration: depends on KVM binary stats uAPI (`struct kvm_stats_header`, `struct kvm_stats_desc`, flag masks), common test assertions, and KVM VM/vCPU creation utilities.

Risks: ABI layout assumptions are intentionally strict. Kernels adding new stat units/types must keep values within advertised max constants or update the test. The test allows no stats but prints a message and returns early.

Test signals: pass confirms binary stats fd structure is self-consistent, descriptor metadata is valid, data can be read both bulk and per-stat, and fd lifecycle is correct. Failures identify malformed offsets, flags, names, exponents, sizes, or read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_binary_stats_test.c -->
