# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/cna_fwimg.c

## Purpose
Loads and exposes BR-series CNA firmware images for CT and CT2 ASIC generations. It is the firmware image provider used during PCI probe and by BFA callback hooks that fetch firmware chunks and sizes for IOC download.

## Important APIs, Types, and Functions
Global `const struct firmware *bfi_fw` is exported through `bnad.h` and released at module exit. Static caches hold `bfi_image_ct_cna`, `bfi_image_ct2_cna`, and their dword sizes. `cna_read_firmware()` calls `request_firmware()`, stores the firmware data pointer as `u32 *`, records the dword count, assigns `bfi_fw`, and converts each LE32 word to CPU byte order in place. `cna_get_firmware_buf()` selects CT2 firmware by exact device ID or CT firmware by ASIC helper. `bfa_cb_image_get_chunk()` and `bfa_cb_image_get_size()` return cached image pointers and sizes by `bfi_asic_gen`.

## Control Flow and State
Firmware is lazy-loaded on first request per ASIC generation. PCI probe calls `cna_get_firmware_buf()` under a global mutex in `bnad.c`, so the static caches are serialized there. Once loaded, later calls return the cached pointer. BFA download code asks for chunks by offset and total size via callbacks.

## State and Persistence Behavior
The firmware data stays resident until module exit. The code mutates the firmware buffer with `le32_to_cpus()` so cached data is host-endian after the first load. Only one global `bfi_fw` pointer is retained even though there are two possible cached firmware images; this means module exit releases only the last assigned firmware object.

## Dependencies and Integration Points
Depends on Linux firmware loading, `bnad.h` for `bfi_fw` and PCI device macros, `bfi.h` for ASIC generation enums, and `cna.h` for firmware filenames. It integrates with `bnad_pci_probe()` and BFA IOC firmware callbacks.

## Risks and Test Signals
The main risk is firmware lifetime and cache ownership. If both CT and CT2 images are loaded in one module lifetime, `bfi_fw` tracks only one `struct firmware`, so the other may not be released. The code also casts `fw->data` away from const and endian-swaps in place, which relies on firmware memory being writable. Offset handling in `bfa_cb_image_get_chunk()` trusts callers. Test signals include probing CT and CT2 adapters in one boot, unload leak checks, missing firmware error paths, firmware download checksum/version validation, and byte-order validation on big-endian systems.
