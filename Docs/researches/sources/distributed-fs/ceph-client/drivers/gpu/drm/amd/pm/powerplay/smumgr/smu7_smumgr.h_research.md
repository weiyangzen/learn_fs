# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.h

## Purpose
This header declares the shared SMU7 backend state and helper APIs used by chip-specific SMU managers such as Polaris, Tonga, and Fiji.

## Important APIs, types, and functions
`struct smu7_buffer_entry` describes a BO-backed firmware exchange buffer with size, MC address, CPU mapping, and BO handle. `struct smu7_smumgr` stores the SMU/header buffers, optional TOC pointer, firmware-discovered SMC table offsets, security key selection, ACPI optimization, and AVFS BTC parameter. Function declarations expose SMC SRAM copy/read/write helpers, SMU message helpers, firmware ID conversion, firmware loading/reload, init/fini, and power-virus setup.

## Control flow, state, dependencies, risks, and test signals
The header establishes the lifecycle: chip-specific code allocates or embeds `struct smu7_smumgr`, `smu7_init` allocates buffers, chip-specific startup uploads/starts SMU firmware, `smu7_request_smu_load_fw` loads dependent microcodes, and `smu7_smu_fini` releases state. Offset fields are populated from SMU firmware headers and then reused for SMC SRAM updates. The structure is frequently embedded, so teardown ownership must match allocation. Test signals are valid BO addresses, populated offsets, successful firmware-load masks, and clean teardown.
