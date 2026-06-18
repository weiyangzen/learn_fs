# sources/distributed-fs/ceph-client/drivers/xen/efi.c

## Purpose
`efi.c` implements Xen paravirtual EFI runtime services. It installs EFI function pointers that proxy runtime calls through Xen platform hypercalls and provides Xen-aware EFI memory descriptor lookup/config-table validation.

## Important APIs, types, and functions
Runtime wrappers include `xen_efi_get_time`, `set_time`, `get_wakeup_time`, `set_wakeup_time`, `get_variable`, `get_next_variable`, `set_variable`, `query_variable_info`, `get_next_high_mono_count`, `update_capsule`, `query_capsule_caps`, and `xen_efi_reset_system`. Public setup and helpers are `xen_efi_runtime_setup`, `efi_mem_desc_lookup`, and `xen_efi_config_table_is_usable`.

## Control flow
Each wrapper builds a `XENPF_efi_runtime_call` platform op, copies scalar structures or sets guest handles for buffers, invokes `HYPERVISOR_platform_op`, and returns either `EFI_UNSUPPORTED` or Xen-reported EFI status. Setup assigns these wrappers into global `efi` ops. Reset maps EFI cold/warm/shutdown to Xen reboot or poweroff. Memory descriptor lookup falls back to native lookup when not paravirt or when a native EFI memmap exists; otherwise it asks Xen firmware info for the descriptor covering the physical address.

## State and persistence
The file mutates global EFI runtime function pointers during early init. Variable/time/capsule state persists in firmware or Xen-mediated firmware storage, not in this driver.

## Dependencies and integration points
It depends on Linux EFI core types, Xen platform/firmware hypercalls, Xen guest handles, Xen reboot operations, and EFI paravirt feature flags.

## Risks and test signals
Risks include structure layout mismatches guarded by `BUILD_BUG_ON`, missing hypercall error propagation in memory descriptor lookup, guest-handle validity for user buffers, runtime-version gating for EFI 2.0 calls, reset default `BUG()`, and accepting unsafe config table memory types. Test signals include EFI time/variable operations under Xen, capsule capability queries, native versus paravirt memmap lookup, invalid hypercall returns, config table validation by memory type, and reset paths.
