# sources/distributed-fs/ceph-client/arch/x86/kvm/smm.c

## Purpose
Implements KVM x86 System Management Mode entry, exit via RSM, SMRAM state-save/load, SMI request processing, SMM hflag transitions, and compile-time validation of emulated SMRAM layouts.

## Important APIs, Types, and Functions
- `check_smram_offsets()` asserts 32-bit and 64-bit SMRAM field offsets and union size.
- `kvm_smm_changed()` toggles SMM hflags, resets MMU context, clears nested NMI/SMM state on exit, and requests event processing.
- `process_smi()` latches pending SMI and requests event handling.
- Save helpers: `enter_smm_save_seg_32()`, `enter_smm_save_seg_64()`, `enter_smm_save_state_32()`, and `enter_smm_save_state_64()`.
- `enter_smm()` writes SMRAM, invokes vendor entry, masks NMI, switches to SMM real-mode-like state, resets control registers/segments, and clears EFER for long-mode guests.
- Load helpers: `rsm_load_seg_32()`, `rsm_load_seg_64()`, `rsm_enter_protected_mode()`, `rsm_load_state_32()`, and `rsm_load_state_64()`.
- `emulator_leave_smm()` implements RSM by reading SMRAM, leaving SMM/vendor state, restoring control/segment/register state, and handling nested-mode failure cases.

## Control Flow
An SMI is latched with `process_smi()`. On entry, KVM builds a zeroed 512-byte SMRAM image, saves 32-bit or 64-bit state, gives vendor code a chance to leave guest mode or adjust state, marks SMM active, writes SMRAM at `smbase + 0xfe00`, handles NMI mask state, sets SMM entry RIP/rflags/interrupt shadow/control registers/IDT/DR7/segments, clears EFER for long-mode guests, marks dynamic CPUID bits dirty, and resets MMU context. RSM reads SMRAM, unmasks NMI if appropriate, clears SMM hflags, transitions to a safe real-mode state to load CR0/CR3/CR4/EFER, invokes vendor `leave_smm`, restores 32-bit or 64-bit saved state, and forces nested guest exit if failed restoration would otherwise deliver shutdown to the wrong level.

## State and Persistence
Persistent state includes `vcpu->arch.hflags` SMM bits, `smbase`, `smi_pending`, interrupt shadow, NMI mask state, saved guest state in guest SMRAM memory, control registers, EFER, DR6/DR7, segment descriptors, descriptor tables, GPRs, optional shadow stack pointer, and MMU context. State is externally visible through guest memory at SMRAM save area and through vCPU architecture state.

## Dependencies and Integration Points
Uses KVM x86 vendor hooks (`enter_smm`, `leave_smm`, control register setters, descriptor table accessors, interrupt/NMI mask operations, EFER writes), emulator context, register cache helpers, CPUID capabilities, nested virtualization helpers, tracepoints, MMU context reset, and optional CET shadow stack MSR storage.

## Risks
SMM transitions are architecturally delicate. Wrong SMRAM layout corrupts guest restore; compile-time offset checks mitigate this. Control register ordering for PCID, PAE, long mode, and EFER.LMA must be preserved. Failure during entry kills the VM because state may be undefined. Nested virtualization RSM ordering is acknowledged as flawed and has explicit cleanup if restoration fails in guest mode. Guest SMRAM memory read/write failures make RSM unhandleable.

## Test Signals
Tests should cover SMI injection and pending-event delivery, 32-bit and 64-bit SMRAM save/restore, long-mode entry/exit, PCID/PAE/EFER ordering, NMI masking across SMM, interrupt shadow preservation, CET SSP save/restore, nested VMX/SVM SMM transitions, bad SMRAM causing unhandleable RSM, and migration preserving `smbase` and SMM hflags.
