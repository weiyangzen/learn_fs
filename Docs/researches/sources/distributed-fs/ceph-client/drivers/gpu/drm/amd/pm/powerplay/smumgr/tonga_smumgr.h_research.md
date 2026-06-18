# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/tonga_smumgr.h

Purpose: Tonga SMU manager private interface. It defines the ASIC ID predicate, default PowerTune data layout, memory-controller register table structures, and the private backend state consumed by `tonga_smumgr.c`.

Important APIs and types: `ASICID_IS_TONGA_P()` identifies Tonga-P device/revision combinations used by clock-stretcher voltage formulas. `struct tonga_pt_defaults` stores PowerTune/BAPM constants, including DTE iteration arrays sized by SMU72 dimensions. `struct tonga_mc_reg_entry` and `struct tonga_mc_reg_table` represent VBIOS memory timing register entries plus valid-address metadata. `struct tonga_smumgr` embeds `struct smu7_smumgr`, the cached `SMU72_Discrete_DpmTable`, ULV settings, PM fuses, MC registers, MC register conversion table, and selected PowerTune defaults.

Control flow and integration: the header is included by the Tonga implementation and bridges common SMU7 code with SMU72-specific firmware table definitions. Its structures are allocated by `tonga_smu_init()`, filled by firmware-header parsing, DPM table population, PowerTune population, and MC register initialization, then used when uploading SRAM payloads.

State and persistence: all fields are driver-resident cached state; persistence to hardware only happens when the C file serializes these structures into SMC SRAM or indirect registers. The MC table caches both original and low-power register aliases so later DPM updates can compact and upload only valid changing registers.

Dependencies and risks: depends on `smu72_discrete.h`, `smu7_smumgr.h`, and `smu72.h`. Risks are array size coupling with firmware definitions, packed hardware table assumptions, and macro device ID drift. Compile coverage across Tonga variants and DPM-table upload tests are the main signals.
