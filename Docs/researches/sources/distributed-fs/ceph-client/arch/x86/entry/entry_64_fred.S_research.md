## sources/distributed-fs/ceph-client/arch/x86/entry/entry_64_fred.S

Purpose: implements the assembly landing points for Flexible Return and Event Delivery (FRED). It builds a register frame for FRED user and kernel event delivery and provides a KVM helper that fabricates a FRED-style frame for VMX-origin IRQ/NMI handling.

Important APIs/functions: `asm_fred_entrypoint_user`, `asm_fred_exit_user`, `asm_fred_entrypoint_kernel`, `asm_fred_entry_from_kvm`, plus `FRED_ENTER`/`FRED_EXIT` macros. It calls `fred_entry_from_user()`, `fred_entry_from_kernel()`, and `__fred_entry_from_kvm()`. It uses `ERETU`, `ERETS`, FRED stack-frame constants, extable recovery for `ERETU`, and exports the KVM helper.

Control flow: the ring-3 entry is 4 KiB aligned because FRED hardware derives the entry RIP from `IA32_FRED_CONFIG`. It pushes/clears GPRs, passes `pt_regs` in `%rdi`, calls the C dispatcher, restores registers, and returns with `ERETU`. Kernel entry is fixed at user entry plus 256 bytes and returns with `ERETS`. The KVM helper emulates FRED redzone/alignment, manually pushes a 64-byte FRED frame, calls the C dispatcher, and either restores the old stack or executes `ERETS` when FRED is active.

State/persistence: no durable kernel data is owned here; it manages transient stack frames, return-state bits, callee-saved registers, and extable metadata.

Integration points: FRED CPU feature enablement, KVM Intel VMX interrupt/NMI exits, C FRED dispatch in `entry_fred.c`, objtool unwind hints, and the generic `pt_regs` layout.

Risks: hardware-mandated alignment and frame layout are exact. A wrong offset in the KVM synthetic frame would confuse C dispatch or return through the wrong FRED instruction. Test signals include FRED boot tests, KVM VMX IRQ/NMI injection tests, objtool validation, nested event tests, and exception-return fault injection around `ERETU`.
