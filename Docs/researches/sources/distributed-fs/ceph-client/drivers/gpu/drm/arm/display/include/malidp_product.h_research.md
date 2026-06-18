# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/include/malidp_product.h

Purpose: defines product/core identification helpers and a compact Komeda configuration ID representation.

Important APIs/types/functions: `MALIDP_CORE_ID()` packs product, major, minor, and status fields. Extractors return product, major, minor, and status from a core ID. Product IDs identify D71, D32, and Linlon D6. `union komeda_config_id` exposes max line size, number of pipelines, scalers, layers, and rich layers as bitfields over a `u32`.

Control flow: chip identification reads `GLB_CORE_ID`, uses the product extractor, and chooses D71-family chip functions. Sysfs `config_id` fills the union from enumerated pipeline resources and emits a hex value.

State and persistence: no dynamic state. The bitfield layout is a stable ABI-like representation exposed through sysfs.

Dependencies/integration: included by `komeda_dev.h` and D71 code. It couples register IDs to Linux-visible product naming and sysfs.

Risks: C bitfield layout depends on compiler/endianness expectations, though use is local to generated value. Product ID expansion requires updating D71 identification. Test signals: probe logs show expected product/revision, sysfs `core_id`/`config_id` match hardware documentation, and unsupported product IDs fail cleanly.
