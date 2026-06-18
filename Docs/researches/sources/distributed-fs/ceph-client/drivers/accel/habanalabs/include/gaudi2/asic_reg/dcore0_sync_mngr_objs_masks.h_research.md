# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_masks.h

Purpose: Defines bitfield shifts and masks for DCORE0 sync-manager object registers. It covers SOB object value/increment/long-SOB/trace-evict fields, monitor arm fields, monitor configuration, payload address/data, monitor status, security vectors, and privilege vectors.

Important APIs/types/functions: Exports 46 `DCORE0_SYNC_MNGR_OBJS_*` constants, including `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_VAL_SHIFT` (0), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_VAL_MASK` (0x7FFF), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_LONG_SOB_SHIFT` (24), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_LONG_SOB_MASK` (0x1000000), `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_TRACE_EVICT_SHIFT` (30), and `DCORE0_SYNC_MNGR_OBJS_SM_PRIV_PRIV_MASK` (0xFFFFFFFF). It provides no functions or types.

Control flow: No code is executed here. Sync-object and monitor programming code uses these masks with the large object-register map to arm monitors, update SOBs, and decode pending/valid/protection state.

State and persistence behavior: The file has no state. Correct masks determine how software interacts with persistent SOB/monitor hardware state.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with synchronization manager object programming, CQ/LBW monitor payloads, and security/privilege controls.

Risks: Incorrect monitor arm/config masks can miss completions or signal too early. Security and privilege vector fields are broad and should be programmed through validated policy paths.

Test signals: SOB increment/value tests, monitor arm and trigger tests, CQ/LBW payload tests, security/privilege negative tests, and register readback of packed object fields.
