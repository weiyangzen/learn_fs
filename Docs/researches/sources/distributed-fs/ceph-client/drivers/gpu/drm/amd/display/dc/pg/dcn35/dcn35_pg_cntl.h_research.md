# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn35/dcn35_pg_cntl.h

## Purpose
Defines DCN35 power-gating register tables, field masks, controller storage, and public PG control prototypes.

## Important APIs, Types, and Macros
`PG_CNTL_REG_LIST_DCN35()` lists domains 0-3, 16-19, 22-25 config/status registers and `DC_IP_REQUEST_CNTL`. `PG_CNTL_MASK_SH_LIST_DCN35(mask_sh)` maps `DOMAIN_POWER_FORCEON`, `DOMAIN_POWER_GATE`, `DOMAIN_DESIRED_PWR_STATE`, `DOMAIN_PGFSM_PWR_STATUS`, and `IP_REQUEST_EN` fields for each domain. `struct pg_cntl_shift`, `struct pg_cntl_mask`, `struct pg_cntl_registers`, and `struct dcn_pg_cntl` hold generated table data and the embedded base controller. Prototypes expose all DCN35 PG operations, create, init-status, and destroy.

## Control Flow and State
The header has no runtime flow but defines the state layout used by `dcn35_pg_cntl.c`. The base `struct pg_cntl` stores software resource state; this header adds immutable register/field table pointers.

## Dependencies and Integration Points
Includes `pg_cntl.h` for the base API and resource enum definitions. DCN35 resource code passes generated register/shift/mask instances into `pg_cntl35_create()`.

## Risks and Test Signals
Risks are incorrect domain coverage or shift/mask mapping, especially because many domains share the same field names. Build tests catch missing symbols; hardware tests should confirm every listed PG domain can report status and transition.
