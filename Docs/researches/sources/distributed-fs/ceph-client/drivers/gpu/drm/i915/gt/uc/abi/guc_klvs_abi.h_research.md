# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_klvs_abi.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_klvs_abi.h

### Purpose
`guc_klvs_abi.h` defines GuC key-length-value encodings for self-config, scheduling policy, context policy, and workaround KLVs.

### Important APIs, Types, And Functions
Important constants are `GUC_KLV_0_KEY`, `GUC_KLV_0_LEN`, self-config keys for H2G/G2H CTB addresses, descriptor addresses, and sizes, scheduling policy IDs, context policy IDs, and workaround keys such as serialized RA mode, block interrupts when MGSR blocked, and avoid GFX clear while active.

### Control Flow
No runtime flow exists; users pack key and length into the first dword and pass one or more value dwords through HOST2GUC self-config or ADS workaround KLV storage.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State lives in GuC self-config messages or ADS KLV sections. Integration includes `intel_guc_self_cfg32/64()` and `intel_guc_ads.c` workaround KLV setup. Risks are key/length mismatch, firmware version gating mistakes, and invalid GGTT addresses for CT buffers. Test signals include GuC acknowledging recognized KLVs, CT channel initialization, and platform workarounds taking effect.
