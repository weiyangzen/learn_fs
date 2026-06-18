# Research: subset-b-006841

Source-tree-aligned research for KVM selftest files under `sources/distributed-fs/ceph-client/tools/testing/selftests/kvm`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/set_id_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/set_id_regs.c

Purpose: this arm64 KVM selftest validates userspace control of selected ID registers. It checks that KVM exposes writable masks for feature ID fields, accepts only architecturally safe values, rejects unsafe feature upgrades/downgrades with `EINVAL`, makes accepted values visible to guest sysreg reads, and preserves written ID register values across `KVM_ARM_VCPU_INIT` reset.

Important APIs, types, and functions: `enum ftr_type`, `struct reg_ftr_bits`, and `struct test_feature_reg` encode per-field safety rules for AArch64 and AArch32 ID registers. `get_safe_value()` and `get_invalid_value()` compute candidate field values from masks, signedness, and `FTR_EXACT`, `FTR_LOWER_SAFE`, `FTR_HIGHER_SAFE`, or `FTR_HIGHER_OR_ZERO_SAFE` semantics. `test_vm_ftr_id_regs()` uses `KVM_ARM_GET_REG_WRITABLE_MASKS` and `KVM_ARM64_SYS_REG()` with `vcpu_get_reg()`, `vcpu_set_reg()`, and `__vcpu_set_reg()`. Special paths cover MPAM (`test_user_set_mpam_reg()`), MTE fractional ID behavior (`test_user_set_mte_reg()`), vCPU-controlled non-feature ID registers (`test_clidr()`, `test_ctr()`, `test_id_reg()`), guest readback (`guest_code()`, `test_guest_reg_read()`), and reset preservation (`test_reset_preserves_id_regs()`).

Control flow: `main()` requires `KVM_CAP_ARM_SUPPORTED_REG_MASK_RANGES` and `KVM_CAP_ARM_WRITABLE_IMP_ID_REGS`, creates one VM/vCPU, enables writable implementation ID regs, finalizes vCPUs, detects AArch64-only guests from `ID_AA64PFR0_EL1.EL0`, and plans kselftest result counts. It then iterates every declared feature field, verifies mask writability, exercises failed and successful writes, applies special MPAM/MTE checks, runs guest code that syncs observed sysreg values back to the host, resets the vCPU, and rechecks all stored values. Guest state is passed through `GUEST_SYNC_ARGS`; host state is retained in `test_reg_vals` indexed by `KVM_ARM_FEATURE_ID_RANGE_IDX`.

State, persistence, and dependencies: all changes are in VM/vCPU KVM register state and process-local arrays; no persistent files are written. The test depends on arm64 sysreg encoding helpers, `processor.h` ID field masks, `kvm_util.h`, `test_util.h`, `linux/bitfield.h`, kselftest reporting, and MTE capability setup via `test_wants_mte()`. It integrates with KVM's arm64 one-reg UAPI, writable feature-ID mask UAPI, vCPU reset path, and guest ucall channel.

Risks and edge cases: feature-field tables must stay aligned with KVM's safe-ID policy and architectural signedness rules. Mutable fields such as `ID_AA64PFR0_EL1.GIC` are normalized before comparisons because KVM may force them after run. AArch32 ID registers are skipped on AArch64-only systems because they are RAZ/WI. MPAM and MTE special cases protect compatibility behavior where old kernels accepted writes to non-officially mutable fields. The code assumes field masks are wider than one bit.

Test signals: success is per-field kselftest pass output, special MPAM/MTE pass/skip/fail messages, no unexpected `KVM_SET_ONE_REG` errors for safe writes, expected `EINVAL` for invalid writes, matching guest-observed register values, and matching post-reset register values. Capability absence causes skip rather than failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/set_id_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/smccc_filter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/smccc_filter.c

Purpose: this arm64 selftest validates the VM-level SMCCC filter UAPI. It verifies argument validation, reserved-range protection, overlap rejection, and runtime behavior for denied versus userspace-forwarded SMCCC calls.

Important APIs, types, and functions: `enum smccc_conduit` selects HVC or SMC. `guest_main()` issues `smccc_hvc()` or `smccc_smc()` and reports `res.a0`. `__set_smccc_filter()` and `set_smccc_filter()` wrap `KVM_ARM_VM_SMCCC_CTRL`/`KVM_ARM_VM_SMCCC_FILTER` device attributes using `struct kvm_smccc_filter`. `setup_vm()` creates a PSCI-enabled vCPU. Test functions cover nonzero `pad`, zero or overflowing ranges, reserved action values, Arm Architecture reserved SMCCC ranges, overlapping filter ranges, `KVM_SMCCC_FILTER_DENY`, and `KVM_SMCCC_FILTER_FWD_TO_USER`.

Control flow: `main()` first checks `kvm_supports_smccc_filter()`, then runs UAPI validation tests followed by runtime action tests. Runtime tests iterate conduits with `for_each_conduit()`, using SMC only when the vCPU can run at EL2 and otherwise HVC plus SMC. Denied calls must return `SMCCC_RET_NOT_SUPPORTED` through the guest ucall path; forwarded calls must exit to userspace with `KVM_EXIT_HYPERCALL`, the expected function number, and the SMC flag set only for SMC.

State, persistence, and dependencies: all filter state is VM-local KVM state; each test uses a fresh VM and frees it. Dependencies include `<linux/arm-smccc.h>`, `<linux/psci.h>`, KVM arm64 vCPU target setup, PSCI feature bits, and selftest ucall helpers.

Risks and edge cases: reserved Arm Architecture calls must not be filterable, because KVM owns mitigation and discovery semantics there. The conduit loop depends on whether the guest has EL2. Overlap and overflow checks protect interval arithmetic. Test failures indicate either too-permissive UAPI acceptance or incorrect exit/return-code behavior.

Test signals: expected `EINVAL` for bad padding, zero range, overflow, and reserved actions; expected `EEXIST` for reserved/overlapping ranges; `SMCCC_RET_NOT_SUPPORTED` for denied calls; and `KVM_EXIT_HYPERCALL` plus correct flags for forwarded calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/smccc_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vcpu_width_config.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vcpu_width_config.c

Purpose: this test verifies arm64 KVM's `KVM_ARM_VCPU_INIT` width consistency rule. Homogeneous 64-bit EL1 vCPUs and homogeneous 32-bit EL1 vCPUs must be accepted, while mixed-width vCPUs in the same VM must be rejected.

Important APIs, types, and functions: `add_init_2vcpus()` creates and initializes vCPU0 before creating and initializing vCPU1. `add_2vcpus_init_2vcpus()` creates both vCPUs first and then initializes them. Both use barebones VMs, `__vm_vcpu_add()`, and `__vcpu_ioctl(..., KVM_ARM_VCPU_INIT, ...)`. `main()` obtains `KVM_ARM_PREFERRED_TARGET`, toggles `KVM_ARM_VCPU_EL1_32BIT`, and requires `KVM_CAP_ARM_EL1_32BIT`.

Control flow: the test runs two ordering variants for all-64-bit, all-32-bit, and mixed 64/32-bit configurations. Accepted cases assert return value zero; mixed cases assert a nonzero return value.

State, persistence, and dependencies: VM state is transient. Dependencies are arm64 KVM vCPU initialization, preferred target discovery, and capability reporting. There is no guest code because the test only validates creation/init policy.

Risks and edge cases: the same rule must hold regardless of whether both vCPUs already exist before initialization. The test does not inspect exact errno for mixed-width rejection, only that initialization fails.

Test signals: skip when `KVM_CAP_ARM_EL1_32BIT` is absent; pass when homogeneous cases succeed and both mixed-ordering cases fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vcpu_width_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_init.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_init.c

Purpose: this is a broad VGIC initialization and device-attribute validation selftest for arm64 KVM. It checks GICv2/GICv3 device creation, distributor/redistributor address rules, first-run initialization errors, GICv3 redistributor region semantics, ITS address validation, GICR_TYPER layout, nASSGIcap mutability, and CPU sysreg accessibility.

Important APIs, types, and functions: `struct vm_gic` carries VM, VGIC fd, and device type. `struct vgic_region_attr` describes address region size/alignment for GICv2 and GICv3. `subtest_dist_rdist()` validates common distributor and redistributor or CPU interface address attributes. `subtest_v3_redist_regions()` exercises `KVM_VGIC_V3_ADDR_TYPE_REDIST_REGION`. `test_vgic_then_vcpus()`, `test_vcpus_then_vgic()`, `test_v2_uaccess_cpuif_no_vcpus()`, `test_v3_new_redist_regions()`, `test_v3_typer_accesses()`, `test_v3_last_bit_redist_regions()`, `test_v3_last_bit_single_rdist()`, `test_v3_redist_ipa_range_check_at_vcpu_run()`, `test_v3_its_region()`, `test_v3_nassgicap()`, and `test_v3_sysregs()` cover the major scenarios. `test_kvm_device()` checks create/test/create-twice behavior and GICv2/GICv3 mutual exclusion.

Control flow: `main()` disables the framework default VGIC, computes the maximum IPA size from guest mode parameters, probes GICv3 and GICv2 devices, and runs the shared or version-specific test suite for each supported device. Many tests deliberately configure invalid overlap or insufficient redistributor space and then assert that the first `KVM_RUN` fails with the expected errno. GICv3 sysreg tests create a vCPU, initialize VGIC, and read/write back advertised CPU sysregs, allowing priority-register array holes when priority bits make them unavailable.

State, persistence, and dependencies: state is KVM VM/device state only. Dependencies include `vgic.h`, `gic_v3.h`, arm64 sysreg definitions, KVM device attr groups (`KVM_DEV_ARM_VGIC_GRP_ADDR`, `KVM_DEV_ARM_VGIC_GRP_CTRL`, `KVM_DEV_ARM_VGIC_GRP_REDIST_REGS`, `KVM_DEV_ARM_VGIC_GRP_DIST_REGS`, `KVM_DEV_ARM_VGIC_GRP_CPU_SYSREGS`), and guest mode IPA limits.

Risks and edge cases: address tests cover misalignment, out-of-range bases, partial frames above IPA limits, overlapping distributor/redistributor windows, mixing legacy and multi-region redistributor APIs, missing redistributors, and late VGIC initialization. GICR_TYPER tests rely on vCPU creation order and sparse vCPU IDs. CPU sysreg tests handle the awkward case where a register is advertised but read/write may be invalid due to implemented priority bits.

Test signals: expected errnos include `ENODEV`, `EEXIST`, `EINVAL`, `E2BIG`, `ENXIO`, `ENOENT`, `EFAULT`, and `EBUSY` in specific paths. Successful runs print GIC version test banners; total absence of GICv2 and GICv3 support skips the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_irq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_irq.c

Purpose: this functional VGICv3 interrupt injection selftest validates userspace injection paths, priority/preemption behavior, active-state restoration, invalid intid handling, EOI split behavior, level versus edge interrupt behavior, and selected two-vCPU corner cases.

Important APIs, types, and functions: `struct test_args` carries IRQ count, EOI split, level sensitivity, routing and irqfd capabilities, and shared data. `enum kvm_inject_cmd` and `struct kvm_inject_args` encode guest-to-host injection requests over ucalls. Injection descriptions separate supported SGI/PPI/SPI targets for edge, level, and active-state operations. Guest handlers call `gic_get_and_ack_irq()`, `gic_irq_get_active()`, `gic_irq_get_pending()`, `gic_set_eoi()`, and optionally `gic_set_dir()`. Host handlers use `kvm_arm_irq_line()`, `kvm_irq_set_level_info()`, `kvm_gsi_routing_*()`, irqfd/eventfd, and direct ISPENDR/ISACTIVER device-register writes.

Control flow: `test_vgic()` creates a one-vCPU VM, maps guest args, sets up VGICv3 with the requested IRQ count, installs an IRQ handler matching EOI split and level mode, and loops on guest ucalls to perform injection commands. Guest code initializes GICv3, configures SPI level/edge state, enables all interrupts, sets priority mask, and runs injection, preemption, failure, and active-restore tests. Default `main()` runs four edge/level by EOI-split combinations plus three two-vCPU tests: asymmetric DIR, group enable gating, and timer PPI/SPI interaction.

State, persistence, and dependencies: interrupt state lives in the emulated GIC and guest globals `irq_handled` and `irqnr_received`. Host state includes eventfds and routing tables for irqfd tests. Dependencies include arm64 GIC helpers, selftest descriptor table setup, pthreads for two-vCPU runs, and `KVM_CAP_IRQ_ROUTING`/`KVM_CAP_IRQFD` capability checks.

Risks and edge cases: invalid interrupt IDs exercise inconsistent UAPI behavior across `KVM_IRQ_LINE`, level-info attributes, routing, irqfd, and register writes. Timer PPIs are excluded from userspace PPI injection tests. Preemption tests manually poll IAR with IRQs masked, so priority programming and AP1R state must be correct. Active-state restoration models live migration where interrupts are active but not deactivated. The two-vCPU asymmetric DIR test checks deactivation from a different vCPU.

Test signals: guest assertions verify exact intid delivery counts, active/pending state transitions, no spurious pending after handling, AP1R returning to zero, expected failure for bad intids, and successful two-vCPU completion. Host assertions verify expected ioctl failures and routing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_lpi_stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_lpi_stress.c

Purpose: this test stresses KVM's emulated GICv3 ITS/LPI path by configuring ITS device/event mappings in the guest, then concurrently signaling many LPIs from host threads while vCPU threads consume them.

Important APIs, types, and functions: `struct test_data` records CPU, device, event counts and guest physical addresses for ITS tables, command queue, ITTs, LPI property table, and pending tables. Guest setup uses `gic_init()`, `gic_rdist_enable_lpis()`, `its_init()`, `its_send_mapc_cmd()`, `its_send_mapd_cmd()`, `its_send_mapti_cmd()`, `its_send_invall_cmd()`, and `its_send_sync_cmd()`. Host setup uses `vgic_its_setup()`, `vm_userspace_mem_region_add()`, `vm_phy_pages_alloc()`, and `virt_map()`. `signal_lpi()` sends `KVM_SIGNAL_MSI` with `KVM_MSI_VALID_DEVID`.

Control flow: `main()` parses `-v`, `-d`, `-e`, and `-i`, warns if thread count exceeds online CPUs, creates the VM/vCPUs, installs an IRQ handler, allocates a high GPA memslot for ITS/LPI tables, sets up the ITS, syncs `test_data` to the guest, and starts the stress run. Each vCPU reaches guest setup then syncs at a barrier. Each device has a host LPI worker that signals all event IDs for the configured iteration count. After LPI workers finish, the host writes `request_vcpus_stop` in guest memory and joins vCPUs.

State, persistence, and dependencies: state is transient VM memory plus host pthread synchronization. Guest table memory is allocated in a dedicated memslot and identity mapped for the command queue. Dependencies include VGICv3 and ITS support, `KVM_SIGNAL_MSI`, GICv3 ITS helper library, pthread barriers, atomics, and enough host CPUs for reliable performance.

Risks and edge cases: table sizing assumes 64 KiB units and one ITT per device. The test intentionally avoids WFI in the guest loop after setup so stop signaling cannot hang indefinitely. Concurrent MSI signaling stresses translation, injection, and LPI handling but does not count every delivered LPI in guest state, so it is more of a crash/performance stressor than an exact delivery accounting test.

Test signals: guest IRQ handler asserts every handled intid is an LPI (`>= 8192`). `KVM_SIGNAL_MSI` must return 1 for translated, unblocked MSIs. Completion prints an LPI/sec rate. Missing VGICv3 support skips the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_lpi_stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_v5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_v5.c

Purpose: this arm64 test probes KVM VGICv5 device creation and verifies userspace-driven software PPI delivery through the GICv5 current-domain instruction interface.

Important APIs, types, and functions: `struct vm_gic` wraps VM and GIC fd. Guest code enables GICv5 CPU interrupts with `gicv5_cpu_enable_interrupts()`, enables software PPI 3 via `SYS_ICC_PPI_ENABLER0_EL1`, and reports readiness with ucalls. The IRQ handler reads `CDIA` via `gicr_insn(CDIA)`, uses `GICV5_GICR_CDIA_VALID()` and `GICV5_GICR_CDIA_INTID`, acknowledges with `gsb_ack()`, drops/deactivates with `gic_insn(..., CDDI)` and `gic_insn(..., CDEOI)`, and completes after two interrupts. Host code creates `KVM_DEV_TYPE_ARM_VGIC_V5`, initializes it, reads `KVM_DEV_ARM_VGIC_USERSPACE_PPIS`, and toggles PPI level with `_kvm_irq_line()`.

Control flow: `main()` disables default VGIC setup, computes max physical size, probes GICv5 device support through trial create, skips if absent, and runs the PPI test. The test creates a one-vCPU VM manually, installs an IRQ handler, initializes the GIC, verifies SW_PPI is userspace-drivable, and loops on guest ucalls to raise/lower PPI level at readiness and EOI points.

State, persistence, and dependencies: all state is VM-local. Dependencies include `arm64/gic_v5.h`, KVM VGIC device creation, guest exception tables, `KVM_ARM_IRQ_TYPE_PPI`, and GICv5 sysreg/instruction definitions.

Risks and edge cases: GICv5 support is optional and new relative to GICv3. The test assumes SW_PPI 3 should always be userspace-drivable and that pending interrupts cause WFI to be skipped. It uses `__vcpu_run()` so run failures can be checked without immediate selftest assertion.

Test signals: unsupported device returns skip. Passing signals include device create errors behaving as expected, SW_PPI present in userspace PPI mask, two interrupt acknowledgements/deactivations from the guest, and final `KVM_RUN` success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_v5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vpmu_counter_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vpmu_counter_access.c

Purpose: this arm64 vPMU selftest verifies that userspace-selected PMU event counter count (`PMCR_EL0.N`) is reflected to the guest, that implemented counters are accessible through both direct and indirect sysregs, that unimplemented counters trap or read-as-zero as required, and that userspace register accesses honor the configured counter count.

Important APIs, types, and functions: `struct vpmu_vm` holds the active VM and vCPU. `struct pmc_accessor` abstracts direct `PMEV{CNTR,TYPER}<n>_EL0` access and indirect `PMXEV{CNTR,TYPER}_EL0` access through `PMSELR_EL0`. `get_pmcr_n()`, `get_counters_mask()`, `pmu_disable_reset()`, `test_bitmap_pmu_regs()`, `test_access_pmc_regs()`, and `test_access_invalid_pmc_regs()` implement guest-side checks. `guest_sync_handler()` validates expected exception classes and skips trapping instructions. Host-side `create_vpmu_vm()`, `test_create_vpmu_vm_with_nr_counters()`, `run_access_test()`, `run_pmregs_validity_test()`, and `run_error_test()` exercise device attributes including `KVM_ARM_VCPU_PMU_V3_SET_NR_COUNTERS` and `KVM_ARM_VCPU_PMU_V3_INIT`.

Control flow: `main()` requires `KVM_CAP_ARM_PMU_V3`, VGICv3, and the set-number-of-counters attribute. It discovers the host/guest PMCR.N limit, runs access and host-register-validity tests for every count from zero through the limit, and then verifies larger counts fail with `EINVAL`. Each access test runs the guest twice: before and after vCPU reset/reinitialization, restoring SP and PC to ensure PMCR.N persistence.

State, persistence, and dependencies: state is VM/vCPU PMU register state and guest exception-handler state (`expected_ec`). Dependencies include arm PMUv3 register definitions from `<perf/arm_pmuv3.h>`, VGIC support for the PMU interrupt, descriptor-table setup, PMEVN register-switch macros, and arm64 exception decoding.

Risks and edge cases: counter count zero is valid and leaves only the cycle counter valid. Unimplemented event counter direct/indirect accesses must raise `ESR_ELx_EC_UNKNOWN`; bitmap registers must mask unimplemented counters. Host register set/clear aliases must not retain invalid bits. The test intentionally uses all accessor combinations to catch inconsistencies between direct and selected register paths.

Test signals: guest assertions validate PMCR.N, bitmap masks, read/write round-trips, undefined exceptions for invalid counters, and reset persistence. Host assertions validate PMUVer exposure, device attr success/failure, and masking in `PMCNTEN`, `PMINTEN`, and `PMOVS` set/clear registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vpmu_counter_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/coalesced_io_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/coalesced_io_test.c

Purpose: this architecture-generic KVM selftest validates coalesced MMIO and, on x86, coalesced PIO. It checks that registered I/O ranges fill KVM's coalesced I/O ring up to one spare entry, that the next write exits to userspace, that ring entries contain correct payload metadata, and that unregistering ranges restores immediate exits.

Important APIs, types, and functions: `struct kvm_coalesced_io` records the ring, ring size, MMIO GPA/HVA, and x86 PIO port. `guest_code()` repeatedly writes enough MMIO/PIO entries to fill the ring and then does ucalls and non-coalesced writes. `vcpu_run_and_verify_io_exit()` checks `KVM_EXIT_MMIO` or `KVM_EXIT_IO`. `vcpu_run_and_verify_coalesced_io()` validates ring fullness and every `struct kvm_coalesced_mmio` entry. `test_coalesced_io()` wraps register/unregister and ucall checks.

Control flow: `main()` requires `KVM_CAP_COALESCED_MMIO` and, on x86, `KVM_CAP_COALESCED_PIO`, creates a one-vCPU VM, derives the ring address from the vCPU run page and capability page offset, computes ring capacity from host page size, identity maps an arbitrary high MMIO GPA, syncs the ring descriptor to the guest, and tests every possible initial ring index.

State, persistence, and dependencies: state is the KVM coalesced ring inside the vCPU run mmap and transient guest writes. Dependencies include KVM coalesced I/O capabilities, selftest VM mapping helpers, and x86 `outl()` for PIO coverage.

Risks and edge cases: KVM intentionally leaves one free ring entry, so the test relies on `ring_size - 1` writes before exit. PIO data must only be read on PIO exits because `data_offset` is invalid for MMIO exits. Ring wrap-around is tested by varying `ring_start`.

Test signals: expected ring first/last positions, exact MMIO or PIO entry contents, immediate ucall exit without ring mutation, and immediate exits after unregistering coalesced ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/coalesced_io_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/config

Purpose: this kselftest config fragment declares kernel configuration options expected for KVM selftests in this tree.

Important entries: `CONFIG_KVM=y` enables core KVM support. `CONFIG_KVM_INTEL=y` and `CONFIG_KVM_AMD=y` enable x86 vendor modules. `CONFIG_EVENTFD=y` supports irqfd/eventfd-based tests. `CONFIG_USERFAULTFD=y` supports demand paging tests. `CONFIG_IDLE_PAGE_TRACKING=y` supports memory tracking scenarios elsewhere in the KVM selftests.

Control flow and state: this file is declarative data consumed by kselftest configuration tooling; it has no runtime control flow and writes no state.

Dependencies and integration: it integrates with kernel build/config checking for `tools/testing/selftests/kvm`. Individual tests still perform runtime `TEST_REQUIRE()` capability checks because kernel config alone does not guarantee host hardware or KVM module support.

Risks and test signals: the fragment is generic and x86-heavy despite the directory containing multi-architecture tests. Missing options can cause build or runtime skips; extra options do not force tests to run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/demand_paging_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/demand_paging_test.c

Purpose: this test measures and validates KVM guest memory demand paging behavior using optional userfaultfd missing or minor fault handling across one or more vCPUs and memory backing types.

Important APIs, types, and functions: `struct test_params` captures UFFD mode, single versus per-vCPU uffd, artificial delay, reader count, backing source, and overlapping versus partitioned memory access. `vcpu_worker()` runs a memstress vCPU until a sync. `handle_uffd_page_request()` services missing faults with `UFFDIO_COPY` and minor faults with `UFFDIO_CONTINUE`, tolerating `EEXIST` races. `prefault_mem()` populates shared backing for minor faults. `run_test()` creates the memstress VM, registers UFFD ranges with `uffd_setup_demand_paging()`, starts vCPU threads, stops UFFD workers, and reports rates.

Control flow: `main()` is compiled only when `__NR_userfaultfd` is present; otherwise it prints a skip. It parses guest modes, UFFD mode, memory size, backing type, vCPU count, CPU pinning, overlap mode, and reader count. Minor-fault mode requires shared backing. For each guest mode, `run_test()` creates the VM, optionally prefaults aliases for minor faults, partitions or shares UFFD registrations, runs all vCPUs, and prints per-vCPU and aggregate paging rates.

State, persistence, and dependencies: state is transient VM memory, UFFD registrations, handler threads, and a `guest_data_prototype` page used for copies. Dependencies include `memstress`, `guest_modes`, `userfaultfd_util`, `ucall_common`, Linux userfaultfd ioctls, pthreads, and selected backing sources.

Risks and edge cases: multiple vCPUs/readers can fault the same page, so duplicate `UFFDIO_COPY` or `UFFDIO_CONTINUE` may return `EEXIST` and is intentionally ignored. Minor faults require shared memory backing and prefaulted aliases. Overlap mode forces a single UFFD. Artificial delays and pinning affect performance output but not correctness.

Test signals: guest reaches `UCALL_SYNC` for each vCPU, UFFD handlers service faults without unexpected errors, all vCPU threads join, and the test prints execution time plus demand paging rates. Missing syscall support or unsupported minor-fault backing skips/fails early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/demand_paging_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_perf_test.c

Purpose: this benchmark-style KVM selftest measures dirty logging overhead while one or more memstress vCPUs dirty guest memory. It times memory population, enabling/disabling dirty logging, guest dirtying iterations, `KVM_GET_DIRTY_LOG`, and optional manual clear-log operations.

Important APIs, types, and functions: global controls include `nr_vcpus`, `guest_percpu_mem_size`, `dirty_log_manual_caps`, `iteration`, and `vcpu_last_completed_iteration`. `vcpu_worker()` loops running guest memstress code and synchronizing on the host iteration counter. `struct test_params` covers iteration count, physical offset, memory partitioning, backing source, slot count, write percentage, and random access. `run_test()` creates the VM through `memstress_create_vm()`, allocates bitmaps, enables manual dirty-log protection when available, coordinates iterations, and reports timings. `main()` parses benchmark options including nested mode and CPU pinning.

Control flow: the test first populates memory with 100 percent sequential writes to avoid later copy-on-write noise. It enables dirty logging over the configured slots, restores requested write percentage and access pattern, then for each iteration releases vCPUs, waits for them to finish, collects dirty logs, and optionally clears dirty bits. At the end it may keep vCPUs running during dirty-log disable to stress SPTE zapping, disables logging, stops vCPU threads, and prints aggregate averages.

State, persistence, and dependencies: state is transient VM memory, KVM dirty bitmap state, host bitmaps, and memstress thread coordination. Dependencies include `memstress`, `guest_modes`, manual dirty-log cap `KVM_CAP_MANUAL_DIRTY_LOG_PROTECT2`, backing source helpers, nested-mode support when requested, and pthreads.

Risks and edge cases: benchmark values are sensitive to backing source, CPU pinning, random seed, write percentage, memslot count, and whether vCPUs run while disabling dirty logging. Manual dirty-log capabilities are masked to `KVM_DIRTY_LOG_MANUAL_PROTECT_ENABLE` and `KVM_DIRTY_LOG_INITIALLY_SET`; `-g` disables them to compare legacy behavior. Iteration count must be at least two.

Test signals: the program prints timing for population, enable, each dirtying/get/clear iteration, disable, and averages. Assertions cover vCPU sync exits, vCPU count limits, write percentage range, and bitmap allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_perf_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_test.c

Purpose: this KVM correctness test verifies dirty page tracking for three modes: legacy `KVM_GET_DIRTY_LOG`, manual get+clear logging, and dirty-ring logging. It checks that dirty bitmaps/rings match guest writes across iterations and that clean pages contain only older iteration values.

Important APIs, types, and functions: shared guest/host globals include page sizes, guest page count, iteration, write count, stop flag, guest physical/virtual test addresses, and dirty-ring bookkeeping. `guest_code()` randomly writes iteration values to test pages until stopped. `enum log_mode_t` and `struct log_mode` abstract mode-specific support, VM setup, collection, and post-run handling. Dirty-ring helpers include `dirty_ring_create_vm_done()`, `dirty_ring_collect_one()`, `dirty_ring_collect_dirty_pages()`, and `dirty_ring_after_vcpu_run()`. `vm_dirty_log_verify()` compares collected bitmaps against host memory contents.

Control flow: `main()` initializes semaphores, parses iteration interval, guest mode, log mode, physical offset, and dirty-ring size, then runs all selected guest modes and log modes. `run_test()` creates a VM with extra memory for page tables, creates a logged test memslot near the top of guest physical memory unless overridden, maps it at a fixed guest virtual address, syncs globals to the guest, and starts one vCPU thread. Each iteration syncs the iteration number, releases the vCPU, periodically collects dirty state while the guest runs when needed, stops the vCPU, performs a final collection, verifies memory, and repeats.

State, persistence, and dependencies: state is transient VM memory, KVM dirty logs/rings, two host bitmaps, semaphores, and the vCPU thread. Dependencies include `guest_modes`, `processor.h`, `ucall_common`, Linux bitmap/bitops helpers, `KVM_CAP_MANUAL_DIRTY_LOG_PROTECT2`, `KVM_CAP_DIRTY_LOG_RING` or `KVM_CAP_DIRTY_LOG_RING_ACQ_REL`, and architecture-specific guest stores.

Risks and edge cases: dirty-ring full exits can record the last GFN before the guest write retires, so verification permits special last-page and previous-last-page cases. s390x segment dirtying requires an initial touch-all-pages workaround and excludes dirty-ring mode. Bitmap modes are destructive on collection, so collection while guest runs is limited. The test enforces a minimum write count per iteration to avoid false coverage.

Test signals: each iteration prints dirty/clean/write counts and asserts dirty pages hold the current iteration except documented exceptions, clean pages hold older values, dirty-ring reset count matches harvested entries, vCPU exits are either sync or dirty-ring-full, and total checked bits are reported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/dirty_log_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/get-reg-list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/get-reg-list.c

Purpose: this architecture-shared test detects regressions in `KVM_GET_REG_LIST` by comparing the current register list for each vCPU configuration against architecture-supplied blessed lists. Missing blessed registers are failures; new registers are reported for maintainers to add to the baseline.

Important APIs, types, and functions: external `vcpu_configs[]` entries provide named register sublists, capability requirements, rejected-set and skipped-set lists. Weak hooks `check_supported_reg()`, `filter_reg()`, `print_reg()`, `check_reject_set()`, and `finalize_vcpu()` allow architecture-specific behavior. On arm64, `prepare_vcpu_init()` applies feature bits before `aarch64_vcpu_setup()`. `run_test()` gets `vcpu_get_reg_list()`, builds the blessed array, tests get/writeback or expected set rejection for present blessed registers, counts new/missing registers, and reports pass/fail.

Control flow: `main()` parses optional `--config=`, `--list`, and `--list-filtered`. Listing modes require a single config. For each selected configuration, it forks a child to isolate skips/failures, runs `run_test()`, and treats non-skip nonzero exit as failure. In normal mode, it prints candidate additions for new regs and missing-reg diagnostics for regressions.

State, persistence, and dependencies: state is process-local allocated register arrays and transient barebones VMs/vCPUs. Dependencies include architecture-specific `processor.h` definitions that supply `vcpu_reg_list` data, KVM one-reg ioctls, fork/wait, and kselftest assertion helpers. It writes no files; `--list` output can be captured manually to update blessed lists elsewhere.

Risks and edge cases: new registers are tolerated but surfaced; missing supported registers are failures because they can break migration from older to newer kernels. Some registers are advertised but must reject set or be skipped for set. The test writes back exactly the value read to avoid inventing unsupported register values. Filtered regs do not count as new.

Test signals: per-config `PASS`, counts of blessed/current/filtered registers when differences exist, printed new-register snippets, missing-register diagnostics, and aggregate child exit status from `main()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/get-reg-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_memfd_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_memfd_test.c

Purpose: this test validates the `KVM_CAP_GUEST_MEMFD` file API, optional mmap/shared initialization flags, fallocate semantics, NUMA policy interactions, SIGBUS behavior for inaccessible ranges, and actual guest access through a `KVM_MEM_GUEST_MEMFD` memslot.

Important APIs, types, and functions: file API checks include `test_file_read_write()`, `test_file_size()`, `test_fallocate()`, and `test_invalid_punch_hole()`. Mapping checks include `test_mmap_supported()`, `test_mmap_not_supported()`, `test_mmap_cow()`, `test_fault_private()`, `test_fault_overflow()`, and `test_collapse()`. NUMA checks use `test_mbind()` and `test_numa_allocation()`. Creation checks use `test_create_guest_memfd_invalid_sizes()`, `test_create_guest_memfd_multiple()`, and `test_guest_memfd_flags()`. `test_guest_memfd_guest()` installs a guest_memfd-backed memslot and runs guest code that reads `0xaa` and writes back `0xff`.

Control flow: `main()` requires `KVM_CAP_GUEST_MEMFD`, gets host page size, enumerates VM types from `KVM_CAP_VM_TYPES` or defaults to the default type, and runs `test_guest_memfd()` for each. That function validates supported flags, always tests flags zero, conditionally tests `GUEST_MEMFD_FLAG_MMAP`, and tests `GUEST_MEMFD_FLAG_MMAP | GUEST_MEMFD_FLAG_INIT_SHARED` when available. The final guest-backed test runs only when guest_memfd flags are queryable and asserts default VM type supports mmap and init-shared flags.

State, persistence, and dependencies: state is guest_memfd file contents, host mappings, NUMA policies, and VM memslot state; files are anonymous KVM guest_memfd descriptors and are closed after each subtest. Dependencies include `KVM_CAP_GUEST_MEMFD`, `KVM_CAP_GUEST_MEMFD_FLAGS`, `KVM_MEM_GUEST_MEMFD`, `mmap`, `fallocate`, `madvise`, `mbind`, `move_pages`, SIGBUS test helpers, hugepage size discovery, and selftest NUMA wrappers.

Risks and edge cases: guest_memfd intentionally rejects normal read/write/pread/pwrite and private COW mappings. Page-size alignment is mandatory for creation and punch-hole operations. Mmap support depends on flags; private mappings SIGBUS on access when not shared-initialized. `MADV_COLLAPSE` must fail to prevent huge folios from exposing data outside shared ranges. NUMA tests skip on single-node systems.

Test signals: expected failures for unsupported flags and invalid sizes, expected mmap/SIGBUS/fallocate behavior, NUMA placement checks when applicable, and guest round-trip verification that host-initialized `0xaa` bytes become `0xff` after guest execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_memfd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_print_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_print_test.c

Purpose: this test validates KVM selftest guest-side formatted output and assertion formatting through `GUEST_PRINTF()` and `__GUEST_ASSERT()`/`GUEST_ASSERT_FMT`-style ucalls for supported integer, character, string, and pointer formats.

Important APIs, types, and functions: `struct guest_vals` carries two arguments and an enum type to guest code. `TYPE_LIST` drives generation of expected printf/assert format strings and host helper functions for signed/unsigned 64-bit, hex, 32-bit, int, char, string, and pointer types. `guest_code()` emits a formatted printf then an assertion comparing `vals.a` and `vals.b`. `run_test()` handles `UCALL_PRINTF`, intentional `UCALL_ABORT`, and `UCALL_DONE`. `test_limits()` runs `guest_code_limits()` to ensure overlong printf buffers abort.

Control flow: `main()` creates one VM/vCPU and runs generated helpers with equal and unequal values for every format. Equal values produce printf then done; unequal values produce printf then an abort whose trailing assertion message is compared with the expected string. After freeing the main VM, `test_limits()` verifies that a string longer than `UCALL_BUFFER_LEN` triggers `UCALL_ABORT`.

State, persistence, and dependencies: state is the synced global `vals` and transient ucall buffers. Dependencies include selftest ucall common infrastructure, guest printf/assert macros, KVM run-page exit reason mapping, and format compatibility between guest and host snprintf.

Risks and edge cases: floats/doubles are deliberately unsupported. Assertion ucalls include extra metadata before the message, so the test compares the expected assertion as a suffix. Pointer and string values are cast through `u64`, which is suitable for the selftest ABI but should not be generalized beyond it.

Test signals: exact string equality for `UCALL_PRINTF`, suffix equality for `UCALL_ABORT`, `UCALL_DONE` after each case, and expected abort for overlong output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/guest_print_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/hardware_disable_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/hardware_disable_test.c

Purpose: this stress test tries to reproduce crashes around `kvm_arch_hardware_disable()` unregistering user return notifiers while vCPU threads and unrelated threads are active and the process is killed.

Important APIs, types, and functions: constants configure four vCPUs, sixteen background threads per vCPU, 512 fork iterations, and up to 2000 us parent delay. `guest_code()` spins forever. `run_vcpu()` runs a vCPU and fails if it exits. `sleeping_thread()` loops opening and closing `/dev/null` to create user-return activity. `run_test()` creates a VM, starts vCPU and background threads pinned to a CPU set, posts a named semaphore when setup is complete, and then waits forever. `wait_for_child_setup()` waits for the semaphore while detecting premature child exit.

Control flow: `main()` creates a named semaphore, then repeatedly forks. Each child runs `run_test()` and should remain alive with active vCPUs/threads. The parent waits until the child has launched threads, sleeps a random short delay, asserts the child has not already exited, and kills it with `SIGKILL`. This forces KVM hardware disable cleanup during abrupt process teardown.

State, persistence, and dependencies: state is mostly kernel KVM/vCPU state, pthreads, process lifetime, and a POSIX named semaphore unlinked immediately after creation. Dependencies include `/dev/kvm`, pthread affinity, fork/kill/waitpid, and `/dev/null`.

Risks and edge cases: the test is intentionally destructive to child processes and does not join background threads. It assumes CPUs 0 through 3 are valid for affinity; systems with fewer CPUs may fail thread affinity. It is race-oriented and may expose rare teardown bugs only under repeated runs.

Test signals: parent completes all fork/kill iterations without child premature exit or host crash. Any vCPU exit, thread creation/affinity failure, unexpected child exit, or semaphore wait failure triggers assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/hardware_disable_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/arch_timer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/arch_timer.h

Purpose: this arm64 helper header provides guest-side generic timer accessors for KVM selftests. It abstracts virtual versus physical timer sysregs, conversion between time units and counter cycles, and host-side helpers for querying the timer IRQ assigned to a vCPU.

Important APIs, types, and functions: `enum arch_timer` distinguishes `VIRTUAL` and `PHYSICAL`. Control bits `CTL_ENABLE`, `CTL_IMASK`, and `CTL_ISTATUS` mirror timer control register fields. Conversion macros use `timer_get_cntfrq()`. Inline helpers read counter values (`timer_get_cntct()`), compare/timer values (`timer_set_cval()`, `timer_get_cval()`, `timer_set_tval()`, `timer_get_tval()`), and control registers (`timer_set_ctl()`, `timer_get_ctl()`). `timer_set_next_cval_ms()` and `timer_set_next_tval_ms()` schedule future events. `vcpu_get_vtimer_irq()` and `vcpu_get_ptimer_irq()` select virtual/hypervisor or physical/hypervisor timer IRQ attributes based on `vcpu_has_el2()`.

Control flow: each accessor switches on timer type and fails the guest on invalid enum values. Reads of counters and TVAL include `isb()` where needed to synchronize system register state.

State, persistence, and dependencies: state is hardware/KVM virtual timer register state only. Dependencies include `processor.h` sysreg accessors and KVM arm64 timer device attributes.

Risks and edge cases: conversions divide by the runtime counter frequency and assume nonzero `CNTFRQ_EL0`. EL2-capable vCPUs use HVTIMER/HPTIMER attributes instead of VTIMER/PTIMER. Invalid timer enum values intentionally fail guest execution.

Test signals: downstream timer tests use these helpers to verify IRQ delivery, compare values, masking, and counter conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/arch_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/delay.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/delay.h

Purpose: this header provides simple guest-side busy-wait delay helpers for arm64 KVM selftests.

Important APIs, types, and functions: `__delay(u64 cycles)` reads the virtual timer counter with `timer_get_cntct(VIRTUAL)` and spins with `cpu_relax()` until the requested cycle delta elapses. `udelay(unsigned long usec)` converts microseconds to cycles with `usec_to_cycles()` from `arch_timer.h`.

Control flow: both helpers are inline and synchronous; they never yield to the host except through normal vCPU scheduling.

State, persistence, and dependencies: no persistent state. Dependencies are the virtual generic timer helpers in `arch_timer.h` and `cpu_relax()` from processor helpers.

Risks and edge cases: this is a busy wait, so long delays consume guest CPU time. Timing precision depends on the virtual counter frequency and scheduling latency.

Test signals: downstream tests use these helpers when they need approximate guest-side delay without host coordination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic.h

Purpose: this header defines the common arm64 GIC selftest interface and address layout used by guest code and VM setup helpers.

Important APIs, types, and functions: `enum gic_type` currently exposes `GIC_V3`. GPA/GVA constants place ITS, distributor, and redistributor regions at fixed identity-mapped guest addresses: `GITS_BASE_GPA`, `GICD_BASE_GPA`, and `GICR_BASE_GPA`. Interrupt ID constants define SGI, PPI, SPI ranges and `IAR_SPURIOUS`. Macros classify intids. Function declarations cover GIC init, IRQ enable/disable, acknowledge, EOI, DIR, EOI split, priority mask/priority, active/pending/config/group state, and LPI redistributor enablement.

Control flow: this file is declarations and macros only; implementation is in arm64 GIC helper sources. Downstream tests call these APIs from guest code after VGIC setup.

State, persistence, and dependencies: no direct state. Dependencies include `<asm/kvm.h>` for KVM VGIC sizes and selftest VM setup that maps the GIC MMIO regions at the declared addresses.

Risks and edge cases: fixed GIC base addresses must not collide with test memory. `MAX_SPI` is 1019 and `IAR_SPURIOUS` is 1023, leaving reserved IDs. LPI use requires separate ITS/GICv3 setup.

Test signals: used by VGIC IRQ and LPI tests for delivery, active/pending state, priorities, and LPI configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3.h

Purpose: this arm64 helper header centralizes GICv3, redistributor, ITS, LPI/VLPI, and CPU-interface register offsets and bitfield definitions used by KVM selftests.

Important APIs, types, and functions: it defines distributor offsets (`GICD_*`), redistributor offsets (`GICR_*`), ITS offsets (`GITS_*`), register size constants, page-size encodings, baser cacheability/shareability helpers, LPI property bits, ITS command opcodes and error numbers, and CPU interface fields such as `ICC_CTLR_EL1_*`, `ICC_SRE_EL1_*`, `ICC_SGI1R_*`, and `ICC_IAR1_EL1_SPURIOUS`. Macros like `GICD_TYPER_SPIS()`, `GICD_TYPER_ESPIS()`, `GICR_TYPER_NR_PPIS()`, `GITS_BASER_ENTRY_SIZE()`, and address conversion helpers decode hardware-emulated register fields.

Control flow: this file has no executable control flow; it supplies compile-time constants consumed by guest helpers, VGIC setup helpers, and tests that read/write KVM VGIC device attributes.

State, persistence, and dependencies: no state. It depends on Linux bit macros such as `GENMASK_ULL` and is included by GIC library/test code that performs actual MMIO/sysreg accesses.

Risks and edge cases: correctness depends on matching the Arm GIC architecture and KVM's emulated register layout. Address-field helpers for 52-bit ITS BASER values and GICR/GITS table cacheability fields are easy to misuse. Some definitions cover GICv4/VLPI even when tests run only GICv3 paths.

Test signals: downstream tests validate these definitions indirectly by successfully initializing VGIC/ITS, programming LPI tables, reading GICR_TYPER, manipulating priorities/groups, and exercising sysreg attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3_its.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3_its.h

Purpose: this header declares guest-side helpers for initializing and programming a GICv3 ITS command queue in KVM selftests.

Important APIs, types, and functions: `its_init()` configures collection table, device table, and command queue base/size. Command helpers emit `MAPD`, `MAPC`, `MAPTI`, `INVALL`, and `SYNC` operations: `its_send_mapd_cmd()`, `its_send_mapc_cmd()`, `its_send_mapti_cmd()`, `its_send_invall_cmd()`, and `its_send_sync_cmd()`.

Control flow: declarations only. Implementations serialize ITS commands into the guest command queue and are used after redistributors and ITS tables are allocated.

State, persistence, and dependencies: no direct state. Dependencies include `gpa_t`, `u32`, `bool`, and table sizing conventions from the surrounding selftest headers. It is integrated by LPI/ITS tests such as `vgic_lpi_stress.c`.

Risks and edge cases: callers must provide correctly aligned and sized ITS tables and command queue memory. Incorrect device IDs, event IDs, collection IDs, or missing sync commands can make `KVM_SIGNAL_MSI` fail translation.

Test signals: successful downstream LPI tests show that mappings and invalidations created through these helpers are accepted by the emulated ITS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3_its.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v5.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v5.h

Purpose: this header provides GICv5 current-domain instruction encodings, bitfield helpers, barriers, and minimal CPU-interface initialization routines for arm64 KVM GICv5 selftests.

Important APIs, types, and functions: `GICV5_OP_GIC_*` and `GICV5_OP_GICR_*` define system instruction encodings for current-domain affinity, enable, priority, pending, acknowledge, deactivate, and EOI operations. Bit masks decode or build instruction operands such as `GICV5_GICR_CDIA_VALID_MASK`, `GICV5_GICR_CDIA_INTID`, and per-operation ID/type/priority fields. `gicr_insn()` reads GICR current-domain instruction results and `gic_insn()` writes GIC instructions. `gsb_ack()` and `gsb_sys()` emit GIC barrier instructions. `gicv5_ppi_priority_init()`, `gicv5_cpu_disable_interrupts()`, and `gicv5_cpu_enable_interrupts()` configure PPI priority registers, `ICC_PCR_EL1`, and `ICC_CR0_EL1`.

Control flow: initialization clears PPI enable registers, writes default priority to all PPI priority registers, sets the priority control register, and enables the CPU interface. Barrier and instruction helpers are inline macros. The header defines executable functions in the header, so every including translation unit receives definitions.

State, persistence, and dependencies: state is guest CPU interface sysreg state. Dependencies include `<asm/barrier.h>`, `<asm/sysreg.h>`, `linux/bitfield.h`, and `processor.h`. It is used by `vgic_v5.c`.

Risks and edge cases: GICv5 is optional and instruction encodings must match the architecture. Header-defined non-static functions can create multiple-definition risk if included by multiple C files in one link unit, though current use is narrow. Priority defaults use repeated 5-bit priority bytes and assume the tested KVM model implements these sysregs.

Test signals: `vgic_v5.c` validates these helpers by enabling PPIs, acknowledging CDIA results, applying barriers, and deactivating/EOIing software PPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/kvm_util_arch.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/kvm_util_arch.h

Purpose: this small architecture-specific header defines arm64 extensions to the shared KVM selftest utility VM structures.

Important APIs, types, and functions: `struct kvm_mmu_arch` is currently empty for arm64. `struct kvm_vm_arch` stores whether a VM has a GIC (`has_gic`) and the associated GIC device fd (`gic_fd`).

Control flow: no executable code; the structures are embedded by shared selftest infrastructure.

State, persistence, and dependencies: `has_gic` and `gic_fd` persist for the lifetime of the in-process `struct kvm_vm` and let helpers avoid creating duplicate VGIC devices or find the existing fd.

Risks and edge cases: the fd must be closed by VM teardown paths that understand arm64 VGIC ownership. Empty `kvm_mmu_arch` signals that generic MMU helper state is sufficient for arm64 today, but future arm64 MMU metadata would be added here.

Test signals: downstream tests indirectly validate this state through `vgic_v3_setup()`, `test_disable_default_vgic()`, and other KVM utility helpers that create or reuse VGIC devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/kvm_util_arch.h -->
