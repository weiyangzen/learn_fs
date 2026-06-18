# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom_uefisecapp.c

## Purpose
This auxiliary driver implements EFI variable operations by talking to Qualcomm's QSEE `qcom.tz.uefisecapp` secure application. It is used on systems where EFI variables cannot be accessed directly and must be mediated by the secure execution environment.

## Important APIs, Types, And Functions
- Secure command structs: `qsee_req/rsp_uefi_get_variable`, `set_variable`, `get_next_variable`, and `query_variable_info`.
- Buffer layout helpers: `qcuefi_buf_align_fields()`, `__field_impl()`, `__reqdata_offs()`, and the array/field offset wrappers. These build contiguous, aligned request/response buffers.
- Secure app operations: `qsee_uefi_get_variable()`, `qsee_uefi_set_variable()`, `qsee_uefi_get_next_variable()`, and `qsee_uefi_query_variable_info()`.
- Global EFI wrappers: `qcuefi_get_variable()`, `qcuefi_set_variable()`, `qcuefi_get_next_variable()`, and `qcuefi_query_variable_info()` implement `struct efivar_operations`.
- Driver lifecycle: `qcom_uefisecapp_probe()`, `qcom_uefisecapp_remove()`, and the auxiliary ID `qcom_qseecom.uefisecapp`.

## Control Flow
Probe obtains the containing `qseecom_client`, creates a managed TZMem pool with 4 KiB initial size, multiplier growth, and 256 KiB cap, installs the singleton `__qcuefi`, and registers efivars. Each efivar callback locks the singleton, builds a command-specific contiguous TZMem buffer, populates UTF-16 variable names, GUIDs, attributes, and data, sends it through `qcom_qseecom_app_send()`, validates response command IDs, lengths, and offsets, converts secure app status to EFI status, and copies out data only after bounds checks.

`GET_VARIABLE` and `GET_NEXT_VARIABLE` handle EFI buffer-size negotiation by updating `data_size` or `name_size` on `EFI_BUFFER_TOO_SMALL`. `SET_VARIABLE` supports zero-length data as EFI deletion. `QUERY_VARIABLE_INFO` returns storage, remaining, and max variable sizes from the secure response.

## State And Persistence
The driver stores one global active client pointer protected by `__qcuefi_lock`, because global efivar operations do not carry per-device context. Firmware-backed EFI variables are persistent in platform storage, but this file only mediates access; it does not cache variable contents. Request buffers are allocated from TZMem and freed automatically by cleanup attributes.

## Dependencies And Integration Points
The driver depends on the QSEECOM auxiliary device, SCM's app send API, TZMem for TrustZone-safe buffers, EFI efivar registration, UTF-16 helpers, and OF/auxiliary module infrastructure. It exposes platform EFI variables to generic EFI users and efivarfs.

## Risks
The secure app is strict about contiguous aligned request and response placement; separate buffers caused missing responses or device crashes according to in-file notes. Response validation is security critical because firmware controls offsets and sizes. The singleton design allows only one active uefisecapp provider. Bad status conversion, name-size accounting, or missing NUL termination can surface as efivarfs corruption or EFI API failures.

## Test Signals
Successful probe should register efivars and allow efivarfs list/read/write/delete operations. Test edge cases include zero-size `GetVariable`, too-small buffers, long variable names near `QSEE_MAX_NAME_LEN`, `GetNextVariableName` iteration, and write/delete status mapping. Device logs with `uefisecapp error` identify secure app status failures.
