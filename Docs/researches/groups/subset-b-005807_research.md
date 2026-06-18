# subset-b-005807 research

Grouped source research for Linux/Ceph-client include headers. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/uaccess.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/uaccess.h

Purpose: generic userspace access helpers for architectures with shared kernel/user address space, especially NOMMU-style configurations. It provides the fallback `get_user`, `put_user`, `clear_user`, raw copy, and nofault kernel access primitives.

Important APIs/types/functions: `__get_user_fn`, `__put_user_fn`, `raw_copy_from_user`, `raw_copy_to_user`, `__put_user`, `put_user`, `__get_user`, `get_user`, `__clear_user`, `clear_user`, `strncpy_from_user`, and `strnlen_user`. Under `CONFIG_UACCESS_MEMCPY`, single-value access uses unaligned loads/stores directly; otherwise the file falls back to `raw_copy_{from,to}_user`.

Control flow: public `get_user`/`put_user` call `might_fault()`, check `access_ok()`, then dispatch through size-specific switch statements for 1/2/4/8-byte transfers. Unsupported object sizes deliberately call noreturn bad-size helpers. `clear_user` returns the uncleared byte count on an access check failure.

State and persistence: no persistent state. The observable state is copied data and the return code/uncopied byte count.

Dependencies and integration points: depends on `linux/string.h`, `linux/unaligned.h` when enabled, `asm-generic/access_ok.h`, and `asm/extable.h`. It is pulled by architecture uaccess layers that do not provide stronger hardware-fault-backed implementations.

Risks: direct memcpy-style access assumes the architecture can safely dereference user pointers after `access_ok`; that is not valid on MMU architectures needing exception-table recovery. Size dispatch must stay compile-time bounded or bad-size paths break callers. Callers must check negative `-EFAULT` returns and partial clear/copy counts.

Test signals: compile coverage across `CONFIG_UACCESS_MEMCPY` on/off, sparse `__user` pointer checking, fault-injection tests for invalid user pointers, and libc/syscall smoke tests exercising user copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/unwind_user.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/unwind_user.h

Purpose: empty generic placeholder for architecture user unwinding support.

Important APIs/types/functions: none; it only provides include guards.

Control flow: none.

State and persistence: none.

Dependencies and integration points: included by generic or architecture code that wants a stable `<asm/unwind_user.h>` include path even when no architecture-specific user unwinder exists.

Risks: consumers must not assume unwind operations are available from this generic header. Architecture ports needing user stack unwinding must override it.

Test signals: build-only coverage that includes this header on architectures without a custom implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/unwind_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/user.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/user.h

Purpose: generic placeholder for the obsolete `struct user` interface historically used by a.out/core-file code.

Important APIs/types/functions: none; the comment explicitly notes new architectures do not support a.out and need not define `struct user`.

Control flow: none.

State and persistence: none.

Dependencies and integration points: provides `<asm/user.h>` compatibility for code that includes it conditionally.

Risks: code expecting a concrete `struct user` cannot rely on this header. Architecture-specific ports must provide their own definition if legacy ABI support is required.

Test signals: build coverage for tools or kernel code that include `<asm/user.h>` on generic architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/vdso/vsyscall.h

Purpose: generic architecture hooks for vDSO/vsyscall data access and synchronization.

Important APIs/types/functions: `__arch_get_vdso_u_time_data`, `__arch_get_vdso_u_rng_data`, `__arch_update_vdso_clock`, and `__arch_sync_vdso_time_data`. Defaults return global `vdso_u_time_data`/`vdso_u_rng_data` and no-op the update/sync hooks.

Control flow: inline default hooks are used only when an architecture has not pre-defined custom macros/functions.

State and persistence: this header does not own state; it references vDSO user data objects maintained elsewhere and allows arch synchronization around those updates.

Dependencies and integration points: integrated with generic vDSO time/RNG code and architecture `<asm/vdso/vsyscall.h>` overrides. It is disabled for assembly inclusion.

Risks: a platform with cache, mapping, or clocksource synchronization requirements must override the no-op hooks. Otherwise userspace vDSO readers may observe stale or incorrectly synchronized time data.

Test signals: vDSO time/rng selftests, architecture boot tests with clocksource updates, and build coverage for both C and assembly include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vermagic.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/vermagic.h

Purpose: generic module version-magic architecture suffix.

Important APIs/types/functions: defines `MODULE_ARCH_VERMAGIC` as an empty string.

Control flow: none.

State and persistence: none.

Dependencies and integration points: included by module build/versioning code when an architecture has no additional vermagic tokens.

Risks: architectures with ABI-affecting options must override this or incompatible modules may appear loadable.

Test signals: module build/load tests and inspection of generated `.modinfo` vermagic strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vga.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/vga.h

Purpose: empty generic VGA compatibility include.

Important APIs/types/functions: none.

Control flow: none.

State and persistence: none.

Dependencies and integration points: satisfies `<asm/vga.h>` includes for architectures with no generic VGA-specific helpers.

Risks: VGA-capable architectures needing I/O address translation or legacy VGA hooks must provide an architecture-specific header.

Test signals: build coverage for framebuffer/console code on architectures using asm-generic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/video.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/video.h

Purpose: generic framebuffer/video I/O helper defaults for architecture `<asm/fb.h>` wrappers.

Important APIs/types/functions: `pgprot_framebuffer`, `video_is_primary_device`, `fb_read{b,w,l,q}`, `fb_write{b,w,l,q}`, `fb_memcpy_fromio`, `fb_memcpy_toio`, and `fb_memset`. The read/write helpers use raw I/O operations rather than ordered endian-swapping accessors.

Control flow: all helpers are inline defaults guarded by `#ifndef`, so architectures can override each function independently.

State and persistence: no owned state. Memory attributes are changed by returning a write-combining `pgprot_t`, and I/O helpers mutate framebuffer memory.

Dependencies and integration points: depends on `linux/io.h`, `mm_types.h`, `pgtable.h`, and type definitions. Used by framebuffer and DRM/fbdev compatibility layers.

Risks: raw framebuffer I/O deliberately allows reordering and no endian conversion; drivers needing ordered MMIO semantics must not use these helpers blindly. Default `video_is_primary_device()` returns false, so platform primary-device detection requires an override.

Test signals: framebuffer console/DRM fbdev smoke tests, architecture compile tests with and without `__raw_readq`, and memory attribute validation for mapped framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vmlinux.lds.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/vmlinux.lds.h

Purpose: central macro library used by architecture linker scripts to construct `vmlinux` sections, boundaries, init/exit ranges, percpu layout, debug sections, discard lists, and feature-specific tables.

Important APIs/types/functions: macro families include `TEXT_MAIN`, `DATA_MAIN`, `RO_DATA`, `RW_DATA`, `INIT_TEXT_SECTION`, `INIT_DATA_SECTION`, `BSS_SECTION`, `PERCPU_SECTION`, `EXCEPTION_TABLE`, `NOTES`, `MODINFO`, `BUG_TABLE`, `ORC_UNWIND_TABLE`, `MCOUNT_REC`, `FTRACE_EVENTS`, `TRACE_SYSCALLS`, `LSM_TABLE`, `OF_TABLE`, `ACPI_PROBE_TABLE`, `KERNEL_DTB`, `KUNIT_TABLE`, `DISCARDS`, and `COMMON_DISCARDS`.

Control flow: there is no C runtime flow; the "flow" is link-time expansion. Architecture linker scripts combine these macros to order input sections, emit start/stop symbols, align special regions, keep required tables, and discard sections that must not remain in the final kernel image.

State and persistence: defines persistent kernel image layout and exported section boundary symbols such as initcall ranges, percpu ranges, tracing metadata, exception tables, and BSS boundaries. These symbols are consumed at boot and by runtime subsystems.

Dependencies and integration points: depends heavily on `CONFIG_*` feature gates and linker-script syntax. Integrated with initcalls, ftrace, jump labels, static calls, BPF raw tracepoints, LSM, OF/ACPI probing, KUnit, firmware loader built-ins, BTF, ORC unwinder, module metadata, and percpu allocator setup.

Risks: small ordering or alignment mistakes can break boot, initcall ordering, exception fixups, module metadata, unwinding, percpu offsets, or security hardening. Feature-gated sections must match producer annotations or data can be discarded or orphaned. Linker differences make orphan-section and KEEP semantics important.

Test signals: full kernel link tests for multiple architectures/configurations, boot tests with tracing/ftrace/static-call/percpu enabled, `readelf`/`objdump` inspection of section boundaries, initcall ordering checks, and linker orphan warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/vmlinux.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/include/asm-generic/word-at-a-time.h

Purpose: endian-aware word scanning helpers used by string routines to detect zero bytes efficiently.

Important APIs/types/functions: `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero`, `prep_zero_mask`, `create_zero_mask`, `find_zero`, `zero_bytemask`, and little-endian `count_masked_bytes`.

Control flow: callers load a machine word, call `has_zero()` to produce a mask/bits value, normalize it with `prep_zero_mask()`/`create_zero_mask()`, then use `find_zero()` to locate the first zero byte. Big-endian and little-endian implementations use different arithmetic and mask conventions.

State and persistence: stateless; constants are passed by caller and no data persists outside the computed masks.

Dependencies and integration points: depends on `linux/bitops.h`, `linux/wordpart.h`, and byteorder definitions. Used by optimized `strlen`, `strnlen`, and related word-at-a-time string scans.

Risks: correctness is highly endian- and word-size-sensitive. Off-by-one byte indexes or mask convention mismatches can cause string functions to overrun buffers or misreport lengths.

Test signals: string selftests over aligned/unaligned buffers, big-endian and little-endian build/runtime tests, 32-bit and 64-bit coverage, and KASAN/UBSAN overread detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/asm-generic/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/arm_arch_timer.h -->
# sources/distributed-fs/ceph-client/include/clocksource/arm_arch_timer.h

Purpose: public definitions for the ARM architected timer clocksource/clockevent subsystem.

Important APIs/types/functions: control and CNTHCTL bit masks, `enum arch_timer_reg`, `enum arch_timer_ppi_nr`, `enum arch_timer_spi_nr`, `struct arch_timer_kvm_info`, `struct arch_timer_mem_frame`, `struct arch_timer_mem`, `arch_timer_get_rate`, `arch_timer_read_counter`, `arch_timer_get_kvm_info`, and `arch_timer_evtstrm_available`.

Control flow: consumers query rate/counter/KVM info through exported functions when `CONFIG_ARM_ARCH_TIMER` is enabled; otherwise stubs return zero/false. Register enums and flags drive low-level timer setup in implementation files.

State and persistence: describes memory-mapped timer frame state and KVM-visible timecounter/IRQ state, but stores no state itself.

Dependencies and integration points: depends on `linux/timecounter.h`, bitops, and types. Integrates with ARM/arm64 clocksource drivers, KVM timer virtualization, event stream support, and device-tree/ACPI timer discovery.

Risks: incorrect IRQ enum use or user-access control flags can break timer interrupts, vDSO counter access, or guest timekeeping. Stubbed builds must not accidentally rely on nonzero timer data.

Test signals: ARM boot/timekeeping tests, KVM guest timer tests, clocksource selftests, and config coverage with `CONFIG_ARM_ARCH_TIMER` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/arm_arch_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/hyperv_timer.h -->
# sources/distributed-fs/ceph-client/include/clocksource/hyperv_timer.h

Purpose: Hyper-V clocksource and synthetic timer interface for guest VMs.

Important APIs/types/functions: `HV_MAX_MAX_DELTA_TICKS`, `HV_MIN_DELTA_TICKS`, `hv_stimer_alloc`, cleanup/init ISR helpers, `hv_init_clocksource`, `hv_remap_tsc_clocksource`, `hv_get_tsc_pfn`, `hv_get_tsc_page`, `hv_adj_sched_clock_offset`, and `hv_read_tsc_page_tsc`.

Control flow: under `CONFIG_HYPERV_TIMER`, callers use Hyper-V timer routines and `hv_read_tsc_page_tsc()` loops over the TSC page sequence: read sequence, reject zero, read scale/offset/raw TSC with memory barriers, then retry if the sequence changed. Disabled builds provide safe null/zero stubs.

State and persistence: reads shared hypervisor `ms_hyperv_tsc_page` state and manages synthetic timer allocations in implementation code. This header itself stores none.

Dependencies and integration points: depends on `linux/clocksource.h`, `math64.h`, Hyper-V HVDK definitions, and architecture raw timer access through `<asm/hyperv_timer.h>`.

Risks: sequence/barrier protocol is correctness-critical for monotonic reference time. CPU hotplug cleanup and legacy synthetic interrupt routing must match VMbus behavior. Disabled stubs must not be treated as a usable clocksource.

Test signals: Hyper-V guest boot/timekeeping tests, CPU hotplug with synthetic timers, TSC-page fallback tests, and clocksource watchdog validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/hyperv_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/pxa.h -->
# sources/distributed-fs/ceph-client/include/clocksource/pxa.h

Purpose: declaration for PXA non-device-tree timer initialization.

Important APIs/types/functions: `pxa_timer_nodt_init(int irq, void __iomem *base)`.

Control flow: board/platform setup calls the init routine with an IRQ and mapped OST base; implementation registers clocksource/clockevent handlers.

State and persistence: no state in the header; implementation owns mapped timer state.

Dependencies and integration points: integrates with legacy PXA platform setup and clocksource registration.

Risks: invalid IRQ/base inputs break early timer setup and boot scheduling.

Test signals: PXA board boot tests and legacy non-DT timer initialization coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/samsung_pwm.h -->
# sources/distributed-fs/ceph-client/include/clocksource/samsung_pwm.h

Purpose: shared Samsung PWM timer clocksource definitions.

Important APIs/types/functions: `SAMSUNG_PWM_NUM`, optional exported `samsung_pwm_lock`, `struct samsung_pwm_variant`, and `samsung_pwm_clocksource_init`.

Control flow: platform code passes PWM MMIO base, IRQ array, and variant capabilities to initialize clocksource use of PWM channels. The lock is shared only when the clocksource driver is compiled in.

State and persistence: variant metadata records bit width, divider base, masks, and tint status support. Runtime state is in implementation; lock coordinates shared PWM access.

Dependencies and integration points: depends on spinlock definitions and integrates with Samsung PWM driver and platform timer setup.

Risks: lock visibility differs by config, so users must match `CONFIG_CLKSRC_SAMSUNG_PWM`. Incorrect variant masks can corrupt PWM channels used by other subsystems.

Test signals: Samsung SoC boot tests, PWM driver coexistence tests, and timer interrupt validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/samsung_pwm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-davinci.h -->
# sources/distributed-fs/ceph-client/include/clocksource/timer-davinci.h

Purpose: platform configuration interface for TI DaVinci clocksource/clockevent timer registration.

Important APIs/types/functions: `DAVINCI_TIMER_*` IRQ indexes, `struct davinci_timer_cfg`, and `davinci_timer_register`.

Control flow: board code supplies register and IRQ resources plus optional compare-register offset; implementation registers timer halves as clocksource/clockevent.

State and persistence: the config struct persists only long enough for registration; implementation owns device state.

Dependencies and integration points: uses `linux/clk.h` and resource definitions; integrates with DaVinci platform clock and interrupt setup.

Risks: compare offset mode changes which timer half generates events, so IRQ/resource mismatch causes lost events. Early init failures can stop scheduler clock setup.

Test signals: DaVinci boot tests, clockevent tick tests, and compare-register configuration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-davinci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-goldfish.h -->
# sources/distributed-fs/ceph-client/include/clocksource/timer-goldfish.h

Purpose: register definitions and init declaration for the Goldfish emulator timer.

Important APIs/types/functions: `TIMER_TIME_LOW/HIGH`, `TIMER_ALARM_LOW/HIGH`, `TIMER_IRQ_ENABLED`, `TIMER_CLEAR_ALARM`, `TIMER_ALARM_STATUS`, `TIMER_CLEAR_INTERRUPT`, and `goldfish_timer_init`.

Control flow: driver reads low time before high time to latch a coherent counter, programs alarms through low/high registers, enables IRQs, and clears alarm/interrupt status through dedicated offsets.

State and persistence: hardware/emulator MMIO registers hold current time, alarm, and IRQ state.

Dependencies and integration points: used by emulator platform clocksource setup.

Risks: wrong read ordering can produce inconsistent 64-bit time. Alarm clear/interrupt clear confusion can produce interrupt storms or missed events.

Test signals: Goldfish emulator boot, alarm scheduling tests, and clocksource watchdog checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-goldfish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-riscv.h -->
# sources/distributed-fs/ceph-client/include/clocksource/timer-riscv.h

Purpose: RISC-V clocksource multiplier/shift helper declaration.

Important APIs/types/functions: `riscv_cs_get_mult_shift(u32 *mult, u32 *shift)`.

Control flow: callers request precomputed clocksource conversion values for RISC-V timer cycles to nanoseconds.

State and persistence: no state in header; implementation supplies current conversion state.

Dependencies and integration points: includes Linux types and integrates with RISC-V timer/clocksource code.

Risks: invalid mult/shift values cause time drift or scheduler tick errors.

Test signals: RISC-V boot/timekeeping tests and clocksource conversion validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-riscv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-ti-dm.h -->
# sources/distributed-fs/ceph-client/include/clocksource/timer-ti-dm.h

Purpose: OMAP/TI dual-mode timer constants, offsets, and minimal public timer type.

Important APIs/types/functions: clock source IDs, interrupt bits, trigger modes, capability flags, empty `struct omap_dm_timer`, `omap_dm_timer_modify_idlect_mask`, v1/v2 register offsets, functional register offsets, control bits, and write-pending bit masks.

Control flow: implementation code uses offsets and flags to select clock source, program IRQs, configure autoreload/compare/prescale/capture/PWM, poll write-pending bits, and support v1/v2 register layout differences.

State and persistence: timer hardware registers hold counter/load/match/control/IRQ state. The header only describes their layout.

Dependencies and integration points: depends on delay, I/O, and platform-device headers; integrates with OMAP dmtimer, clocksource, PWM, and platform hwmod code.

Risks: posted write-pending handling is fragile; failing to wait on the right `WP_*` bit can race register updates. v1/v2 offset mismatch can program the wrong register.

Test signals: OMAP boot tests, PWM/timer shared use, tick accuracy, suspend/resume timer retention, and register layout coverage on v1 and v2 IP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-ti-dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-xilinx.h -->
# sources/distributed-fs/ceph-client/include/clocksource/timer-xilinx.h

Purpose: Xilinx AXI timer register definitions and shared private helper interface.

Important APIs/types/functions: register offsets `TCSR*`, `TLR*`, `TCR*`; control bits `TCSR_MDT` through `TCSR_CASC`; `struct xilinx_timer_priv`; `xilinx_timer_tlr_cycles`; and `xilinx_timer_get_period`.

Control flow: drivers program counter control/status registers, convert desired periods to load-register values, and convert current load/control values back to nanosecond periods.

State and persistence: `xilinx_timer_priv` carries regmap, parent clock, and counter maximum. Hardware registers hold active timer state.

Dependencies and integration points: integrates with regmap, clk, device-tree clocksource/clockevent/PWM users.

Risks: callers must ensure cycle counts are representable as TLR values. Up/down and cascade bits affect period math; using wrong `tcsr` flags gives wrong timing.

Test signals: Xilinx timer probe tests, period conversion unit tests, clockevent tick validation, and PWM/clocksource coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/clocksource/timer-xilinx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/acompress.h -->
# sources/distributed-fs/ceph-client/include/crypto/acompress.h

Purpose: asynchronous compression API front-end for kernel crypto algorithms of type `CRYPTO_ALG_TYPE_ACOMPRESS`.

Important APIs/types/functions: request flags for virtual/DMA/non-DMA buffers, `struct acomp_req_chain`, `struct acomp_req`, `struct crypto_acomp`, `struct comp_alg_common`, `crypto_alloc_acomp`, `crypto_alloc_acomp_node`, `crypto_free_acomp`, `crypto_has_acomp`, request alloc/free/clone/on-stack helpers, source/destination setters for SG, DMA virtual, non-DMA virtual, and folios, plus `crypto_acomp_compress` and `crypto_acomp_decompress`.

Control flow: callers allocate a `crypto_acomp`, allocate or stack-initialize an `acomp_req`, configure callback and source/destination buffers, then dispatch compress/decompress. Setter helpers maintain private request flags so implementations can distinguish SG from virtual and DMA-safe from non-DMA buffers.

State and persistence: tfm state includes algorithm callbacks and request context size. Requests hold transient buffer pointers, lengths, callback data, and private chained SG/folio state. Requests are zeroized on free unless stack-allocated.

Dependencies and integration points: depends on core crypto request APIs, scatterlists, folios, slab, atomics, and allocation hooks. Used by compression users that need async hardware or software fallback support.

Risks: private flags must be preserved when callbacks are set; otherwise buffer interpretation can be corrupted. DMA safety flags must match actual memory. `dlen` is both capacity and produced length, so callers must inspect it after completion.

Test signals: async compression/decompression vectors, SG/virtual/folio buffer coverage, DMA/non-DMA fallback tests, request clone/on-stack tests, and memory zeroization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/acompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aead.h -->
# sources/distributed-fs/ceph-client/include/crypto/aead.h

Purpose: authenticated encryption with associated data API for `CRYPTO_ALG_TYPE_AEAD` algorithms.

Important APIs/types/functions: `struct aead_request`, `struct aead_alg`, `struct crypto_aead`, `struct crypto_sync_aead`, `SYNC_AEAD_REQUEST_ON_STACK`, allocation/free helpers, getters for IV/auth/block/align sizes and flags, `crypto_aead_setkey`, `crypto_aead_setauthsize`, `crypto_aead_encrypt`, `crypto_aead_decrypt`, request allocation/free, `aead_request_set_callback`, `aead_request_set_crypt`, and `aead_request_set_ad`.

Control flow: callers allocate a tfm, set key and authentication tag size, allocate/configure a request with SG source/destination, IV, crypt length, and associated-data length, then call encrypt/decrypt. Decrypt returns `-EBADMSG` for authentication failure.

State and persistence: tfm stores auth size and request context size. Requests store transient SG pointers, IV, lengths, callbacks, and per-request context. Algorithm definitions persist callback tables and capability sizes.

Dependencies and integration points: built on `linux/crypto.h` and async crypto requests; used by GCM, CCM, authenc, IPsec AEAD wrappers, and synchronous wrapper users.

Risks: source/destination layout must be `AAD || text || tag` as documented. Destination must reserve tag growth on encryption and include tag on decryption. IPsec RFC variants require an IV copy in associated data. Authentication errors must not be collapsed into generic I/O success.

Test signals: AEAD known-answer tests, in-place/out-of-place SG tests, bad-tag `-EBADMSG` tests, authsize validation, sync wrapper stack-size checks, and IPsec RFC quirk coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aes-cbc-macs.h -->
# sources/distributed-fs/ceph-client/include/crypto/aes-cbc-macs.h

Purpose: library interface for AES-CMAC, AES-XCBC-MAC, and AES-CBC-MAC support.

Important APIs/types/functions: `struct aes_cmac_key`, `struct aes_cmac_ctx`, `aes_cmac_preparekey`, `aes_xcbcmac_preparekey`, `aes_cmac_init`, `aes_cmac_update`, `aes_cmac_final`, one-shot `aes_cmac`, `struct aes_cbcmac_ctx`, `aes_cbcmac_init`, `aes_cbcmac_update`, and `aes_cbcmac_final`.

Control flow: callers prepare a key, initialize a context that points to the prepared key, feed any number of updates, then finalize to produce a block-size MAC and zeroize the context. The one-shot helper wraps this sequence.

State and persistence: key structs retain expanded AES key and finalization subkeys; contexts retain the chaining value and partial block length until finalization.

Dependencies and integration points: depends on `<crypto/aes.h>`. AES-CBC-MAC is explicitly for AES-CCM internals and not a general variable-length MAC.

Risks: context stores a pointer to the key, so key lifetime must exceed context lifetime. CBC-MAC is insecure for arbitrary variable-length messages and should remain restricted to CCM construction.

Test signals: CMAC/XCBC known-answer tests, split-update tests, partial-block finalization tests, context zeroization checks, and CCM integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aes-cbc-macs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aes.h -->
# sources/distributed-fs/ceph-client/include/crypto/aes.h

Purpose: common AES constants, key schedule structures, generic key preparation APIs, and architecture-specific AES entry points.

Important APIs/types/functions: AES size constants, `struct p8_aes_key`, `union aes_enckey_arch`, `union aes_invkey_arch`, `struct aes_enckey`, `struct aes_key`, legacy `struct crypto_aes_ctx`, `aes_check_keylen`, `aes_expandkey`, `aes_preparekey`, `aes_prepareenckey`, `aes_encrypt`, `aes_decrypt`, exported tables, CFB helpers, and many ARM64/PPC/SPARC64 assembly function declarations.

Control flow: callers validate or pass key length to prepare functions, which expand raw keys into encryption-only or encryption/decryption key structures. Block/mode implementations then use prepared keys for per-block or multi-block operations, optionally through arch optimized entry points.

State and persistence: prepared key structures persist round keys or arch-specific raw/optimized formats. Raw keys are caller-owned and must be zeroized by callers when sensitive.

Dependencies and integration points: depends on core crypto types and architecture Kconfig. Used by AES modes, MACs, GCM, CCM, CFB, XTS, and arch crypto implementations.

Risks: architecture-specific union layouts must remain ABI-compatible with assembly code. Encryption-only keys reduce memory/time but cannot support decryption modes. Key length validation failures must be propagated.

Test signals: AES KATs for 128/192/256-bit keys, arch/generic fallback comparison, mode tests using prepared keys, alignment tests, and key zeroization audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/akcipher.h -->
# sources/distributed-fs/ceph-client/include/crypto/akcipher.h

Purpose: public key cipher API for algorithms such as RSA under the kernel crypto framework.

Important APIs/types/functions: `struct akcipher_request`, `struct crypto_akcipher`, `struct akcipher_alg`, `crypto_alloc_akcipher`, tfm/alg casts, request allocation/free/callback/crypt setters, `crypto_akcipher_maxsize`, async `crypto_akcipher_encrypt/decrypt`, sync encrypt/decrypt helpers, and public/private key setters.

Control flow: callers allocate a tfm, set public or private key, allocate and configure a request with source/destination SGs and lengths, then invoke encrypt/decrypt. Inline dispatch calls the algorithm callback. Sync helpers wrap this for virtual buffers.

State and persistence: tfm holds algorithm context and request size. Requests carry transient SGs and lengths; `dst_len` is updated with actual or required output length.

Dependencies and integration points: built on core crypto async requests and scatterlists. Integrated with key handling and public-key users such as signature/encryption code.

Risks: `crypto_akcipher_maxsize()` assumes a successful prior key set; otherwise callbacks may dereference missing key state. Callers must honor updated `dst_len` on insufficient output buffers.

Test signals: RSA KATs, too-small destination tests, key decode error tests, async callback tests, sync wrapper tests, and request zeroization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/akcipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/algapi.h -->
# sources/distributed-fs/ceph-client/include/crypto/algapi.h

Purpose: low-level kernel crypto algorithm/template registration and queue helper API.

Important APIs/types/functions: max block/align constants, `CRYPTO_DMA_ALIGN`, `MODULE_ALIAS_CRYPTO`, `struct crypto_instance`, `struct crypto_template`, `struct crypto_spawn`, `struct crypto_queue`, `struct scatter_walk`, registration/unregistration functions for algorithms/templates/instances, spawn helpers, attr parsing helpers, crypto queue operations, `crypto_inc`, tfm/instance context helpers, inherited flag helpers, notifier APIs, `crypto_request_complete`, and request flag/type helpers.

Control flow: algorithm providers register `crypto_alg` objects or templates; templates grab child spawns, create instances, and register them. Async providers enqueue/dequeue requests and complete callbacks through `crypto_request_complete`.

State and persistence: registration creates global crypto algorithm/template state. Queues track pending requests and backlog. Instances contain private context and spawn relationships.

Dependencies and integration points: foundational for all crypto providers, templates, and async engines. Depends on list, workqueue, module, and crypto core structures.

Risks: registration lifetime, module references, and spawn `dead/registered` transitions are subtle. Incorrect inherited flag masking can expose blocking or fallback behavior incorrectly. Queue backlog handling affects async caller semantics.

Test signals: crypto manager registration tests, template instance creation/removal tests, module autoload alias checks, async queue/backlog tests, and lockdep around provider unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/algapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/arc4.h -->
# sources/distributed-fs/ceph-client/include/crypto/arc4.h

Purpose: ARC4 stream cipher constants, context, and primitive operations.

Important APIs/types/functions: key/block size macros, `struct arc4_ctx`, `arc4_setkey`, and `arc4_crypt`.

Control flow: caller initializes permutation state with `arc4_setkey`, then encrypts/decrypts by XORing the generated keystream via `arc4_crypt`.

State and persistence: `arc4_ctx` contains mutable S-box and indices `x/y`; encryption advances state.

Dependencies and integration points: lightweight primitive used by legacy crypto users.

Risks: ARC4 is cryptographically obsolete for new designs; state reuse or weak keys are severe. Context is mutable and not reusable concurrently without locking/copying.

Test signals: ARC4 known-answer tests, streaming split equivalence tests, and deprecation policy checks for new users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/arc4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aria.h -->
# sources/distributed-fs/ceph-client/include/crypto/aria.h

Purpose: ARIA block cipher constants, context, S-box tables, inline round transformations, and crypto API key/encrypt/decrypt declarations.

Important APIs/types/functions: ARIA size constants, `struct aria_ctx`, static S-box/precomputed tables, `rotl32`, `rotr32`, `bswap32`, `get_u8`, `make_u32`, `aria_m`, S-box layer helpers, `aria_diff_word`, `aria_diff_byte`, `aria_add_round_key`, odd/even substitution-diffusion helpers, `aria_gsrk`, `aria_encrypt`, `aria_decrypt`, and `aria_set_key`.

Control flow: key setup fills encryption/decryption round keys and round count. Encrypt/decrypt implementations apply add-round-key and alternating S-box/diffusion layers using the inline helpers.

State and persistence: `aria_ctx` persists round keys, round count, and key length. Static lookup tables are read-only implementation data.

Dependencies and integration points: includes crypto algapi/module/init/types/errno and byteorder. Used by ARIA cipher provider and mode wrappers.

Risks: large static tables and inline transforms must match RFC 5794 exactly; byte ordering mistakes break all vectors. Table-based S-boxes may be side-channel sensitive depending on usage context.

Test signals: ARIA known-answer tests for 128/192/256-bit keys, encryption/decryption inverse tests, endian coverage, and crypto API setkey failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/aria.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/authenc.h -->
# sources/distributed-fs/ceph-client/include/crypto/authenc.h

Purpose: key parsing helpers for authenc-style AEAD wrappers, including IPsec and Kerberos variants.

Important APIs/types/functions: `CRYPTO_AUTHENC_KEYA_*`, `struct crypto_authenc_key_param`, `struct crypto_authenc_keys`, `crypto_authenc_extractkeys`, and `crypto_krb5enc_extractkeys`.

Control flow: callers pass a composite key blob; extraction helpers split it into authentication and encryption key pointers/lengths.

State and persistence: output key struct points into caller-provided key memory, so lifetime follows the original key buffer.

Dependencies and integration points: used by `authenc(hmac(...), cipher)` and related AEAD templates.

Risks: malformed key blobs can produce wrong key boundaries. Because outputs are borrowed pointers, callers must not free or overwrite the backing key prematurely.

Test signals: authenc key decode vectors, invalid length/parameter tests, and IPsec/Kerberos AEAD integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/authenc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/b128ops.h -->
# sources/distributed-fs/ceph-client/include/crypto/b128ops.h

Purpose: common 128-bit block element representations and XOR helpers.

Important APIs/types/functions: `be128`, `le128`, `be128_xor`, and `le128_xor`.

Control flow: inline helpers XOR two 128-bit values word-by-word into a result.

State and persistence: none beyond caller-supplied 128-bit values.

Dependencies and integration points: used by GF(2^128), XTS/GHASH/LRW-style operations and any code needing typed endian 128-bit blocks.

Risks: endian-specific structs are not interchangeable; using `be128` where `le128` is expected changes polynomial interpretation.

Test signals: finite-field mode KATs and endian conversion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/b128ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/blake2b.h -->
# sources/distributed-fs/ceph-client/include/crypto/blake2b.h

Purpose: BLAKE2b hash library interface with keyed and unkeyed modes.

Important APIs/types/functions: `enum blake2b_lengths`, `struct blake2b_ctx`, IV constants, `__blake2b_init`, `blake2b_init`, `blake2b_init_key`, `blake2b_update`, `blake2b_final`, and one-shot `blake2b`.

Control flow: initialization seeds state with IV and parameter block; optional key is buffered as the first block; callers update with data and finalize to write `outlen` bytes while zeroizing context.

State and persistence: context stores hash state, counters, finalization flags, partial block buffer, buffer length, and output length.

Dependencies and integration points: depends on bug checks, types, and string helpers. Used by code needing a direct BLAKE2b primitive outside the crypto API tfm model.

Risks: debug `WARN_ON` checks do not enforce validity in production; callers must respect output/key length limits and non-null buffers. Context is sensitive and should not be copied after keying unless intended.

Test signals: BLAKE2b KATs, keyed/unkeyed vectors, split update tests, invalid-parameter debug tests, and context zeroization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/blake2b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/blake2s.h -->
# sources/distributed-fs/ceph-client/include/crypto/blake2s.h

Purpose: BLAKE2s hash library interface with keyed and unkeyed modes.

Important APIs/types/functions: `enum blake2s_lengths`, `struct blake2s_ctx`, IV constants, `__blake2s_init`, `blake2s_init`, `blake2s_init_key`, `blake2s_update`, `blake2s_final`, and one-shot `blake2s`.

Control flow: initialization configures IV-derived state and buffers an optional key block; update processes message bytes; finalization emits the configured digest length and zeroizes context.

State and persistence: context stores 32-bit state words, counters, finalization words, partial block, buffer length, and output length.

Dependencies and integration points: depends on kconfig, bug, types, and string helpers; used by in-kernel direct BLAKE2s users.

Risks: production callers must validate lengths because debug warnings are not hard errors. Keyed contexts contain secret material in the buffer until finalization.

Test signals: BLAKE2s KATs, keyed vectors, incremental update equivalence, and finalization zeroization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/blake2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/blowfish.h -->
# sources/distributed-fs/ceph-client/include/crypto/blowfish.h

Purpose: Blowfish cipher constants, context, and key setup declaration.

Important APIs/types/functions: `BF_BLOCK_SIZE`, min/max key sizes, `struct bf_ctx`, and `blowfish_setkey`.

Control flow: crypto API setkey fills P-array and S-box state in `bf_ctx`; mode implementations use that context for block operations elsewhere.

State and persistence: `bf_ctx` stores expanded key material in P and S arrays.

Dependencies and integration points: integrates with Linux crypto block cipher providers and modes.

Risks: Blowfish has a 64-bit block size and is not suitable for high-volume modern encryption modes. Expanded state is large and sensitive.

Test signals: Blowfish KATs, key length rejection tests, and mode-level crypto tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/blowfish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cast5.h -->
# sources/distributed-fs/ceph-client/include/crypto/cast5.h

Purpose: CAST5 cipher constants, context, and primitive operation declarations.

Important APIs/types/functions: `CAST5_BLOCK_SIZE`, key size bounds, `struct cast5_ctx`, `cast5_setkey`, `__cast5_encrypt`, and `__cast5_decrypt`.

Control flow: setkey fills masking/rotation subkeys and selects reduced/full rounds; block helpers encrypt/decrypt one block with prepared context.

State and persistence: context stores 16 masking subkeys, 16 rotation subkeys, and round selector.

Dependencies and integration points: depends on CAST common S-box declarations and crypto core types.

Risks: 64-bit block size limits safe data volume. Round selector must match RFC 2144 key-size behavior.

Test signals: CAST5 known-answer tests, reduced-round key tests, and crypto mode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cast5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cast6.h -->
# sources/distributed-fs/ceph-client/include/crypto/cast6.h

Purpose: CAST6 cipher constants, context, and primitive operation declarations.

Important APIs/types/functions: `CAST6_BLOCK_SIZE`, key size bounds, `struct cast6_ctx`, `__cast6_setkey`, `cast6_setkey`, `__cast6_encrypt`, and `__cast6_decrypt`.

Control flow: setkey expands key into 12 rounds of masking and rotation subkeys; encrypt/decrypt operate on a block using the context.

State and persistence: context stores 12x4 masking words and 12x4 rotation bytes.

Dependencies and integration points: uses CAST common S-boxes and crypto API setkey wrapper.

Risks: key schedule dimensions must match CAST6 spec; mode users must account for 16-byte block size and alignment.

Test signals: CAST6 KATs, key length validation, and crypto API provider tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cast6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cast_common.h -->
# sources/distributed-fs/ceph-client/include/crypto/cast_common.h

Purpose: shared CAST cipher S-box table declarations.

Important APIs/types/functions: external arrays `cast_s1`, `cast_s2`, `cast_s3`, and `cast_s4`.

Control flow: none in header; CAST5/CAST6 implementations index these tables during key schedule and rounds.

State and persistence: read-only global table data defined elsewhere.

Dependencies and integration points: included by CAST cipher headers/implementations.

Risks: table definitions must be linked exactly once and match the CAST specifications.

Test signals: CAST5/CAST6 KATs and link-time coverage for table providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cast_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/chacha.h -->
# sources/distributed-fs/ceph-client/include/crypto/chacha.h

Purpose: common ChaCha/XChaCha stream cipher constants, state setup, block, HChaCha, and encryption helpers.

Important APIs/types/functions: IV/key/block size macros, `struct chacha_state`, `chacha_block_generic`, `chacha20_block`, `hchacha_block_generic`, `hchacha_block`, constants enum, `chacha_init_consts`, `chacha_init`, `chacha_crypt`, `chacha20_crypt`, and `chacha_zeroize_state`.

Control flow: initialize constants/key/counter/nonce into state, generate blocks with a selected round count, XOR keystream with input in `chacha_crypt`, and zeroize state when done.

State and persistence: `chacha_state` stores the mutable 16-word state including counter and nonce; encryption advances counter in implementation.

Dependencies and integration points: used by ChaCha20, XChaCha, and ChaCha20-Poly1305 code; depends on unaligned little-endian access and string zeroization.

Risks: nonce/counter reuse with the same key is catastrophic. Round-count variants must be chosen intentionally. State contains key material and should be zeroized.

Test signals: RFC7539 ChaCha20 vectors, XChaCha/HChaCha vectors, split encryption tests, counter rollover tests, and zeroization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/chacha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/chacha20poly1305.h -->
# sources/distributed-fs/ceph-client/include/crypto/chacha20poly1305.h

Purpose: direct ChaCha20-Poly1305 and XChaCha20-Poly1305 AEAD helper declarations.

Important APIs/types/functions: nonce/key/tag length enum, buffer encrypt/decrypt helpers, XChaCha variants, and in-place scatterlist encrypt/decrypt helpers.

Control flow: encrypt writes ciphertext and tag; decrypt authenticates and returns `bool` success before plaintext should be trusted. SG helpers operate in place over scatterlists.

State and persistence: no persistent state in header; keys/nonces are caller-owned and transient.

Dependencies and integration points: depends on scatterlists and is used by direct library AEAD consumers outside the generic AEAD request API.

Risks: nonce uniqueness is mandatory. Decrypt return value is `__must_check`; ignoring it can accept forged plaintext. Source length must account for tag placement expected by implementation.

Test signals: RFC8439 and XChaCha vectors, forged tag rejection, SG in-place vectors, empty AAD/plaintext cases, and nonce-size validation at call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/chacha20poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cryptd.h -->
# sources/distributed-fs/ceph-client/include/crypto/cryptd.h

Purpose: software async crypto daemon wrapper interface for AEAD algorithms.

Important APIs/types/functions: `struct cryptd_aead`, `__cryptd_aead_cast`, `cryptd_alloc_aead`, `cryptd_aead_child`, `cryptd_aead_queued`, and `cryptd_free_aead`.

Control flow: callers allocate a cryptd AEAD wrapper for a child algorithm, submit through normal AEAD APIs, query whether work is queued without CPU migration, and free wrapper state.

State and persistence: wrapper embeds `crypto_aead` base and maintains child/queue state in implementation.

Dependencies and integration points: depends on AEAD API; integrates with cryptd worker threads to provide asynchronous behavior for synchronous algorithms.

Risks: `cryptd_aead_queued()` requires CPU stability, so callers must disable migration or otherwise satisfy that condition. Child lifetime must track wrapper lifetime.

Test signals: async completion tests, child algorithm passthrough vectors, CPU migration/queue tests, and wrapper free under pending work checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/cryptd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ctr.h -->
# sources/distributed-fs/ceph-client/include/crypto/ctr.h

Purpose: constants for CTR mode and RFC3686 nonce/IV/block sizing.

Important APIs/types/functions: `CTR_RFC3686_NONCE_SIZE`, `CTR_RFC3686_IV_SIZE`, and `CTR_RFC3686_BLOCK_SIZE`.

Control flow: none; consumers use constants to parse keys/IVs and construct counter blocks.

State and persistence: none.

Dependencies and integration points: used by CTR skcipher implementations and IPsec RFC3686 wrappers.

Risks: nonce/IV/counter layout mistakes cause keystream reuse or interoperability failures.

Test signals: CTR/RFC3686 known-answer tests and IV construction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ctr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/curve25519.h -->
# sources/distributed-fs/ceph-client/include/crypto/curve25519.h

Purpose: Curve25519 scalar multiplication and key generation helper interface.

Important APIs/types/functions: `CURVE25519_KEY_SIZE`, `curve25519_generic`, optimized `curve25519`, `curve25519_generate_public`, `curve25519_clamp_secret`, and `curve25519_generate_secret`.

Control flow: secret generation fills 32 random bytes then clamps them. Public/shared computation multiplies secret scalar by basepoint or peer point and returns `bool` success.

State and persistence: no global state; secrets/public keys are caller buffers.

Dependencies and integration points: depends on kernel random bytes and is used by key agreement protocols such as WireGuard-like code.

Risks: caller must check boolean result and protect secret buffers. Secret clamping is required before use. Random generation waits for initialized RNG.

Test signals: Curve25519 test vectors, public-key generation tests, all-zero/invalid point handling, RNG readiness tests, and `__must_check` enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/curve25519.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/des.h -->
# sources/distributed-fs/ceph-client/include/crypto/des.h

Purpose: DES and 3DES-EDE constants, contexts, block operations, and key expansion declarations.

Important APIs/types/functions: DES/3DES key/block/expanded-key sizes, `struct des_ctx`, `struct des3_ede_ctx`, encrypt/decrypt functions, `des_expand_key`, and `des3_ede_expand_key`.

Control flow: callers expand a raw key into schedule state, then call encrypt/decrypt for one block. Expansion returns `-EINVAL` for rejected keys and `-ENOKEY` for weak accepted keys, with FIPS changing weak-key handling for 3DES.

State and persistence: expanded key schedules persist in context structs and are sensitive.

Dependencies and integration points: used by legacy DES/3DES crypto providers and modes.

Risks: DES is obsolete and 3DES has limited security margin and block-size constraints. Weak-key and FIPS behavior must be propagated correctly.

Test signals: DES/3DES KATs, weak-key rejection tests, FIPS-mode tests, and mode-level block cipher tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/des.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/df_sp80090a.h -->
# sources/distributed-fs/ceph-client/include/crypto/df_sp80090a.h

Purpose: SP800-90A CTR-DRBG derivation-function helper declarations.

Important APIs/types/functions: `crypto_drbg_ctr_df_datalen` and `crypto_drbg_ctr_df`.

Control flow: callers compute scratch data length from state/block sizes, then invoke the derivation function with an AES encryption key, output length, seed list, block length, and state length.

State and persistence: no state in header; caller supplies AES key and working buffers.

Dependencies and integration points: depends on internal cipher, AES key structures, and seed lists. Used by CTR-DRBG seeding/reseeding logic.

Risks: buffer sizing must match `crypto_drbg_ctr_df_datalen`; undersizing can corrupt memory in implementation. Correct seed list construction is required for SP800-90A compliance.

Test signals: DRBG CAVP vectors, scratch-size tests, reseed tests, and boundary cases for state/block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/df_sp80090a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/dh.h -->
# sources/distributed-fs/ceph-client/include/crypto/dh.h

Purpose: Diffie-Hellman private key parameter encoding helpers for the KPP API.

Important APIs/types/functions: `struct dh`, `crypto_dh_key_len`, `crypto_dh_encode_key`, `crypto_dh_decode_key`, and `__crypto_dh_decode_key`.

Control flow: callers package key/p/g buffers and sizes into a packet representation for `crypto_kpp_set_secret`, or decode a packet into borrowed pointers inside the original buffer.

State and persistence: decoded fields point into the packet buffer; the packet must outlive the decoded `struct dh` use.

Dependencies and integration points: used by DH KPP implementations and callers preparing DH secrets.

Risks: invalid sizes or truncated buffers must be rejected. Borrowed pointer lifetime is easy to misuse. Parameter validation beyond packet structure belongs to algorithm implementations.

Test signals: encode/decode round-trip tests, truncated buffer tests, invalid size tests, and KPP DH shared-secret vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/dh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/drbg.h -->
# sources/distributed-fs/ceph-client/include/crypto/drbg.h

Purpose: internal/public structures and helpers for NIST SP800-90A DRBG implementations.

Important APIs/types/functions: `drbg_flag_t`, `struct drbg_core`, `struct drbg_state_ops`, `struct drbg_test_data`, `enum drbg_seed_state`, `struct drbg_state`, `drbg_statelen`, `drbg_blocklen`, `drbg_keylen`, max limit helpers, test wrappers for `crypto_rng_generate/reset`, DRBG type/strength flags, and prefix enum.

Control flow: DRBG operations are mediated by state ops for update/generate/crypto init/fini. RNG wrapper helpers pass additional input and test entropy into the crypto RNG API. Seed state tracks unseeded, partial, and full seeding.

State and persistence: `drbg_state` is substantial persistent RNG state: mutex, V/C/key material, reseed counters/thresholds, scratch buffers, CTR cipher/request/wait/SGs, seed status, last seed time, prediction resistance, FIPS continuous-test state, Jitter RNG handle, ops/core pointers, and test data.

Dependencies and integration points: depends on random, scatterlist, hash, skcipher, internal DRBG/RNG headers, FIPS, mutexes, lists, and workqueues. Integrates with kernel RNG crypto API.

Risks: RNG state is highly sensitive; locking, reseed thresholds, FIPS continuous tests, and partial-seed handling are security-critical. Test-only entropy injection must not leak into production paths.

Test signals: SP800-90A CAVP vectors for hash/HMAC/CTR modes, reseed limit tests, prediction-resistance tests, FIPS continuous-test failures, partial entropy boot tests, and lockdep around generate/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/drbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ecc_curve.h -->
# sources/distributed-fs/ceph-client/include/crypto/ecc_curve.h

Purpose: elliptic curve metadata structures and lookup helpers.

Important APIs/types/functions: `struct ecc_point`, `struct ecc_curve`, `ecc_get_curve`, and `ecc_get_curve25519`.

Control flow: callers request curve parameters by ID or Curve25519 accessor and receive a const curve descriptor or NULL.

State and persistence: curve descriptors point to static field/order/parameter arrays and generator points.

Dependencies and integration points: used by ECDH/ECDSA/ECC implementations and keyed public-key code.

Risks: returned curve pointers are const shared data; callers must not mutate them. Curve IDs must match `ecdh.h` definitions. Header guard typo is benign but notable.

Test signals: curve lookup tests, ECDH/ECDSA vectors for supported curves, and NULL handling for unknown IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ecc_curve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ecdh.h -->
# sources/distributed-fs/ceph-client/include/crypto/ecdh.h

Purpose: ECDH private key packet helpers and curve ID definitions for the KPP API.

Important APIs/types/functions: curve ID macros for NIST P-192/P-256/P-384/P-521, `struct ecdh`, `crypto_ecdh_key_len`, `crypto_ecdh_encode_key`, and `crypto_ecdh_decode_key`.

Control flow: callers encode a private key packet before `crypto_kpp_set_secret`, or decode packet data into an `ecdh` struct whose key pointer references the packet buffer.

State and persistence: decoded key memory is borrowed from the input buffer.

Dependencies and integration points: used by ECDH KPP implementations and callers; curve metadata links to `ecc_curve.h`.

Risks: only key bytes are represented here; curve selection is handled by algorithm context/ID elsewhere. Borrowed pointer lifetime and length validation are key correctness risks.

Test signals: encode/decode round trips, truncated packet tests, KPP ECDH vectors, and unsupported curve handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ecdh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/engine.h -->
# sources/distributed-fs/ceph-client/include/crypto/engine.h

Purpose: crypto hardware engine queue/registration API for offloaded AEAD, hash, akcipher, KPP, and skcipher algorithms.

Important APIs/types/functions: `struct crypto_engine_op`, engine algorithm wrapper structs for each algorithm class, transfer helpers, finalize helpers, start/stop/allocation/exit functions, and register/unregister helpers for single and array algorithm providers.

Control flow: providers wrap algorithm callbacks with a `do_one_request` engine operation, register engine algorithms, transfer incoming crypto requests to the engine queue, and call finalize helpers when hardware/software processing completes.

State and persistence: opaque `struct crypto_engine` owns queues, worker state, retry behavior, and device association in implementation. Wrapper alg structs persist registration metadata and engine operation callbacks.

Dependencies and integration points: depends on AEAD, akcipher, hash, KPP, skcipher APIs, and device model. Used by hardware accelerator drivers.

Risks: finalize must be called exactly once per transferred request. Start/stop and unregister ordering must drain or reject queued work safely. Request type mismatches can corrupt container casts.

Test signals: hardware-driver selftests, crypto manager vectors through engine providers, queue full/retry tests, unregister-with-inflight tests, and runtime PM/error-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/gcm.h -->
# sources/distributed-fs/ceph-client/include/crypto/gcm.h

Purpose: AES-GCM helper constants, auth/tag validation, context, and direct AES-GCM routines.

Important APIs/types/functions: `GCM_AES_IV_SIZE`, RFC4106/RFC4543 IV sizes, `crypto_gcm_check_authsize`, `crypto_rfc4106_check_authsize`, `crypto_ipsec_check_assoclen`, `struct aesgcm_ctx`, `aesgcm_expandkey`, `aesgcm_encrypt`, and `aesgcm_decrypt`.

Control flow: callers validate tag and associated-data sizes, expand AES and GHASH keys into context, then encrypt/decrypt with IV, associated data, ciphertext/plaintext length, and tag. Decrypt returns bool authentication result.

State and persistence: context stores prepared GHASH key, AES encryption key, and auth tag size.

Dependencies and integration points: depends on AES and GF128 hash helpers. Used by direct GCM and IPsec GCM implementations.

Risks: GCM nonce reuse is catastrophic. Tag sizes are constrained and must be validated. Decrypt result must be checked before using plaintext.

Test signals: AES-GCM KATs, RFC4106/RFC4543 assoclen/tag tests, forgery rejection, and nonce/IV size checks at call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/gcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/gf128hash.h -->
# sources/distributed-fs/ceph-client/include/crypto/gf128hash.h

Purpose: GHASH and POLYVAL finite-field hashing interface over GF(2^128).

Important APIs/types/functions: `POLYVAL_*` constants, `struct polyval_elem`, `struct ghash_key`, `struct polyval_key`, `struct ghash_ctx`, `struct polyval_ctx`, key preparation functions, init/import/export helpers, update/final functions, and one-shot `ghash`/`polyval`.

Control flow: callers prepare a key, initialize a context pointing to the key, feed arbitrary-length data, and finalize with automatic zero-padding of the last partial block. POLYVAL supports block-aligned accumulator export/import.

State and persistence: key structs store raw/precomputed hash keys with architecture-specific layouts. Contexts store key pointer, accumulator, and partial byte count. Contexts are zeroized on finalization by implementation.

Dependencies and integration points: depends on GHASH constants and string/types. Used by GCM, AES-GCM-SIV/POLYVAL-style constructions, and architecture-optimized GF hashing.

Risks: key lifetime must outlive contexts. GHASH and POLYVAL use different byte/bit conventions; mixing formats breaks authentication. Architecture-specific key layouts must match assembly implementations.

Test signals: GHASH/POLYVAL vectors, partial-block padding tests, export/import round trips, arch/generic comparison, and GCM integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/gf128hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/gf128mul.h -->
# sources/distributed-fs/ceph-client/include/crypto/gf128mul.h

Purpose: GF(2^128) multiplication primitives and table helpers for multiple endian/bit-order conventions.

Important APIs/types/functions: `gf128mul_lle`, `gf128mul_mask_from_bit`, `gf128mul_x_lle`, `gf128mul_x_bbe`, `gf128mul_x_ble`, `gf128mul_x8_ble`, `struct gf128mul_64k`, `gf128mul_init_64k_bbe`, `gf128mul_free_64k`, and `gf128mul_64k_bbe`.

Control flow: inline multiply-by-x helpers load endian-specific words, compute reduction masks branchlessly, shift the field element, and conditionally apply reduction constants. Table helpers precompute 64 KiB lookup state for faster bbe multiplication.

State and persistence: table objects allocate precomputed multiplication tables and must be freed. Inline helpers are stateless.

Dependencies and integration points: depends on byteorder, `b128ops`, and slab allocation. Used by GCM/GHASH, XTS, LRW, and other block modes over GF(2^128).

Risks: endian convention confusion (`lle`, `bbe`, `ble`) is the dominant correctness risk. Table allocation failure must be handled. Constant-time mask logic should not be replaced by branches in sensitive paths.

Test signals: GF multiplication vectors for all conventions, XTS/GHASH/LRW mode tests, big/little-endian runtime coverage, table-vs-generic comparison, and allocation failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/gf128mul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ghash.h -->
# sources/distributed-fs/ceph-client/include/crypto/ghash.h

Purpose: GHASH block and digest size constants.

Important APIs/types/functions: `GHASH_BLOCK_SIZE` and `GHASH_DIGEST_SIZE`, both 16 bytes.

Control flow: none.

State and persistence: none.

Dependencies and integration points: included by GHASH/POLYVAL and GCM code for common sizing.

Risks: consumers must still respect GHASH format and padding rules defined elsewhere; this header only provides sizes.

Test signals: compile-time size assertions in GHASH/GCM users and AEAD vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/ghash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/hash.h -->
# sources/distributed-fs/ceph-client/include/crypto/hash.h

Purpose: kernel crypto API definitions for asynchronous hash (`ahash`) and synchronous hash (`shash`) algorithms and requests.

Important APIs/types/functions: `CRYPTO_AHASH_REQ_VIRT`, `struct hash_alg_common`, `struct ahash_request`, `struct ahash_alg`, `struct shash_desc`, `struct shash_alg`, `struct crypto_ahash`, `struct crypto_shash`, stack/clone allocation macros, allocation/free/clone/has helpers, digest/block/state/request size getters, flag helpers, setkey/init/update/final/finup/digest/export/import functions, request setters for SG and virtual buffers, and shash descriptor helpers.

Control flow: ahash callers allocate a tfm and request, set callback and data buffers, then call init/update/final/finup/digest or export/import state. shash callers allocate a tfm, provide a descriptor, and call init/update/final or one-shot digest. Some inline final/update helpers reduce to `finup` with zero data or null output.

State and persistence: tfms store algorithm context; requests/descriptors store transient operation state plus implementation-private context. Export/import APIs persist intermediate hash state in caller buffers. Sensitive request/descriptor memory is zeroized by free/zero helpers.

Dependencies and integration points: foundational for all kernel hash/HMAC/KDF users, DRBG, signatures, integrity, and crypto engine wrappers. Depends on scatterlists, slab, string, and core crypto APIs.

Risks: request flags include private virtual-buffer bits that callback setters must preserve. Stack request macros require conservative maximum sizes. Export/import state sizes must match algorithm state. Callers must allocate digest buffers of the advertised digest size.

Test signals: ahash and shash crypto manager vectors, SG and virtual-buffer request tests, keyed hash setkey tests, export/import resume tests, async callback/backlog tests, stack request coverage, and zeroization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/hash_info.h -->
# sources/distributed-fs/ceph-client/include/crypto/hash_info.h

Purpose: hash algorithm metadata constants and lookup arrays.

Important APIs/types/functions: digest-size constants for RIPEMD, Whirlpool, Tiger, and SM3-256 not defined elsewhere; external arrays `hash_algo_name` and `hash_digest_size`.

Control flow: consumers index arrays by `HASH_ALGO_*` IDs from UAPI to map IDs to names and digest lengths.

State and persistence: arrays are read-only global metadata defined elsewhere.

Dependencies and integration points: includes SHA, MD5, Streebog, and UAPI hash info headers. Used by integrity, signature, and key subsystems that serialize hash algorithm IDs.

Risks: array ordering must match UAPI `HASH_ALGO__LAST`; mismatches break ABI interpretation of signatures or measurements.

Test signals: compile-time/boot checks for array length, integrity subsystem tests, and hash ID/name/digest-size mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/hash_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/hmac.h -->
# sources/distributed-fs/ceph-client/include/crypto/hmac.h

Purpose: HMAC inner and outer pad byte constants.

Important APIs/types/functions: `HMAC_IPAD_VALUE` (`0x36`) and `HMAC_OPAD_VALUE` (`0x5c`).

Control flow: none; HMAC implementations XOR normalized keys with these constants to derive inner and outer pads.

State and persistence: none.

Dependencies and integration points: used by HMAC implementations and tests.

Risks: constants are fundamental to HMAC; any change breaks compatibility. Header does not define full HMAC API.

Test signals: HMAC known-answer tests across hash functions and compile-time use by HMAC providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/crypto/hmac.h -->
