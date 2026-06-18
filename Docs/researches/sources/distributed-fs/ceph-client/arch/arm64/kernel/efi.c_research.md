## sources/distributed-fs/ceph-client/arch/arm64/kernel/efi.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/efi.c` implements ARM64-specific EFI runtime
mapping, permission, call setup, call teardown, runtime stack allocation, and firmware-fault
recovery. It adapts generic EFI runtime support to ARM64 page permissions, BTI, TTBR0 PAN handling,
FPSIMD state, and shadow-call-stack concerns.

### Important APIs, Types, And Functions
Mapping helpers are `region_is_misaligned()`, `create_mapping_protection()`,
`efi_create_mapping()`, `set_permissions()`, and `efi_set_mapping_permissions()`. Runtime-call
helpers are `efi_poweroff_required()`, `efi_handle_corrupted_x18()`, `arch_efi_call_virt_setup()`,
`arch_efi_call_virt_teardown()`, and `efi_runtime_fixup_exception()`. Initialization is handled by
`arm64_efi_rt_init()`, which allocates the dedicated EFI runtime stack and initializes
`efi_rt_stack_top`.

### Control Flow
During EFI memory-map setup, `efi_create_mapping()` chooses device, read-only, executable, or
non-executable kernel page protections from EFI memory descriptor type and attributes. Misaligned
runtime regions are forced to page mappings and weaker permissions because OS pages can overlap
adjacent EFI regions. Later `efi_set_mapping_permissions()` tightens page-level RO/XN/BTI guarded
page bits for runtime code/data regions when the descriptors and mapping granularity allow it.

Before each runtime call, `arch_efi_call_virt_setup()` asserts the EFI runtime lock, either borrows
`efi_mm` in a preemptible kthread with migration disabled or loads the EFI virtual map directly,
enables TTBR0 access and erratum workaround state, and begins EFI FPSIMD handling. Teardown ends
FPSIMD handling, disables TTBR0 access before unloading the EFI map, and releases borrowed mm or
migration state. If a synchronous exception occurs while executing firmware,
`efi_runtime_fixup_exception()` disables runtime services, taints the kernel for firmware workaround,
sets the return value to `EFI_ABORTED`, restores LR and optionally `x18` from the EFI stack record,
and redirects PC to `__efi_rt_asm_recover`.

### State, Persistence, And Dependencies
Persistent state includes `efi_rt_stack_top`, EFI runtime service enable bits in `efi.flags`, EFI
runtime mappings in `efi_mm`, and the allocated vmap stack. Dependencies include generic EFI memory
attribute parsing, page table creation, `apply_to_page_range()`, protected MMIO helpers, BTI feature
detection, kthread borrowed-mm support, migration control, TTBR0/PAN helpers, `post_ttbr_update_workaround()`,
EFI FPSIMD wrappers, stacktrace/current-in-EFI state, kmemleak, and vmap stack allocation.

### Integration Points
Generic EFI runtime code calls the mapping and setup/teardown hooks. The assembly wrapper in
`efi-rt-wrapper.S` uses `efi_rt_stack_top` and recovery semantics. Exception handling calls
`efi_runtime_fixup_exception()` when faults may have occurred in firmware. Poweroff and capsule
update behavior depends on `efi_poweroff_required()`.

### Risks
Miscomputed permissions can leave firmware code writable/executable or make valid runtime code
unexecutable. Misaligned regions force weaker protection and can conflict with adjacent descriptors.
Incorrect TTBR0 or EFI virtual map sequencing can expose user page tables or fault in runtime calls.
Failure to disable migration for preemptible kthread calls can resume firmware-polling flows on the
wrong CPU. Firmware faults disable all runtime services, so false positives are disruptive.

### Test Signals
EFI variable reads/writes, time service calls, capsule update/poweroff flows, memory-attribute-table
permission checks, BTI EFI runtime mappings, fault injection in firmware calls, lockdep around the
EFI runtime lock, shadow-call-stack builds, and kthread/preemptible runtime callers are key signals.
