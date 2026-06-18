# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_types.h

## Purpose

`odm_types.h` provides foundational ODM type aliases, endian selection, status enum, adapter-to-ODM accessor, and table-reader helper macros. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

It defines `GET_ODM`, `enum hal_status`, `ODM_ENDIAN_BIG`, `ODM_ENDIAN_LITTLE`, `ODM_ENDIAN_TYPE`, `STA_INFO_T`, `PSTA_INFO_T`, `USE_WORKITEM`, `FPGA_TWO_MAC_VERIFICATION`, `READ_NEXT_PAIR`, `COND_ELSE`, and `COND_ENDIF`.

## Control Flow

There is no runtime flow except macro expansion. `READ_NEXT_PAIR` advances generated table parsing indices safely enough to avoid reading past `ArrayLen`.

## State and Persistence Behavior

The header owns no state. `GET_ODM` locates adapter-scoped `hal_com_data.odmpriv`.

## Dependencies and Integration Points

It includes `drv_types.h` and is the first ODM include in `odm_precomp.h`.

## Risks and Edge Cases

Endian detection depends on `__LITTLE_ENDIAN`. `GET_ODM` assumes `HalData` is allocated and typed as `struct hal_com_data`. `READ_NEXT_PAIR` requires callers to maintain `ArrayLen` and `i` semantics consistently.

## Test Signals

Compile coverage, endian-layout checks for PHY status structs, and generated table parser tests that hit `READ_NEXT_PAIR` boundary behavior are useful.
