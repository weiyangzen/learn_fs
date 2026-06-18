# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_interface.h

## Purpose

`odm_interface.h` provides macro indirection for resolving generic ODM register and bit names to 11n-specific macro names. The source was read as a complete 40-line file.

## Important APIs, Types, and Functions

Important macros are `_reg_11N`, `_bit_11N`, `_cat`, `ODM_REG(_name)`, and `ODM_BIT(_name)`.

## Control Flow

There is no runtime flow. At preprocessing time, `ODM_REG(IGI_A)` becomes `ODM_REG_IGI_A_11N`, and `ODM_BIT(IGI)` becomes `ODM_BIT_IGI_11N`.

## State and Persistence Behavior

The header owns no state; it maps symbolic references to hardware register macros.

## Dependencies and Integration Points

It depends on `odm_RegDefine11N.h` providing the target macros. It is included by `odm_precomp.h` and used throughout ODM code.

## Risks and Edge Cases

Only 11n expansion is supported in this snapshot, so adding 11ac or chip-specific variants requires changing macro dispatch. Missing target macros fail at compile time.

## Test Signals

Compile coverage of all `ODM_REG`/`ODM_BIT` call sites is the main signal.
