# sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt.c

## Purpose
Defines the default x86 paravirtualization operation table for bare hardware and provides native fallback functions that paravirtual backends can override or patch.

## APIs, Types, And Functions
Exports `pv_info` and `pv_ops`. Important functions and stubs include `paravirt_ret0`, `default_banner()`, native IRQ flag helpers (`pv_native_save_fl`, `pv_native_irq_disable`, `pv_native_irq_enable`), CR2/CR3/debug register wrappers, `pv_native_safe_halt()`, and paravirt page-table operation defaults.

## Control Flow
At boot, `pv_info` identifies the environment as bare hardware unless a hypervisor overwrites it. `default_banner()` prints the chosen paravirt provider. `pv_ops` is initialized with native CPU, IRQ, halt, TLB, page-table, lazy-MMU, and fixmap operations, with XXL-only entries populated when configured. Paravirt patching machinery later rewrites call sites to these entries or hypervisor replacements.

## State And Persistence
The central persistent state is the global `pv_ops` template and `pv_info`. Some entries are callee-save asm thunks, and identity PTE conversion helpers are encoded as paravirt callee-save patch targets. These values persist after init and influence core low-level operations.

## Dependencies And Integration
Integrates with `asm/paravirt.h`, descriptor loading, TLB flushing, CR/MSR access, I/O bitmap operations from `process.c`, APIC and delay code, and static/paravirt patch infrastructure. Hypervisor code such as Xen or KVM paravirt paths replace fields before or during alternatives/paravirt patching.

## Risks And Test Signals
Incorrect defaults can break boot on bare metal or hypervisors because these hooks sit under interrupt, MMU, and CPU control paths. The functions marked `noinstr`/`NOKPROBE_SYMBOL` are sensitive to tracing and kprobe recursion. Test signals include successful boot across bare metal and paravirt guests, paravirt patch validation, TLB/MMU stress, and interrupt flag/halt behavior under tracing.
