# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.c

## Purpose

`ras_aca_v1_0.c` implements ACA v1.0 bank matching and parsing for UMC, GFX, SDMA, MMHUB, and XGMI RAS blocks. It decodes MCA IPID/status/syndrome fields into block identity and CE/UE/DE counts.

## Important APIs, Types, And Functions

The exported object is `ras_aca_func_v1_0`. Important helpers decode bank info, match hardware IP/mcatype, match GFX XCD banks, match SDMA/MMHUB banks by SMU syndrome error codes, classify UMC deferred/uncorrectable/correctable conditions, and parse default, UMC, and XGMI banks. Static `aca_block_info` entries define names, ras block IDs, hardware IPs, supported masks, and parser callbacks.

## Control Flow, State, And Persistence

Bank matching compares `IPID` hardware ID and MCA type against the v1.0 table, with additional instance/syndrome filters for GFX, SDMA, and MMHUB. Parsing decodes socket and die IDs from IPID instance fields, derives XCD ID for GFX/SMU banks, copies status/IPID/address into `aca_bank_ecc`, and sets one or more CE/UE/DE counts based on status flags and MISC0 error count. UMC poison/deferred errors are separated from UE/CE when poison mode is supported.

## Dependencies And Integration Points

It depends on bitfield macros from `ras_aca_v1_0.h`, rascore poison mode, block IDs from `ras.h`, and the generic ACA engine in `ras_aca.c`. It is selected by ACA IP version 1.0.0.

## Risks And Test Signals

Risks include hard-coded SMU syndrome codes, incorrect unified die/socket decoding, special-case GFX XCD mapping, UMC status classification differences across firmware, and XGMI extended error-code filtering. Test signals include synthetic bank register decode tests, real CE/UE/DE injections for each block, multi-socket/AID/XCD validation, poison-mode UMC behavior, and unsupported or unknown HWIP rejection.
