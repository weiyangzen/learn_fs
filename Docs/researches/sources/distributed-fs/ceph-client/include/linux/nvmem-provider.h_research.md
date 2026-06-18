
# sources/distributed-fs/ceph-client/include/linux/nvmem-provider.h

Purpose: declares the NVMEM provider and layout-driver API used by hardware drivers to export non-volatile memory regions and by layout parsers to add derived cells.

Important APIs/types/functions: callback typedefs define raw register read/write and cell post-processing. `enum nvmem_type` classifies EEPROM, OTP, battery-backed, and FRAM storage. `struct nvmem_keepout` marks forbidden ranges. `struct nvmem_cell_info` describes named cells, bit slicing, raw/cooked lengths, OF nodes, and optional read post-processing. `struct nvmem_config` describes provider registration: parent, name/id, owner, predefined cells, legacy OF cell parsing, DT fixups, keepouts, type, read-only/root-only/write-protect behavior, layout, callbacks, size, word size, stride, private data, and legacy compatibility. `struct nvmem_layout` and `nvmem_layout_driver` define dynamic parsers. APIs register/unregister providers and layouts, add cells, and provide devm/module helpers.

Control flow: a hardware provider fills `nvmem_config` with access callbacks and metadata, then registers an `nvmem_device`. The core validates stride/word size, exposes cells, applies keepouts and post-processing, and notifies consumers. Layout drivers can probe attached layouts and add parsed cells at runtime.

State and persistence: provider state includes registered device objects, cell tables, lookup metadata, layout devices, and hardware-backed non-volatile content. Actual persistence depends on the storage type and provider callbacks.

Dependencies and integration points: depends on device model, driver core, GPIO write-protect control, OF layout containers, modules, and NVMEM consumer metadata. It integrates EEPROM/OTP/SoC fuse drivers, device tree bindings, and consumers needing calibration/MAC/key data.

Risks and test signals: risks include incorrect size/stride/word-size validation, keepout ranges not sorted or enforced, bit-cell extraction mistakes, write-protect handling, post-processing changing expected lengths, and layout-added cell lifetime issues. Test signals include provider registration tests, raw and cell read/write boundary tests, keepout fill-value checks, read-only/root-only permission checks, OF layout parsing, and disabled-config compile stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvmem-provider.h -->
