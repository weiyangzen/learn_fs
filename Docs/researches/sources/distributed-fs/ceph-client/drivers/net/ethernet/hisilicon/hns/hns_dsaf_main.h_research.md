# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.h

## Purpose
`hns_dsaf_main.h` defines the DSAF device model, operating modes, hardware table structures, stats structures, interrupt-source layouts, misc operation callbacks, private TCAM mirror entries, inline TCAM address/pulse helpers, and public DSAF service prototypes.

## Important APIs and Types
Core types include `enum dsaf_mode`, `struct dsaf_device`, `struct dsaf_misc_op`, `struct dsaf_hw_stats`, `struct hnae_vf_cb`, TCAM data/config structs, MAC single/multi destination entries, and `struct dsaf_drv_priv`. Inline helpers `hns_dsaf_tbl_tcam_addr_cfg`, `hns_dsaf_tbl_tcam_load_pul`, and `hns_dsaf_tbl_line_addr_cfg` encapsulate common table register writes. `hns_ae_get_vf_cb` maps an HNAE handle back to its DSAF VF wrapper.

## Control Flow
The header describes the layering used by implementation files: DSAF probe initializes `dsaf_device`; misc ops provide reset/LED/PHY abstraction for OF versus ACPI; MAC and AE layers call declared TCAM, stats, pause, register, and flow-drain helpers.

## State and Persistence
`struct dsaf_device` persists all driver-wide runtime state for a platform device: MMIO bases, regmap handles, version/mode, descriptor and buffer config, component arrays, misc ops, stats, interrupt status, and TCAM lock. `struct dsaf_drv_priv` persists the software MAC table allocated beside the device object.

## Dependencies and Integration Points
It includes `hnae.h`, `hns_dsaf_reg.h`, and `hns_dsaf_mac.h`, tying together the HNAE framework, register map, and MAC abstraction. The header is shared across DSAF main, MAC, misc, and AE adapter code.

## Risks
Many constants encode hardware capacities and offsets; incorrect values affect memory allocation, TCAM masks, stats sizes, and queue routing. `hnae_vf_cb` requires `ae_handle` to be the final member for flexible-array allocation assumptions. The mutual dependency with MAC headers is fragile but protected by include guards.

## Test Signals
Compile-time structure layout, TCAM port mask sizing from `DSAF_PORT_MSK_NUM`, stats count constants (`DSAF_STATIC_NUM`, `DSAF_V2_STATIC_NUM`), register dump size `DSAF_DUMP_REGS_NUM`, and correct mapping from `hnae_handle` to `hnae_vf_cb` are key validation points.
