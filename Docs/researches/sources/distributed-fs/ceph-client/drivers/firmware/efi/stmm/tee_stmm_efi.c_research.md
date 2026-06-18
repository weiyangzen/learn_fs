# sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/tee_stmm_efi.c

Purpose: Provides an EFI variable backend that routes variable runtime services through OP-TEE to StandaloneMM. On probe it replaces the generic EFI variable operations with TEE-backed operations and restores the generic backend on removal.

Important APIs/types/functions: `tee_stmm_efi_private` stores the TEE context, session, and device. `tee_mm_communicate()` registers a kernel buffer as TEE shared memory and invokes `PTA_STMM_CMD_COMMUNICATE`. `setup_mm_hdr()` allocates and fills the MM/SMM headers. `get_max_payload()` discovers StMM payload limits. Runtime service callbacks are `tee_get_variable()`, `tee_get_next_variable()`, `tee_set_variable()`, `tee_set_variable_nonblocking()`, and `tee_query_variable_info()`.

Control flow: Probe opens an OP-TEE context matching `TEE_IMPL_ID_OPTEE`, opens a PTA session using the StMM UUID, queries maximum payload size, unregisters generic efivars, and registers `tee_efivar_ops`. Each variable call builds a packed communication buffer, sends it through `tee_client_invoke_func()`, maps SPM errors to EFI statuses, reads `ret_status`, then copies returned data back into kernel buffers.

State and persistence behavior: Global `pvt_data`, `max_payload_size`, `max_buffer_size`, and `tee_efivars` represent process-wide backend state. Persistent variable state lives in StMM firmware. The driver enforces StMM read-only variable properties before set operations.

Dependencies and integration points: Integrates the TEE client bus, OP-TEE PTA ABI, `efivars_register()`, `efivars_generic_ops_unregister()`, UCS-2 helpers, and allocation via `alloc_pages_exact()`. It consumes the protocol definitions in `mm_communication.h`.

Risks and test signals: Key risks are shared-memory registration failures, firmware payload limit mismatches, truncated variable buffers, races around global backend replacement, and property handling that converts `EFI_NOT_FOUND` to writable state. Tests should exercise get/set/delete/enumerate/query through `/sys/firmware/efi/efivars` and `efi_test`, including oversized names/data, null data pointers, read-only variables, and module unload/reprobe.
