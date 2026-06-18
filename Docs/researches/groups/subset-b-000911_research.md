# Research: subset-b-000911

Grouped research for x86 BPF JIT and x86 PCI support files under `sources/distributed-fs/ceph-client`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp.c -->
# sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp.c

## Purpose
Implements the x86-64 eBPF JIT backend, including machine-code emission for BPF instructions, text patching for BPF calls and tail calls, exception-table metadata for fault-tolerant probe/arena accesses, BPF trampoline generation, dispatcher generation, private BPF stacks, and architecture feature declarations. It is a core integration point between the verifier-produced `struct bpf_prog`, x86 text patching, CFI/IBT, retpoline/SLS mitigations, BPF maps, kfunc calls, and fentry/fexit/fmod_ret trampoline execution.

## Important APIs, types, and functions
- `struct jit_context` carries offsets for cleanup and direct/indirect tail-call labels across JIT passes.
- `struct x64_jit_data` persists partially finalized subprogram JIT state across extra passes for BPF subprogram compilation.
- `bpf_int_jit_compile()` is the top-level compiler entry. It allocates address maps, performs convergence passes, allocates executable/RW image packs, fills extable storage, finalizes text, updates instruction pointers, and installs `prog->bpf_func`.
- `do_jit()` is the main BPF-to-x86 translation loop. It emits the prologue, iterates over every BPF instruction, maps BPF opcodes to x86 encodings, populates exception tables, and validates pass stability.
- `emit_prologue()`, `emit_return()`, `push_callee_regs()`, `pop_callee_regs()`, and private-stack helpers define BPF frame layout and ABI preservation.
- `emit_bpf_tail_call_indirect()`, `emit_bpf_tail_call_direct()`, `bpf_tail_call_direct_fixup()`, and `bpf_arch_poke_desc_update()` implement BPF tail-call fast paths and runtime target patching.
- `bpf_arch_text_poke()`, `__bpf_arch_text_poke()`, `bpf_arch_text_copy()`, and `bpf_arch_text_invalidate()` wrap x86 text poking for BPF-generated code.
- `ex_handler_bpf()` is the x86 exception handler for JITed probe memory and arena accesses.
- `arch_prepare_bpf_trampoline()`, `__arch_prepare_bpf_trampoline()`, `arch_bpf_trampoline_size()`, allocation/free helpers, and `invoke_bpf*()` generate BPF trampoline images.
- `arch_prepare_bpf_dispatcher()` emits a binary-search dispatcher for multiple program entry addresses.
- Feature hooks include `bpf_jit_supports_kfunc_call()`, `bpf_jit_supports_subprog_tailcalls()`, `bpf_jit_supports_percpu_insn()`, `bpf_jit_supports_exceptions()`, `bpf_jit_supports_private_stack()`, `bpf_jit_supports_arena()`, `bpf_jit_supports_ptr_xchg()`, `bpf_jit_supports_timed_may_goto()`, and `bpf_jit_supports_fsession()`.

## Control flow
Compilation starts only when `prog->jit_requested` is set. The compiler either resumes stored `aux->jit_data` for an extra subprogram pass or allocates `addrs[]` with an overestimated per-instruction layout. `do_jit()` is run repeatedly until program length converges; late passes enable padding so short/near jump choices stop oscillating. Once length is stable, a packed executable image and RW alias are allocated, with exception-table space appended after aligned code. A final pass copies emitted bytes into the RW image and validates that `addrs[]` did not change. Finalization copies/pokes RW bytes into executable text, applies direct tail-call fixups, fills jited line info, and publishes the function pointer offset by any CFI prefix.

Inside `do_jit()`, the prologue handles CFI/IBT, a patchable call slot, frame setup, stack allocation, tail-call counter layout, optional arena base in `r12`, and optional per-CPU private stack pointer in `r9`. Each BPF instruction emits into a temporary buffer, then its length is accumulated into `addrs[]`. ALU, load/store, atomic, branch, call, tail-call, and exit opcodes are translated directly. Probe and arena accesses populate exception-table records that let `ex_handler_bpf()` skip faulting instructions and zero destination registers. Exit emits one cleanup epilogue; later exits branch to it.

Trampoline generation separately builds a stack frame around traced kernel calls. It saves arguments into a synthetic context, optionally calls fentry/fmod_ret/fexit programs, invokes the original function when requested, restores registers/return values, and emits a return or frame skip. Dispatcher generation sorts function addresses and emits a recursive binary-search tree of compares and direct/indirect jumps.

## State and persistence
Persistent mutable state is mostly stored in `struct bpf_prog` and `prog->aux`: `bpf_func`, `jited`, `jited_len`, `extable`, `poke_tab`, `priv_stack_ptr`, `jit_data`, kallsyms metadata, and instruction pointer arrays. During compilation, `addrs[]`, `ctx`, image pointers, and old program length are pass state. Direct tail-call patch descriptors persist target, bypass, and adjustment addresses for later map updates. Private stacks are per-CPU allocations with guard words checked during free. Text mutation is serialized with `text_mutex`, and runtime tail-call target replacement uses RCU synchronization on removal paths.

## Dependencies and integration points
The file depends on Linux BPF core structures (`struct bpf_prog`, verifier metadata, BPF maps, trampoline links), x86 code patching (`text_poke_*`, `smp_text_poke_single`, `bpf_jit_binary_pack_*`), CFI/IBT helpers, retpoline/call-depth mitigation helpers, ORC unwind support, exception tables, BTF function models, kfunc metadata, per-CPU allocation, and PCI-unrelated generic kernel memory APIs. It exposes architecture hooks consumed by the BPF core and by tracing/trampoline infrastructure.

## Risks and edge cases
Critical risks are incorrect instruction length accounting, non-converging branch-size decisions, out-of-range call/jump offsets, wrong exception-table metadata, incorrect callee-saved register tracking, unsafe text patch state transitions, and stale tail-call patch descriptors. Arena and probe-memory paths are sensitive because faults must skip only the faulting x86 instruction and must clear the right destination register. Private stack guard failures indicate overflow/underflow after JIT execution. Trampoline code is ABI-sensitive, especially for stack arguments, CFI/FineIBT prefixes, call-depth accounting, fmod_ret branch patching, original-call frame skipping, and tail-call context propagation.

## Test signals
Useful validation includes BPF selftests for JITed ALU/branch/load/store/atomic behavior, tail calls, subprogram tail calls, kfunc calls, arena access, probe memory fault recovery, trampolines/fentry/fexit/fmod_ret, dispatcher behavior, private stack execution, timed may-goto support, and CFI/IBT kernel configurations. Kernel logs containing `bpf_jit: fatal`, `cond_jmp gen bug`, `extable is not populated`, `Target call ... out of range`, or private stack guard errors are strong failure signals. Comparing interpreter and JIT results plus enabling `bpf_jit_enable > 1` dumps helps diagnose emitted instruction mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp32.c -->
# sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp32.c

## Purpose
Implements the IA32 x86 eBPF JIT backend. Because 32-bit x86 lacks enough 64-bit general registers, it maps most BPF registers to scratch stack slots and emits paired 32-bit operations for 64-bit BPF semantics. It supports normal calls, kfunc calls, direct memory operations, tail calls, and core ALU/branch operations, but explicitly rejects several newer or complex operations such as BPF-to-BPF pseudo calls, 64-bit div/mod, and atomic RMW instructions.

## Important APIs, types, and functions
- `bpf2ia32` maps each BPF register to two IA32 registers or scratch offsets. `BPF_REG_AX` is backed by `esi:edi`; most other BPF registers live in stack scratch space.
- `emit_ia32_*()` helpers generate 32-bit moves, ALU ops, 64-bit add/sub/carry sequences, byte-order conversion, shifts, multiply, division/modulo, and stack argument pushes.
- `emit_prologue()` and `emit_epilogue()` establish the IA32 BPF frame, save/restore `ebp`, `edi`, `esi`, and `ebx`, reserve `SCRATCH_SIZE`, initialize BPF FP and tail-call count, and return `edx:eax`.
- `emit_bpf_tail_call()` implements the 32-bit tail-call helper path and jumps through `edx` to `prog->bpf_func + PROLOGUE_SIZE`.
- `emit_kfunc_call()` adapts BPF register arguments to the i386 `-mregparm=3` calling convention using `btf_func_model`.
- `do_jit()` translates BPF instructions and validates output length against the convergence pass.
- `bpf_int_jit_compile()` drives up to 20 convergence passes, allocates executable memory with `bpf_jit_binary_alloc()`, locks it read-only, and publishes `prog->bpf_func`.
- `bpf_jit_needs_zext()` returns true, telling the verifier/JIT contract that explicit zero extension is required.

## Control flow
The top-level compile path exits immediately unless JIT is requested. It allocates an `addrs[]` array for every BPF instruction and seeds it with a 64-byte estimate. `do_jit()` first emits the fixed-size prologue, then iterates instruction by instruction, emitting into a temporary buffer and recording cumulative offsets. On stable length, executable memory is allocated and a final pass copies bytes into the image. If the image pass changes length or an unsupported opcode is encountered, compilation falls back by leaving the program not JITed.

Instruction translation is stack-register heavy. BPF 64-bit registers are split into low/high halves. 64-bit arithmetic emits carry/borrow logic over the low/high halves; shifts handle `<32`, `>=32`, and `>=64` cases; loads/stores perform low/high memory transfers for `BPF_DW`; branches compare high halves before low halves for 64-bit semantics. Calls marshal BPF arguments to IA32 ABI registers/stack, call either helper base or kfunc target, and store return values back into BPF R0 scratch slots.

## State and persistence
State is limited compared with x86-64: `addrs[]`, `jit_context.cleanup_addr`, `prog->bpf_func`, `prog->jited`, and `prog->jited_len`. Tail-call count is stored in the JIT scratch stack area as a synthetic BPF register. There is no packed RW/executable alias state, trampoline state, exception-table population, or private stack persistence in this file.

## Dependencies and integration points
The backend depends on BPF core program metadata, BTF kfunc models, i386 calling convention behavior, x86 direct machine-code encoding, retpoline thunk `__x86_indirect_thunk_edx` when configured, and generic BPF JIT allocation/RO locking. It includes x86 mitigation and cacheflush headers but is far less integrated with modern x86-64 CFI/trampoline machinery.

## Risks and edge cases
Main risks are split-register semantic bugs, missing high-half zeroing when verifier zext expectations are wrong, branch offset instability, unsupported opcode fallback, and ABI mistakes in helper/kfunc call marshalling. Tail calls depend on `PROLOGUE_SIZE` staying exactly 35 bytes. Memory operations ignore high address halves because IA32 addresses are 32-bit, which is expected but must align with verifier constraints. Unsupported atomics and 64-bit div/mod should be covered by verifier or fallback behavior.

## Test signals
Run BPF selftests on 32-bit x86 configurations with JIT enabled, especially ALU32/ALU64, zext, endian conversion, shifts around 31/32/63/64, helper calls, kfunc calls, branches, memory loads/stores, and tail calls. Logs with `*** NOT YET: opcode`, `bpf_jit: fatal error`, `unsupported BPF func`, or `cond_jmp gen bug` indicate either verifier/JIT contract drift or encoder defects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/bpf_jit_comp32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/bpf_timed_may_goto.S -->
# sources/distributed-fs/ceph-client/arch/x86/net/bpf_timed_may_goto.S

## Purpose
Provides the x86-64 assembly thunk `arch_bpf_timed_may_goto`, used by the BPF JIT timed may-goto feature. It preserves BPF caller-visible registers, calls the C helper `bpf_check_timed_may_goto()`, and returns the helper result in BPF temporary register `r10`/`BPF_REG_AX`.

## Important APIs, types, and functions
- `SYM_FUNC_START(arch_bpf_timed_may_goto)` defines the exported assembly entry.
- `ANNOTATE_NOENDBR` marks the function as not requiring an ENDBR landing pad.
- `CALL_DEPTH_ACCOUNT` emits x86 call-depth mitigation accounting before the helper call.
- The external integration point is `bpf_check_timed_may_goto`.

## Control flow
The caller passes stack depth in `r10`. The thunk computes a pointer to the count/timestamp storage by adding `r10` to BPF frame pointer `rbp`. It creates a normal frame, saves BPF R0-R5 physical registers (`rax`, `rdi`, `rsi`, `rdx`, `rcx`, `r8`), moves the count/timestamp pointer into `rdi`, performs call-depth accounting, and calls `bpf_check_timed_may_goto`. The return value in `rax` is moved to `r10`, saved registers are restored, and the function returns through the mitigation-aware `RET` macro.

## State and persistence
The only state touched is the caller stack slot referenced through `rbp + stack_depth`, as consumed by `bpf_check_timed_may_goto`. The assembly preserves BPF-visible argument/result registers except for the intended result in `r10`.

## Dependencies and integration points
This file depends on x86-64 mode, Linux linkage macros, export/linkage infrastructure, and x86 nospec branch macros. It is enabled by the x86-64 JIT feature hook `bpf_jit_supports_timed_may_goto()` in `bpf_jit_comp.c`.

## Risks and edge cases
The register-save set must match the JIT ABI. A wrong stack-depth convention would pass the helper an invalid count/timestamp pointer. Missing call-depth accounting or an incorrect return macro could violate x86 mitigation expectations. The thunk is 64-bit only and assumes a BPF frame pointer in `rbp`.

## Test signals
BPF timed may-goto selftests should confirm counter/timestamp updates and register preservation across the helper call. Kernel objtool/linkage checks should validate annotations and return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/net/bpf_timed_may_goto.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/pci/Makefile

## Purpose
Defines the x86 PCI support object composition for the kernel build. It selects core PCI initialization/resource files and conditionally includes BIOS, MMCONFIG, direct config access, platform quirks, and x86 platform-specific PCI backends.

## Important build rules
- Always builds `i386.o`, `init.o`, `fixup.o`, `legacy.o`, `irq.o`, `common.o`, `early.o`, and `bus_numa.o`.
- Adds `pcbios.o` for `CONFIG_PCI_BIOS`.
- Adds `mmconfig_$(BITS).o`, `direct.o`, and `mmconfig-shared.o` for `CONFIG_PCI_MMCONFIG`.
- Adds `direct.o` for `CONFIG_PCI_DIRECT`; this can overlap with MMCONFIG selection.
- Adds `olpc.o`, `xen.o`, `acpi.o`, `ce4100.o`, `intel_mid.o`, `numachip.o`, `amd_bus.o`, and `broadcom_bus.o` based on platform/config symbols.
- Adds `-DDEBUG` when `CONFIG_PCI_DEBUG` is enabled.

## Control flow and integration
This file has no runtime control flow. Its build-time decisions determine which PCI probing and access methods can register at boot. For this subset, it wires `acpi.c`, `amd_bus.c`, `broadcom_bus.c`, `bus_numa.c`, `ce4100.c`, `common.c`, `direct.c`, and `early.c` into the arch PCI subsystem.

## State and persistence
No runtime state is stored here. Build configuration determines which object files become part of the kernel image.

## Dependencies and integration points
Depends on Kbuild `obj-y`/`obj-*` semantics and config symbols under PCI, ACPI, x86 platform, Xen, OLPC, AMD NB, and Broadcom CNB20LE quirk options.

## Risks and test signals
Duplicate inclusion of `direct.o` is controlled by Kbuild object de-duplication, but config changes should be checked for unexpected missing config access backends. Build tests across `CONFIG_PCI_MMCONFIG`, `CONFIG_PCI_DIRECT`, `CONFIG_ACPI`, 32-bit/64-bit, and platform options are the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/acpi.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/acpi.c

## Purpose
Integrates ACPI PCI root discovery with x86 PCI bus scanning, IRQ routing, NUMA node selection, host bridge resource windows, and MMCFG/ECAM setup. It decides whether to trust ACPI `_CRS`, whether to clip host bridge windows with E820 reservations, and how to treat removable/tunneled PCIe devices behind Thunderbolt/USB4 paths.

## Important APIs, types, and functions
- Local `struct pci_root_info` wraps `struct acpi_pci_root_info`, `struct pci_sysdata`, and optional MMCFG tracking fields.
- Global policy flags are `pci_use_e820`, `pci_use_crs`, and `pci_ignore_seg`.
- `pci_acpi_crs_quirks()` applies BIOS-year heuristics, DMI quirks, and `pci=` command-line overrides for `_CRS` and E820 clipping policy.
- `arch_pci_dev_is_removable()` classifies external/tunneled PCIe devices using root-port external-facing state, USB4 host-interface properties, and known Intel Thunderbolt root-port IDs.
- `setup_mcfg_map()` and `teardown_mcfg_map()` insert/delete ACPI root ECAM ranges when `CONFIG_PCI_MMCONFIG` is enabled.
- `pci_acpi_root_get_node()` resolves NUMA node from ACPI `_PXM`, with fallback to hardware-probed `x86_pci_root_bus_node()`.
- `pci_acpi_root_prepare_resources()` gathers ACPI root resources, filters config-space IO ports, or falls back to hardware-probed/default resources when `_CRS` is ignored.
- `pci_acpi_scan_root()` creates or updates root buses via `acpi_pci_root_create()`.
- `pcibios_root_bridge_prepare()` attaches ACPI companions to root bridges.
- `pci_acpi_init()` installs ACPI IRQ routing callbacks.

## Control flow
Early ACPI PCI setup first calls `pci_acpi_crs_quirks()` to set policy. Root scan enters `pci_acpi_scan_root()`, which handles ignored segments, rejects unsupported multiple domains, reuses an existing bus or allocates `pci_root_info`, and delegates bus creation to ACPI PCI root ops. Root ops call `setup_mcfg_map()` during init, `pci_acpi_root_prepare_resources()` before bus creation, and `teardown_mcfg_map()` on release. After scanning, child PCIe buses are configured. IRQ init later binds `pcibios_enable_irq`/`pcibios_disable_irq` to ACPI routing and optionally routes all existing devices for `pci=routeirq`.

## State and persistence
The file maintains global policy flags and per-root `pci_root_info` allocations owned by ACPI root lifecycle callbacks. MMCFG ranges inserted for an ACPI root are tracked by `mcfg_added`, `start_bus`, and `end_bus` so teardown can delete only ranges this root added. Bus `sysdata` persists domain, node, and ACPI companion pointers.

## Dependencies and integration points
Depends on ACPI PCI root APIs, DMI matching, x86 NUMA helpers, `bus_numa.c` fallback resources, MMCONFIG insertion/deletion, PCI core resource lists, firmware node properties, PCIe topology helpers, and ACPI IRQ routing. It integrates with `common.c` through `pci_root_ops`, global `pci_probe` command-line flags, `pci_routeirq`, and `pcibios_*` hooks.

## Risks and edge cases
Firmware defects dominate the risk surface: bad `_CRS`, bogus E820 reservations, missing `_PXM`, broken `_SEG`, and incomplete USB4 host-interface properties. Incorrect `_CRS` policy can either hide usable windows or allocate into reserved host-bridge space. MMCFG failures are tolerated for segment zero but fatal for nonzero segments because extended config access may be impossible. Removable-device classification has topology exceptions for discrete Thunderbolt/USB4 controllers directly under external-facing root ports.

## Test signals
Boot logs should show whether ACPI host bridge windows and E820 reservations are used or ignored. Validate root bus domains/nodes/resources, ECAM access, Thunderbolt/USB4 hotplug classification, ACPI IRQ routing, and `pci=use_crs`, `pci=nocrs`, `pci=use_e820`, `pci=no_e820`, and DMI quirk behavior. Regressions often appear as missing devices, failed BAR assignment, broken hotplug, or no extended config space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/amd_bus.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/amd_bus.c

## Purpose
Provides native early PCI host bridge resource and NUMA topology probing for older AMD/Hygon systems, plus enables extended CF8 config-space access on AMD family 10h and newer CPUs. It fills the shared `pci_root_infos` list for fallback use when ACPI is absent, incomplete, or ignored.

## Important APIs, types, and functions
- `struct amd_hostbridge` and `hb_probes[]` identify legacy AMD northbridge devices supported by the maintenance-mode probe.
- `early_root_info_init()` reads AMD northbridge bus-range, IO, MMIO, TOM/TOM2, and MMCONFIG registers, allocates `pci_root_info` entries, and populates root resources.
- `find_pci_root_info()` locates an existing root by AMD node/link.
- `cap_resource()` clamps 64-bit hardware ranges to `resource_size_t`.
- `amd_bus_cpu_online()` enables `ENABLE_CF8_EXT_CFG` in `MSR_AMD64_NB_CFG` for each online CPU.
- `pci_enable_pci_io_ecs()` enables extended CF8 config through PCI northbridge function registers when possible.
- `pci_io_ecs_init()` installs the CPU hotplug callback and marks `PCI_HAS_IO_ECS`.
- `amd_postcore_init()` gates everything to AMD/Hygon vendors and runs as a `postcore_initcall`.

## Control flow
At postcore init, non-AMD/Hygon systems return immediately. `early_root_info_init()` first checks `early_pci_allowed()`, scans known host bridge locations, creates bus-range records from function 1 config-map registers, and on older families extracts IO/MMIO aperture routing. It subtracts RAM and MMCONFIG holes from candidate ranges, adds explicit bridge windows, assigns leftovers to the default node/link, and logs the resulting resources. Then `pci_io_ecs_init()` enables extended config access through PCI/MSR paths and registers a CPU hotplug state to keep ECS enabled on secondary CPUs.

## State and persistence
The main persistent state is the global `pci_root_infos` list allocated by `alloc_pci_root_info()` and appended with `update_res()`. CPU MSR state is changed to enable extended CF8 config. `pci_probe` is updated with `PCI_HAS_IO_ECS` when ECS is available.

## Dependencies and integration points
Depends on early CF8 config helpers from `early.c`, AMD northbridge helpers (`amd_get_mmconfig_range`, `amd_nb_bus_dev_ranges`, `early_is_amd_nb`), CPU hotplug, topology/resource range helpers, and `bus_numa.c` resource list APIs. ACPI code may use the populated node/resource information as fallback when firmware data is missing or disabled.

## Risks and edge cases
This code intentionally supports only older families through Fam15h_00h-0fh for topology and through Fam11h for native resource extraction. Firmware/ACPI should be authoritative on newer systems. Range subtraction around TOM/TOM2 and MMCONFIG must avoid exposing RAM or ECAM as PCI MMIO. MSR writes must be applied on all CPUs. Early config access can be disabled by `pci=noearly`.

## Test signals
Boot old AMD/Hygon systems with and without ACPI `_CRS`; inspect `PCI: root bus` resources, node/link logs, TOM/TOM2 messages, and availability of extended config space. CPU hotplug should leave ECS enabled. Resource assignment failures or devices on the wrong NUMA node suggest incorrect bridge register interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/amd_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/broadcom_bus.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/broadcom_bus.c

## Purpose
Extracts host bridge bus and resource windows from Broadcom/ServerWorks CNB20LE bridges when ACPI is unavailable. It populates `pci_root_infos` so generic x86 PCI root scanning can use hardware-derived resources.

## Important APIs and functions
- `cnb20le_res()` reads bus range and IO/memory windows for one CNB20LE bridge function and records them in a `pci_root_info`.
- `broadcom_postcore_init()` detects the ServerWorks LE host bridge on bus 0 slot 0 and runs the two-function resource probe.

## Control flow
At postcore init, the code exits if ACPI is enabled and has a root pointer because ACPI should provide host bridge information. Otherwise it reads vendor/device ID from bus 0 slot 0 function 0. On ServerWorks LE, it calls `cnb20le_res()` for functions 0 and 1. Each call reads first/last bus numbers, creates a root info entry, adds legacy IDE IO ranges for bus 0, reads non-prefetchable memory, prefetchable memory, and IO windows from bridge registers, and logs the resulting windows.

## State and persistence
Persistent state is added to the shared `pci_root_infos` list. No teardown path is implemented because these early host bridge records live for the boot lifetime.

## Dependencies and integration points
Depends on early direct PCI reads, DMI/ACPI availability checks, ServerWorks PCI IDs, and `bus_numa.c` allocation/resource helpers. `common.c` or `acpi.c` later consumes the recorded resources through `x86_pci_root_bus_resources()`.

## Risks and edge cases
The code is a hardware quirk for old systems and uses hard-coded assumptions, including undocumented legacy IDE ports and two bridge functions. It deliberately avoids running when ACPI is present. Incorrect register values can create bad root windows, but this only affects the narrow CNB20LE fallback path.

## Test signals
On affected systems without ACPI, boot logs should show CNB20LE host bridge ranges and PCI devices should receive correct IO/MMIO resources. On ACPI systems, this file should be silent and inactive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/broadcom_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.c

## Purpose
Maintains a shared list of hardware-probed PCI root bus descriptors, including bus ranges, NUMA node/link identifiers, and root resources. It is used by AMD and Broadcom native probes and consumed by ACPI/common root scanning as fallback topology/resource information.

## Important APIs and functions
- `LIST_HEAD(pci_root_infos)` is the global root-info registry.
- `x86_pci_root_bus_node()` returns a NUMA node for a root bus or `NUMA_NO_NODE`.
- `x86_pci_root_bus_resources()` appends hardware-probed resources for a root bus, or defaults to global `ioport_resource` and `iomem_resource`.
- `alloc_pci_root_info()` allocates and initializes a root descriptor.
- `update_res()` adds or merges a root resource.

## Control flow
Native probes allocate entries with a bus range and later add IO/MMIO resources. Root scan code asks for the node and resource list by root bus number. If an entry exists, `x86_pci_root_bus_resources()` ensures an `IORESOURCE_BUS` window is present and appends each recorded resource. If no entry exists, it falls back to legacy global IO and memory resources.

## State and persistence
All state lives in the boot-lifetime `pci_root_infos` linked list. Each `pci_root_info` owns a linked list of dynamically allocated `pci_root_res` records. `update_res()` can merge adjacent/overlapping resources with identical flags.

## Dependencies and integration points
Depends on Linux resource/list APIs and the local `bus_numa.h` structures. Integrated with `amd_bus.c`, `broadcom_bus.c`, `acpi.c`, and `common.c`.

## Risks and edge cases
The lookup matches `info->busn.start == bus`, so overlapping or non-start bus queries will not match. Resource merging uses inclusive ranges and must avoid overflow around `common_end + 1`. The fallback to entire IO/memory resources is broad but preserves historical behavior when no native bridge data exists.

## Test signals
Boot logs should distinguish `hardware-probed resources` from `using default resources`. Validate that native bridge probes create one root entry per root bus and that resources are not duplicated when ACPI has already supplied a bus resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.h -->
# sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.h

## Purpose
Declares the shared data structures and helper prototypes used for x86 native PCI root bus NUMA/resource discovery.

## Important APIs and types
- `struct pci_root_res` wraps a `struct resource` in a linked-list node.
- `struct pci_root_info` stores list linkage, a short name, resource list, bus-number resource, NUMA node, and AMD link ID.
- `pci_root_infos` is the external global list.
- `alloc_pci_root_info()` allocates a root descriptor.
- `update_res()` adds or merges resources into a descriptor.

## Control flow, state, and dependencies
This header has no executable control flow. It defines the contract between resource producers (`amd_bus.c`, `broadcom_bus.c`) and consumers (`bus_numa.c`, ACPI/common scan paths). State is owned by the implementation file and dynamically allocated records.

## Risks and test signals
The fixed `name[12]` fits names like `PCI Bus #ff`; callers should not write longer names. The comment notes transparent subordinate buses need enough resource entries from root resources. Compile coverage across users is the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/ce4100.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/ce4100.c

## Purpose
Provides custom PCI config-space access for Intel CE4100 hardware whose PCI registers misbehave. It simulates selected bus 1 device registers, special-cases the bus 0 bridge, and delegates all other config accesses to normal type-1 direct access.

## Important APIs, types, and functions
- `struct sim_reg` stores simulated value/mask pairs.
- `struct sim_dev_reg` describes one simulated config register, with optional init/read/write callbacks.
- `bus1_fixups[]` lists per-device/function/register simulations for BARs, revision/class ID, interrupt pin masking, EHCI quirks, and SATA-derived BAR behavior.
- `init_sim_regs()` initializes simulated values from hardware or constants.
- `bridge_read()` fabricates bridge config fields such as bus numbers, memory base/limit, and disabled IO/prefetch windows.
- `ce4100_bus1_read()` and `ce4100_bus1_write()` handle simulated bus 1 accesses under `pci_config_lock`.
- `ce4100_conf_read()` and `ce4100_conf_write()` are `struct pci_raw_ops` callbacks.
- `ce4100_pci_init()` installs the CE4100 raw PCI ops and requests legacy init.

## Control flow
Platform init calls `ce4100_pci_init()`, which initializes simulated register table entries and assigns `raw_pci_ops`. Reads first check bus 1 fixups, then bus 0 bridge special cases, then fall back to `pci_direct_conf1`. Writes update simulated registers when a writable fixup exists, discard writes to the A/V bridge BAR, and otherwise fall back to direct type-1 writes.

## State and persistence
The static `bus1_fixups[]` table stores mutable simulated register values for the boot lifetime. Updates are serialized with `pci_config_lock`. The global `raw_pci_ops` pointer is replaced with CE4100-specific callbacks.

## Dependencies and integration points
Depends on CE4100 platform selection, generic x86 PCI raw ops, `pci_direct_conf1`, and the shared `pci_config_lock` from `common.c`. It integrates with the generic PCI subsystem through `raw_pci_ops`.

## Risks and edge cases
The simulated masks define which bits software can change; wrong masks can break BAR sizing or resource assignment. Byte extraction must match PCI config access size and offset. Since register callbacks assume `pci_config_lock` is held, any bypass would be unsafe. The implementation warns on nonzero PCI segments because CE4100 expects segment 0 only.

## Test signals
On CE4100, PCI enumeration should see stable BAR sizes/classes and avoid bogus bridge resources. Validate config reads/writes on bus 1, bridge window calculation, interrupt pin masking, and fallback direct access. Unexpected writes to bridge BARs should not alter hardware state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/ce4100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/common.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/common.c

## Purpose
Provides common x86 PCI glue: global probing flags, raw config access dispatch, root bus ops, config-space locking, DMI boot quirks, command-line `pci=` parsing, root scanning without ACPI, cacheline setup, resource fixups, MSI domain initialization, device enable/disable hooks, and VMD DMA-device resolution.

## Important APIs, variables, and functions
- Globals include `pci_probe`, `pci_routeirq`, `noioapicquirk`, `noioapicreroute`, `pcibios_last_bus`, `pirq_table_addr`, `raw_pci_ops`, `raw_pci_ext_ops`, and `pci_config_lock`.
- `raw_pci_read()` and `raw_pci_write()` dispatch to base or extended raw config ops.
- `pci_root_ops` exposes PCI core config access callbacks.
- `dmi_check_skip_isa_align()` and `dmi_check_pciprobe()` apply DMI quirks for ISA alignment skipping, breadth-first sorting, bus renumbering, and scanning all PCIe devices.
- `pcibios_fixup_bus()` reads bridge bases and applies BAR/ROM assignment policy.
- `pcibios_scan_root()` creates a non-ACPI root bus using `x86_pci_root_bus_node()` and `x86_pci_root_bus_resources()`.
- `pcibios_set_cache_line_size()` sets default PCI cacheline size from CPU data.
- `pcibios_init()` surveys resources and optionally sorts devices breadth-first.
- `pcibios_setup()` parses many `pci=` options and updates global flags.
- `pcibios_device_add()` attaches setup ROM info and initializes MSI domain.
- `pcibios_enable_device()`, `pcibios_disable_device()`, `pcibios_release_device()`, `pci_ext_cfg_avail()`, and `pci_real_dma_dev()` provide arch hooks.

## Control flow
Raw config requests from the PCI core enter `pci_root_ops`, which call `raw_pci_read/write()`. During boot, DMI checks and command-line parsing shape `pci_probe`. PCI root scanning either occurs through ACPI or `pcibios_scan_root()`, which allocates `pci_sysdata`, retrieves fallback resources, scans the bus, and adds devices. `pcibios_init()` runs after raw config backends are selected and performs cacheline/resource setup. Device add/enable hooks run during enumeration and driver binding.

## State and persistence
Most state is global and boot-lifetime: probe bitmasks, raw ops pointers, IRQ policy flags, last bus, PIRQ table address, and config lock. Per-root `pci_sysdata` allocations persist with root buses. Device-specific ROM metadata and MSI domain pointers are stored on `struct pci_dev`/device objects.

## Dependencies and integration points
Depends on the PCI core, ACPI PCI bus hooks, DMI, setup_data boot parameters, x86 IRQ domains, VMD helpers, raw backends from `direct.c`, MMCONFIG/BIOS backends, and resource survey code from other x86 PCI files. It is the central junction for many files in this directory.

## Risks and edge cases
Command-line flags can disable or force probing modes, so interactions between BIOS, direct, MMCONFIG, ACPI, ROM/BAR assignment, and IRQ routing must remain coherent. Raw config dispatch only uses `raw_pci_ops` for domain 0 and registers below 256; extended/nonzero-domain access requires `raw_pci_ext_ops`. Setup ROM scanning maps boot memory and must unmap every record. MSI domain selection must preserve special domains such as VMD.

## Test signals
Boot matrix testing with `pci=off`, `conf1`, `conf2`, `nommconf`, `assign-busses`, `routeirq`, `nobar`, `norom`, CRS/E820 flags, and DMI-quirked systems is useful. Check root resources, cacheline size logs, raw config availability, MSI domain assignment, ROM setup data attachment, and device enable/disable IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/direct.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/direct.c

## Purpose
Implements x86 direct PCI configuration-space access through legacy type 1 and type 2 IO port mechanisms. It probes whether those mechanisms work and installs raw PCI ops for base and sometimes extended config access.

## Important APIs and functions
- `pci_direct_conf1` provides type-1 `read`/`write` callbacks using ports `0xCF8`/`0xCFC`.
- `pci_direct_conf2` provides type-2 callbacks using `0xCF8`, `0xCFA`, and `0xC000`-based device windows.
- `pci_sanity_check()` verifies a candidate raw op by scanning bus 0 for plausible host bridge/VGA/vendor IDs, unless checks are disabled or BIOS year is new enough.
- `pci_check_type1()` and `pci_check_type2()` test hardware behavior while interrupts are disabled.
- `pci_direct_init()` installs a forced type and optionally enables type-1 extended access when `PCI_HAS_IO_ECS` is set.
- `pci_direct_probe()` requests IO regions, probes type 1 then type 2, sets `raw_pci_ops`, and marks `port_cf9_safe`.

## Control flow
The normal probe path tries type 1 first if allowed by `pci_probe`, reserves `0xCF8-0xCFF`, validates CF8 behavior and sanity, and installs `pci_direct_conf1` on success. If type 1 fails, it releases resources and tries type 2 by reserving `0xCF8-0xCFB` plus `0xC000-0xCFFF`. Read/write callbacks validate segment/bus/devfn/register limits, take `pci_config_lock`, program address ports, perform size-specific IO, and release the lock.

## State and persistence
The file updates global `raw_pci_ops`, optionally `raw_pci_ext_ops`, and `port_cf9_safe`. IO port reservations persist after a successful probe. Config operations are serialized through the global raw spinlock.

## Dependencies and integration points
Depends on x86 IO port accessors, DMI BIOS year, global `pci_probe` flags from `common.c`, `pci_config_lock`, and PCI core raw ops. `ce4100.c` delegates fallback operations to `pci_direct_conf1`; `amd_bus.c` can enable type-1 extended config.

## Risks and edge cases
Direct IO config is legacy and platform-sensitive. Type 1 only supports segment 0 in this path and uses extended register bits up to 4095; type 2 is limited to the first 256 config bytes and devices below slot 16. Incorrect sanity results can hide PCI or use a broken mechanism. IO region reservation failures correctly block use.

## Test signals
Boot logs should state selected configuration type. Validate config reads/writes before and after MMCONFIG availability, forced `pci=conf1/conf2`, old BIOS sanity-check behavior, and graceful failure when IO regions are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/early.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/early.c

## Purpose
Provides minimal early-boot direct PCI config access helpers using type-1 CF8/CFC IO ports before the full PCI subsystem and locking/probing infrastructure are available.

## Important APIs and functions
- `read_pci_config()`, `read_pci_config_byte()`, and `read_pci_config_16()` read 32/8/16-bit config values.
- `write_pci_config()`, `write_pci_config_byte()`, and `write_pci_config_16()` write 32/8/16-bit config values.
- `early_pci_allowed()` reports whether early type-1 access is allowed by `pci_probe` flags.

## Control flow
Each read/write composes a type-1 config address from bus, slot, function, and offset, writes it to `0xcf8`, then performs the requested IO operation at `0xcfc` plus byte/word offset. `early_pci_allowed()` requires `PCI_PROBE_CONF1` and absence of `PCI_PROBE_NOEARLY`.

## State and persistence
No state is stored locally. The functions directly touch hardware IO ports and observe global `pci_probe` policy.

## Dependencies and integration points
Depends on x86 IO accessors and `pci_probe` from `common.c`. Used by early native bridge probes such as `amd_bus.c` and `broadcom_bus.c`, and by AMD ECS enabling before normal PCI enumeration is fully established.

## Risks and edge cases
There is no locking in these early helpers, so callers must use them only during safe early boot phases. They assume type-1 config access and segment 0. Incorrect use after `pci=noearly` or on systems without CF8/CFC support can produce invalid hardware accesses.

## Test signals
Early bridge resource probes should disappear when `pci=noearly` is used and should work on systems where type-1 access is valid. Failures surface as missing hardware-probed root resources or inability to enable AMD ECS early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/early.c -->
