# Research: subset-b-000685

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/ffa.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/ffa.c

## Purpose
`ffa.c` implements the nVHE/pKVM proxy for Arm FF-A firmware calls made by the host. It intercepts standard FF-A SMCs, rejects unsupported memory-management and messaging calls, forwards safe calls to EL3/SPMD, and wraps share/lend/reclaim operations with host stage-2 ownership checks so the host cannot expose protected guest memory to secure-world firmware.

## Important APIs, Types, and Functions
`struct kvm_ffa_descriptor_buffer` stores a hyp-private descriptor scratch area for fragmented retrieve responses. `struct kvm_ffa_buffers` tracks locked RX/TX mailboxes for the host and hypervisor. `kvm_host_ffa_handler()` is the trap entry point from `hyp-main.c`. `hyp_ffa_init()` probes firmware FF-A support and partitions proxy pages into hyp TX, hyp RX, and descriptor storage. `do_ffa_rxtx_map()` and `do_ffa_rxtx_unmap()` share, pin, unpin, and unshare host mailbox pages. `do_ffa_mem_xfer()`, `do_ffa_mem_frag_tx()`, and `do_ffa_mem_reclaim()` mirror descriptors through hyp buffers and call `__pkvm_host_share_ffa()` / `__pkvm_host_unshare_ffa()` around firmware transactions. `do_ffa_version()`, `do_ffa_features()`, and `do_ffa_part_get()` handle version negotiation, feature discovery, and partition-info copying.

## Control Flow, State, and Persistence
The file maintains persistent hyp state in `hyp_ffa_version`, `has_version_negotiated`, `host_buffers`, `hyp_buffers`, and `ffa_desc_buf`; all RX/TX buffer operations are serialized by `host_buffers.lock`, and version negotiation by `version_lock`. Host calls must negotiate `FFA_VERSION` before other FF-A calls. RXTX map first maps hyp buffers into SPMD, then shares and pins the host pages in hyp; unmap reverses that state. Memory share/lend copies the first fragment into hyp memory, validates descriptor shape and range counts, updates host page state to shared-owned, issues the SMC, and rolls back host state if firmware rejects the transfer. Reclaim retrieves the descriptor from firmware, handles fragments into `ffa_desc_buf`, calls firmware reclaim, then marks pages owned by the host again.

## Dependencies and Integration Points
It depends on Arm SMCCC 1.2 wrappers, Linux FF-A ABI definitions, pKVM ownership helpers from `mem_protect.c`, hyp virtual/physical conversion helpers, and the host SMC trap path in `hyp-main.c`. It also relies on PSCI/SMCCC version information initialized by the host and on setup-provided FF-A proxy pages.

## Risks and Test Signals
Key risks are descriptor parsing bugs from untrusted host TX contents, rollback gaps after partial fragments, stale pinned host mailbox pages, incorrect FF-A version downgrade behavior, and firmware quirks around fragmented retrieve responses. Useful tests include FF-A version negotiation before/after downgrade attempts, RXTX map/unmap error unwind, share/lend with malformed offsets or counts, fragment rollback on firmware failure, reclaim with fragmented descriptors, and verifying host stage-2 page states after each path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/ffa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/gen-hyprel.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/gen-hyprel.c

## Purpose
`gen-hyprel.c` is a host build tool that scans the relocatable nVHE ELF object and emits assembly for `.hyp.reloc`, allowing the final kernel link to record absolute kernel virtual addresses embedded in hyp sections so they can be converted to hyp virtual addresses at runtime.

## Important APIs, Types, and Functions
Global `elf` stores the mmaped ELF, section table, and string table. `init_elf()` opens and validates an ELF64 AArch64 relocatable object with the configured endianness. `emit_prologue()` and `emit_epilogue()` wrap output in `.hyp.reloc`. `emit_rela_section()` filters relocations whose target section begins with `.hyp`, accepts known PC-relative and data relocation types, and calls `emit_rela_abs64()` for `R_AARCH64_ABS64`. `emit_rela_abs64()` emits one `.word` plus a `R_AARCH64_PREL32` relocation against `__hyp_section_<section> + offset`. `emit_all_relocs()` rejects `SHT_REL` and processes all `SHT_RELA` sections.

## Control Flow, State, and Persistence
The program is a one-shot build-time transformer: `main()` validates one input path, maps it read-only, emits fixed assembly to stdout, and exits. It persists no repository state itself; generated assembly becomes part of the vmlinux link. Its only mutable state is the process-local `elf` descriptor and the static `reloc_offset` used to place generated PREL32 relocations.

## Dependencies and Integration Points
It integrates the nVHE partial link, `hyp.lds.S` section symbols, the vmlinux linker, and runtime hyp relocation code that consumes `.hyp.reloc`. It depends on `<generated/autoconf.h>` for endianness and carries local definitions for AArch64 relocation constants missing from older host toolchains.

## Risks and Test Signals
Risks include rejecting newly emitted relocation types after compiler/toolchain upgrades, relying on section-name prefixes, lack of deep bounds validation beyond assertions, and only tracking ABS64 absolute addresses. Test signals are successful builds across little/big endian configurations, deliberate object files with ABS64/ABS32/PC-relative relocations, failure on SHT_REL or unexpected relocation types, and link-time presence of `.hyp.reloc` entries for hyp absolute data references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/gen-hyprel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/host.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/host.S

## Purpose
`host.S` contains the nVHE host exception vector and low-level host/hyp transition assembly. It saves host CPU context on traps into EL2, calls the C trap handler, restores host state for `eret`, handles hyp panic return to the host, supports legacy stub HVC calls before protected mode, and forwards unhandled SMCs to firmware.

## Important APIs, Types, and Functions
`__host_exit` saves host registers, optionally switches pointer-authentication keys to hyp keys, calls `handle_trap()`, then restores host registers and returns. `__host_enter` restores a supplied host context and never returns in C terms. `__hyp_do_panic` prepares host panic-handler entry with ESR/ELR/PAR/FAR/HPFAR arguments. `__host_hvc` chooses between protected-mode trap handling, legacy stub HVC dispatch, and full host-exit handling. `__kvm_hyp_host_vector` defines EL2 and lower-EL vector slots. `__kvm_hyp_host_forward_smc` loads x0-x17 from `struct kvm_cpu_context`, executes `smc #0`, and stores the result.

## Control Flow, State, and Persistence
The file persists CPU state only by writing the per-CPU host context selected by `get_host_ctxt`. Synchronous lower-EL vectors push x0/x1, inspect ESR, dispatch HVC64 specially, and otherwise enter `__host_exit`. Invalid EL2 vectors detect stack overflow using the `NVHE_STACK_SHIFT` guard bit and route to panic, optionally on the overflow stack. Pointer-authentication state is saved/restored only under configured alternatives and protected mode.

## Dependencies and Integration Points
It depends on assembler macros for KVM context offsets, ptrauth save/restore, hyp/kimage address conversion, host vector constants, and panic symbols. It is entered from `hyp-init.S` via VBAR_EL2 and calls C handlers in `hyp-main.c` and panic support in `switch.c` / `stacktrace.c`.

## Risks and Test Signals
Risks include register-save omissions, mismatch with `struct kvm_cpu_context` offsets, incorrect ptrauth key switching, stack-overflow detection depending on stack alignment, and forwarding SMC register sets wider than the firmware ABI guarantees. Test signals are booting nVHE with and without protected mode, HVC/SMC trap smoke tests, panic stacktrace capture, ptrauth-enabled kernels, and objtool/assembler checks for vector slot size constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/host.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-init.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-init.S

## Purpose
`hyp-init.S` is the identity-mapped EL2 bootstrap for nVHE. It accepts the initial host HVC, initializes EL2 state and MMU registers from `kvm_nvhe_init_params`, installs host vectors, provides CPU_ON/resume entry points for PSCI relay, handles hyp-stub reset calls, and switches to rebuilt protected page tables during pKVM initialization.

## Important APIs, Types, and Functions
`__kvm_hyp_init` is an idmap vector whose lower-EL sync slot accepts `KVM_HOST_SMCCC_FUNC(__kvm_hyp_init)` or stub HVC calls. `___kvm_hyp_init` loads stack, MAIR, HCR, TPIDR_EL2, VTTBR, VTCR, TTBR0, TCR, SCTLR, and VBAR_EL2. `__kvm_init_el2_state` wraps common EL2 initialization macros. `kvm_hyp_cpu_entry` and `kvm_hyp_cpu_resume` initialize secondary/resumed CPUs and branch into PSCI C entry points. `__kvm_handle_stub_hvc` implements soft restart and vector reset. `__pkvm_init_switch_pgd` turns MMU off, installs a new TTBR0_EL2 and stack, re-enables MMU, and tail-calls a C finalizer.

## Control Flow, State, and Persistence
Initial HVCs arrive while executing in idmap text. The code validates the SMCCC function id, initializes EL2 state without clobbering callee-saved SMCCC registers, enables the EL2 MMU, and returns success. CPU_ON/resume paths verify the core is at EL2, replay EL2 setup, leave idmap through PSCI entry callbacks, or park forever on failure. `__pkvm_init_switch_pgd` is used once pKVM has built replacement page tables and must preserve architectural ordering with TLB invalidation and ISBs.

## Dependencies and Integration Points
It depends on `kvm_nvhe_init_params` layout constants, EL2 setup assembler macros, hyp host vectors from `host.S`, PSCI relay entry functions from `psci-relay.c`, and pKVM setup in `setup.c`. It integrates with the host stub ABI and architecture alternatives for CnP, pointer authentication, and BTI.

## Risks and Test Signals
Risks include incorrect ordering around MMU disable/enable, stale TLBs, bad hVHE E2H replay, wrong stack or VBAR setup on secondary CPUs, and kCFI-sensitive indirect calls to idmap code. Test signals are nVHE boot on primary and secondary CPUs, suspend/resume paths, protected-mode finalization, soft-restart/reset-vector behavior, and architectural feature combinations for CnP, ptrauth, BTI, and hVHE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-init.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-main.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-main.c

## Purpose
`hyp-main.c` is the C trap and hypercall dispatcher for nVHE. It handles host HVC/SMC/memory-abort traps, runs guest vCPUs, synchronizes host and hyp vCPU state, exposes pKVM memory/VM/tracing hypercalls, forwards PSCI/FF-A/unknown SMCs, and injects host exceptions when EL2 must reflect faults back to EL1.

## Important APIs, Types, and Functions
`handle_trap()` dispatches by ESR exception class. `handle_host_hcall()` decodes KVM host SMCCC ids and calls the `host_hcall[]` table. `handle_host_smc()` routes PSCI through `kvm_host_psci_handler()`, FF-A through `kvm_host_ffa_handler()`, and other calls through `__kvm_hyp_host_forward_smc()`. `handle___kvm_vcpu_run()` chooses direct unprotected guest run or protected hyp-vCPU run. `flush_hyp_vcpu()` and `sync_hyp_vcpu()` copy registers, debug state, VGIC state, FP/SVE ownership, HCR flags, faults, and iflags between host and hyp vCPU objects. Numerous `handle___pkvm_*` wrappers validate loaded handles/vCPUs, refill memcaches, and call `mem_protect.c`, `pkvm.c`, `mm.c`, and `trace.c`.

## Control Flow, State, and Persistence
The persistent state is mainly per-CPU `kvm_init_params` and transient host context register values. Early pKVM setup hypercalls are rejected after protected mode initialization except finalization; later hypercalls operate through published VM handles or the currently loaded hyp vCPU. Guest entry copies host vCPU state to hyp state before `__kvm_vcpu_run()` and copies it back after exit. SMC traps advance ELR after handling; host memory aborts are resolved by lazily mapping allowed host stage-2 regions or injecting aborts.

## Dependencies and Integration Points
It integrates host assembly entry/exit, pKVM VM lifecycle (`pkvm.c`), ownership transitions (`mem_protect.c`), TLB operations (`tlb.c`), timer and VGIC helpers, PSCI relay, FF-A proxy, tracing, protected VM sysreg/HVC handlers, and generic KVM ARM guest-run code.

## Risks and Test Signals
Risks include wrong hypercall gating before/after pKVM initialization, accepting stale or missing loaded hyp vCPUs, incomplete vCPU state synchronization, memcache refill failures propagating poorly, and host exception injection bugs. Tests should cover each host hypercall id, protected and non-protected vCPU runs, pKVM memory share/donate/unshare with empty memcaches, PSCI/FF-A passthrough interactions, host abort reinjection, tracing hypercalls, and invalid hypercall ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-smp.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-smp.c

## Purpose
`hyp-smp.c` provides nVHE-local CPU topology and per-CPU base helpers. It mirrors the host CPU logical map and per-CPU base array into hyp-readable storage for code that cannot trust or directly use host data after pKVM finalization.

## Important APIs, Types, and Functions
`hyp_cpu_logical_map[NR_CPUS]` stores MPIDR hardware ids, initialized to `INVALID_HWID`. `cpu_logical_map()` returns the hyp copy for a logical CPU and asserts bounds. `kvm_arm_hyp_percpu_base[NR_CPUS]` stores host-provided per-CPU base addresses. `__hyp_per_cpu_offset()` converts a CPU’s kernel VA base to a hyp VA offset relative to `__per_cpu_start`.

## Control Flow, State, and Persistence
Both arrays are `__ro_after_init`, so they are populated by setup before becoming immutable. The file has no complex control flow: callers query a CPU index and get either an MPIDR or per-CPU offset. Bounds errors are fatal via `BUG_ON`.

## Dependencies and Integration Points
It integrates with PSCI CPU selection (`psci-relay.c`), per-CPU macros, `kvm_init_params` setup, and nVHE per-CPU storage in the linker script. It depends on `kern_hyp_va()` address translation and hyp section symbols.

## Risks and Test Signals
Risks include stale CPU maps if CPUs come online after KVM initialization, bounds BUGs from corrupted CPU ids, and mismatched per-CPU bases causing silent state corruption. Test signals are CPU hotplug restrictions, PSCI CPU_ON only for initialized CPUs, per-CPU variable access on all initialized CPUs, and boot on systems with sparse MPIDRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp.lds.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp.lds.S

## Purpose
`hyp.lds.S` is the partial-link linker script for nVHE EL2 objects. It groups and renames hyp sections so they can later be linked into vmlinux while retaining distinct hyp text, rodata, data, percpu, bss, idmap text, and optional tracing event-id ranges.

## Important APIs, Types, and Functions
The script uses `HYP_SECTION(...)`, `BEGIN_HYP_SECTION(...)`, and `END_HYP_SECTION` macros from `asm/hyp_image.h`. It emits `.idmap.text`, `.text`, `.data..ro_after_init`, `.rodata`, optional `.event_ids`, page-aligned `.data..percpu` using `PERCPU_INPUT(L1_CACHE_BYTES)`, `.bss`, and `.data`.

## Control Flow, State, and Persistence
There is no runtime control flow. Its persistent effect is the shape and alignment of the intermediate hyp ELF. Page-aligning percpu sections preserves alignment when embedded in vmlinux; optional tracing event ids are sorted and page-aligned for runtime lookup.

## Dependencies and Integration Points
It is consumed by the kernel build and paired with `gen-hyprel.c`, hyp image macros, vmlinux linker definitions, per-CPU data access in `hyp-smp.c`, and tracing event metadata in `trace.c` / hypevents.

## Risks and Test Signals
Risks include section-order changes breaking runtime symbol assumptions, missing alignment for percpu or tracing metadata, and mismatches with relocation generation. Test signals are successful nVHE partial linking, expected `__hyp_section_*` symbols, per-CPU alignment checks, optional tracing builds, and boot-time hyp relocation success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/list_debug.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/list_debug.c

## Purpose
`list_debug.c` provides minimal list corruption checks for nVHE code using Linux `list_head` helpers without depending on the full kernel debug implementation at EL2.

## Important APIs, Types, and Functions
`nvhe_check_data_corruption()` preserves boolean values while satisfying `__must_check`. `NVHE_CHECK_DATA_CORRUPTION()` reports or BUGs depending on `CONFIG_BUG_ON_DATA_CORRUPTION`. `__list_add_valid_or_report()` validates adjacent links and self-insertion before add. `__list_del_entry_valid_or_report()` checks poison pointers and adjacent links before delete.

## Control Flow, State, and Persistence
The functions are pure validation helpers; they persist no state. On corruption they either invoke `BUG()` or `WARN_ON(1)` and return false, allowing list callers to stop the unsafe operation.

## Dependencies and Integration Points
It integrates with nVHE users of Linux list helpers, notably the hyp buddy allocator’s free lists in `page_alloc.c`. It depends only on `linux/list.h`, `linux/bug.h`, and kernel config.

## Risks and Test Signals
Risks include limited diagnostics in EL2, potential fatal BUGs in protected mode when configured, and divergence from upstream `lib/list_debug.c` predicates. Test signals are allocator/list selftests with intentional corruption under warn and bug configurations, plus normal boot allocation paths without false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/list_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mem_protect.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mem_protect.c

## Purpose
`mem_protect.c` is the pKVM memory-ownership and stage-2 protection state machine. It builds host and guest stage-2 page tables, tracks page ownership in hyp vmemmap metadata, transitions pages between host, hyp, guest, and FF-A/shared states, resolves host stage-2 faults, poisons reclaimed guest pages, and provides debug selftests for ownership invariants.

## Important APIs, Types, and Functions
`host_mmu` and `host_s2_pool` hold the protected host stage-2 page table and allocator. `kvm_host_prepare_stage2()` initializes the host idmap page table. `kvm_guest_prepare_stage2()` initializes each hyp VM’s guest stage-2 and mm ops. `__pkvm_prot_finalize()` enables host stage-2 translation per CPU. `handle_host_mem_abort()` lazily maps allowed host memory/MMIO or injects host aborts. Ownership APIs include `__pkvm_host_share_hyp()`, `__pkvm_host_unshare_hyp()`, `__pkvm_host_donate_hyp()`, `__pkvm_hyp_donate_host()`, `__pkvm_host_share_ffa()`, `__pkvm_host_unshare_ffa()`, `__pkvm_host_donate_guest()`, `__pkvm_host_share_guest()`, `__pkvm_host_unshare_guest()`, `__pkvm_guest_share_host()`, `__pkvm_guest_unshare_host()`, `__pkvm_host_force_reclaim_page_guest()`, and `__pkvm_host_reclaim_page_guest()`. Guest maintenance helpers implement dirty/young/write-protect and permission relaxation for non-protected VMs.

## Control Flow, State, and Persistence
The file persists page ownership in `struct hyp_page` host/hyp state fields, guest state in guest stage-2 PTEs, donated guest owner metadata in invalid host stage-2 PTE annotations, and transient current guest VM in per-CPU `__current_vm`. Component locks are always acquired in host/hyp/guest order through `host_lock_component()`, `hyp_lock_component()`, and `guest_lock_component()`. Host stage-2 mappings are rebuilt lazily on host faults and may recycle MMIO mappings on allocation pressure. Guest donation annotates the host PTE with guest handle/GFN metadata, then maps the guest IPA as owned. Reclaim unmaps or poisons guest mappings and returns ownership to the host.

## Dependencies and Integration Points
It depends on KVM page-table primitives, memblock memory ranges from `mm.c`, hyp buddy allocation from `page_alloc.c`, pKVM VM handles from `pkvm.c`, hyp fixmap/fixblock helpers from `mm.c`, host trap handling in `hyp-main.c`, FF-A proxy calls in `ffa.c`, and architecture workarounds for speculative AT and SME DVM sync.

## Risks and Test Signals
Risks are high because this file enforces confidentiality: lock-order bugs, invalid range validation, host PTE annotation corruption, block mapping side effects, incomplete TLB/cache maintenance, refcount errors on pinned shared pages, and guest reclaim races can all break pKVM guarantees. Built-in `pkvm_ownership_selftest()` covers many transitions under `CONFIG_NVHE_EL2_DEBUG`; additional signals include protected VM boot/teardown, forced reclaim of poisoned pages, FF-A share/reclaim cycles, host abort injection, MMIO lazy mapping under low page-table memory, and permission operations rejected for protected VMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mem_protect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mm.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mm.c

## Purpose
`mm.c` manages nVHE hypervisor stage-1 mappings, private virtual address allocation, vmemmap backing, fixmap/fixblock temporary mappings, protected stacks, branch-prediction vectors, and host-provided memcache admission for pKVM.

## Important APIs, Types, and Functions
`pkvm_pgtable` and `pkvm_pgd_lock` hold the hyp stage-1 page table. `hyp_memory[]` and `hyp_memblock_nr` describe physical memory. `pkvm_alloc_private_va_range()` and `__pkvm_create_private_mapping()` reserve private VA space above `__io_map_base`. `pkvm_create_mappings()` maps linear hyp addresses. `hyp_back_vmemmap()` maps `struct hyp_page` backing memory. `pkvm_cpu_set_vector()` and `hyp_map_vectors()` select direct or spectre-hardened vectors. `hyp_fixmap_map()` / `hyp_fixmap_unmap()` and `hyp_fixblock_map()` / `hyp_fixblock_unmap()` provide temporary PA access. `hyp_create_idmap()`, `hyp_create_fixmap()`, `pkvm_create_stack()`, and `refill_memcache()` support setup and runtime allocation.

## Control Flow, State, and Persistence
`hyp_create_idmap()` establishes the initial idmap and computes the private VA layout for IO mappings and vmemmap. Private VA allocation monotonically advances `__io_map_base` and never frees ranges. Fixmap creation maps placeholder leaves, captures their PTE pointers, invalidates them, and later rewrites them by hand with required TLB invalidation. Protected stacks allocate a guard page plus mapped stack page(s), returning a top-of-stack address. `refill_memcache()` copies the host memcache, donates pages from host to hyp, and updates the host-visible memcache only after top-up.

## Dependencies and Integration Points
It integrates `setup.c` initialization, `mem_protect.c` ownership transitions, page-table primitives, hyp allocator mm ops, spectre vector selection, host SVE mappings, and trace/memory helpers that need temporary physical mappings.

## Risks and Test Signals
Risks include private VA exhaustion, fixmap break-before-make violations, incorrect TLB invalidation when rewriting PTEs, guard-stack alignment assumptions, vmemmap overlap with IO space, and memcache donation races. Test signals are pKVM initialization, vmemmap-backed allocator use, stack overflow detection, fixmap/fixblock stress on PAGE_SHIFT variants, spectre vector selection, and memcache refills with partial host page lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/page_alloc.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/page_alloc.c

## Purpose
`page_alloc.c` implements the nVHE buddy page allocator over hyp-owned memory. It uses hyp vmemmap metadata and free-list nodes stored in free pages themselves to allocate zeroed pages for page tables, VM metadata, and other hyp pools.

## Important APIs, Types, and Functions
`__hyp_vmemmap` points at hyp `struct hyp_page` metadata. `hyp_pool_init()` initializes a pool range, marks metadata refcounted, and attaches free pages after reserved pages. `hyp_alloc_pages()` finds and splits a suitable free block, marks it refcounted, and returns its hyp VA. `hyp_put_page()` decrements refcount and coalesces on zero. `hyp_get_page()` increments refcount. `hyp_split_page()` converts a high-order allocation into individual refcounted order-0 pages. Internal helpers find buddies, add/remove list nodes, coalesce in `__hyp_attach_page()`, and split in `__hyp_extract_page()`.

## Control Flow, State, and Persistence
Each `struct hyp_pool` owns a lock, max order, range bounds, and free lists. Free pages are zeroed on the put path before list insertion, so allocation can return already-zeroed memory. Refcount and buddy-tree updates are done under the pool lock to avoid transient states visible to readers. Pages outside the pool range can be freed into the pool without coalescing, supporting external donated pages.

## Dependencies and Integration Points
It depends on hyp physical/virtual/page conversion helpers, list primitives, spinlocks, and `struct hyp_page` metadata. It is used by hyp stage-1 page tables (`setup.c`/`mm.c`), host and guest stage-2 page-table pools (`mem_protect.c`), and teardown/refill paths.

## Risks and Test Signals
Risks include list corruption, refcount underflow/overflow, wrong order metadata for tail pages, zeroing memory still in use, and fragmented pools failing high-order allocations. Test signals are ownership selftests, allocator exhaustion, split/coalesce sequences, reserved page handling, list debug checks, and page-table initialization/destruction under protected VM churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/page_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/pkvm.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/pkvm.c

## Purpose
`pkvm.c` manages protected-KVM VM and vCPU metadata inside the hypervisor. It allocates and publishes VM handles, pins host-visible KVM/vCPU/SVE state, initializes protected feature and trap state, maps host-donated metadata into hyp, tears down dying VMs, and handles protected guest hypercalls for memory sharing.

## Important APIs, Types, and Functions
Global exported state includes `__icache_flags`, `kvm_arm_vmid_bits`, and `kvm_host_sve_max_vl`. `loaded_hyp_vcpu` tracks the current vCPU per physical CPU. VM-table APIs include `pkvm_hyp_vm_table_init()`, `__pkvm_reserve_vm()`, `__pkvm_unreserve_vm()`, `get_vm_by_handle()`, `get_pkvm_hyp_vm()`, and `get_np_pkvm_hyp_vm()`. `pkvm_load_hyp_vcpu()` / `pkvm_put_hyp_vcpu()` enforce single-load and VM refcounts. `__pkvm_init_vm()` and `__pkvm_init_vcpu()` consume host-donated pages for hyp VM/vCPU structures and stage-2 PGD. `__pkvm_start_teardown_vm()`, `__pkvm_finalize_teardown_vm()`, and `__pkvm_reclaim_dying_guest_page()` reclaim resources. `kvm_handle_pvm_hvc64()` handles protected guest KVM vendor hypercalls.

## Control Flow, State, and Persistence
The VM table is hyp-owned persistent state protected by `vm_table_lock`; handles start at `HANDLE_OFFSET`, and entries move from empty to `RESERVED_ENTRY` to initialized VM pointer to removed. VM and vCPU metadata pages are transferred from host to hyp via `__pkvm_host_donate_hyp()`, zeroed on map, and returned via memcaches on teardown. Protected VMs receive restricted features and trap settings; non-protected VMs copy host-selected features. vCPU registration uses release-store publication, and load uses acquire-load plus a per-vCPU loaded pointer to prevent concurrent execution.

## Dependencies and Integration Points
It depends on `mem_protect.c` for ownership, `mm.c` for donated-memory mapping, `sys_regs.c` for protected ID-register views, generic KVM ARM HCR/MDCR/SVE helpers, host hypercall wrappers in `hyp-main.c`, and guest exit handling in `switch.c`.

## Risks and Test Signals
Risks include VM-handle lifetime races, leaked pinned host pages on initialization failure, feature exposure mistakes for protected VMs, SVE state size mismatch, teardown while a vCPU is loaded, and guest memshare paths that deliberately convert missing mappings into host-visible data aborts. Test signals include reserve/unreserve/init/fail paths, concurrent vCPU load rejection, protected/non-protected feature masks, SVE enabled/disabled setup, full teardown memcache accounting, guest MEM_SHARE/MEM_UNSHARE HVCs, and dying-VM page reclaim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/pkvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/psci-relay.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/psci-relay.c

## Purpose
`psci-relay.c` intercepts host PSCI SMCs so CPU_ON and suspend resume through hyp entry points, preserving EL2 control while still forwarding firmware power-management calls. It validates target CPUs against the hyp CPU map and stores boot arguments until the target CPU reaches hyp.

## Important APIs, Types, and Functions
`kvm_host_psci_config` stores host-configured PSCI version and function IDs. `struct psci_boot_args` stores a lock, target PC, and x0. `psci_cpu_on()`, `psci_cpu_suspend()`, and `psci_system_suspend()` replace firmware entry addresses with `kvm_hyp_cpu_entry` or `kvm_hyp_cpu_resume`. `__kvm_host_psci_cpu_on_entry()` and `__kvm_host_psci_cpu_resume_entry()` restore saved host PC/x0 and enter the host through `__host_enter()`. `psci_0_1_handler()`, `psci_0_2_handler()`, `psci_1_0_handler()`, and `kvm_host_psci_handler()` select version-specific handling.

## Control Flow, State, and Persistence
CPU_ON finds the logical CPU by MPIDR, locks that CPU’s boot args, records host PC/x0, issues firmware SMC with the hyp entry physical address and that CPU’s init params, and leaves the lock held until the target CPU consumes it. CPU suspend/system suspend use per-current-CPU suspend args without a lock because only the current CPU can suspend itself. Entry functions restore EL1 SCTLR/PSTATE/ELR context and return to the host.

## Dependencies and Integration Points
It depends on `hyp-smp.c` CPU maps, `hyp-init.S` CPU entry/resume labels, `kvm_init_params`, SMCCC wrappers, tracing, and host SMC dispatch in `hyp-main.c`.

## Risks and Test Signals
Risks include rejecting valid CPUs not online at KVM init, boot-args lock leaks if firmware behavior is unexpected, PSCI 0.1 function-id configuration errors, and resume-state ordering. Test signals include CPU_ON success/failure, duplicate CPU_ON returning already-on, suspend/resume, system suspend, PSCI version variants, invalid MPIDR rejection, and tracing of PSCI enter/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/psci-relay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/setup.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/setup.c

## Purpose
`setup.c` performs protected nVHE initialization after the host donates a contiguous memory pool. It partitions the pool, rebuilds hyp mappings, backs the vmemmap, creates host stage-2 and fixmaps, reconciles ownership metadata, initializes FF-A and the VM table, and tail-calls back to the host with the result.

## Important APIs, Types, and Functions
`divide_memory_pool()` carves selftest, vmemmap, VM table, hyp stage-1 page tables, host stage-2 page tables, and FF-A proxy pages. `recreate_hyp_mappings()` builds a fresh hyp page table and maps idmap text, vectors, vmemmap, hyp text/data/rodata/bss, donated pool, per-CPU areas, stacks, and host SVE state. `update_nvhe_init_params()` publishes the new PGD to every CPU. `fix_host_ownership()` walks hyp mappings and sets matching host/hyp page states. `fix_hyp_pgtable_refcnt()` fixes allocator refcounts for table pages. `__pkvm_init_finalise()` installs full allocators and subsystems after switching page tables. `__pkvm_init()` validates inputs and invokes the idmapped PGD switch.

## Control Flow, State, and Persistence
Initialization first uses the early allocator on the donated pool, then switches to a proper hyp pool once the vmemmap is backed. `__pkvm_init()` builds all mappings, updates init params, and calls `__pkvm_init_switch_pgd()` by physical address; control resumes in `__pkvm_init_finalise()` on the new stack/page tables. Finalization writes the return value into the saved host context and exits with `__host_enter()`.

## Dependencies and Integration Points
It integrates early allocation, `mm.c` mapping helpers, `page_alloc.c`, host stage-2 setup in `mem_protect.c`, FF-A initialization, VM table setup in `pkvm.c`, per-CPU init params, host SVE data, and optional ownership selftests.

## Risks and Test Signals
Risks include mispartitioning the donated pool, missing mappings for per-CPU/stack/SVE data, wrong ownership conversion for executable hyp text, page-table refcount leaks, and failures after PGD switch that must still return cleanly. Test signals are pKVM initialization under different CPU counts and SVE support, forced allocation failures per partition, ownership selftest success, host stage-2 finalization, and boot-time mapping permission audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/stacktrace.c

## Purpose
`stacktrace.c` prepares nVHE stacktrace information for host-side panic reporting. In non-protected mode it records stack bounds and starting FP/PC; in protected mode with `CONFIG_PKVM_STACKTRACE` it unwinds inside hyp into a shared per-CPU buffer.

## Important APIs, Types, and Functions
`overflow_stack` provides the per-CPU overflow stack used by assembly vectors. `kvm_stacktrace_info` stores non-protected reporting metadata. `hyp_prepare_backtrace()` records normal and overflow stack bases plus FP/PC. With protected stacktrace enabled, `pkvm_stacktrace` is the per-CPU output buffer, `stackinfo_get_overflow()` and `stackinfo_get_hyp()` define unwindable ranges, `pkvm_save_backtrace_entry()` stores PCs with a zero delimiter, and `pkvm_save_backtrace()` runs the nVHE unwinder. `kvm_nvhe_prepare_backtrace()` selects protected or non-protected behavior.

## Control Flow, State, and Persistence
The file writes per-CPU panic-report state only when a panic path calls `kvm_nvhe_prepare_backtrace()`. Protected mode avoids exposing live stack memory by copying PC entries into a bounded buffer. Non-protected mode leaves enough metadata for the host to unwind directly.

## Dependencies and Integration Points
It integrates with `host.S` overflow-stack vectors, `switch.c` panic handling, per-CPU init params, protected mode status, and optional `asm/stacktrace/nvhe.h` unwinding support.

## Risks and Test Signals
Risks include truncated protected traces, bad stack bounds after stack allocation changes, recursion or faults during panic unwinding, and exposing too much stack state outside protected mode. Test signals are induced hyp panic on normal and overflow stacks, protected and non-protected stacktrace dumps, bounded buffer delimiter correctness, and frame-pointer unwind validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/switch.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/switch.c

## Purpose
`switch.c` implements nVHE guest entry/exit. It saves host state, restores guest state, switches stage-2 context, enables traps/timers/VGIC/debug/PMU state, loops through handled guest exits, then restores host state and handles hyp panic cleanup.

## Important APIs, Types, and Functions
Per-CPU `kvm_host_data`, `kvm_hyp_ctxt`, and `kvm_hyp_vector` store host context and selected vectors. `__activate_traps()` and `__deactivate_traps()` program HCR/MDCR/CPTR/VBAR and speculative-AT workaround state. `__hyp_vgic_save_state()` / `__hyp_vgic_restore_state()` handle GICv3/v5 CPU interfaces. `hyp_exit_handlers[]` and `pvm_exit_handlers[]` map ESR exception classes to handlers. `fixup_guest_exit()` enforces protected-VM AArch64-only state and calls common exit fixups. `__kvm_vcpu_run()` is the main guest-run function. `hyp_panic()` restores host context enough to report a panic.

## Control Flow, State, and Persistence
Guest run sets `host_ctxt->__hyp_running_vcpu`, switches PMU counters, saves host sysregs and debug buffers, restores guest sysregs/stage-2/traps/VGIC/timer/debug state, enters the guest via `__guest_enter()`, and repeats while exits are handled in hyp. On final exit it saves guest state, disables traps, reloads host stage-2/sysregs/debug/PMU state, clears the running vCPU, and returns the exit code. Protected VMs use stricter handler tables that handle HVC/sysregs in hyp or inject undefined exceptions.

## Dependencies and Integration Points
It depends on generic hyp switch/sysreg/debug/VGIC/timer helpers, protected sysreg/HVC handlers in `sys_regs.c` and `pkvm.c`, TLB/stage-2 loading, host context assembly, tracing, and stacktrace panic support.

## Risks and Test Signals
Risks include ordering bugs around stage-1/stage-2 switches, failing to restore host debug/SPE/PMU state, pVM exit misclassification, 32-bit protected guest escape, and IRQ priority masking mistakes. Test signals are guest boot and exit storms, protected VM restricted sysreg/HVC handling, PMU/debug/SPE save-restore tests, GICv3/v5 paths, timer trap behavior, panic cleanup while a vCPU is active, and speculative-AT workaround configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sys_regs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sys_regs.c

## Purpose
`sys_regs.c` defines the protected-VM system-register policy. It computes sanitized AArch64 ID-register values, handles allowed RAZ/WI or host-handled sysregs, injects undefined/synchronous exceptions for restricted accesses, and validates that the sysreg descriptor table is sorted.

## Important APIs, Types, and Functions
Global `id_aa64*_*_sys_val` variables hold sanitized host CPU feature values visible to hyp. `struct pvm_ftr_bits` describes feature-field maximums and optional VM-support predicates. `get_restricted_features()` clamps system feature fields to pVM-supported values. `pvm_calc_id_reg()` computes individual ID register values. Accessors include `pvm_access_raz_wi()`, `pvm_access_id_aarch32()`, `pvm_access_id_aarch64()`, `pvm_gic_read_sre()`, and `pvm_idst_access()`. `pvm_sys_reg_descs[]` is the sorted policy table. Public APIs are `kvm_init_pvm_id_regs()`, `kvm_check_pvm_sysreg_table()`, `kvm_handle_pvm_sysreg()`, and `kvm_handle_pvm_restricted()`.

## Control Flow, State, and Persistence
During vCPU initialization, protected VM ID registers are calculated once under `vm_table_lock` and stored in `kvm->arch.id_regs`, then `KVM_ARCH_FLAG_ID_REGS_INITIALIZED` is set. Runtime sysreg exits decode ESR into parameters, binary-search the descriptor table, inject undefined for absent descriptors, return false for host-handled descriptors, and otherwise execute the hyp accessor and optionally skip the guest instruction.

## Dependencies and Integration Points
It depends on KVM sysreg descriptors, ID register field macros, pKVM feature gating, exception injection helpers, VGIC definitions, and protected guest exit dispatch in `switch.c`. It also interacts with `pkvm.c` when initializing protected vCPU features and trap settings.

## Risks and Test Signals
Risks include exposing unsupported CPU features to protected guests, descriptor table ordering errors, wrong signed-field clamping, accidental host handling for sensitive registers, and exception injection while sysregs are live. Test signals are `kvm_check_pvm_sysreg_table()` at init, guest reads of each ID register, writes to ID registers injecting undef, RAZ/WI debug/error registers, GIC SRE reads, IDS-dependent behavior, and fuzzing unlisted sysreg encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sys_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sysreg-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sysreg-sr.c

## Purpose
`sysreg-sr.c` provides the non-VHE save/restore wrappers for CPU system-register state. In nVHE, host and guest both need complete EL1/common/user/return-state save and restore around guest execution.

## Important APIs, Types, and Functions
`__sysreg_save_state_nvhe()` calls `__sysreg_save_el1_state()`, `__sysreg_save_common_state()`, `__sysreg_save_user_state()`, and `__sysreg_save_el2_return_state()`. `__sysreg_restore_state_nvhe()` restores EL1 state using saved MIDR/MPIDR, then common, user, and EL2 return state.

## Control Flow, State, and Persistence
The file has linear save/restore flow and persists state only in the caller-provided `struct kvm_cpu_context`. It is invoked for both host and guest contexts during `__kvm_vcpu_run()`.

## Dependencies and Integration Points
It depends on generic hyp sysreg save/restore primitives and `struct kvm_cpu_context` layout. It integrates directly with `switch.c` guest entry/exit and indirectly with pKVM vCPU synchronization in `hyp-main.c`.

## Risks and Test Signals
Risks include omissions when new sysregs are added to common helpers, MIDR/MPIDR restore assumptions, and ordering issues with stage-2/trap activation. Test signals are guest/host sysreg preservation across exits, migration of vCPUs between CPUs with compatible MIDR handling, and architecture feature additions that expand generic save/restore helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/sysreg-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/timer-sr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/timer-sr.c

## Purpose
`timer-sr.c` manages nVHE timer trap state and virtual counter offset writes. It switches CNTHCTL_EL2 settings between host-friendly and guest-constrained access modes.

## Important APIs, Types, and Functions
`__kvm_timer_set_cntvoff()` writes `cntvoff_el2`. `__timer_disable_traps()` allows host physical timer/counter access. `__timer_enable_traps()` disallows guest physical timer access as required, allows physical counter access for protected mode or no physical offset, handles hVHE bit shifts, and traps virtual timer/counter on broken CNTVOFF implementations.

## Control Flow, State, and Persistence
Timer state is stored in system registers, primarily `cnthctl_el2` and `cntvoff_el2`. Guest entry calls enable traps; guest exit calls disable traps. The hVHE path shifts control bits by 10. Protected mode avoids physical counter offsetting and therefore allows PCT access.

## Dependencies and Integration Points
It depends on arch timer definitions, KVM timer data in `struct kvm`, hVHE detection, protected-mode status, and `switch.c` guest entry/exit plus host hypercall dispatch for CNTVOFF updates.

## Risks and Test Signals
Risks include exposing physical timer/counter access incorrectly, bit-shift mistakes on hVHE, broken CNTVOFF workaround regressions, and offset policy differences for protected VMs. Test signals are timer interrupts in guests, physical counter access trapping expectations, hVHE/nVHE configurations, protected VM timer behavior, and hosts with broken CNTVOFF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/timer-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/tlb.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/tlb.c

## Purpose
`tlb.c` implements nVHE TLB and instruction-cache maintenance for host and guest stage-2 contexts. It temporarily switches VMID/stage-2 context when needed, applies architecture workarounds for speculative address translation, and issues shareable or non-shareable invalidation sequences.

## Important APIs, Types, and Functions
`struct tlb_inv_context` records the previous MMU context and workaround register state. `enter_vmid_context()` switches from host or guest context into the target MMU’s VMID, with required barriers and optional TCR/SCTLR manipulation for `ARM64_WORKAROUND_SPECULATIVE_AT`. `exit_vmid_context()` restores the prior context. Public operations include `__kvm_tlb_flush_vmid_ipa()`, `__kvm_tlb_flush_vmid_ipa_nsh()`, `__kvm_tlb_flush_vmid_range()`, `__kvm_tlb_flush_vmid()`, `__kvm_flush_cpu_context()`, and `__kvm_flush_vm_context()`.

## Control Flow, State, and Persistence
Each targeted flush enters the requested VMID, performs TLBI operations, executes required DSB/ISB synchronization, and restores the previous stage-2. IPA flushes also invalidate stage-1 because only IPA is known. CPU-context flush invalidates local stage-1 and I-cache. VM-context flush invalidates all EL1 inner-shareable TLBs without a VMID switch.

## Dependencies and Integration Points
It depends on `host_mmu` from `mem_protect.c`, `kvm_host_data.__hyp_running_vcpu`, stage-2 load helpers, arm64 TLBI macros, speculative-AT alternatives, and host hypercall wrappers in `hyp-main.c`.

## Risks and Test Signals
Risks include leaving the wrong VMID loaded, insufficient barriers leading to stale complete walks, mishandling guest context when called outside `__kvm_vcpu_run()`, and workaround register restore bugs. Test signals are dirty-log/unmap permission-change correctness, host and guest TLB shootdown stress, nested calls from host vs guest context, non-shareable flush users, and CPUs affected by ARM 1319367/1319537 style workarounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/trace.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/trace.c

## Purpose
`trace.c` implements hyp-side tracing buffer management for nVHE. It loads a host-provided descriptor, admits backing pages into hyp or pins shared pages depending on protected mode, initializes per-CPU simple ring buffers, enables/disables tracing, swaps reader pages, updates the trace clock, and resets buffers.

## Important APIs, Types, and Functions
`trace_buffer` holds per-CPU `simple_rb_per_cpu` state, donated backing pages, and a lock. `tracing_reserve_entry()` and `tracing_commit_entry()` are the hyp event write path. `__tracing_load()` admits the host descriptor, validates it, and calls `hyp_trace_buffer_load()`. `hyp_trace_desc_validate()` bounds-checks descriptor entries, CPU ordering, and backing page counts. `__tracing_unload()`, `__tracing_enable()`, `__tracing_swap_reader()`, `__tracing_update_clock()`, and `__tracing_reset()` expose host hypercall operations.

## Control Flow, State, and Persistence
The trace buffer is globally loaded or unloaded under `trace_buffer.lock`; loaded state is indicated by nonzero backing size. In protected mode, descriptor/backing memory is donated to hyp and per-buffer page VAs are pinned as shared pages; unload reverses these operations after zeroing backing memory. Clock updates wait until all per-CPU buffers are not in `SIMPLE_RB_WRITING`, then update the shared clock bank.

## Dependencies and Integration Points
It depends on `simple_ring_buffer.c`, hyp clock helpers, pKVM memory donation/pinning from `mem_protect.c`, address translation helpers, `hyp_nr_cpus`, tracing hypercalls in `hyp-main.c`, and generated hyp event IDs.

## Risks and Test Signals
Risks include trusting malformed descriptors, CPU/order mismatches, leaked donated backing pages on partial load failure, busy-wait clock updates, tracing while unloaded, and protected/non-protected memory admission differences. Test signals are load/unload success and failure paths, descriptor fuzzing, per-CPU swap/reset, enable without load returning error, trace event write/read integrity, and memory ownership after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/trace.c -->
