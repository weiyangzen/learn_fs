# subset-b-000690 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic.c

Purpose: implements the central ARM64 KVM virtual GIC interrupt lifecycle: IRQ lookup, LPI reference management, pending/active state updates, AP-list queueing, physical IRQ mapping, LR population/folding, hardware state load/save, pending IRQ discovery, and mapped level IRQ resampling.

Important APIs/types/functions: global `kvm_vgic_global_state`, `vgic_get_irq`, `vgic_get_vcpu_irq`, `vgic_put_irq`, `vgic_flush_pending_lpis`, `vgic_target_oracle`, `vgic_queue_irq_unlock`, `kvm_vgic_inject_irq`, physical mapping helpers, `vgic_prune_ap_list`, `vgic_flush_lr_state`, `kvm_vgic_sync_hwstate`, `kvm_vgic_flush_hwstate`, `kvm_vgic_load`, `kvm_vgic_put`, `kvm_vgic_vcpu_pending_irq`, and `vgic_irq_handle_resampling`.

Control flow: callers resolve private IRQs from a vCPU, SPIs from the distributor array, and LPIs from the distributor xarray with refcount protection. Injection lazily initializes VGIC state, validates owner and edge/level semantics, updates `line_level` or `pending_latch`, then queues through `vgic_queue_irq_unlock`. Queueing computes a target with `vgic_target_oracle`, drops and reacquires locks in AP-list order, retries if pending state or affinity changed, takes an IRQ reference, inserts on the target AP list, and kicks either the target vCPU or all vCPUs for broadcast TDIR cases. Guest entry prunes/sorts AP lists, populates LRs, clears unused LRs, configures v2/v3 HCR maintenance bits, restores CPU interface state, and commits direct IRQ state when supported. Guest exit saves hardware state, folds LR state back into software, and prunes interrupts that no longer need service.

State and persistence: state is in-memory per VM/vCPU/IRQ. LPIs have refcounts and delayed release via `pending_release` because AP-list removal may happen under locks that cannot free immediately. `irq->vcpu`, AP-list membership, `active`, `pending_latch`, `line_level`, `hw`, `host_irq`, `hwintid`, and `owner` are protected by documented raw spinlock ordering. `active_spis` tracks whether deactivation trapping must be broadcast. No disk persistence is performed.

Dependencies/integration: integrates with KVM run-loop requests (`KVM_REQ_IRQ_PENDING`, nested hyp IRQ requests), GICv2/v3/v5 backends, ITS/LPI xarrays, IRQ chip state APIs, GICv4 direct injection hooks, nested virtualization VGIC hooks, KVM lazy VGIC initialization, tracing, and architecture static keys/capabilities.

Risks: deadlock avoidance depends on the exact lock hierarchy and retry protocol after dropping `irq_lock`. LPI refcount misuse can release an IRQ still on an AP list. LR overflow handling is subtle because pending, active, SGI, LPI, EOImode, and direct-injection behavior interact. Physical mapped level IRQ resampling must clear host active state at the right time or lose future edges. GICv5 currently rejects non-private IRQ lookup.

Test signals: concurrent injection with affinity changes, LPI deletion while queued, AP-list migration across vCPUs, LR overflow with mixed pending/active interrupts, edge reinjection while already queued, mapped level resampling after EOI, owner mismatch, direct-injection enable/disable, nested VGIC paths, and v2/v3/v5 model selection on load/put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic.h

Purpose: provides the private VGIC interface shared by KVM ARM64 VGIC implementation files. It defines register encodings, ITS table layouts, helper predicates, VMCR/AP-list structures, v2/v3/v4/v5/nested prototypes, and direct interrupt capability helpers.

Important APIs/types/functions: affinity and userspace CPU-reg macros, `kvm_get_guest_vtr_el2`, ITS CTE/ITE/DTE/L1E masks, `vgic_vmcr`, `vgic_reg_attr`, ITS device/collection/ITE structures, `ap_list_summary`, `irq_is_pending`, `vgic_irq_get_lr_count`, `vgic_write_guest_lock`, `vgic_ich_hcr_trap_bits`, `vgic_try_get_irq_ref`, `vgic_v3_max_apr_idx`, redistributor region helpers, `kvm_has_gicv3`, `kvm_has_gicv5`, and `vgic_supports_direct_irqs`.

Control flow: implementation files call the inline helpers to normalize GIC state: VMCR is the backend-neutral CPU interface representation, pending state derives from edge latch or level line, SGI LR count reflects source bits plus active state, and VTR_EL2 is masked to expose only supported guest-visible fields. The prototype set routes operations to v2, v3, v4, v5, ITS, nested, and debug code.

State and persistence: this header owns no storage except type layout contracts. It encodes transient KVM VGIC state carried in `struct vgic_irq`, `struct vgic_dist`, `struct vgic_cpu`, and ITS lists. `vgic_write_guest_lock` toggles `table_write_in_progress` around guest-memory writes so ITS table persistence into guest RAM is observable to related code.

Dependencies/integration: depends on Linux IRQ/GIC common definitions, KVM MMU definitions, KVM device ABI encodings, ARM system register encodings, ITS userspace documentation contracts, and `kvm_vgic_global_state`.

Risks: ABI bit masks and shifts must stay synchronized with KVM device documentation and userspace save/restore tooling. Helper predicates such as `irq_is_pending` and `vgic_irq_get_lr_count` directly affect LR packing and interrupt visibility. Direct IRQ capability checks combine host and guest model state, so a wrong predicate can expose unsupported acceleration.

Test signals: compile coverage for all VGIC models/configs, userspace register attr encode/decode round trips, ITS table serialization/deserialization, pending-state helpers for edge/level SGI/LPI cases, redistributor overlap/size checks, and direct IRQ capability decisions on GICv3, GICv4.1, and GICv5 hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vmid.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vmid.c

Purpose: implements KVM VMID allocation for ARM64 stage-2 address spaces, based on the kernel ASID rollover algorithm but tuned for less frequent VMID exhaustion.

Important APIs/types/functions: `kvm_arm_vmid_bits`, `vmid_generation`, `vmid_map`, per-CPU `active_vmids` and `reserved_vmids`, `flush_context`, `check_update_reserved_vmid`, `new_vmid`, `kvm_arm_vmid_clear_active`, `kvm_arm_vmid_update`, `kvm_arm_vmid_alloc_init`, and `kvm_arm_vmid_alloc_free`.

Control flow: `kvm_arm_vmid_update` fast-paths when the VMID already matches the current generation and the current CPU has a nonzero active VMID slot. Otherwise it takes `cpu_vmid_lock`, allocates or refreshes a VMID, and installs it into this CPU's active slot. `new_vmid` first tries to preserve a still-reserved old VMID in the new generation, then reuses the old index if free, then scans for a free index. Exhaustion increments the generation, rebuilds the bitmap from active/reserved VMIDs, and broadcasts `__kvm_flush_vm_context` through hyp code.

State and persistence: allocation state is process-local kernel memory: a generation counter, bitmap, and per-CPU active/reserved slots. VMID zero is reserved, and `VMID_ACTIVE_INVALID` marks schedule-out state so rollover does not preserve VMIDs needlessly. No disk persistence exists.

Dependencies/integration: depends on KVM hyp calls, ARM64 VMID width discovery through `kvm_get_vmid_bits`, per-CPU atomics, raw spinlocks, and the vCPU scheduling path that calls clear/update around guest execution.

Risks: rollover correctness relies on atomic ordering between per-CPU active slots and the global lock. VMID space must exceed possible CPUs; otherwise post-rollover allocation can fail. Broadcast TLB plus I-cache invalidation is heavier than ASID's deferred per-CPU flush but avoids stale stage-2 translations across VMs.

Test signals: VMID reuse without rollover, rollover with active and scheduled-out VMs, concurrent update while generation changes, VMID zero never allocated, warnings when VMID count is too small, and hyp flush invocation on exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vmid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/Makefile

Purpose: selects the ARM64 architecture library objects that provide low-level memory, string, checksum, delay, instruction encoding, MTE, KASAN tag, uaccess flushcache, and error-injection helpers.

Important APIs/types/functions: `lib-y` always includes clear/copy/user-copy/page-copy/checksum/instruction/string/tishift objects. Conditional object lines add `uaccess_flushcache.o`, `error-inject.o`, `mte.o`, and `kasan_sw_tags.o` based on kernel configuration.

Control flow: Kbuild consumes this Makefile during ARM64 library build and links these objects into the architecture library. Conditional symbols gate code that depends on persistent-memory cache flush support, function error injection, ARM64 MTE, and software-tag KASAN.

State and persistence: no runtime state. The file controls build-time object presence and therefore which exported symbols are available.

Dependencies/integration: integrates with top-level ARM64 Kbuild and configuration symbols `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE`, `CONFIG_FUNCTION_ERROR_INJECTION`, `CONFIG_ARM64_MTE`, and `CONFIG_KASAN_SW_TAGS`.

Risks: missing an object breaks exported symbol resolution for core kernel code; enabling an object without matching CPU/toolchain/config support can fail build or runtime alternatives. Order is conventional but objects must match source filenames.

Test signals: all relevant `allyesconfig`/`allnoconfig` ARM64 builds, symbol export checks for copy/string routines, and config matrix coverage for MTE, KASAN SW tags, and uaccess flushcache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/clear_page.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/clear_page.S

Purpose: provides the page-aligned `clear_page` primitive for zeroing a full kernel page.

Important APIs/types/functions: `__pi_clear_page`, alias `clear_page`, MOPS alternatives, DC ZVA fallback, and store-pair fallback.

Control flow: when assembler and CPU MOPS support are available, the routine uses `setpn/setmn/seten` over `PAGE_SIZE`. Without MOPS it reads `dczid_el0`; if DC ZVA is permitted it zeros one ZVA block at a time until the page boundary, otherwise it writes 64 bytes per loop with paired zero stores.

State and persistence: mutates only the destination page contents. It has no persistent state and assumes the caller provides a page-aligned page-sized destination.

Dependencies/integration: exported to core MM and page allocation code; depends on alternative patching, assembler helpers, `PAGE_SIZE`, and CPU DC ZVA/MOPS feature reporting.

Risks: incorrect ZVA size handling or non-page-aligned inputs can overrun or leave data uncleared. MOPS alternatives must patch correctly for CPUs without FEAT_MOPS. Cache and memory ordering are left to callers.

Test signals: boot/page allocator tests, zero-page verification across page sizes, CPU feature matrix with and without MOPS and DC ZVA, and KASAN/KMSAN checks for full-page initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/clear_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/clear_user.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/clear_user.S

Purpose: implements `__arch_clear_user`, clearing a user memory range and returning the number of bytes not cleared on fault.

Important APIs/types/functions: `__arch_clear_user`, `USER` exception annotations, MOPS `setpt/setmt/setet`, unprivileged `sttr/sttrh/sttrb` stores, and fixup labels that compute residual byte count.

Control flow: computes `end = addr + size`. With MOPS it attempts tagged user clear operations and returns zero on success. The fallback stores eight-byte chunks, then handles 4/2/1 byte tails. Exception fixups translate the faulting pointer and Option A MOPS residual state into the required "bytes not cleared" return value.

State and persistence: writes zeroes to user memory only for successfully accessed bytes. No kernel persistent state changes.

Dependencies/integration: used by uaccess clear paths; depends on `asm-uaccess.h` exception table macros, TTBR0/user access setup by callers, and ARM64 MOPS alternatives.

Risks: residual byte accounting must be exact for partial faults. User access annotations must match actual faulting instructions or `fixup_exception` will not recover. Arithmetic assumes no caller-provided wraparound range is allowed past uaccess validation.

Test signals: clear valid ranges of all small sizes, page-boundary partial faults, inaccessible first byte returning full size, MOPS and non-MOPS CPU paths, and fault injection through usercopy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/clear_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_from_user.S

Purpose: implements `__arch_copy_from_user`, copying bytes from a user pointer into kernel memory and returning bytes not copied.

Important APIs/types/functions: `__arch_copy_from_user`, load/store wrapper macros, `USER_CPY` MOPS copy operations, included `copy_template.S`, and exception fixups `9996/9997/9998`.

Control flow: sets `end` and original source, then instantiates the common copy template with user loads and kernel stores. MOPS uses forward/main/end copy instructions when available. On success it returns zero. On faults it adjusts the destination pointer using MOPS residual state or copy-template fault labels, tries a single-byte load/store if no progress was made, then returns `end - dst`.

State and persistence: writes only copied bytes into kernel destination. No persistent state. Fault paths may leave a partially copied destination, consistent with raw usercopy semantics.

Dependencies/integration: used by raw copy-from-user machinery; depends on `asm-uaccess.h`, exception-table `EX_TYPE_UACCESS_CPY`, `copy_template.S`, cache-line alignment constants, and ARM64 MOPS alternatives.

Risks: user fault direction metadata must identify a read-side uaccess fault, otherwise kernel destination faults could be incorrectly fixed up. The final one-byte retry affects exact residual behavior. Overlap is not a supported contract for usercopy.

Test signals: full copy, zero-length copy, faults at first/middle/last byte, destination unchanged after first-byte fault, MOPS and generic paths, and hardened usercopy/KASAN interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_page.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_page.S

Purpose: provides `copy_page`, copying one page from a page-aligned source to a page-aligned destination.

Important APIs/types/functions: `__pi_copy_page`, alias `copy_page`, MOPS `cpypwn/cpymwn/cpyewn`, and the 128-byte pipelined ldp/stnp fallback.

Control flow: the MOPS path copies exactly `PAGE_SIZE` bytes. The fallback preloads 128 bytes, advances source/destination, then loops storing the previous cache-line-sized block while loading the next until the page boundary, finishing with the final preloaded block.

State and persistence: mutates only the destination page contents. No persistent state.

Dependencies/integration: exported to core MM page copy paths; depends on `PAGE_SIZE`, alternatives, CPU MOPS support, and normal cacheable kernel mappings.

Risks: assumes source and destination are page aligned and non-overlapping. Any loop-boundary error corrupts pages. Non-temporal stores (`stnp`) may have microarchitectural performance sensitivity.

Test signals: page-copy selftests, migration/COW page copy validation, multiple page sizes, MOPS vs non-MOPS paths, and KASAN checks for exact page bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_template.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_template.S

Purpose: common ARM64 copy template included by usercopy routines, parameterized by macros for user/kernel load/store behavior and optional MOPS copy.

Important APIs/types/functions: register aliases `dstin`, `src`, `count`, `dst`, temporary registers, macro calls `ldrb1/ldrh1/ldr1/ldp1/strb1/strh1/str1/stp1/cpy1`, MOPS alternative block, small/tail/large-copy labels, and `.Lexitfunc`.

Control flow: starts with `dst = dstin`, optionally uses MOPS, aligns source to 16 bytes, copies leading bytes in increasing address order, handles sub-64 byte tails, and uses a 64-byte software-pipelined loop for large ranges. The template deliberately avoids the older backward-tail technique so `memmove`-like overlap behavior remains simpler for its instantiations.

State and persistence: no standalone symbol. It mutates registers and writes through whichever store macros the including file provides.

Dependencies/integration: included by `copy_from_user.S` and `copy_to_user.S`, and depends on their exception labels, macro definitions, and ARM64 alternative patching.

Risks: as an include template, register alias conflicts or missing labels in including files break correctness. Fault labels must line up with the user-side operations. The algorithm assumes hardware handles unaligned accesses.

Test signals: both copy-from-user and copy-to-user test matrices, all tail sizes 0..63, source alignment permutations, large copies, partial user faults, and MOPS alternatives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_template.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_to_user.S

Purpose: implements `__arch_copy_to_user`, copying bytes from kernel memory into a user destination and returning bytes not copied.

Important APIs/types/functions: `__arch_copy_to_user`, kernel load macros, user store macros, MOPS `cpyfpwt/cpyfmwt/cpyfewt`, included `copy_template.S`, and exception fixup labels.

Control flow: initializes end and original source, runs the shared copy template with kernel loads and user stores, and returns zero on success. Fault handlers adjust `dst` from MOPS residual state, retry a first-byte store when no progress occurred, then return `end - dst`.

State and persistence: writes copied bytes to user memory. It does not persist kernel state and may leave a partial user write on fault.

Dependencies/integration: used by raw copy-to-user; depends on exception-table uaccess annotations, `copy_template.S`, and ARM64 MOPS alternatives.

Risks: residual accounting and fault-side discrimination are critical because user-visible copy APIs depend on exact remaining bytes. The final retry must not mask kernel-source faults. Store-side faults must be represented as uaccess write faults in extable metadata.

Test signals: valid and faulting user destinations, page-boundary residual counts, no-progress first-byte fault, all alignments/tail sizes, MOPS vs generic path, and hardened usercopy coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/csum.c -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/csum.c

Purpose: implements optimized ARM64 Internet checksum helpers, including raw buffer checksum accumulation and IPv6 pseudo-header checksum.

Important APIs/types/functions: `accumulate`, `do_csum`, `csum_ipv6_magic`, explicit `kasan_check_read`, 64/128-bit accumulation, endian-specific folding, and exported `csum_ipv6_magic`.

Control flow: `do_csum` validates length, performs a manual KASAN read check, aligns down to an 8-byte boundary, masks leading overread bytes, accumulates 64-byte and 16-byte body chunks using 128-bit carry folding, masks tail overread bytes, folds to 16 bits, and compensates odd initial alignment. `csum_ipv6_magic` loads source/destination IPv6 addresses as 128-bit values, adds length/protocol/checksum, folds each address half, and returns `csum_fold`.

State and persistence: reads packet buffers and returns checksum values. No persistent state.

Dependencies/integration: used by network checksum paths; depends on `<net/checksum.h>`, KASAN APIs, compiler support for `__uint128_t`, and endian configuration.

Risks: deliberate head/tail overreads require the explicit KASAN check and assumptions that the rounded reads stay within safe cache/page context. Endian and odd-byte alignment handling are easy to regress. Miscompiled 128-bit arithmetic would affect packet integrity.

Test signals: checksum selftests for all lengths and alignments, odd/even start address cases, IPv6 pseudo-header known vectors, KASAN-enabled tests, big-endian build coverage, and randomized comparison with a simple reference implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/csum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/delay.c

Purpose: implements calibrated busy-wait delay primitives on ARM64 using the architectural counter, optional WFxT wait instructions, and timer event stream hints.

Important APIs/types/functions: `USECS_TO_CYCLES`, `xloops_to_cycles`, `__delay_cycles`, `__delay`, `__const_udelay`, `__udelay`, and `__ndelay`.

Control flow: delay requests convert loop or time units to counter cycles. `__delay` captures a stable CNTVCT start value, optionally uses `wfit` and `wfet` until the deadline on WFxT-capable CPUs, otherwise uses event-stream `wfe` for long enough waits, and finally spins with `cpu_relax` until elapsed cycles reach the target.

State and persistence: reads `loops_per_jiffy`, `HZ`, and the architectural counter. No persistent state.

Dependencies/integration: exported to generic delay APIs; depends on ARM arch timer, alternatives for `ARM64_HAS_WFXT`, preemption guards, and event-stream availability.

Risks: counter source must match WFxT deadline semantics, especially under KVM/EL1 CNTVOFF behavior. Calibration overflow or early wake handling can produce too-short delays. Busy waits consume CPU when WFxT/event stream is unavailable.

Test signals: delay calibration tests, udelay/ndelay minimum-duration checks, WFxT and non-WFxT hardware, KVM host/guest counter offset scenarios, and preemption/interrupt stress during delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/error-inject.c

Purpose: supplies ARM64 function error-injection support by rewriting a kprobe-captured function entry context to return directly to the caller.

Important APIs/types/functions: `override_function_with_return`, `instruction_pointer_set`, `procedure_link_pointer`, and `NOKPROBE_SYMBOL`.

Control flow: when a kprobe captures a predefined injectable function on entry, this helper sets the saved instruction pointer to the procedure link pointer, so returning from the probe skips the probed function body and resumes at its caller.

State and persistence: mutates only the transient `pt_regs` exception frame. No persistent state.

Dependencies/integration: enabled by `CONFIG_FUNCTION_ERROR_INJECTION`; integrates with kprobes and Linux error-injection infrastructure.

Risks: only valid for contexts where the link pointer reflects the caller return address. Misuse on functions with unusual entry conventions or missing return-value setup can corrupt control flow.

Test signals: function error-injection selftests, kprobe entry-only invocation, return-value override tests, and `NOKPROBE_SYMBOL` recursion protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/insn.c -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/insn.c

Purpose: provides ARM64/AArch32 instruction decode and generation helpers used by patching, probes, alternatives, BPF, and other runtime code emitters.

Important APIs/types/functions: immediate/register encoders and decoders, branch generators, load/store generators, acquire/release/exclusive/atomic/CAS generators, add/sub/bitfield/movewide/logical/data processing generators, ADR/ADRP helpers, branch offset get/set, system register extraction, AArch32 MCR helpers, logical-immediate encoder, `aarch64_insn_gen_dmb`, `aarch64_insn_gen_dsb`, and `aarch64_insn_gen_mrs`.

Control flow: helper functions select an instruction template from `asm/insn.h`, validate enum values and range constraints, set variant bits, encode registers and immediates into fixed fields, and return the final 32-bit instruction. Invalid inputs generally log an error and return `AARCH64_BREAK_FAULT`; branch offset functions `BUG()` on unsupported input instruction classes. Logical-immediate encoding reconstructs the architecture's repeated bitmask fields by detecting element size, contiguous one ranges, and rotation.

State and persistence: no mutable global state. It returns instruction words only.

Dependencies/integration: depends on architecture instruction constants, bitfield helpers, kprobes annotations, and users such as live patching, ftrace, alternatives, probes, BPF JIT, and static branch code.

Risks: returning a break instruction is safer than emitting an invalid operation, but callers must check it. Range, alignment, signed-offset, and immediate encoding bugs can patch wrong code into executable text. Some helpers support only a subset of legal instruction forms. Logical immediate encoding is algorithmically delicate.

Test signals: unit vectors for every encoder/decoder, disassembly round trips, boundary offsets for B/BL/CBZ/TBZ/ADR/ADRP, invalid enum/range rejection, logical-immediate exhaustive or randomized tests against assembler, and kprobe/static-patching integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/kasan_sw_tags.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/kasan_sw_tags.S

Purpose: implements the low-level SW tag KASAN mismatch thunk that adapts the compiler's non-AAPCS call frame into a normal call to `kasan_tag_mismatch`.

Important APIs/types/functions: `__hwasan_tag_mismatch`, `bti c`, register save/restore block, call to `kasan_tag_mismatch`, and exported symbol.

Control flow: the compiler-generated thunk enters with a 256-byte stack object and nonstandard preserved registers. The routine creates a frame record, saves x2-x15 and optionally x18, passes x0/x1 plus the call site in x2 to `kasan_tag_mismatch`, restores all expected registers and frame values, drops the 256-byte object, and returns.

State and persistence: mutates only the temporary trap stack frame and calls KASAN reporting. No persistent state except whatever the KASAN report path records.

Dependencies/integration: built with `CONFIG_KASAN_SW_TAGS`; depends on compiler HWASAN ABI expectations, shadow call stack configuration, BTI, and KASAN runtime.

Risks: register or stack layout mismatch corrupts the interrupted function. Shadow call stack handling of x18 must remain consistent with config. The calling convention is compiler-specific and fragile.

Test signals: SW-tag KASAN mismatch tests, stack unwinding through the thunk, shadow-call-stack config builds, BTI-enabled execution, and register preservation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/kasan_sw_tags.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memchr.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/memchr.S

Purpose: optimized ARM64 implementation of `memchr`, returning the first matching byte in a bounded memory range.

Important APIs/types/functions: `__pi_memchr`, weak alias `memchr`, byte replication constants, word-loop zero-byte-style match detection, endian fixup, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: masks the search character to one byte, scans 8-byte words with a replicated character and parallel byte-match detection, then scans any trailing bytes. On a matching word, it reverses the syndrome on little-endian, counts leading zeros, and computes the matching address.

State and persistence: read-only scan of caller memory. No persistent state.

Dependencies/integration: used by kernel string/memory library callers and exported without KASAN instrumentation.

Risks: word loads require the full word to be inside the caller's valid range; the routine only loads complete 8-byte chunks derived from `n`. Endian syndrome math must locate the first matching byte, not just any match.

Test signals: all byte values, lengths 0..16, unaligned buffers, match at first/last/no byte, big-endian builds, and comparison with generic C `memchr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memcmp.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/memcmp.S

Purpose: optimized ARM64 implementation of `memcmp`, returning ordering for the first differing byte in two bounded buffers.

Important APIs/types/functions: `__pi_memcmp`, weak alias `memcmp`, less-than-8 byte path, 16-byte loop, alignment optimization, endian-aware return normalization, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: handles small lengths with word/byte paths, compares initial 8/16 bytes, optionally aligns `src1` for large ranges, loops over 16-byte pairs using conditional compare, then checks last overlapping bytes. On word difference it reverses data on little-endian so numeric compare reflects byte order and returns -1/0/1 or byte difference for tiny path.

State and persistence: reads caller buffers only. No persistent state.

Dependencies/integration: exported kernel memory routine; assumes ARMv8 unaligned access support.

Risks: overlapping tail loads must remain within the bounded range. Endian-specific comparison controls observable ordering. Misalignment optimization overlaps loads and needs correct length thresholds.

Test signals: randomized buffers and lengths, first difference at every position, equal buffers, lengths 0..128 and large sizes, unaligned pairs, big-endian coverage, and comparison against generic implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/memcpy.S

Purpose: optimized ARM64 implementation of `memcpy` and `memmove`, including overlap-safe large copies and optional FEAT_MOPS acceleration.

Important APIs/types/functions: `__pi_memcpy_generic`, `__pi_memcpy`, aliases `__memcpy`, `memcpy`, `__pi_memmove`, `__memmove`, `memmove`, small/medium/large copy paths, backward overlap path, MOPS `cpyp/cpym/cpye`, and exports.

Control flow: for <=32 bytes it uses branch-light byte/word/end loads; for 33..128 bytes it copies fixed leading/trailing blocks; for >128 bytes it checks destination-source overlap. Non-overlap large copies align destination and pipeline 64-byte forward loops with an end copy. Overlap uses a symmetric backward loop. If MOPS is supported, `__pi_memcpy` dispatches to copy instructions; otherwise it aliases the generic implementation.

State and persistence: writes destination memory and reads source memory. No persistent state.

Dependencies/integration: core kernel memory API, alternative patching, ARMv8 unaligned accesses, FEAT_MOPS, and exported symbols expected by generic code.

Risks: despite `memcpy` semantics, the shared implementation also handles memmove overlap; any overlap decision bug corrupts data. Tail and end-copy overlap loads/stores are delicate. MOPS behavior must match generic memmove semantics.

Test signals: libc-style memcpy/memmove torture tests, overlap forward/backward cases, all small sizes, 33..128 boundaries, large unaligned buffers, MOPS and non-MOPS CPUs, and KASAN bounds tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/memset.S

Purpose: optimized ARM64 implementation of `memset` with special zero-fill DC ZVA and optional MOPS acceleration.

Important APIs/types/functions: `__pi_memset_generic`, `__pi_memset`, aliases `__memset` and `memset`, byte replication setup, small/tail/large store loops, `.Lzero_mem` DC ZVA path, MOPS `setp/setm/sete`, and exports.

Control flow: expands the byte value to a 64-bit pattern, handles <=15 bytes with scalar stores, aligns the destination, uses pair stores for nonzero or shorter zero fills, and for large zero fills reads `dczid_el0` to use DC ZVA when permitted and useful. MOPS-capable CPUs use set instructions through alternatives.

State and persistence: writes the destination buffer. No persistent state.

Dependencies/integration: core memory API, cache-line constants, DC ZVA, FEAT_MOPS, and alternative patching.

Risks: DC ZVA path intentionally aligns and may over-store inside the requested range; boundary arithmetic must prevent overruns. MOPS and generic return value must preserve original destination. Non-cacheable memory callers may have different expectations, so callers must use appropriate APIs.

Test signals: memset tests for all sizes/alignments/values, zero fills across ZVA sizes, nonzero large fills, MOPS matrix, and memory sanitizer/KASAN range checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/mte.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/mte.S

Purpose: implements ARM64 Memory Tagging Extension page tag operations and ptrace tag copy helpers.

Important APIs/types/functions: `multitag_transfer_size`, `mte_clear_page_tags`, `mte_zero_clear_page_tags`, `mte_copy_page_tags`, `mte_copy_tags_from_user`, `mte_copy_tags_to_user`, `mte_save_page_tags`, and `mte_restore_page_tags`.

Control flow: page clear/copy loops use GMID-derived multi-tag block size with `stgm`/`ldgm`. Zero-clear uses DC GZVA when permitted, otherwise `stz2g` granule stores. Ptrace helpers transfer one tag byte per MTE granule between user buffers and kernel-address tags, with `USER` fixups returning the count copied. Save/restore compresses or expands page tags into `MTE_PAGE_TAG_STORAGE` groups.

State and persistence: mutates allocation tags attached to memory and, for zero-clear, page data. Saved tags are stored in caller-provided memory. No independent persistent state.

Dependencies/integration: built for `CONFIG_ARM64_MTE`; depends on ARMv8.5 memtag instructions, MTE granule constants, uaccess exception macros, page size, and ptrace/swap/page-copy MTE paths.

Risks: tag operations require correct address tag clearing and granule alignment. User tag copy residual counts must be exact. Save/restore packing assumes tag storage size and GMID block size match architecture expectations.

Test signals: MTE page allocation/tagging tests, ptrace PEEK/POKE MTE tags with partial faults, swap save/restore, huge/small page tag copy, DC GZVA availability matrix, and tag preservation across migration/COW.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/mte.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strchr.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/strchr.S

Purpose: simple ARM64 `strchr` implementation returning the first occurrence of a character in a NUL-terminated string.

Important APIs/types/functions: `__pi_strchr`, weak alias `strchr`, byte loop, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: masks the character to 8 bits, loads bytes one at a time until the byte equals the target or is NUL, backs up to the matching position, and returns either that address or zero.

State and persistence: read-only string scan. No persistent state.

Dependencies/integration: exported kernel string helper; assumes caller supplies a valid NUL-terminated string.

Risks: no bound is enforced, so unterminated or invalid strings can fault. Character comparison treats input as unsigned byte.

Test signals: target before NUL, target is NUL, absent target, empty string, high-bit character values, and comparison with generic `strchr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strcmp.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/strcmp.S

Purpose: optimized ARM64 `strcmp` comparing two NUL-terminated strings with MTE-compatible access patterns.

Important APIs/types/functions: `__pi_strcmp`, weak alias `strcmp`, aligned loop, mutual-alignment path, misaligned path, parallel NUL detection, endian-sensitive syndrome handling, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: if the two strings share alignment, it compares 8-byte words after masking pre-string bytes. Otherwise it byte-aligns `src1`, carefully reads from aligned `src2` without crossing beyond its NUL, and combines shifted words. The first difference or NUL builds a syndrome; the routine locates the earliest significant byte and returns unsigned-byte subtraction.

State and persistence: reads both strings only. No persistent state.

Dependencies/integration: exported string API; assumes valid NUL-terminated strings, ARMv8 unaligned access support where used, and endian assembler helpers.

Risks: misaligned string logic must avoid reading past a valid page when `src2` is close to a boundary. Big-endian NUL-detection carry behavior requires byte reversal. No length bound means bad strings can fault.

Test signals: equal strings, differences at every offset, prefixes, empty strings, misalignment combinations, page-boundary strings, high-bit/non-ASCII bytes, big-endian builds, and MTE/KASAN compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strlen.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/strlen.S

Purpose: optimized ARM64 `strlen` with page-crossing care and hardware-tag KASAN granule awareness.

Important APIs/types/functions: `__pi_strlen`, weak alias `strlen`, `MIN_PAGE_SIZE` selection, first-16-byte probe, main 32-byte loop, non-ASCII accurate loop, page-cross path, parallel NUL detection, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: checks whether the first unaligned 16-byte load crosses the minimum page or MTE granule boundary. If safe, it probes two words for early NUL. Longer strings enter an aligned 32-byte loop using a fast ASCII NUL check, falling back to a precise check when high-bit bytes are present. If the first access would cross a boundary, it reads from an aligned address and masks bytes before `srcin`.

State and persistence: read-only string scan. No persistent state.

Dependencies/integration: exported string API; depends on MTE granule definitions when `CONFIG_KASAN_HW_TAGS` is enabled and endian handling macros.

Risks: unbounded scan can fault on invalid or unterminated strings. The page/granule cross guard is critical for KASAN HW tags. Fast non-ASCII detection must not miss NUL bytes.

Test signals: strings of length 0..64 and large, start addresses near page and MTE-granule boundaries, non-ASCII bytes, big-endian builds, KASAN HW tags, and comparison with generic `strlen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strncmp.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/strncmp.S

Purpose: optimized ARM64 `strncmp`, comparing at most a caller-provided limit of bytes from two strings.

Important APIs/types/functions: `__pi_strncmp`, weak alias `strncmp`, zero-limit fast return, aligned and mutual-aligned loops, misaligned word comparison, syndrome/limit checks, endian-specific result paths, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: returns zero for limit zero, then chooses aligned/misaligned strategy based on source alignment. Aligned loops subtract eight from the limit per word, detect differences and NUL in parallel, and use a syndrome to decide whether the first significant byte lies before the limit. Misaligned sources compare bytes until `src1` alignment, then combine shifted aligned reads from `src2` in several steps while masking irrelevant bytes.

State and persistence: reads caller strings up to the bounded comparison pattern. No persistent state.

Dependencies/integration: exported string API; assumes source ranges are valid for the accesses implied by the optimized algorithm and uses endian assembler helpers.

Risks: limit accounting near `ULONG_MAX` and misaligned source combinations is complex. Big-endian result generation cannot rely on the same syndrome trick when NUL is present. Page-boundary behavior depends on caller-valid string memory.

Test signals: zero limit, equal prefixes shorter/longer than limit, difference at each byte before/after limit, NUL before limit, all alignments, high-bit bytes, big-endian builds, and randomized comparison with generic `strncmp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strncmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strnlen.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/strnlen.S

Purpose: optimized ARM64 `strnlen`, returning string length capped at a maximum count.

Important APIs/types/functions: `__pi_strnlen`, weak alias `strnlen`, aligned 16-byte loop, misaligned first-block handling, parallel NUL detection, endian correction, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: zero limit returns zero. Otherwise it aligns the base down to 16 bytes, computes a bounded word count without overflow, masks bytes before the string for misaligned starts, scans two words per iteration for NUL, and returns the smaller of found length and limit.

State and persistence: read-only bounded scan. No persistent state.

Dependencies/integration: exported string API; depends on ARM64 unaligned access behavior and endian macros.

Risks: overflow-safe limit word calculation is important for huge limits. Misaligned masking must ignore bytes before `srcin` without hiding real NULs. As with other string routines, caller must provide accessible memory up to NUL or limit.

Test signals: limit zero, NUL before/at/after limit, no NUL up to limit, unaligned starts, large limits near word overflow boundaries, big-endian builds, and generic implementation comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strnlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strrchr.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/strrchr.S

Purpose: simple ARM64 `strrchr` implementation returning the last occurrence of a character before the terminating NUL.

Important APIs/types/functions: `__pi_strrchr`, weak alias `strrchr`, byte loop with last-match register, and `EXPORT_SYMBOL_NOKASAN`.

Control flow: masks the target character to one byte, initializes last-match to zero, scans byte by byte until NUL, updates the last-match address whenever the byte equals the target, and returns the saved address.

State and persistence: read-only string scan. No persistent state.

Dependencies/integration: exported kernel string helper; assumes a valid NUL-terminated string.

Risks: as implemented, it stops before testing the terminating NUL as a match, so callers searching for `'\0'` should be covered by tests against expected kernel semantics. Unbounded invalid strings can fault.

Test signals: multiple matches, no match, empty string, target near terminator, target `'\0'`, high-bit character values, and comparison with generic `strrchr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/strrchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/tishift.S -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/tishift.S

Purpose: supplies compiler helper routines for 128-bit integer shifts on ARM64.

Important APIs/types/functions: `__ashlti3`, `__ashrti3`, `__lshrti3`, each exported for left shift, arithmetic right shift, and logical right shift of a two-register 128-bit value.

Control flow: each routine handles shift count zero directly. For counts below 64, it shifts low/high halves and transfers cross-boundary bits. For counts >=64, it moves the remaining high/low half into position and fills the other half with zero or sign bits for arithmetic right shift.

State and persistence: pure register computation. No memory or persistent state.

Dependencies/integration: used by compiler-generated code when 128-bit shifts are emitted; depends on AAPCS register return conventions.

Risks: shift counts outside compiler-expected ranges could produce undefined helper behavior. Arithmetic right shift must preserve sign extension exactly.

Test signals: compiler runtime tests for `__int128` shifts, counts 0, 1, 63, 64, 65, 127, signed negative values for `__ashrti3`, and comparison with compiler/emulator reference results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/tishift.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/uaccess_flushcache.c -->
# sources/distributed-fs/ceph-client/arch/arm64/lib/uaccess_flushcache.c

Purpose: implements copy helpers that clean written cache lines to persistence after kernel or user-source copies.

Important APIs/types/functions: `memcpy_flushcache`, `__copy_user_flushcache`, `dcache_clean_pop`, `raw_copy_from_user`, and exported `memcpy_flushcache`.

Control flow: `memcpy_flushcache` copies from kernel source to destination, then cleans the destination range to point of persistence. `__copy_user_flushcache` performs raw copy-from-user, then cleans only the successfully copied prefix `n - rc`.

State and persistence: writes destination memory and issues cache maintenance to PoP. It does not keep software state.

Dependencies/integration: enabled by `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE`; integrates with persistent memory and uaccess paths, cacheflush assembly, and raw usercopy.

Risks: assumes destination is cacheable memory and does not require an extra barrier against the preceding memcpy. A faulting user copy must clean only bytes actually written. Persistent memory ordering semantics depend on surrounding caller barriers.

Test signals: pmem/DAX flush tests, partial usercopy faults, zero-length copies, cache line boundary ranges, and validation that only copied bytes are flushed after faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/lib/uaccess_flushcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/Makefile

Purpose: selects ARM64 MM subsystem objects for DMA cache maintenance, exception fixups, fault handling, init, cache routines, page copy, flush, ioremap, mmap, page tables, context switching, page attributes, fixmap, and optional features.

Important APIs/types/functions: `obj-y` base list, optional `contpte.o`, `hugetlbpage.o`, `ptdump.o`, `trans_pgd.o`, `physaddr.o`, `mteswap.o`, `gcs.o`, `kasan_init.o`, and KASAN sanitizer disables for `physaddr.o` and `kasan_init.o`.

Control flow: Kbuild links the base MM objects unconditionally and adds feature-specific objects according to ARM64 config symbols.

State and persistence: no runtime state. It controls build-time composition of MM code.

Dependencies/integration: depends on Kbuild and config symbols including `CONFIG_ARM64_CONTPTE`, `CONFIG_HUGETLB_PAGE`, `CONFIG_PTDUMP`, `CONFIG_TRANS_TABLE`, `CONFIG_DEBUG_VIRTUAL`, `CONFIG_ARM64_MTE`, `CONFIG_ARM64_GCS`, and `CONFIG_KASAN`.

Risks: missing optional object inclusion can silently disable feature support or break symbols. Sanitizer settings are important for early MM and physical address debugging code.

Test signals: ARM64 config build matrix, feature-specific boot tests for CONTPTE/MTE/GCS/KASAN/PTDUMP, and linker symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/cache.S -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/cache.S

Purpose: implements ARM64 cache maintenance primitives for I/D coherency, user executable mappings, DMA/cache invalidation and cleaning to PoU, PoC, and PoP.

Important APIs/types/functions: `caches_clean_inval_pou`, `caches_clean_inval_user_pou`, `icache_inval_pou`, `dcache_clean_inval_poc`, `dcache_clean_pou`, `dcache_inval_poc`, `dcache_inval_poc_nosync`, `dcache_clean_poc`, `dcache_clean_poc_nosync`, and `dcache_clean_pop`.

Control flow: PoU clean/invalidate skips D-cache work when IDC is present and skips I-cache invalidation when DIC is present. User PoU maintenance enables TTBR0 and returns `-EFAULT` through a fixup if user access fails. PoC/PoP routines walk cache lines with the appropriate `dc` operation, using clean+invalidate for partial invalidation endpoints to avoid data loss. PoP falls back to PoC when DC CVAP is unsupported.

State and persistence: no software state. It issues architectural cache maintenance and barriers affecting memory visibility and persistence.

Dependencies/integration: called by MM flush code, DMA mapping, uaccess flushcache, module/text patching, and PMEM support. Depends on assembler cache macros, CPU feature alternatives IDC/DIC/DCPOP, and uaccess helpers.

Risks: missing barriers can leave stale instructions or dirty data. Invalidation must clean partial lines to prevent losing unrelated bytes. User range faults must be reported without leaving TTBR0 access enabled. PoP fallback changes persistence guarantees on unsupported CPUs.

Test signals: self-modifying code/module load tests, DMA cache sync tests, user executable mapping flush faults, PMEM persistence tests, IDC/DIC/DCPOP feature matrix, and cache-line unaligned ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/cache.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/context.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/context.c

Purpose: implements ARM64 user ASID allocation, rollover, pinning, TLB flush coordination, and TTBR switching.

Important APIs/types/functions: `asid_bits`, `asid_generation`, `asid_map`, per-CPU `active_asids`/`reserved_asids`, `tlb_flush_pending`, pinned ASID map/counters, `verify_cpu_asid_bits`, `flush_context`, `new_context`, `check_and_switch_context`, `arm64_mm_context_get`, `arm64_mm_context_put`, `post_ttbr_update_workaround`, `cpu_do_switch_mm`, `asids_update_limit`, and `asids_init`.

Control flow: context switching fast-paths when the mm ASID matches the current generation and this CPU has a nonzero active ASID. Slow path takes `cpu_asid_lock`, allocates or refreshes the ASID, performs pending local TLB flush after rollover, installs the active ASID, applies branch predictor hardening, and switches TTBRs unless TTBR0 PAN defers it. Rollover rebuilds the ASID bitmap from KPTI reservations, pinned ASIDs, and per-CPU reserved active ASIDs, then marks all CPUs pending for local TLB flush.

State and persistence: maintains kernel memory allocator state and per-mm `context.id`/`pinned`. No disk persistence. Pinned ASIDs reserve slots across rollovers for external users; KPTI reserves paired kernel/user ASIDs.

Dependencies/integration: core scheduler/mm context switch, CPU feature detection, KPTI, CnP, SW TTBR0 PAN, TLB flush code, branch predictor hardening, Cavium erratum workaround, and exported pinned-ASID APIs.

Risks: memory ordering around active ASID cmpxchg and rollover is subtle. Too many pinned ASIDs can starve the allocator, so `max_pinned_asids` must leave room for CPUs and rollover. ASID bit mismatch on hotplug is fatal. TTBR update ordering and errata workaround are architecture-critical.

Test signals: process context-switch stress, ASID rollover under many mms, CPU hotplug with ASID bit validation, pinned ASID get/put exhaustion, KPTI pair allocation, CnP/SW PAN configurations, and TLB stale-translation litmus tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/contpte.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/contpte.c

Purpose: implements ARM64 contiguous-PTE folding and unfolding for user mappings, plus wrappers that keep core-MM PTE operations correct when a logical mapping spans a hardware contiguous block.

Important APIs/types/functions: `mm_is_user`, alignment helpers, `contpte_convert`, `__contpte_try_fold`, `__contpte_try_unfold`, `contpte_ptep_get`, `contpte_ptep_get_lockless`, `contpte_set_ptes`, clear/get-clear wrappers, young/dirty clearing wrappers, `contpte_wrprotect_ptes`, and `contpte_ptep_set_access_flags`.

Control flow: folding checks user mm, folio coverage, contiguous PFNs, and matching protections while ignoring young/dirty state, aggregates dirty/young bits, clears the block, optionally flushes depending on BBML2 no-abort support, and reinstalls `CONT_PTE` entries. Unfolding clears `CONT_PTE` and repaints individual entries. Get helpers gather young/dirty state across sub-PTEs; the lockless path retries until it observes a consistent contiguous block. Range operations unfold partial blocks when required or expand operations to whole blocks when core-MM tracks state per folio.

State and persistence: mutates user page tables and TLB-visible attributes. No disk persistence. It deliberately avoids dynamic contiguous-bit changes for kernel and EFI mappings.

Dependencies/integration: core MM PTE APIs, ARM64 TLB flush machinery, folio metadata, BBML2 capability, exported symbols used by page-table helpers, and `CONFIG_ARM64_CONTPTE`.

Risks: contiguous entries require consistent attributes across all sub-PTEs; partial write-protect or access-flag changes can be unpredictable if not unfolded or applied to the whole block. Lockless reads can race with fold/unfold and must retry correctly. TLB flush elision relies on precise Arm BBML behavior.

Test signals: THP/large-folio mappings, fold/unfold under concurrent faults, write-protect/access-flag changes on partial and full blocks, lockless GUP reads during modification, dirty/young tracking, SMMU or no-DBM behavior, and BBML0 vs BBML2 CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/contpte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/copypage.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/copypage.c

Purpose: implements high-level page copy routines that combine raw page copying with KASAN tag reset, MTE tag propagation, and user-page cache flush handling.

Important APIs/types/functions: `copy_highpage`, `copy_user_highpage`, `copy_page`, `page_kasan_tag_reset`, `mte_copy_page_tags`, `try_page_mte_tagging`, hugetlb MTE tag helpers, and `flush_dcache_page`.

Control flow: `copy_highpage` copies page data, resets KASAN HW tags if enabled, then if MTE is supported copies allocation tags. Hugetlb tagged folios copy tags for all subpages when the source folio is tagged and the copy starts at the first folio page; normal pages copy tags only when the source page is MTE-tagged. `copy_user_highpage` calls `copy_highpage` and marks the destination D-cache dirty for later executable-user synchronization.

State and persistence: writes destination page data and MTE tag state, updates page/folio MTE tagged flags, and marks D-cache clean state dirty. No disk persistence.

Dependencies/integration: core COW/migration page copy, MTE, KASAN HW tags, hugetlb, cache flush code, and exported page-copy symbols.

Risks: huge page tag copy must account for subpage starts and avoid duplicating partial tag state. Reused pages during migration may already be tagged. Missing cache dirty marking can expose stale I-cache for executable mappings.

Test signals: COW and migration with MTE-tagged pages, hugetlb tagged folio copy, KASAN HW tag reset, user executable page copy followed by execution, and no-MTE fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/copypage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/dma-mapping.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/dma-mapping.c

Purpose: provides ARM64 DMA cache synchronization hooks and per-device DMA coherency setup.

Important APIs/types/functions: `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`, `arch_dma_prep_coherent`, and `arch_setup_dma_ops`.

Control flow: device sync cleans the physical range's linear-map alias to PoC. CPU sync invalidates from PoC for inbound or bidirectional DMA and skips `DMA_TO_DEVICE`. Coherent allocation prep cleans the page range. Setup warns if a non-coherent device's CPU cache writeback granule exceeds `ARCH_DMA_MINALIGN`, records coherency, and applies Xen DMA ops.

State and persistence: issues cache maintenance and sets `dev->dma_coherent`. No disk persistence.

Dependencies/integration: DMA mapping core, cacheflush routines, Xen DMA operation setup, CPU cache line size reporting, and device model.

Risks: `phys_to_virt` assumes the physical range is linearly mapped. Skipping invalidation for `DMA_TO_DEVICE` is correct only for direction semantics. Misreported coherency or cache granule can corrupt DMA buffers.

Test signals: non-coherent DMA tests for all directions, Xen guest DMA setup, cache-line alignment warning paths, coherent allocation visibility, and device-tree/ACPI coherency property coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/dma-mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/extable.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/extable.c

Purpose: handles ARM64 exception table fixups for uaccess, BPF, kernel access zeroing, copy faults, and unaligned zeropad loads.

Important APIs/types/functions: `cpy_faulted_on_uaccess`, `insn_may_access_user`, `get_ex_fixup`, `ex_handler_uaccess_err_zero`, `ex_handler_uaccess_cpy`, `ex_handler_load_unaligned_zeropad`, and `fixup_exception`.

Control flow: `fixup_exception` looks up the faulting instruction in exception tables, dispatches by type, updates registers and PC to the fixup target, and returns whether the exception was handled. Copy fixups validate ESR write/read direction so kernel-side faults are not hidden as user faults. Unaligned zeropad reads the aligned word, shifts based on endian offset, writes the result register, and resumes at fixup.

State and persistence: mutates transient `pt_regs` and possibly register values. No persistent state.

Dependencies/integration: fault handler calls, exception table encoding from `asm-extable.h`, BPF exception handler, uaccess assembly, ESR fields, and ARM64 register access helpers.

Risks: incorrect exception type metadata can hide real kernel faults or fail valid uaccess recovery. `LOAD_UNALIGNED_ZEROPAD` dereferences an aligned kernel word during fixup and relies on surrounding extable assumptions. Unknown extable types `BUG()`.

Test signals: uaccess copy/read/write faults, kernel access err-zero fixups, BPF probe fault recovery, zeropad unaligned loads across page ends, ESR WnR direction mismatch, and fault-injection into annotated assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/fault.c

Purpose: implements ARM64 memory abort handling, page fault resolution, kernel fault reporting, MTE tag fault handling, GCS access checks, pkey/POE reporting, external abort notification, and MTE-aware page allocation/tag clearing.

Important APIs/types/functions: `fault_info`, ESR decode helpers, `show_pte`, `__ptep_set_access_flags_anysz`, permission/spurious/pKVM checks, `__do_kernel_fault`, `set_thread_esr`, `do_page_fault`, `do_translation_fault`, `do_alignment_fault`, `do_sea`, `do_tag_check_fault`, `do_mem_abort`, `do_sp_pc_abort`, `vma_alloc_zeroed_movable_folio`, and `tag_clear_highpages`.

Control flow: `do_mem_abort` indexes `fault_info` by FSC and calls the handler. Translation/access/permission faults enter `do_page_fault`, which rejects no-context faults, derives `vm_flags` and `FAULT_FLAG_*` from ESR, detects illegal kernel user-memory access outside uaccess routines, handles pKVM stage-2 aborts, tries the RCU VMA fault path, falls back to mmap lock, calls `handle_mm_fault`, and converts errors into SIGSEGV/SIGBUS/OOM/MCE signals. Kernel faults attempt exception-table fixup, spurious translation fault detection with AT/PAR, MTE tag recovery, EFI fixup, and finally die with decoded ESR and page table dump.

State and persistence: updates current thread fault address/code, page table access flags, TLB state, MTE tag checking mode on recovery, task signals, folio allocation flags, and page MTE-tagged state. No disk persistence.

Dependencies/integration: core MM fault handling, KASAN/KFENCE, kprobes, perf page-fault events, pkeys/POE, GCS, pKVM, EFI runtime fixups, APEI SEA, MTE, hugetlb, TLB flush helpers, and signal delivery.

Risks: ESR interpretation drives signal codes and kernel oops classification. Permission checks must distinguish PAN/user-memory misuse from normal user faults. RCU VMA fast path must unwind locks correctly on retry/completion. MTE tag recovery disables checking locally and relies on lazy handling elsewhere. pKVM stage-2 abort recovery and spurious fault detection are security-sensitive.

Test signals: user read/write/exec faults, COW and retry paths, OOM/hwpoison/SIGBUS cases, kernel uaccess fixups, illegal kernel user access, PAN translation faults, pkey faults, GCS invalid access, MTE sync tag faults, SEA/APEI, pKVM protected-memory aborts, and access-flag atomic updates on different page sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/fixmap.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/fixmap.c

Purpose: initializes and manipulates ARM64 fixmap page tables and provides early FDT remapping through fixmap slots.

Important APIs/types/functions: bootstrap page table arrays `bm_pte`, `bm_pmd`, `bm_pud`, `early_fixmap_init`, `__set_fixmap`, and `fixmap_remap_fdt`.

Control flow: early init populates fixmap P4D/PUD/PMD/PTE tables using `__pa_symbol` because normal virtual-to-physical helpers are not available yet. `__set_fixmap` validates the fixed-address index, sets or clears the corresponding PTE, and flushes the kernel TLB when clearing. `fixmap_remap_fdt` validates physical FDT alignment, maps the first page, verifies magic and total size, rejects oversized blobs, and extends the mapping if the FDT crosses the first page.

State and persistence: owns early boot fixmap page-table arrays and mutates fixmap PTEs. No disk persistence.

Dependencies/integration: early boot memory setup, device tree parsing, fixed-address definitions, page-table population helpers, TLB flush, and PCI I/O region layout assertions.

Risks: runs very early, so wrong physical address conversion or table population can break boot. `__set_fixmap` can be called in IRQ context, limiting future TLB broadcast mechanisms. FDT remap must avoid accepting misaligned, invalid, or oversized blobs.

Test signals: early boot on page-table-level/page-size variants, FDT physical alignment and size checks, fixmap set/clear TLB behavior, 16K page configuration where kernel/fixmap share top-level entries, and IRQ-context fixmap users such as GHES.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/fixmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/flush.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/flush.c

Purpose: provides higher-level ARM64 cache flush integration for executable user mappings, ptrace page writes, D-cache dirty tracking, and persistent memory cache operations.

Important APIs/types/functions: `sync_icache_aliases`, `copy_to_user_page`, `__sync_icache_dcache`, `flush_dcache_folio`, `flush_dcache_page`, `caches_clean_inval_pou` export, `arch_wb_cache_pmem`, and `arch_invalidate_pmem`.

Control flow: executable writes call `sync_icache_aliases`, which either cleans D-cache and invalidates all I-cache on aliasing caches or uses PoU clean+invalidate for non-aliasing caches. `copy_to_user_page` memcpy's into the page then flushes if the VMA is executable. `__sync_icache_dcache` performs the folio-wide sync only once while `PG_dcache_clean` is clear, then marks it clean. Kernel writes clear that bit through `flush_dcache_folio/page`. PMEM writeback orders prior non-cacheable writes then cleans to PoP; invalidation uses PoC invalidation.

State and persistence: mutates folio `PG_dcache_clean` flag and issues cache maintenance. PMEM routines affect persistence visibility.

Dependencies/integration: core MM executable mapping setup, ptrace access, cache.S routines, folio/page flags, libnvdimm PMEM API, and architecture cache alias detection.

Risks: missing icache synchronization can execute stale instructions. Dirty flag races must remain benign across folio mappings. PMEM ordering depends on the outer-shareable barrier and DC CVAP/PoP support.

Test signals: ptrace writes to executable mappings, JIT/module text coherency, folio dirty-clean transitions, aliasing I-cache hardware, PMEM persistence tests, and DAX/libnvdimm cache API coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/gcs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/gcs.c

Purpose: implements ARM64 Guarded Control Stack user shadow-stack allocation, syscall mapping, per-task mode programming, cleanup, and prctl-style status/lock operations.

Important APIs/types/functions: `alloc_gcs`, `gcs_size`, `gcs_alloc_thread_stack`, `SYSCALL_DEFINE3(map_shadow_stack)`, `gcs_set_el0_mode`, `gcs_free`, `arch_set_shadow_stack_status`, `arch_get_shadow_stack_status`, and `arch_lock_shadow_stack_status`.

Control flow: thread clone allocation checks system support and task mode, preserves current GCSPR for vfork/non-VM-sharing clones, otherwise allocates a shadow stack sized from clone stack size or defaults. `map_shadow_stack` validates flags, alignment, and overflow, maps shadow-stack VM memory, optionally writes a cap token and marker near the end, and orders it with `gcsb_dsync`. Status setting validates support, compat mode, unknown bits, and locked bits, allocates a stack on first enable for current task, writes GCSPR_EL0, stores mode flags, and programs GCSCRE0_EL1 for enable/write/push permissions.

State and persistence: stores per-task `gcs_base`, `gcs_size`, `gcspr_el0`, `gcs_el0_mode`, and locked flags, and maps/unmaps shadow-stack VMAs. No disk persistence.

Dependencies/integration: ARM64 GCS CPU feature, `vm_mmap_shadow_stack`, `vm_munmap`, clone/prctl/syscall paths, user access helpers for cap token writes, system registers `SYS_GCSPR_EL0` and `SYS_GCSCRE0_EL1`, and compat-thread checks.

Risks: re-enabling after disable is intentionally rejected when old stack state remains. Token placement must avoid overflow and wrong address writes. Only current task can allocate on enable, so remote task changes can return `-EBUSY`. Compat tasks are unsupported. Freeing requires the task mm to match current mm.

Test signals: `map_shadow_stack` flag/alignment/overflow validation, cap token and marker placement, first enable allocation, disable/re-enable rejection, clone with CLONE_VM vs vfork behavior, locked status bits, compat rejection, GCS fault handling integration, and cleanup on thread exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/gcs.c -->
