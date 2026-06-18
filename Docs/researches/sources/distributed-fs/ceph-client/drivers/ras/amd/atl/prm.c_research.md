# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/prm.c

Purpose: provides ATL plumbing for ACPI Platform Runtime Mechanism address translation. It lets newer platforms or firmware-backed implementations translate a UMC normalized address to a system physical address without using the in-kernel DF register decoder.

Important APIs and types: `struct norm_to_sys_param_buf` is the packed PRM parameter buffer containing `norm_addr`, `socket`, `bank_id`, and an `out_buf` pointer. `prm_umc_norm_to_sys_addr(u8 socket_id, u64 bank_id, unsigned long addr)` is the only exported-in-file function and calls `acpi_call_prm_handler(norm_to_sys_guid, &p_buf)`.

Control flow: the function builds the PRM buffer on the stack, points `out_buf` at local `ret_addr`, and invokes the firmware handler. A zero return means `ret_addr` is valid and returned. `-ENODEV` is logged at debug level as absent PRM support; other failures emit a once-only notice and the negative error is returned as an unsigned long error value.

State and persistence: no persistent state is owned here. The function uses stack-local request and response storage. The handler GUID is defined in `system.c` as `norm_to_sys_guid`.

Dependencies and integration: includes `internal.h` and `<linux/prmt.h>`. Called by `convert_umc_mca_addr_to_sys_addr()` in `umc.c` before the software `norm_to_sys_addr()` fallback. It also supports PRM-only systems detected in `system.c`.

Risks: the PRM ABI relies on packed layout and firmware documentation, so field order and pointer validity are critical. A returned negative error is cast through `unsigned long`; callers must use `IS_ERR_VALUE()`. Stack output storage assumes the handler writes synchronously during `acpi_call_prm_handler()`.

Test signals: verify absent-handler `-ENODEV`, firmware failure notice throttling, successful handler output, PRM-only fallback behavior in `umc.c`, and ABI conformance on platforms with AMD PRMT support.
