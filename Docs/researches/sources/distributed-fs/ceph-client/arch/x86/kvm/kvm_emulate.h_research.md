<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_emulate.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_emulate.h

### Purpose
`kvm_emulate.h` is the public internal interface for KVM's generic x86 instruction decoder and emulator. It defines exception reporting, memory/register operation callbacks, operand and decode-cache structures, emulation modes, intercept metadata, return codes, and register-cache helpers used by the emulator implementation and KVM x86 callers.

### Important APIs, Types, And Functions
Major types include `struct x86_exception`, `struct x86_instruction_info`, `struct x86_emulate_ops`, `struct operand`, `struct fetch_cache`, `struct read_cache`, `enum x86emul_mode`, `struct x86_emulate_ctxt`, `enum x86_intercept_stage`, and `enum x86_intercept`. Public functions include `x86_decode_insn()`, `x86_page_table_writing_insn()`, `init_decode_cache()`, `x86_emulate_insn()`, `emulator_task_switch()`, `emulate_int_real()`, `emulator_invalidate_register_cache()`, `emulator_writeback_register_cache()`, and `emulator_can_use_gpa()`. Inline helpers `reg_read()`, `reg_write()`, and `reg_rmw()` cache GPR operands inside the emulator context.

### Control Flow
The emulator calls back through `x86_emulate_ops` for GPR access, standard memory, emulated memory, atomic cmpxchg, PIO, segment/table access, CR/DR/MSR/PMC access, halt, wbinvd, hypercall fixup, nested intercept checks, CPUID, mode checks, NMI masking, SMM exit, triple fault, XCR access, address untagging, canonicality, and page validity. Decode state tracks prefixes, opcode bytes, ModRM/SIB fields, operands, fetch cache, memory read cache, and dirty/valid GPR bitmaps. Return codes distinguish continue, unhandleable, propagate fault, retry, cmpxchg failure, I/O needed, nested intercept, and vectoring failure.

### State, Persistence, And Dependencies
The context persists only for one emulated instruction or restartable I/O operation. It stores eflags, eip, mode, interruptibility, exception state, GPA availability, decoded operands, cached registers, and small fetch/read caches. Dependencies include x86 descriptor definitions, FPU vector types, CPUID vendor constants, KVM callback implementations, and nested virtualization intercept enums.

### Integration Points
KVM x86 calls the decoder/emulator for MMIO, PIO, instruction interception, nested intercept reflection, task switches, real-mode interrupts, SMM transitions, and page-table-writing detection. The ops table is the boundary between generic decode logic and VMX/SVM/KVM architectural state.

### Risks
The emulator assumes only one emulated memory location per instruction and that instruction fetch/stack accesses are standard memory; violating this in callbacks can mis-handle faults. Usercopy-sensitive fields begin at `src`, so structure layout matters. Register-cache dirty writeback must happen after emulation. Intercept stage ordering is subtle for nested virtualization. Vector and MM/XMM/YMM operand storage requires proper alignment and size handling.

### Test Signals
Run KVM emulator tests for ModRM/SIB decoding, string I/O/MMIO, page faults during standard and emulated accesses, LOCK cmpxchg, CR/DR/MSR intercepts, nested intercept stages, real/protected/long mode instructions, task switch and interrupt emulation, vendor CPUID paths, vector operands, and emulator restart after `X86EMUL_IO_NEEDED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_emulate.h -->
