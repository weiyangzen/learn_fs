# Research Group subset-b-009399

This grouped report covers syzkaller executor KVM helpers for SYZOS guest payloads and architecture-specific virtual CPU setup. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_amd64_syzos.h -->
# sources/test-tools/syzkaller/executor/common_kvm_amd64_syzos.h

## Purpose

`common_kvm_amd64_syzos.h` implements the x86-64 SYZOS guest runtime that runs inside a KVM VM. It decodes fuzzer-authored guest commands, executes raw instruction blobs, performs privileged x86 operations, installs simple interrupt handlers, and exposes a nested-virtualization test surface for both Intel VMX and AMD SVM. The file is intentionally self-contained so syzkaller can embed it into executor and csource reproducers.

## Important APIs, Types, and Functions

The `syzos_api_id` enum defines the guest command ABI and must match `sys/linux/dev_kvm_amd64.txt`. Command payloads include `api_call_uexit`, `api_call_code`, `api_call_cpuid`, `api_call_nested_load_code`, and `api_call_nested_load_syzos`. `guest_main()` is the top-level command dispatcher. Basic handlers include `guest_uexit`, `guest_execute_code`, `guest_handle_cpuid`, `guest_handle_wrmsr`, `guest_handle_rdmsr`, `guest_handle_wr_crn`, `guest_handle_wr_drn`, `guest_handle_in_dx`, `guest_handle_out_dx`, and `guest_handle_set_irq_handler`.

Nested state is described by `l2_guest_regs`, `mem_region`, `syzos_boot_args`, and `syzos_globals`. VMX helpers include `nested_enable_vmx_intel`, `nested_vmptrld`, `vmread`, `vmwrite`, `init_vmcs_control_fields`, `init_vmcs_host_state`, `init_vmcs_guest_state`, `nested_create_vm_intel`, and `guest_handle_nested_vmentry_intel`. SVM helpers include `nested_enable_svm_amd`, VMCB read/write helpers, `init_vmcb_guest_state`, `nested_create_vm_amd`, and `guest_run_amd_vm`. Cross-vendor nested handlers normalize exits through `map_intel_exit_reason`, `map_amd_exit_reason`, `guest_uexit_l2`, `nested_vm_exit_handler_intel`, and `nested_vm_exit_handler_amd`.

## Control Flow

`guest_main(cpu)` reads per-vCPU text size from `X86_SYZOS_ADDR_GLOBALS`, walks the command stream at `X86_SYZOS_ADDR_USER_CODE + cpu * KVM_PAGE_SIZE`, validates each command size and API id, and dispatches through an if/else chain instead of a switch to avoid compiler-emitted jump tables. Normal completion calls `guest_uexit(UEXIT_END)`; malformed command streams call `UEXIT_INVALID_MAIN`.

Basic command handlers execute inline assembly directly: CPUID, MSR reads/writes, CR/DR writes, I/O port reads/writes, raw code calls, and IDT entry replacement. Nested setup first enables VMX or SVM according to `get_cpu_vendor()`, then creates a per-CPU/per-L2-VM control block, page table root, and code/stack backing. `setup_l2_page_tables()` mirrors the L1 boot memory layout into EPT/NPT mappings while leaving `NO_HOST_MEM` regions unmapped so L2 writes to the uexit page become nested page faults.

Intel vmentry loads the active VMCS, records `active_vm_id`, updates `VMCS_HOST_RSP`, restores persisted L2 GPRs from `syzos_globals`, and executes `vmlaunch` or `vmresume`. The VM-exit assembly shim saves L2 registers, reads `VMCS_VM_EXIT_REASON`, calls `nested_vm_exit_handler_intel`, unwinds back to the L1 command loop, and reports VM-entry failures through a synthetic uexit. AMD vmentry similarly prepares host stack context, syncs RAX into the VMCB, executes `vmrun`, saves VMCB/GPR state on return, calls `nested_vm_exit_handler_amd`, restores L1 state, and re-enables GIF with `stgi`.

Nested exit handlers persist L2 registers, detect EPT/NPT faults on `X86_SYZOS_ADDR_EXIT`, map those into nested uexit codes by incrementing the high-byte nesting level, and otherwise report normalized HLT, INVD, CPUID, RDTSC, RDTSCP, and page-fault exits. Vendor-specific mutator APIs let the fuzzer mask-write VMCS fields or VMCB offsets, inject AMD events, edit AMD intercept fields, and run SVM `invlpga`, `stgi`, `clgi`, `vmload`, and `vmsave`.

## State and Persistence Behavior

State is stored in guest physical memory, not process globals. `syzos_globals` at `X86_SYZOS_ADDR_GLOBALS` persists per-vCPU text sizes, a non-reclaiming bump allocator over the unused-memory region, L2 register snapshots indexed by `[cpu][vm_id]`, and the active nested VM id per CPU. VMCS/VMCB pages, per-VM code buffers, stacks, MSR bitmaps, architecture-specific VMXON/HSAVE pages, and nested page tables are all addressed by macros from `kvm.h`. The allocator lazily initializes its total size from boot args and uses atomic fetch-add, so allocations persist for the lifetime of the guest and are never freed.

## Dependencies and Integration Points

The header depends on `common_kvm_syzos.h` for `GUEST_CODE`, no-inline attributes, and shared API-call structs, and on `kvm.h` for x86 SYZOS addresses, selectors, VMCS/VMCB constants, EPT/NPT bits, MSR ids, and limits such as `KVM_MAX_VCPU` and `KVM_MAX_L2_VMS`. The host-side x86 KVM setup must map the guest code section, boot args, globals, IDT/GDT/TSS, uexit page, user code, nested VM buffers, and unused heap at the exact addresses expected here. The command ids are coupled to syzkaller descriptions in `dev_kvm_amd64.txt`.

## Risks and Edge Cases

This file is intentionally executing privileged instructions and corruptible guest-provided data, so most failures are expected to manifest as KVM exits, uexits, or guest faults. The command ABI is fragile: changing enum values breaks existing reproducers. Jump tables, global data references, or compiler-generated helper calls are dangerous because SYZOS guest code is copied without normal relocations. Nested virtualization is especially sensitive to stack layout comments matching the assembly save/restore order, VMCS/VMCB offset correctness, and vendor detection. `guest_handle_nested_load_syzos()` seeds L2 globals for all vCPUs but reuses the L1 `globals->l2_ctx` storage for register defaults, so index and VM id bounds rely on the surrounding syscall descriptions. Mask writes to arbitrary VMCS/VMCB fields can create invalid control state by design, but wrapper failures should still produce deterministic uexit codes rather than corrupting L1 execution.

## Test Signals

Useful signals include executor/csource builds for amd64 with both GCC and Clang, style tests that catch forbidden switch/jump-table forms, and KVM smoke programs that exercise each command id. Runtime tests should cover CPUID/MSR/CR/DR/I/O exits, IDT handler installation, `UEXIT_INVALID_MAIN` on malformed command sizes, Intel VMX enable/create/load/vmlaunch/vmresume, AMD SVM enable/create/load/vmrun, nested uexit propagation from L2, normalized exit reason reporting, VM-entry failure reporting, VMCB/VMCS mask mutation, AMD intercept/event injection, and allocator exhaustion in the unused-memory region.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_amd64_syzos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_arm64.h -->
# sources/test-tools/syzkaller/executor/common_kvm_arm64.h

## Purpose

`common_kvm_arm64.h` is the host-side ARM64 implementation of syzkaller KVM pseudo-syscalls. It maps the guest physical layout expected by ARM64 SYZOS, installs the guest runtime into KVM memory, initializes vCPU registers, loads per-vCPU user programs, creates additional SYZOS vCPUs, sets up a VGICv3 device, and exposes assertion helpers for uexit and register values.

## Important APIs, Types, and Functions

`kvm_text` and `kvm_opt` are the user command descriptors. Memory setup is handled by `addr_size`, `alloc_guest_mem`, `vm_set_user_memory_region`, `validate_guest_code`, `install_syzos_code`, and `setup_vm`. vCPU setup uses `vcpu_set_reg`, `reset_cpu_regs`, `install_user_code`, and `setup_cpu_with_opts`. Public pseudo-syscall entry points are `syz_kvm_setup_cpu`, `syz_kvm_setup_syzos_vm`, `syz_kvm_add_vcpu`, `syz_kvm_vgic_v3_setup`, `syz_kvm_assert_syzos_uexit`, and `syz_kvm_assert_reg`.

## Control Flow

`syz_kvm_setup_cpu()` reads the first `kvm_text`, maps the whole SYZOS VM layout with `setup_vm()`, initializes the vCPU target with optional feature bits, copies the user code into CPU 0's user page, and sets PC/SP/TPIDR_EL1/X0/X1 for `guest_main`. `syz_kvm_setup_syzos_vm()` stores a small `kvm_syz_vm` control block in the first host page, maps the rest as guest memory, and returns that control block to the fuzzer. `syz_kvm_add_vcpu()` creates the next KVM vCPU, applies the same CPU init, installs that CPU's code page, increments `next_cpu_id` only after successful creation, and returns the vCPU fd.

`setup_vm()` uses a simple bump allocator over `KVM_GUEST_MEM_SIZE`, maps the executor guest code read-only at `SYZOS_ADDR_EXECUTOR_CODE`, dirty-log pages at `ARM64_ADDR_DIRTY_PAGES`, per-vCPU user code read-only at `ARM64_ADDR_USER_CODE`, stack and scratch pages, ITS tables, and finally any remaining pages at GPA 0. VGIC setup creates `KVM_DEV_TYPE_ARM_VGIC_V3`, configures IRQ count, distributor address, redistributor region, and initializes the device. Assertions validate MMIO uexit shape and expected code or read one KVM one-reg value.

## State and Persistence Behavior

Host-visible state is the `kvm_syz_vm` record containing `vmfd`, `next_cpu_id`, and the host pointer for the user-text slot. Guest memory contents persist in the caller-provided `host_mem` backing area after registration with KVM. `setup_vm()` is destructive with respect to the supplied memory because it copies SYZOS code and later user code into fixed offsets. There is no filesystem persistence and no dynamic allocation beyond slicing the provided mapping.

## Dependencies and Integration Points

The header includes `common_kvm.h`, `kvm.h`, Linux KVM ioctls, and conditionally `common_kvm_arm64_syzos.h` so host setup can reference `__start_guest`, `__stop_guest`, `guest_main`, and `executor_fn_guest_addr`. It depends on ARM64 constants in `kvm.h` for GIC, dirty page, scratch, stack, user-code, ITS, and SYZOS code addresses. The pseudo-syscall signatures are coupled to syzkaller `dev_kvm_arm64.txt` descriptions.

## Risks and Edge Cases

`validate_guest_code()` rejects ADRP instructions because the SYZOS copy path does not process relocations; this catches global-data and jump-table regressions early. Most `ioctl()` calls in memory setup ignore return values, so failures can surface later as guest failures rather than immediate pseudo-syscall errors. `setup_cpu_with_opts()` accepts at most one option and only uses type 1 as ARM feature bits. User text count is ignored and only element 0 is consumed. `gicv3_enable_redist()` in the guest-side companion uses redistributor addresses that must stay consistent with this host mapping. The returned `kvm_syz_vm` lives inside the same host memory area used for guest backing, so the first page is reserved by convention.

## Test Signals

Build coverage should include executor and csource modes with each guarded pseudo-syscall enabled. Runtime signals are successful KVM memory registration, ADRP rejection for deliberately bad guest code, `syz_kvm_setup_cpu` booting one vCPU to `guest_main`, `syz_kvm_setup_syzos_vm` plus repeated `syz_kvm_add_vcpu` up to `KVM_MAX_VCPU`, VGICv3 creation and initialization, dirty-page logging on the dirty region, register assertions through `KVM_GET_ONE_REG`, and uexit assertion failures for wrong MMIO address or code.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_arm64_syzos.h -->
# sources/test-tools/syzkaller/executor/common_kvm_arm64_syzos.h

## Purpose

`common_kvm_arm64_syzos.h` implements the ARM64 SYZOS guest runtime. It decodes guest command streams, executes raw AArch64 instruction blobs, dynamically emits MRS/MSR instructions, invokes SMC/HVC/SVC calls, writes guest memory, configures GICv3 interrupts and vector handling, and programs a virtual ITS/LPI setup for interrupt fuzzing from inside the guest.

## Important APIs, Types, and Functions

The command ABI is `syzos_api_id`, with payload structs `api_call_uexit`, `api_call_code`, `api_call_smccc`, `api_call_irq_setup`, `api_call_memwrite`, and `api_call_its_send_cmd`. `guest_main(size, cpu)` dispatches to `guest_uexit`, `guest_execute_code`, `guest_handle_mrs`, `guest_handle_msr`, `guest_handle_smc`, `guest_handle_hvc`, `guest_handle_svc`, `guest_handle_eret`, `guest_handle_irq_setup`, `guest_handle_memwrite`, `guest_handle_its_setup`, and `guest_handle_its_send_cmd`.

Low-level helpers include `flush_cache_range`, `reg_to_msr`, `reg_to_mrs`, `get_cpu_id`, raw MMIO `readl`/`writel`/`readq`/`writeq`, `guest_udelay`, and RWP polling helpers. Interrupt setup uses `gicv3_dist_init`, `gicv3_enable_redist`, `gicv3_cpu_init`, `gicv3_irq_enable`, `one_irq_handler`, `guest_irq_handler`, and `guest_vector_table`. ITS support is built around `its_cmd_block`, `its_send_cmd`, table installers, command encoders, `guest_setup_its_mappings`, `gic_rdist_enable_lpis`, `configure_lpis`, and `guest_prepare_its`.

## Control Flow

`guest_main(size, cpu)` starts at `ARM64_ADDR_USER_CODE + cpu * 0x1000`, validates command bounds, dispatches by API id, advances by `cmd->size`, and emits `UEXIT_END` when the stream is exhausted. `guest_execute_code()` flushes D-cache and I-cache over the supplied instruction range before branching to it. MRS/MSR handlers synthesize one privileged instruction plus `RET` into per-CPU scratch cache lines at `ARM64_ADDR_SCRATCH_CODE`, flush that scratch code, and branch through it with x0 used for the operand/result convention.

SMC, HVC, and SVC handlers load x0-x5 from the command and execute immediate `#0`, clobbering the normal SMCCC scratch registers. IRQ setup initializes distributor and redistributors, enables SPI lines, installs `guest_vector_table` into `VBAR_EL1`, and clears interrupt masks. The assembly IRQ entry saves general registers plus ELR/SPSR into `ex_regs`, calls `guest_irq_handler`, restores state, and returns with `eret`; the C handler acknowledges IAR0/IAR1, emits `UEXIT_IRQ`, writes EOIR, and deactivates via DIR.

ITS setup configures GITS_BASER tables, command queue, redistributor LPI property/pending tables, and initial MAPC/MAPD/MAPTI mappings. Later `guest_handle_its_send_cmd()` deliberately uses volatile if-chains instead of a switch, encodes the requested ITS command, and writes it to the command queue by advancing GITS_CWRITER.

## State and Persistence Behavior

The runtime stores no normal C globals because the guest section is copied without relocation handling. Persistent state lives in guest physical memory: user code pages, per-CPU scratch code, GIC/ITS MMIO registers, ITS command/table memory, LPI property and pending tables, and host-observed uexit MMIO. Per-CPU identity comes from `TPIDR_EL1`, set by host setup. Interrupt vector code and handlers are compiled into the guest section and installed by address at runtime.

## Dependencies and Integration Points

The header depends on `common_kvm_syzos.h` and `kvm.h` for guest-section attributes, shared command structs, `executor_fn_guest_addr`, address layout, GIC/ITS constants, and bit macros. It integrates with `common_kvm_arm64.h`, which maps the GIC, redistributor, user-code, scratch, stack, dirty-page, executor-code, and ITS-table regions. API ids must stay synchronized with `sys/linux/dev_kvm_arm64.txt`.

## Risks and Edge Cases

The code carefully avoids jump tables, global constants, and relocations; compiler changes that emit ADRP, literal pools, vectorized stores, or helper calls can break copied SYZOS code. Cache maintenance is mandatory for generated code. MMIO polling uses assertion uexits to avoid infinite hangs, but many setup writes assume the host mapped matching devices. `guest_handle_irq_setup()` bounds SPI count but trusts CPU count. ITS command encoders depend on precise bit positions and table sizing, and `SYZOS_NUM_IDBITS` fixes the property table to 64K. Memory write commands can target arbitrary guest physical addresses by design.

## Test Signals

Good coverage includes building the guest section with ADRP validation, executing raw code blobs after cache flush, generated MRS/MSR access to safe registers, SMC/HVC/SVC exits, `ERET` behavior, bounded malformed command streams, VGICv3 setup followed by injected IRQ and `UEXIT_IRQ`, MMIO writes of 1/2/4/8 bytes, ITS setup with MAPD/MAPC/MAPTI mappings, each supported ITS command path, and assertion behavior when RWP polling never clears.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_arm64_syzos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_ppc64.h -->
# sources/test-tools/syzkaller/executor/common_kvm_ppc64.h

## Purpose

`common_kvm_ppc64.h` implements the PowerPC64 KVM CPU setup pseudo-syscall for syzkaller. It maps the guest memory pages, configures Book3S exception vectors, optionally builds radix MMU page tables, sets CPU register state and endian/user-mode flags, enables hypercall and RTAS coverage, and installs the fuzzer-provided guest instruction blob.

## Important APIs, Types, and Functions

The file defines Book3S interrupt offsets, PPC bit and mask helpers, radix table sizing constants, endian conversion helpers, LPCR/PATB/PRTB constants, fallback KVM capability/ioctl definitions, and setup flags `KVM_SETUP_PPC64_LE`, `KVM_SETUP_PPC64_IR`, `KVM_SETUP_PPC64_DR`, `KVM_SETUP_PPC64_PR`, and `KVM_SETUP_PPC64_PID1`. Helper APIs are `kvmppc_define_rtas_kernel_token`, `kvmppc_get_one_reg`, `kvmppc_set_one_reg`, `kvm_vcpu_enable_cap`, `kvm_vm_enable_cap`, and debug-only `dump_text`. The public entry point is `syz_kvm_setup_cpu()`.

## Control Flow

`syz_kvm_setup_cpu()` reads one `kvm_text`, enables PAPR on the vCPU and nested HV on the VM, maps 24 64K pages with `KVM_SET_USER_MEMORY_REGION`, fetches sregs/regs, and initializes MSR bits for 64-bit mode, optional little endian, problem state, instruction/data relocation, and PID. It fetches KVM's debug instruction opcode and writes it into nearly all exception vectors so unexpected guest exceptions exit reliably; the decrementer vector gets a small recharge sequence from `kvm_ppc64le.S.h` followed by the debug instruction.

If instruction or data relocation is requested, the function builds a radix process table plus PGD/PUD/PMD/PTE pages in guest memory, maps all 24 pages read/write/execute, configures `KVM_PPC_CONFIGURE_V3_MMU`, and sets LPCR radix/process-table bits. It then copies the fuzzer text at the next free guest physical offset, appends a debug instruction sentinel, optionally byte-swaps code and decrementer handler for big-endian execution, writes sregs/regs/LPCR/PID, enables broad hypercall ranges and four KVM-handled RTAS tokens, sets the decrementer expiry, and returns.

## State and Persistence Behavior

All guest-visible state is written into the caller-provided `host_mem`: memory slots, exception vectors, optional radix tables, process table, payload text, and debug sentinel. CPU state persists in KVM vCPU registers, special registers, LPCR, PID, guest debug configuration, enabled capabilities, hypercall bits, RTAS token definitions, and decrementer expiry. The function has no heap allocation and no state outside KVM and the supplied memory.

## Dependencies and Integration Points

The header includes `kvm_ppc64le.S.h` for the decrementer recharge code and relies on Linux KVM PPC structs/constants from the broader executor include environment. It is shared between executor and csource generation and is coupled to the `syz_kvm_setup_cpu` signature in syzkaller's PowerPC KVM descriptions. The guest memory size and page count match `vma[24]` from `dev_kvm.txt`.

## Risks and Edge Cases

The code assumes 64K guest pages and only maps 24 pages. Text size is not clamped before `memcpy`, so syscall descriptions must bound the provided text to available guest memory. Many capability and ioctl calls fail on unsupported hosts, especially nested HV and radix MMU configuration. Big-endian conversion only covers the loaded payload words and decrementer blob. PR mode forcibly enables IR/DR and PID1 because hardware requires translations. Exception-vector debug exits are a mitigation for KVM HV loops but can hide which exact exception happened unless debug output is enabled.

## Test Signals

Signals include successful compilation on ppc64le, `syz_kvm_setup_cpu` returning 0 on hosts with PAPR/nested HV support, expected failure on missing capabilities, execution with LE and BE flags, IR/DR radix page-table boot, PR-mode setup, debug breakpoint exits from unexpected vectors, decrementer recharge behavior, enabled hypercall coverage, RTAS token definitions, and byte-swapped payload inspection under `DEBUG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_ppc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_riscv64.h -->
# sources/test-tools/syzkaller/executor/common_kvm_riscv64.h

## Purpose

`common_kvm_riscv64.h` is the host-side RISC-V 64-bit KVM setup layer for syzkaller. It provides the legacy `syz_kvm_setup_cpu` path for one vCPU, the SYZOS VM/multi-vCPU path, guest memory registration, register initialization, assertion helpers, and guest code validation/installation for RISC-V SYZOS.

## Important APIs, Types, and Functions

The file defines KVM register id helpers `RISCV_CORE_REG` and `RISCV_CSR_REG`, enum indices for KVM core and CSR registers, SSTATUS bits, `kvm_set_reg`, and `kvm_text`. Legacy setup is implemented by `syz_kvm_setup_cpu()`. SYZOS VM setup uses `kvm_syz_vm`, `addr_size`, `alloc_guest_mem`, `vm_set_user_memory_region`, `validate_guest_code`, `install_syzos_code`, `mem_region`, `syzos_mem_regions`, `setup_vm`, `syz_kvm_setup_syzos_vm`, `reset_cpu_regs`, `install_user_code`, and `syz_kvm_add_vcpu`. `syz_kvm_assert_reg` and `syz_kvm_assert_syzos_uexit` provide validation pseudo-syscalls.

## Control Flow

The legacy `syz_kvm_setup_cpu()` maps 24 pages at `RISCV64_ADDR_USER_CODE`, copies the user text into the first page, installs `guest_unexp_trap` into the next page as STVEC target, and initializes PC, SP, S-mode, SSTATUS, STVEC, and GP. The SYZOS path stores a `kvm_syz_vm` header in the first host page, uses the rest as guest backing memory, iterates `syzos_mem_regions`, skips MMIO/no-host-memory ranges, allocates backing for mapped ranges, copies exception-vector code or SYZOS executor code where needed, records the user-code host slot, and maps any remaining backing at GPA 0.

`syz_kvm_add_vcpu()` validates the VM pointer and CPU limit, creates a KVM vCPU with the next id, increments only on success, installs one page of user code into that CPU's slot, and calls `reset_cpu_regs()`. `reset_cpu_regs()` points PC at `guest_main` inside the executor code, sets stack and TP, passes text size and CPU id in A0/A1, enters S-mode, sets SSTATUS, GP, and STVEC to the exception vector page. Assertions read KVM one-reg values or validate MMIO uexit shape and code.

## State and Persistence Behavior

`kvm_syz_vm` persists in host memory and tracks `vmfd`, `next_cpu_id`, backing memory pointer, total page count, and the host address of the per-vCPU user-code region. Guest memory persists in the caller's mapping once registered with KVM. The code uses a bump allocator during setup only; no runtime host allocation is performed. vCPU state persists in KVM registers and CSRs.

## Dependencies and Integration Points

The header includes `common_kvm.h`, `kvm.h`, Linux ioctl definitions, and conditionally `common_kvm_riscv64_syzos.h` for guest symbols. Address constants for CLINT, PLIC, exit, dirty pages, user code, executor code, scratch, stacks, and exception vectors must match `kvm.h` and syzkaller syscall descriptions. The command ABI is coupled to `dev_kvm_riscv64.txt`.

## Risks and Edge Cases

`validate_guest_code()` rejects AUIPC instructions because copied SYZOS code cannot use data relocations; this protects against globals, constants, and jump-table emission. Several `KVM_SET_USER_MEMORY_REGION` calls ignore ioctl errors. Legacy setup copies `guest_unexp_trap` based on guest-section symbol distance and clamps by page size. SYZOS setup reserves the first host page for `kvm_syz_vm`, so total guest backing is `KVM_GUEST_PAGES - 1`. The user text is truncated to one page per vCPU. Register ids and CSR indices must match the kernel KVM RISC-V ABI.

## Test Signals

Coverage should include executor/csource builds, AUIPC rejection for relocated guest code, legacy one-vCPU boot to S-mode, STVEC unexpected-trap SBI exit, SYZOS VM setup with all mapped regions, multi-vCPU creation up to `KVM_MAX_VCPU`, per-vCPU user-code isolation, dirty-log region behavior, register assertions, and uexit assertions for both wrong MMIO metadata and wrong exit code.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_riscv64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_riscv64_syzos.h -->
# sources/test-tools/syzkaller/executor/common_kvm_riscv64_syzos.h

## Purpose

`common_kvm_riscv64_syzos.h` implements the RISC-V 64-bit SYZOS guest runtime. It decodes command streams, executes raw instruction blobs, dynamically emits CSR read/write instructions, performs guest memory reads/writes with fences, reports host-observable uexits through MMIO, and provides an unexpected-trap SBI call target for the host-side setup.

## Important APIs, Types, and Functions

The command ABI is `syzos_api_id` with `SYZOS_API_UEXIT`, `SYZOS_API_CODE`, `SYZOS_API_CSRR`, `SYZOS_API_CSRW`, and `SYZOS_API_MEMOP`. `api_call_code` carries inline instructions; generic `api_call_1`, `api_call_2`, and `api_call_5` come from `common_kvm_syzos.h`. Main functions are `guest_main`, `guest_uexit`, `guest_execute_code`, `get_cpu_id`, `guest_handle_csrr`, `guest_handle_csrw`, `guest_handle_memop`, `sbi_ecall`, and `guest_unexp_trap`. CSR instruction generation uses `ENCODE_CSR_INSN` with RISC-V SYSTEM opcode fields.

## Control Flow

`guest_main(size, cpu)` walks the per-vCPU command stream at `RISCV64_ADDR_USER_CODE + cpu * 0x1000`, validates command size and stop id, then uses volatile if/else dispatch to avoid jump-table generation. Code commands run `fence.i` and branch to the supplied instruction buffer. CSR read/write commands write a two-instruction sequence into a per-CPU cache-line slot at `RISCV64_ADDR_SCRATCH_CODE`, execute `fence.i`, and call it with `jalr`; CSR reads place the result in A0 and CSR writes pass the requested value in A0.

Memory operations compute `base + offset`, issue `fence rw,rw`, perform volatile 1/2/4/8-byte loads or stores, fence again, and return read results through the `sscratch` CSR. `guest_uexit()` writes the exit code to `RISCV64_ADDR_UEXIT`, causing the host to observe an MMIO exit. `guest_unexp_trap()` is an aligned trap target that invokes a custom KVM SBI extension/function for unexpected traps.

## State and Persistence Behavior

The runtime avoids normal globals. Persistent effects are guest memory writes, scratch-code writes, CSR changes, `sscratch` read results, and MMIO uexit writes. CPU id is read from `tp`, which the host initializes. The unexpected-trap path communicates through an SBI ecall rather than local state.

## Dependencies and Integration Points

The header depends on `common_kvm_syzos.h` for guest-section attributes and shared API structs, and `kvm.h` for RISC-V guest addresses. It integrates with `common_kvm_riscv64.h`, which maps user code, scratch code, exception vectors, and sets PC/SP/TP/SSTATUS/STVEC/GP. API ids must match `sys/linux/dev_kvm_riscv64.txt`.

## Risks and Edge Cases

The no-relocation constraint makes compiler-emitted globals and jump tables hazardous; this file uses if/else chains and generated scratch instructions to reduce that risk. `guest_handle_memop()` treats any op other than 1 as a read and any length other than 1/2/4 as 8 bytes. CSR ids and target addresses are fuzzer-controlled, so illegal instruction and access faults are expected coverage paths. Scratch-code slots assume `MAX_CACHE_LINE_SIZE` separation is enough for all vCPUs. Read results in `sscratch` require host or follow-up guest code to inspect the CSR.

## Test Signals

Signals include build checks for the guest section, command streams ending in `UEXIT_END`, malformed command bounds returning without overrun, raw code execution after `fence.i`, CSR read/write to safe CSRs, illegal CSR fault behavior through `guest_unexp_trap`, memory read/write widths with `sscratch` result verification, per-vCPU scratch separation, and host assertion of uexit MMIO codes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_riscv64_syzos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_syzos.h -->
# sources/test-tools/syzkaller/executor/common_kvm_syzos.h

## Purpose

`common_kvm_syzos.h` provides shared definitions for SYZOS guest runtimes across architectures. It centralizes compiler attributes for copied guest code and defines common command payload headers used by architecture-specific KVM command decoders.

## Important APIs, Types, and Functions

The file defines `noinline`, `always_inline`, `__no_stack_protector`, `__addrspace_guest`, `__optnone`, and `GUEST_CODE`. `GUEST_CODE` places functions in the `guest` section and disables stack protector behavior so the host can copy a contiguous guest-code section into guest memory. It declares `__start_guest` and `__stop_guest` section boundaries. Shared command structs are `api_call_header`, `api_call_1`, `api_call_2`, `api_call_3`, and `api_call_5`.

## Control Flow

There is no runtime control flow in this header. Its macros influence how functions in `common_kvm_*_syzos.h` compile, where they are linked, and whether they are safe to copy into the guest. Architecture-specific `guest_main()` implementations consume the shared `api_call_header` and fixed-width argument structs while walking command streams.

## State and Persistence Behavior

No mutable state is defined here. The only declared state is linker-provided guest-section start/end symbols. The struct layouts are part of the persistent ABI between syzkaller-generated command streams, host pseudo-syscalls, and in-guest decoders.

## Dependencies and Integration Points

This header assumes syzkaller executor typedefs such as `uint64` are available from the including environment. It is included by the AMD64, ARM64, and RISC-V SYZOS headers and indirectly by host-side KVM setup files that need guest section symbols. Compiler-specific branches support Clang address-space annotations and GCC fallback stack-protector disabling.

## Risks and Edge Cases

If `GUEST_CODE` does not place all required functions into one copyable section, host setup will omit code. If stack protector instrumentation is emitted, guest code may reference unavailable globals. GCC versions before 11 use an optimize-attribute fallback for stack-protector disabling. Struct layout changes or argument-count mismatches break all architecture command ABIs. `__addrspace_guest` is active only under Clang, so compiler differences must be covered by builds.

## Test Signals

Primary signals are successful guest-section link symbols, no stack-protector references in generated guest code, architecture guest headers compiling under supported GCC and Clang versions, stable `api_call_*` struct sizes, and host-side copy/install code seeing a nonzero `__stop_guest - __start_guest` range.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_syzos.h -->
