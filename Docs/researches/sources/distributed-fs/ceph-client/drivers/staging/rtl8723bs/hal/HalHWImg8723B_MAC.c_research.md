# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_MAC.c

## Purpose

`HalHWImg8723B_MAC.c` embeds and loads the generated RTL8723B MAC register initialization table. The file was read as a complete 237-line source.

## Important APIs, Types, and Functions

The main API is `ODM_ReadAndConfig_MP_8723B_MAC_REG`. Static state includes `Array_MP_8723B_MAC_REG`, and helper `CheckPositive` matches generated conditions against `struct dm_odm_t` board/cut/platform/package/interface fields.

## Control Flow

The loader walks `(offset, data)` pairs. Direct entries call `odm_ConfigMAC_8723B(pDM_Odm, offset, (u8)data)`. Conditional markers trigger the same generated IF/ELSE/ENDIF mini-parser used by the BB and RF image files: evaluate `CheckPositive`, skip unmatched entries, and configure matched entries until the branch ends.

## State and Persistence Behavior

The table is static and immutable. Runtime persistence is the programmed MAC register state, including coexistence-related defaults such as `0x765` and `0x76e` values near the end of the table.

## Dependencies and Integration Points

It includes `<linux/kernel.h>` and `odm_precomp.h`, uses `READ_NEXT_PAIR`, condition macros, and `odm_ConfigMAC_8723B`. It is part of chip initialization before normal firmware/HAL operation.

## Risks and Edge Cases

All writes are byte writes, so values must remain in the expected width. Conditional parser bugs or board metadata mistakes can silently skip critical MAC settings. The duplicated `CheckPositive` implementation can diverge from BB/RF image loaders.

## Test Signals

Compile coverage, register-write trace comparison, board-variant conditional tests, and device bring-up tests that verify MAC register defaults, beacon/control behavior, and coexistence baseline registers are expected.
