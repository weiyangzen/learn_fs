# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_geo.h

Purpose: UV hardware geolocation ID structures and helpers for rack/slot/blade naming.

Important APIs/types/functions: `GEOID_SIZE`, `struct geo_common_s`, `struct geo_node_s`, `struct geo_rtr_s`, `struct geo_iocntl_s`, `struct geo_pcicard_s`, `struct geo_cpu_s`, `struct geo_mem_s`, `union geoid_u`, `GEO_TYPE_*`, `geo_rack()`, `geo_slot()`, and `geo_blade()`.

Control flow: helper functions return `-1` for invalid geo IDs and otherwise derive rack, upos slot, and blade number (`blade * 2 + slot`) from common fields.

State/persistence: no runtime state. The union is a compact 8-byte firmware-provided hardware location encoding used in diagnostics.

Dependencies/integration: used with UV BIOS geoinfo enumeration, sysfs/diagnostics, and platform topology reporting.

Risks/test signals: incorrect packing or blade calculation mislabels physical hardware. Test by enumerating UV geoinfo, comparing rack/slot/blade labels with firmware/service-processor data, and validating invalid geoid handling.
