## sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-rt-wrapper.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/efi-rt-wrapper.S` provides the assembly wrapper
used to call EFI runtime services on ARM64. It preserves kernel callee-saved state, switches to a
dedicated EFI runtime stack, protects the platform/shadow-call-stack register `x18`, and provides a
recovery landing path for synchronous exceptions inside firmware.

### Important APIs, Types, And Functions
`__efi_rt_asm_wrapper` takes an EFI function pointer and up to five register arguments, preserves
frame, LR, `x18`, and callee-saved registers, records the interrupted task SP at the top of the EFI
stack, calls firmware, checks whether firmware corrupted `x18`, and tail-calls
`efi_handle_corrupted_x18()` if needed. `__efi_rt_asm_recover` restores state after
`efi_runtime_fixup_exception()` redirects control out of a faulting firmware call.

### Control Flow
The wrapper saves kernel state on the current stack, loads `efi_rt_stack_top`, switches SP to the EFI
stack, records `x18` and the old frame pointer, moves arguments into EFI ABI positions, and branches
to the firmware function. On normal return it restores the old SP, clears the saved task SP slot,
restores registers, and returns if `x18` survived. If `x18` changed, shadow-call-stack builds reload
`x18` from the EFI stack record before reporting corruption. The recovery path uses `x30` as the
saved kernel stack pointer supplied by the C exception fixup and restores callee-saved state without
returning through firmware.

### State, Persistence, And Dependencies
State is transient register and stack state plus the global `efi_rt_stack_top` allocated by
`efi.c`. Dependencies include ARM64 AAPCS, EFI runtime calling conventions, shadow call stack use of
`x18`, C handlers `efi_handle_corrupted_x18()` and `efi_runtime_fixup_exception()`, and stack layout
agreement with `efi.c`.

### Integration Points
`arch_efi_call_virt_setup()`/`teardown()` prepare address-space and FPSIMD state around calls that
enter this wrapper. Synchronous exception handling consults the EFI stack records and redirects to
`__efi_rt_asm_recover` when firmware faults.

### Risks
Register-save ordering and stack offsets are ABI-critical. Failing to restore `x18` corrupts shadow
call stack or platform state. Clearing the recorded SP too early or too late can break firmware
exception recovery. EFI calls that unexpectedly use stack arguments would violate the wrapper's
assumption that ARM64 runtime services use at most five arguments.

### Test Signals
EFI runtime service tests (`GetTime`, variables, `ResetSystem` paths), fault injection inside EFI
runtime calls, shadow-call-stack builds, preemptible kthread EFI calls, and register-corruption
instrumentation around `x18` validate this file.
