# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt7986/mt7986-afe-common.h

## Purpose

This header defines MT7986 AFE IDs, private platform state, rate-transform declaration, and ETDM registration entry point.

## Important APIs, Types, and Functions

Memif enum covers `DL1` and `VUL12`; `MT7986_DAI_ETDM` follows the memifs. IRQ enum exposes three IRQs. `struct mt7986_afe_private` stores bulk clocks, clock count, runtime-PM register-control bypass flag, and per-DAI private pointers. `mt7986_afe_rate_transform()` and `mt7986_dai_etdm_register()` are declared.

## Control Flow

The platform probe allocates this private structure, fills bulk clock data, uses the bypass flag during regmap initialization, and lets ETDM `set_fmt()` allocate per-DAI format state in `dai_priv`.

## State and Persistence Behavior

Bulk clocks and ETDM format state persist while the platform device is bound. `pm_runtime_bypass_reg_ctl` is a transient probe-time/runtime-PM guard that prevents register writes before regmap defaults are captured.

## Dependencies and Integration Points

Includes ALSA SoC, CCF, list/regmap, and common MediaTek base AFE. Shared by MT7986 platform, ETDM DAI, and machine driver.

## Risks and Edge Cases

`dai_priv` is indexed by DAI ID, so enum stability matters. ETDM code assumes `set_fmt()` has initialized `dai_priv[dai->id]` before `hw_params`; machine drivers must supply a valid DAI format.

## Test Signals

Compile coverage, platform probe, ETDM format negotiation, and runtime PM around regmap initialization validate this contract.
