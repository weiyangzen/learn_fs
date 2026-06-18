# sources/distributed-fs/ceph-client/arch/x86/boot/pm.c

Purpose: prepares the CPU and interrupt hardware for transition from real mode to protected mode.

Important APIs and state: exports `go_to_protected_mode()`. Local helpers handle optional real-mode switch hook, interrupt masking, FPU IGNNE reset, GDT setup, and IDT setup. Static GDT contains boot CS, DS, and TSS descriptors.

Control flow: calls loader-provided `realmode_swtch` or disables interrupts/NMI, enables A20, resets coprocessor, masks PIC interrupts, loads a null IDT and boot GDT, then calls `protected_mode_jump()` with `code32_start` and the physical boot_params address.

Dependencies and integration: called at the end of `main()`. Depends on BIOS/port I/O, A20 helper, boot protocol fields, and `pmjump.S`.

Risks and test signals: failures in A20 or descriptor setup prevent boot. The static GDT pointer workaround supports Xen HVM quirks. Test legacy BIOS, Xen HVM, A20 failure injection, and bootloader real-mode switch hook behavior.
