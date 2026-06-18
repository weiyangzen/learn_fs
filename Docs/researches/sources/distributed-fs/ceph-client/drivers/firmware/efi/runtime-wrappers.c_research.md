
# sources/distributed-fs/ceph-client/drivers/firmware/efi/runtime-wrappers.c

Purpose: serializes and safely dispatches EFI runtime service calls through a workqueue-backed wrapper layer, providing kernel-facing `efi.*` runtime operations.

Important APIs/types/functions: exports `efi_call_virt_save_flags()`, `efi_call_virt_check_flags()`, `efi_native_runtime_setup()`, optional `efi_call_acpi_prm_handler()`, and `efi_runtime_assert_lock_held()`. Central types are `union efi_rts_args`, global `efi_rts_work`, `efi_runtime_lock`, and `efi_runtime_lock_owner`.

Control flow: callers enter wrapper functions such as `virt_efi_get_variable()` or `virt_efi_set_time()`, take the binary semaphore, populate `efi_rts_work`, queue work to `efi_rts_wq`, and wait for completion. The work function switches to architecture EFI runtime calling context, saves IRQ flags, dispatches the selected runtime service, checks/restores corrupted IRQ flags, stores status, completes, and clears lock ownership. Nonblocking variable operations use `down_trylock()` and direct virtual calls for interrupt-sensitive users. ResetSystem uses trylock and direct call because it may not return.

State and persistence behavior: global work object and semaphore serialize all runtime calls. `efi_native_runtime_setup()` installs wrapper function pointers into global `efi`. Lock ownership is tracked for assertions and UV platform aliases the lock when configured.

Dependencies and integration points: depends on EFI runtime tables, `efi_rts_wq`, completions/workqueues, architecture `arch_efi_call_virt_setup()/teardown()`, IRQ flag handling, pstore/variable users, capsule update users, reset/reboot paths, and optional ACPI PRMT.

Risks and test signals: all queued calls share one global work object, so serialization is mandatory. Firmware can corrupt IRQ flags, runtime calls can block, nonblocking paths can fail with `EFI_NOT_READY`, and ResetSystem lock contention prevents reset. Test signals include concurrent variable/time/capsule calls, pstore nonblocking set-variable, runtime services disabled, firmware IRQ flag corruption warnings, reset path, ACPI PRM handler, and lock-held assertions.
