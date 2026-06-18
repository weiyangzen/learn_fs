# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/bf.c

## Purpose
`bf.c` implements shared beamforming helper logic for `rtw88` chips. It decides whether a connected BSS can use SU or MU beamformee mode, tracks beamformer resource counts, programs common beamforming registers, handles MU group ID table updates, and exposes helper functions for chip-specific wrappers.

## Important APIs and control flow
`rtw_bf_assoc()` runs on association when global beamforming support is enabled. It skips non-5 GHz chips, finds the AP station entry under RCU, compares local VHT beamformee capabilities with peer beamformer capabilities, and chooses MU first, then SU. MU setup fills `bfee->mac_addr`, role, partial AID, and association ID, checks `chip->bfer_mu_max_num`, increments `bf_info.bfer_mu_cnt`, and calls `rtw_chip_config_bfee(..., true)`. SU setup checks `chip->bfer_su_max_num`, records sounding dimensions, allocates a register slot from `bf_info.bfer_su_reg_maping`, increments `bfer_su_cnt`, and calls the same chip hook.

`rtw_bf_disassoc()` reverses the association role by decrementing SU/MU counters, invoking `rtw_chip_config_bfee(..., false)`, and clearing the vif role. `rtw_bf_set_gid_table()` copies `conf->mu_group.membership` and `position` into a `cfg_mumimo_para` and programs the MU tables only when the vif is currently an MU beamformee.

Low-level helpers program hardware registers: `rtw_bf_init_bfer_entry_mu()` writes MU beamformer MAC/PAID/CSI control; `rtw_bf_cfg_sounding()` configures sounding protocol and BF report poll filters; `rtw_bf_cfg_mu_bfee()` loads MU GID/user position tables; `rtw_bf_del_bfer_entry_mu()` and `rtw_bf_del_sounding()` clear MU and sounding state. `rtw_bf_enable_bfee_su()` and `rtw_bf_enable_bfee_mu()` set CSI report parameters and RX filter acceptance, while remove helpers clear the corresponding register slots. `rtw_bf_phy_init()` initializes MU-MIMO control defaults. `rtw_bf_cfg_csi_rate()` switches CSI report rate based on RSSI threshold.

## State and dependencies
Persistent runtime state is split between `struct rtw_vif::bfee` and `struct rtw_dev::bf_info`. `bfee` stores role, peer MAC, partial AID, sounding dimensions, SU register index, and MU AID. `bf_info` stores active MU/SU counts, SU register slot bitmap, and current CSI report rate. Hardware state persists in MAC/BB registers until removed or reinitialized. Dependencies include mac80211 station/BSS data, VHT capability bits, `main.h` beamforming structs, register definitions, chip operation callbacks, and exported symbols used by chip files such as 8822B/8822C/8821C.

## Integration points
mac80211 BSS change handling calls `rtw_bf_assoc()` on association and `rtw_bf_disassoc()` on disassociation. MU group updates enter through `rtw_chip_set_gid_table()`, which is implemented by capable chips as `rtw_bf_set_gid_table()`. Chip-specific operation tables provide `config_bfee` and `cfg_csi_rate`; chips without support leave those hooks NULL.

## Risks and test signals
Counter and bitmap accounting is the main correctness risk: double association/disassociation or missing role checks can underflow counters or leak SU register slots. Capability handling is VHT-only and 5 GHz-gated, so HE/EHT or 2.4 GHz cases are intentionally outside this path. Register programming is chip-sensitive; incorrect CSI parameters can break sounding or rate feedback. Test signals include association with SU/MU-capable APs, MU group changes, disassociation cleanup, repeated roam cycles, debug category `RTW_DBG_BF`, CSI rate changes around RSSI 40, and register traces for `REG_ASSOCIATED_BFMER*`, `REG_MU_TX_CTL`, and `REG_BBPSF_CTRL`.
