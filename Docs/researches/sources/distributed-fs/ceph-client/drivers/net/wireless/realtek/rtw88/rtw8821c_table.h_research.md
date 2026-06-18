<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.h

## Purpose

This header exposes the RTW8821C PHY table descriptors produced by `rtw8821c_table.c`. It is the narrow compile-time contract between the generated/static hardware data file and the executable chip implementation in `rtw8821c.c`.

## Important APIs and Types

The header declares seven `extern const struct rtw_table` symbols:

- `rtw8821c_mac_tbl`
- `rtw8821c_agc_tbl`
- `rtw8821c_agc_btg_type2_tbl`
- `rtw8821c_bb_tbl`
- `rtw8821c_bb_pg_type0_tbl`
- `rtw8821c_rf_a_tbl`
- `rtw8821c_txpwr_lmt_type0_tbl`

The only type used directly is `struct rtw_table`, supplied by the surrounding `rtw88` headers included by C files before or alongside this header. The include guard is `__RTW8821C_TABLE_H__`.

## Control Flow and Integration

This header has no runtime control flow. Its declarations allow `rtw8821c.c` to assign table pointers inside `rtw8821c_hw_spec`, while `rtw8821c_table.c` provides the definitions through `RTW_DECL_TABLE_*` macros. The common PHY loader later consumes those pointers from the chip info structure.

The exported symbols form part of this sequence:

1. `rtw8821c_table.c` defines static arrays and macro-generated `struct rtw_table` descriptors.
2. This header declares the descriptors.
3. `rtw8821c.c` includes the header and places selected descriptors in `rtw8821c_hw_spec`.
4. Bus glue drivers pass `rtw8821c_hw_spec` to common probe routines.
5. `rtw_phy_load_tables()` applies the referenced table descriptors during chip initialization.

## State and Persistence Behavior

The header declares immutable table descriptors only. It does not define mutable state, allocate resources, register devices, or persist data. The persistent effect of these declarations is ABI-like within the driver module: symbol names must remain synchronized with the table definitions and chip spec fields.

## Dependencies and Integration Points

- Definition provider: `rtw8821c_table.c`.
- Primary consumer: `rtw8821c.c`.
- Indirect consumers: PCI/SDIO/USB 8821C bus modules and common PHY loader code.
- Shared type provider: `struct rtw_table` from the `rtw88` PHY/table infrastructure.

## Risks

- If an extern declaration is removed or renamed without matching changes in `rtw8821c_table.c` and `rtw8821c.c`, the driver fails to link.
- If a table is declared here but not wired into `rtw8821c_hw_spec` or RFE selection logic, it can become dead data and hide missing hardware variant support.
- The header does not include the type definition itself, so include ordering must keep `struct rtw_table` visible where required. This matches local style but is a coupling to surrounding includes.

## Test Signals

- Kernel build/link tests are the primary signal because the header is a symbol contract.
- Static search should verify every declaration has exactly one definition and every expected table pointer in `rtw8821c_hw_spec` resolves to the intended symbol.
- Device probe tests indirectly validate the declarations by exercising table load through the chip info structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.h -->
