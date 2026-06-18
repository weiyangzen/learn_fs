<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_feature.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_feature.h

## Purpose
This header defines the legacy PowerMac feature-control API, model/type flags, feature call selectors, MacIO chip metadata, and helper macros for manipulating MacIO feature-control registers.

## Important APIs, Types, And Functions
It enumerates many `PMAC_TYPE_*` machine IDs and motherboard flags, defines `pmac_call_feature()`, feature selectors for SCC, modem, SWIM3, MESH, IDE, BMAC/GMAC, sound, Airport, CPU reset, USB, FireWire, sleep, motherboard info, GPIO, MPIC, AACK delay, and wake capability, plus `pmac_do_feature_call()`, `pmac_feature_init()`, early video resume hooks, AGP power-management hooks, `struct macio_chip`, `macio_chips[]`, MacIO flags, `macio_find()`, and register access macros.

## Control Flow
Drivers call `pmac_call_feature()` or AGP/MacIO helpers to enable, reset, suspend, resume, or query platform devices. Feature dispatch goes through `ppc_md.feature_call`.

## State And Persistence Behavior
Power/reset bits persist in MacIO/feature-control registers. `macio_chips[]` stores discovered controller state, base mappings, flags, and OF nodes. Early video resume callback state is stored for sleep recovery.

## Dependencies And Integration Points
It depends on MacIO, machdep feature call hooks, PCI, device tree, and old PowerMac platform code. It integrates with serial, storage, network, USB/FireWire, sound, sleep, GPIO, MPIC, and AGP drivers.

## Risks And Edge Cases
Machine type values overlap across generations and are historical. Feature calls mutate hardware power/reset lines. MacIO register macros assume little-endian IO access and a local `macio` variable.

## Test Signals
Boot representative PowerMac models, test device enable/reset, sleep/resume, AGP suspend/resume, GPIO reads/writes, MacIO discovery, and all affected onboard devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_feature.h -->
