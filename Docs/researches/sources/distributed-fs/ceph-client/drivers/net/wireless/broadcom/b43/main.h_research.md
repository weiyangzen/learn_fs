# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/main.h

## Purpose
`main.h` is the local public interface for the central b43 driver implementation. It exposes logging verbosity state, rate classification helpers, shared-memory/host-flag/TSF accessors, core reset and restart hooks, MAC suspend/enable helpers, power-save flags, firmware request/release helpers, and a padding macro used by b43 structures.

## Important APIs, Types, and Functions
- `enum b43_verbosity` defines error, warning, info, and debug verbosity levels and derives the default from `B43_DEBUG`.
- `b43_modparam_verbose` is exported for other b43 files to honor the module's log level.
- `b43_is_cck_rate()` and `b43_is_ofdm_rate()` classify b43 rate IDs for PLCP, rate table, and template code.
- Declared helpers include `b43_ieee80211_antenna_sanitize`, `b43_tsf_read/write`, SHM read/write, host flag read/write, `b43_dummy_transmission`, wireless core reset, controller restart, power-save control, PLL reset, MAC suspend/enable, MAC/PHY clock control, MAC frequency switching, and firmware request/release functions.
- `B43_PS_*` flags encode requested hardware power-save and awake/asleep state.

## Control Flow
The header has no runtime control flow. It defines callable contracts used by PHY, DMA/PIO, debug, xmit, and other b43 implementation files to reach central `main.c` services.

## State and Persistence
The header declares accessors for persistent hardware and driver state but owns no state itself. The global `b43_modparam_verbose` mirrors the module parameter in `main.c`, while the declared functions mutate hardware registers, shared memory, firmware references, or `struct b43_wldev` state in their implementations.

## Dependencies and Integration Points
- Includes `b43.h`, so it depends on the main b43 device types and rate constants.
- Bridges non-`main.c` modules to shared memory, host flags, TSF, firmware, MAC lifecycle, and power-save primitives.
- The padding macros are intended for structure layout preservation without naming real fields.

## Risks and Edge Cases
- The verbosity enum and module parameter help text must stay synchronized with `main.c`.
- `b43_is_ofdm_rate()` treats every non-CCK value as OFDM; callers must pass only valid b43 rate IDs.
- Power-save flags can express conflicting states; the implementation warns but currently overrides behavior, so callers should not infer full power-save semantics from the header alone.
- Firmware helpers expose low-level request/release mechanics; callers must respect ownership of `struct b43_firmware_file`.

## Test Signals
- Build tests across b43 submodules catch declaration drift.
- Rate helper users should be covered by PLCP and beacon-template tests that include all CCK and OFDM hardware rate IDs.
- Firmware request helper usage should be exercised by missing, malformed, cached, and released firmware cases.
