# sources/distributed-fs/ceph-client/include/drm/amd_asic_type.h

Purpose: enumerates AMD GPU ASIC family identifiers and quirk mapping data used by AMD DRM drivers.

Important APIs, types, and flow: `enum amd_asic_type` lists GPU families from older Southern Islands parts through IP discovery, ending at `CHIP_LAST`. `amdgpu_asic_name[]` maps types to printable names. `struct amdgpu_asic_type_quirk` maps a PCI device/revision pair to the real ASIC type when discovery needs correction.

State and persistence: no runtime state is stored here, aside from extern name table data defined elsewhere.

Dependencies and integration: used by amdgpu/radeon-style code, firmware selection, feature masks, and platform data such as AMD ISP setup.

Risks and test signals: enum value stability matters because tables and logs depend on it; quirk omissions can select wrong IP blocks. Signals include PCI ID probe tests, ASIC name output, firmware loading by family, quirk table coverage for revised devices, and compile checks for `CHIP_LAST`-sized arrays.
