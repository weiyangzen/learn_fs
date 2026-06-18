# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.h

## Purpose

This small header defines firmware stage indices for the PCXHR load sequence and declares the firmware setup/reset functions shared with the main and core driver files.

## Important APIs, Types, And Functions

- `PCXHR_FIRMWARE_XLX_INT_INDEX`, `PCXHR_FIRMWARE_XLX_COM_INDEX`, `PCXHR_FIRMWARE_DSP_EPRM_INDEX`, `PCXHR_FIRMWARE_DSP_BOOT_INDEX`, and `PCXHR_FIRMWARE_DSP_MAIN_INDEX` enumerate the five possible firmware stages.
- `PCXHR_FIRMWARE_FILES_MAX_INDEX` documents the firmware-stage count.
- `pcxhr_setup_firmware()` loads and initializes firmware.
- `pcxhr_reset_board()` resets/mutes loaded hardware during cleanup.

## Control Flow

The indices drive the ordered firmware loop in `pcxhr_setup_firmware()` and the stage switch in `pcxhr_dsp_load()`. The reset function is called from the manager free path if any firmware stage was loaded.

## State And Persistence

No state is stored here, but the constants define the bit positions used in `mgr->dsp_loaded`.

## Dependencies And Integration Points

This header is consumed by `pcxhr.c`, `pcxhr_core.c`, and `pcxhr_hwdep.c`. Its stage indices must match the firmware filename arrays and load dispatch logic.

## Risks

Changing index values without updating firmware arrays, loaded-bit tests, and reset logic would break staged loading and cleanup. The header name may suggest an ALSA hwdep device, but current code uses direct firmware loading.

## Test Signals

Compile and firmware-load tests verify declarations and indices. Cleanup after failures at each firmware stage is the key runtime signal.
