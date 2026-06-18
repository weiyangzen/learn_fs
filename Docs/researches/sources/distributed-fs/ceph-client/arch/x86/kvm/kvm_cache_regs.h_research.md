<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_cache_regs.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_cache_regs.h

### Purpose
`kvm_cache_regs.h` provides inline helpers for KVM's x86 vCPU register cache. It centralizes direct GPR accessors, lazy caching and dirty tracking for special registers, CR0/CR3/CR4/PDPTR reads, RIP/RSP helpers, EDX:EAX composition, and guest-mode state transitions.

### Important APIs, Types, And Functions
The `BUILD_KVM_GPR_ACCESSORS()` macro creates raw array accessors for RAX, RBX, RCX, RDX, RBP, RSI, RDI, and on x86-64 R8-R15. Cache helpers include `kvm_register_is_available()`, `kvm_register_is_dirty()`, `kvm_register_mark_available()`, `kvm_register_mark_dirty()`, `kvm_register_test_and_mark_available()`, `kvm_register_read_raw()`, and `kvm_register_write_raw()`. Control-register helpers include `kvm_read_cr0_bits()`, `kvm_is_cr0_bit_set()`, `kvm_read_cr0()`, `kvm_read_cr3()`, `kvm_read_cr4_bits()`, `kvm_is_cr4_bit_set()`, and `kvm_read_cr4()`. Mode helpers are `enter_guest_mode()`, `leave_guest_mode()`, and `is_guest_mode()`.

### Control Flow
Reads check availability bits and call `kvm_x86_call(cache_reg)` on demand. Writes update cached fields and mark the register dirty so VMX/SVM code can write back before guest entry. CR0/CR4 bit reads only force a cache fill for guest-owned bits that can reside in hardware state. `leave_guest_mode()` also converts a pending EOI-exitmap load into a KVM request. Assertions restrict register-cache use from interrupt context except for bounded PMI/NMI VM-exit handling.

### State, Persistence, And Dependencies
State is stored in `vcpu->arch.regs`, `regs_avail`, `regs_dirty`, `cr0`, `cr3`, `cr4`, guest-owned bit masks, PDPTR arrays in the active MMU, `hflags`, and statistics. Dependencies include KVM x86 ops, lockdep, bit operations, CR bit definitions, guest-mode flags, and PMI-in-guest checks.

### Integration Points
This header is used across x86 KVM instruction emulation, MSR/hypercall handling, VMX/SVM run paths, nested virtualization, MMU code, and event injection. Hyper-V code relies on GPR helpers for hypercall ABI decoding and result return.

### Risks
The cache availability/dirty invariant is critical: unavailable+dirty is invalid, and writes must mark dirty. Interrupt-context misuse can read stale state or clobber pending writes. Raw register helpers ignore current guest mode operand width, so using them where architectural truncation is required can be wrong. Guest-mode transitions must preserve EOI-exitmap reloads for nested/APIC behavior.

### Test Signals
Exercise register caching through instruction emulation, hypercalls, CR reads/writes with guest-owned bits, PDPTR reads on SVM, nested guest entry/exit, PMI/NMI exits, `leave_guest_mode()` EOI-exitmap requests, and debug assertions under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_cache_regs.h -->
