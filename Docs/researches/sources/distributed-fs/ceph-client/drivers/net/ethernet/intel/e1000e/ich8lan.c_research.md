# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ich8lan.c

## Purpose

`ich8lan.c` is the Intel e1000e hardware-family implementation for ICH8/ICH9/ICH10 and PCH LAN controllers, including 82566/82567/82577/82578/82579 and later I217/I218 style integrated MAC/PHY devices. It binds this silicon family into the generic e1000e core by defining MAC, PHY, and NVM operation tables plus one `struct e1000_info` per supported family generation. The file is responsible for hardware reset, link setup, PHY workarounds, ultra-low-power transitions, flash-backed NVM access, receive address programming under manageability constraints, LED control, and family-specific statistics cleanup.

## Important APIs, Types, And Functions

The local flash helper unions model hardware sequencing registers: `ich8_hws_flash_status`, `ich8_hws_flash_ctrl`, `ich8_hws_flash_regacc`, and `ich8_flash_protected_range`. Inline helpers `__er16flash`, `__er32flash`, `__ew16flash`, and `__ew32flash` access `hw->flash_address`.

Initialization flows are centered on `e1000_get_variants_ich8lan`, `e1000_init_mac_params_ich8lan`, `e1000_init_nvm_params_ich8lan`, `e1000_init_phy_params_ich8lan`, and `e1000_init_phy_params_pchlan`. These populate `hw->mac`, `hw->phy`, and `hw->nvm` ops, select media as copper, assign PHY register accessors, size flash banks, clear shadow RAM, and adjust feature flags such as jumbo support, K1 workarounds, and PCIm-to-PCI arbiter workarounds.

Reset and bring-up are handled by `e1000_reset_hw_ich8lan`, `e1000_init_hw_ich8lan`, `e1000_initialize_hw_bits_ich8lan`, `e1000_get_cfg_done_ich8lan`, `e1000_phy_hw_reset_ich8lan`, and `e1000_post_phy_reset_ich8lan`. Link paths include `e1000_setup_link_ich8lan`, `e1000_setup_copper_link_ich8lan`, `e1000_setup_copper_link_pch_lpt`, `e1000_check_for_copper_link_ich8lan`, and `e1000_get_link_up_info_ich8lan`.

Power and workaround entry points exported through `ich8lan.h` include `e1000_configure_k1_ich8lan`, `e1000_set_eee_pchlan`, `e1000_enable_ulp_lpt_lp`, `e1000_suspend_workarounds_ich8lan`, `e1000_resume_workarounds_pchlan`, `e1000e_igp3_phy_powerdown_workaround_ich8lan`, `e1000e_gig_downshift_workaround_ich8lan`, `e1000_copy_rx_addrs_to_phy_ich8lan`, and `e1000_lv_jumbo_workaround_ich8lan`.

NVM operations are supplied through `ich8_nvm_ops` and `spt_nvm_ops`: `e1000_read_nvm_ich8lan`, `e1000_read_nvm_spt`, `e1000_write_nvm_ich8lan`, `e1000_update_nvm_checksum_ich8lan`, `e1000_update_nvm_checksum_spt`, `e1000_validate_nvm_checksum_ich8lan`, and `e1000e_write_protect_nvm_ich8lan`.

## Control Flow

Probe-time integration starts in the e1000e PCI table, which selects one of the exported `e1000_info` records at the bottom of this file. The generic core copies `ich8_mac_ops`, `ich8_phy_ops`, and one NVM ops table into `hw`; then `get_variants` runs MAC/NVM/PHY parameter initialization. PHY initialization first gates hardware PHY configuration where needed, disables unknown ULP state, acquires the PHY semaphore, probes or recovers PHY accessibility, possibly toggles `LANPHYPC`, resets the PHY, then assigns type-specific PHY callbacks.

Reset flow disables PCIe master access, masks interrupts, stops Rx/Tx, applies pre-reset errata, optionally includes PHY reset, issues global reset, waits for config done, runs post-PHY-reset workarounds, clears interrupt state, and disables later autonomous power gating on newer PCH. Hardware init then sets required MAC bits, reconfigures K1, initializes LEDs and receive address registers, clears MTA, handles 82578 wakeup errata, sets up link/flow control, adjusts TX descriptor policy, sets no-snoop behavior, enables newer DMA-clock workarounds, and clears counters.

Link-change flow is guarded by `mac->get_link_status`. It checks PHY link, applies K1, TIPG, RX latency, PLL clock, beacon, LTR, and EEE workarounds by MAC/PHY generation, then delegates collision distance and flow-control resolution to generic MAC helpers. If link is down or an error occurs, it restores `get_link_status` so the core checks again later.

NVM update flow is deliberately two-phase. Writes only mark `dev_spec->shadow_ram[offset]` modified. Checksum update writes a generic checksum into shadow RAM, detects the active bank, erases the inactive bank, copies every word or dword from old bank with modified values overlaid, keeps the new bank invalid until copying is complete, marks the new signature valid last, invalidates the old bank, clears shadow RAM, reloads EEPROM, and delays for reload visibility.

## State And Persistence Behavior

The file mutates hardware registers, PHY registers, Kumeran registers, host/ME handoff registers, flash sequencing registers, and `hw` software state. Persistent state is mostly flash-backed NVM. Shadow RAM is transient in `hw->dev_spec.ich8lan.shadow_ram`; it becomes persistent only when an update/checksum operation successfully commits to flash. Bank signatures at NVM word `0x13` determine which bank is active. `e1000e_write_protect_nvm_ich8lan` sets flash protected range PR0 and flash lock-down, making later write/erase cycles ignored until hardware reset.

Power state is tracked with `dev_spec->ulp_state`, `eee_disable`, `eee_lp_ability`, `nvm_k1_enabled`, and `kmrn_lock_loss_workaround_enabled`. These fields coordinate ULP entry/exit, EEE link behavior, suspend/resume workarounds, and K1 policy across resets and link changes.

## Dependencies And Integration Points

This file depends on the generic e1000e register macros and helper layers from `e1000.h`, PHY helpers such as `e1000e_phy_hw_reset_generic`, `e1000e_setup_copper_link`, `e1000_copper_link_setup_82577`, M88/IGP/IFE setup helpers, NVM checksum helpers, PCI config access, Linux delay APIs, mutexes, bit operations, and Ethernet CRC helpers. It integrates with `netdev.c` through exported `struct e1000_info` records and with the generic MAC/manageability layers through operation callbacks.

ME/manageability integration is explicit: shared RAR/SHRA programming respects ME locks in `FWSM`, reset paths check `check_reset_block`, ULP can be delegated to ME through `H2ME`, PHY power-down avoids breaking management mode, and receive address writes use `EXTCNF_CTRL.SWFLAG`.

## Risks

Highest-risk areas are flash erase/write sequencing, active-bank detection, and signature updates because failures can leave the controller with no valid NVM bank. The code mitigates this by writing inactive banks, validating last, invalidating old banks after success, retrying flash cycles, and using a global NVM mutex, but interrupted power or bad flash protection can still leave update failures. PHY/ME arbitration is another risk: missing semaphore release, ignoring reset blocks, or writing SHRA entries locked by ME can cause link loss or failed address programming. Workaround code is generation- and revision-sensitive; broadening conditions can regress older silicon. Many routines use busy waits and sleeps in driver paths, so test coverage should include timeout and blocked-firmware cases.

## Test Signals

Useful signals are successful probe across ICH8/ICH9/ICH10/PCH generations, link up/down at 10/100/1000 half/full where supported, suspend/resume with and without WoL/ME, ULP entry/exit on LPT-LP/I218 devices, EEE negotiation, jumbo enable/disable on 82579 and newer, alternate receive address programming under ME locks, NVM checksum validation/update with read-only flash, and `dmesg` absence of messages such as flash cycle timeout, "Reset blocked by ME" during unexpected paths, "No valid NVM bank present", "ULP_CONFIG_DONE took..." warnings, or repeated K1/PHY access failures.
