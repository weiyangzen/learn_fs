# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smumgr.h

## Purpose

`smumgr.h` is the public PowerPlay SMU manager façade. It defines generic table/member IDs and declares wrapper functions that higher-level hardware managers use without binding directly to a generation-specific SMU implementation. The actual work is delegated through `pp_smumgr_func` implementations such as `ci_smu_funcs`.

## Important APIs, types, and constants

`enum SMU_TABLE` names update targets for UVD, VCE, and BIF tables. `enum SMU_TYPE` and `enum SMU_MEMBER` describe logical offset queries into soft-register and discrete DPM table structures. `enum SMU_MAC_DEFINITION` provides logical maximums such as graphics, memory, link, SMIO, VDDC, VDDGFX, VDDCI, MVDD, and UVD handshake definitions.

`enum SMU9_TABLE_ID` and `enum SMU10_TABLE_ID` enumerate generation-specific table IDs used by transfer-manager paths. SMU9 has PP, watermark, AVFS, tools, and AVFS fuse tables; SMU10 has watermark and clock tables.

The declared functions cover PP table download/upload, SMC message send with or without a parameter, SCLK threshold update, SMC table update, firmware-header parsing, thermal AVFS and fan setup, SMC table initialization, graphics/memory level population, MC register table initialization, logical offset/max queries, DPM-running and hardware-AVFS presence checks, DPM-profile updates, generic SMU table manager transfer, and stopping the SMC.

## Control flow

Callers invoke `smum_*` wrappers with a `struct pp_hwmgr *`. The wrapper layer looks up the generation-specific function table installed in the hardware manager and calls the implementation if present. That lets SMU7, SMU8, SMU9, SMU10, and ASIC-specific managers provide different register sequences under a common interface.

Typical initialization flow is: initialize the SMU backend, process firmware headers to discover firmware-owned table offsets, initialize MC and DPM tables, upload the SMC table, configure thermal/fan behavior, and then service runtime updates through message sends and table updates.

## State and persistence behavior

`smumgr.h` itself stores no state. State lives in `pp_hwmgr`, its `backend`, and its `smu_backend`. The functions declared here may mutate firmware SRAM, GPU registers, DPM enable masks, software table copies, thermal/fan tables, and PowerPlay runtime profile settings.

Because the interface uses logical IDs for offsets and table updates, state persistence depends on the implementation: some updates write SMC SRAM directly; others send messages that make firmware update internal state; others populate host-side cache structures first.

## Dependencies and integration points

The header includes Linux types plus `amd_powerplay.h` and `hwmgr.h`. It integrates with every PowerPlay hardware manager that needs firmware-mediated power management. Generation-specific headers supply the message IDs and table layouts used below this abstraction.

This file is also an integration contract between policy code and firmware transport code. Policy code should use these wrappers instead of reaching into implementation-private SMU tables unless no generic operation exists.

## Risks

The abstraction returns generic `int`/`bool` values but hides generation-specific semantics. A wrapper may be implemented as a no-op or may return success even if firmware logged an error, depending on the backend. Logical member IDs can also map to different offsets across generations, so a missing `get_offsetof` case can return zero, which may look like a valid offset.

Because many APIs accept `void *` or raw table pointers, type safety is limited. Callers must know which generation and table ID they are targeting.

## Test signals

Build signals include successful compilation of all PowerPlay SMU manager implementations against this interface. Runtime signals include successful firmware-header processing, SMC message exchange, DPM table initialization, UVD/VCE table updates, fan table upload, and clean SMU stop/unload paths across supported ASIC families.
