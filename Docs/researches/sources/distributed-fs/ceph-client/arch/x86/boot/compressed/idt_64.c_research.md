## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_64.c

### Purpose
`compressed/idt_64.c` constructs and loads the minimal early IDT used by compressed boot for SEV #VC handling, page faults, and NMIs.

### Important APIs, Types, And Functions
Exports are `load_stage1_idt()`, `load_stage2_idt()`, and `cleanup_exception_handling()`. Helpers include `set_idt_entry()` and `load_boot_idt()`. It uses `boot_idt`, `boot_idt_desc`, and handler symbols from `idt_handlers_64.S`.

### Control Flow
`load_stage1_idt()` sets the IDT base and, for AMD memory encryption builds, installs a stage-1 #VC handler before loading IDT. `load_stage2_idt()` installs page-fault and NMI handlers, then either installs stage-2 #VC or clears the #VC entry based on `sev_status`. `cleanup_exception_handling()` shuts down the SEV GHCB, sets a null IDT descriptor, and loads it before jumping to the real kernel.

### State, Persistence, And Dependencies
State is the boot IDT array and descriptor. Dependencies include x86 gate descriptor layout, trap vector numbers, SEV status, and handler entry points.

### Integration Points
Called from `head_64.S` before SEV CPUID-sensitive code and before identity-map initialization. It connects assembly exception entry points to C handlers in `ident_map_64.c` and SEV code.

### Risks
Installing the wrong #VC handler stage can break SEV-ES/SNP boot because GHCB availability changes over time. Nulling exception handling too early would remove page-fault support; leaving it enabled when entering the real kernel could expose stale boot handlers.

### Test Signals
Boot plain x86_64, SEV, SEV-ES, and SEV-SNP guests, trigger early page faults, count spurious NMIs, and verify `cleanup_exception_handling()` runs before kernel entry.
