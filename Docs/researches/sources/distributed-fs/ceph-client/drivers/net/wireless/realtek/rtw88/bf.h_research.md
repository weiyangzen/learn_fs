# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.h

## Purpose
`bf.h` is the public beamforming interface for the `rtw88` core and chip implementations. It centralizes beamforming register offsets, bit definitions, CSI/sounding enums, parameter structs, function prototypes, and thin chip-operation dispatch helpers.

## Important definitions and APIs
The header defines beamforming register addresses such as `REG_TXBF_CTRL`, `REG_ASSOCIATED_BFMER0_INFO`, `REG_ASSOCIATED_BFMER1_INFO`, `REG_TX_CSI_RPT_PARAM_BW20`, `REG_SND_PTCL_CTRL`, `REG_MU_TX_CTL`, `REG_MU_STA_GID_VLD`, `REG_MU_STA_USER_POS_INFO`, `REG_WMAC_MU_BF_OPTION`, and `REG_WMAC_MU_BF_CTL`. Bit fields cover sounding protocol control, MU retry/table validity, CSI report rate forcing, RX filter bits, and NDP/NDPA behavior.

`enum csi_rsc` selects CSI bandwidth source, and `enum csi_seg_len` selects MU CSI segment length. `struct cfg_mumimo_para` carries MU-MIMO group/user-position table data from mac80211 BSS configuration to hardware programming. `struct mu_bfer_init_para` carries the MU beamformer address, PAID, CSI parameter, AID, and segment length for register initialization.

The declared functions split into association policy (`rtw_bf_assoc`, `rtw_bf_disassoc`), register setup/cleanup (`rtw_bf_init_bfer_entry_mu`, `rtw_bf_cfg_sounding`, `rtw_bf_cfg_mu_bfee`, `rtw_bf_del_bfer_entry_mu`, `rtw_bf_del_sounding`), SU/MU enable and remove helpers, GID table programming, PHY init, and CSI rate adaptation.

## Control flow and integration
The static inline wrappers are the key integration contract. `rtw_chip_config_bfee()` checks `rtwdev->chip->ops->config_bfee` before dispatching to chip-specific enable/remove code. `rtw_chip_set_gid_table()` and `rtw_chip_cfg_csi_rate()` similarly guard optional chip hooks. This allows the core mac80211 path to invoke beamforming operations while unsupported chips safely do nothing.

## State and persistence behavior
The header itself owns no state, but it defines the register and parameter ABI that manipulates persistent device state in `struct rtw_bfee`, `struct rtw_bf_info`, and hardware registers. Register definitions here must match the common Realtek MAC/BB layout expected by `bf.c` and chip-specific wrappers.

## Dependencies and risks
Dependencies include `main.h` structures, `reg.h` register access helpers, Linux bit macros, and chip operation tables. Risks include stale register constants, mismatched bit masks, and unguarded chip callbacks. Since these helpers are included by multiple chip files, changing a prototype or struct layout can break all beamforming-capable chips.

## Test signals
Compile coverage should include chips with populated beamforming hooks and chips with NULL hooks. Runtime signals include successful SU/MU association, GID table updates, CSI report rate changes, debug logs from `RTW_DBG_BF`, and absence of NULL callback crashes on unsupported chips.
