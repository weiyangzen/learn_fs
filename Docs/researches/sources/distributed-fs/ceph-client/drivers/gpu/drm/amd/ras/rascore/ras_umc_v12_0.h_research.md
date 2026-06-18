# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc_v12_0.h

Purpose: defines AMD UMC v12.0 RAS address/register constants and conversion macros used to decode machine-check memory-error records into SOC physical-address fields, UMC channel/socket identifiers, and bad-page retirement candidates.

Important APIs/types/functions: exports `ras_umc_func_v12_0`, `ras_umc_get_badpage_count()`, and `ras_umc_get_badpage_record()`. The main API surface is macro based: MCA/MCMP field masks, UMC instance/channel counts, normalized-address mapping counts, SOC PA field extractors/builders, bank/channel hash macros, ACA IPID decoders, bad-column masking, and retirement-loop sizing.

Control flow: no runtime code is implemented here. Consumers include this header to transform `MCA_UMC_UMC0_MCUMC_ADDRT0.ErrorAddr` and ACA IPID fields. A likely flow is: extract MCA error address, derive die/socket/UMC/channel from IPID, generate candidate PAs through bank/channel hashing and normalized-address expansion, mask bad column bits, then hand results to RAS bad-page reporting.

State and persistence: header constants encode hardware topology assumptions: 4 UMC instances, 8 channel instances, 4 AID nodes, 8 sockets, 192 GiB socket local-fabric size, and 16 retirement-loop variants. Persistent effect is indirect through page-retirement records produced by callers.

Dependencies/integration: depends on `ras.h`, `REG_GET_FIELD`, AMD RAS core context types, and UMC v12.0 hardware register layout. It integrates with AMDGPU RAS bad-page query paths.

Risks: macro arithmetic has side effects if arguments are expressions with mutations. Incorrect bit positions or hash enable constants can retire the wrong physical pages. Topology constants are brittle across ASIC variants. `0x...L` masks rely on width assumptions. Test signals: decode known MCA/IPID samples, validate candidate PA count and socket/channel mapping, exercise bad-column masking, and compare bad-page records with firmware/hardware error injection.
