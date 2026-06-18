# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ich8lan.h

## Purpose

`ich8lan.h` is the private family header for the ICH8/PCH implementation. It defines flash register offsets, flash cycle constants, firmware/management bits, shared receive address register layout, NVM signature values, PHY page/register encodings, PHY workaround registers, EEE/ULP/LTR constants, and the public prototypes exported from `ich8lan.c` to the rest of e1000e.

## Important APIs, Types, And Constants

Flash access definitions include `ICH_FLASH_GFPREG`, `ICH_FLASH_HSFSTS`, `ICH_FLASH_HSFCTL`, `ICH_FLASH_FADDR`, `ICH_FLASH_FDATA0`, `ICH_FLASH_PR0`, cycle values `ICH_CYCLE_READ`, `ICH_CYCLE_WRITE`, `ICH_CYCLE_ERASE`, timeout constants, address masks, repeat counts, and erase segment sizes. These constants drive the hardware sequencing implementation in `ich8lan.c`.

Management and power constants include `E1000_ICH_FWSM_FW_VALID`, `E1000_ICH_FWSM_RSPCIPHY`, `E1000_FWSM_ULP_CFG_DONE`, `E1000_H2ME_ULP`, `E1000_H2ME_ENFORCE_SETTINGS`, `E1000_EXFWSM_DPG_EXIT_DONE`, and `E1000_FWSM_WLOCK_MAC_*`. They encode firmware validity, reset blocking, ULP handoff, and ME receive-address ownership.

PHY definitions include the `PHY_REG(page, reg)` macro, Kumeran and HV register constants, BM wakeup-page RAR/MTA registers, LPLU/OEM bits, SMBus control/address registers, ULP configuration bits, K1/KMRN controls, EEE EMI addresses, Rapid Start support registers, and LTR register fields. The exported functions include NVM protection, K1/EEE/ULP controls, suspend/resume workarounds, jumbo workaround, EMI accessors, and receive-address copy helpers.

## Control Flow

This header does not execute control flow directly, but it shapes the control flow in `ich8lan.c`: flash cycle helpers use the `ICH_FLASH_*` offsets and cycles; reset and link workarounds branch on FWSM/H2ME/CTRL_EXT/FEXTNVM bits; receive address programming uses `E1000_SHRAL_PCH_LPT` and `E1000_SHRAH_PCH_LPT`; PHY helpers form extended register addresses through `PHY_REG`; EEE and ULP flows select EMI and PHY registers from these constants.

## State And Persistence Behavior

Persistent state represented here is NVM layout and flash protection: `E1000_ICH_NVM_SIG_WORD`, signature masks/values, flash bank sizing helpers, and protected range registers determine how active NVM banks are identified and secured. Runtime state represented here includes firmware validity, ME locks, SMBus-vs-PCIe PHY interface forcing, EEE advertisement/partner ability, ULP sticky bits, LTR latencies, and wakeup address registers. The header itself stores no data, but mistakes in these constants directly affect hardware state and NVM persistence.

## Dependencies And Integration Points

The header assumes types such as `struct e1000_hw`, `s32`, `u16`, and `bool` are available through the including e1000e headers. It is included by `hw.h` after core hardware structures are defined, and its prototypes are used by `netdev.c`, PHY/link setup code, power-management code, and family-specific `e1000_info` operation callbacks.

## Risks

Most risks are definition drift: a wrong bit mask, register offset, page encoding, timeout, or signature constant can break flash updates, low-power transitions, link workarounds, or ME coexistence. Several constants are generation-specific but share similar names, so extending support for newer PCH devices requires careful matching to hardware documentation and existing switch conditions in `ich8lan.c`.

## Test Signals

Header correctness is reflected indirectly by compile success, no sparse/build warnings for missing prototypes, successful NVM reads/updates, stable PHY access after suspend/resume, correct EEE/ULP behavior, working LED identification, and successful receive address programming on PCH devices with ME-reserved SHRA entries.
