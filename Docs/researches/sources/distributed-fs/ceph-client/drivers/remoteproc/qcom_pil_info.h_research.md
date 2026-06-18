# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_pil_info.h

## Purpose

`qcom_pil_info.h` is the small public-local declaration for Qualcomm PIL relocation info storage. It exposes the function used by Qualcomm image loader drivers to publish firmware relocation metadata.

## Important APIs, types, and data

- `qcom_pil_info_store(const char *image, phys_addr_t base, size_t size)` stores or updates one PIL relocation record containing image identifier, physical base, and size.

## Control flow

The header has no control flow. Callers include it and call `qcom_pil_info_store()` after loading a firmware image. The implementation performs lazy IMEM mapping and table update.

## State and persistence behavior

No state lives in the header. The function it declares updates persistent IMEM state managed by `qcom_pil_info.c`.

## Dependencies and integration points

The header includes `linux/types.h` for `phys_addr_t` and `size_t`. It is intended for in-kernel Qualcomm PIL/remoteproc users rather than a generic subsystem ABI.

## Risks and edge cases

- The declaration does not document the 8-byte image-name truncation or optional `-ENOENT` behavior; callers need to know implementation constraints.
- The function returns negative errno values and callers should not treat failures as fatal unless their platform requires post-mortem relocation info.

## Test signals

Compile tests should verify every caller includes this header rather than open-coding the prototype. Integration tests should pair calls through this declaration with the IMEM table behavior in `qcom_pil_info.c`.
