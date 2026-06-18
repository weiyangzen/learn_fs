# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_firmware.h

Purpose: `sh_css_firmware.h` is the public host-side interface for loaded CSS firmware state. It defines the firmware file header format visible to user-supplied firmware blobs and declares the global descriptors and loader helpers implemented in `sh_css_firmware.c`.

Important APIs/types/functions: `struct sh_css_fw_bi_file_h` contains a 64-byte version string, binary count, and header size. Extern globals are `sh_css_sp_fw`, `sh_css_blob_info`, and `sh_css_num_binaries`. The exported functions are `sh_css_get_fw_version()`, `sh_css_check_firmware_version()`, `sh_css_load_firmware()`, `sh_css_unload_firmware()`, `sh_css_load_blob()`, and `sh_css_load_blob_info()`.

Control flow and state: the header itself has no executable logic. It defines the contract that callers use before initializing the SP, selecting ISP binaries, and copying blobs into HMM memory. The global variables represent persistent loaded-firmware state and are reset by the implementation during unload.

Dependencies and integration: it includes `system_local.h`, `ia_css_err.h`, and `ia_css_acc_types.h` for `ia_css_ptr`, firmware descriptors, acceleration types, and error conventions. It forward-declares `struct device` so loader calls can log through Linux device APIs without forcing all users to include device headers. It is included by internal CSS code, MMU code, and parameter/binary selection paths.

Risks: this header exposes mutable global firmware state, so ordering matters: consumers must not use `sh_css_sp_fw` or `sh_css_blob_info` before successful load or after unload. The header does not encode ownership rules; `sh_css_blob_info` points to allocated implementation-owned memory and must not be freed by consumers.

Test signals: compile tests should ensure all consumers see consistent prototypes. Integration tests should exercise firmware load/unload ordering and verify users fail gracefully when globals are unset or binary counts are invalid.
