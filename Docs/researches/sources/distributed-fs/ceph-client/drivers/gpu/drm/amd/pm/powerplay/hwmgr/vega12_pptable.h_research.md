# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_pptable.h

`vega12_pptable.h` defines the packed ATOM BIOS Vega12 PowerPlay table layout consumed by `vega12_processpptables.c`. It bridges persistent VBIOS table data to `phm_ppt_v3_information`, platform capabilities, thermal limits, OD limits, clock limits, and the SMU `PPTable_t`.

Important constants identify Vega12 thermal-controller IDs, platform capability bits, and the expected table revision. `enum ATOM_VEGA12_ODSETTING_ID` indexes OD setting min/max arrays; `enum ATOM_VEGA12_PPCLOCK_ID` indexes power-saving clock arrays. `ATOM_Vega12_POWERPLAYTABLE` contains the common table header, revision/size, platform caps, thermal controller, power limits, software shutdown temperature, clock limits, OD limits, and embedded `PPTable_t smcPPTable`.

There is no executable flow. Runtime consumers cast ATOM data to this packed structure, validate revision and size, copy indexed arrays, and duplicate `smcPPTable` for SMU upload. The state described here is persistent firmware data; the driver copies it into volatile hwmgr and SMU table state.

Dependencies include ATOM common table types and the Vega12 SMU `PPTable_t`. Risks are packed layout drift, endian mistakes, invalid VBIOS revisions, and enum/array index mismatches. Test signals include PPTable validation, sensible OD and clock limits in sysfs, correct software shutdown temperature, and SMU accepting the uploaded PPTable.
