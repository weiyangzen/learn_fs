# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/pg/dcn42/dcn42_pg_cntl.h

## Purpose
Defines DCN42 power-gating register/field tables, controller storage, and public prototypes. It is the register contract for `dcn42_pg_cntl.c`.

## Important APIs, Types, and Macros
`PG_CNTL_REG_LIST_DCN42()` lists config/status registers for domains 0-3, 16-19, 22-26 plus `DC_IP_REQUEST_CNTL`. `PG_CNTL_MASK_SH_LIST_DCN42(mask_sh)` maps force-on, power-gate, desired state, FSM status, and IP request fields for all domains. `struct pg_cntl_shift`, `struct pg_cntl_mask`, `struct pg_cntl_registers`, and `struct dcn_pg_cntl` carry table data and the base controller. Prototypes expose all DCN42 PG control functions, create, init-status, and both `dcn42_pg_cntl_destroy()` and generic `dcn_pg_cntl_destroy()`.

## Control Flow and State
The header is declarative. Runtime state is the embedded `struct pg_cntl` plus immutable pointers to generated register/field tables. Domain 26 coverage is the notable expansion over DCN35.

## Dependencies and Integration Points
Includes `pg_cntl.h`. DCN42 resource initialization supplies generated tables and receives a `struct pg_cntl *` with the DCN42 function table attached.

## Risks and Test Signals
Risks include domain list mismatch with implementation switch statements and wrong field mapping for new DIO controls. Build tests and hardware PG transition tests for domains 22, 23, 24, 25, and 26 are important signals.
