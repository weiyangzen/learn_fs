# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_setup.c

## Purpose

`nv_setup.c` initializes shared NVIDIA register-bank pointers, provides VGA/DAC register accessors over MMIO, discovers framebuffer memory/clock limits, detects display heads/connectors, probes EDID through I2C or Open Firmware, and decides whether the active output is CRT, flat panel, or TV. The source was read as a complete 649-line file.

## Important APIs, Types, and Functions

Exported low-level accessors are `NVWriteCrtc`, `NVReadCrtc`, `NVWriteGr`, `NVReadGr`, `NVWriteSeq`, `NVReadSeq`, `NVWriteAttr`, `NVReadAttr`, `NVWriteMiscOut`, `NVReadMiscOut`, `NVWriteDacMask`, `NVWriteDacReadAddr`, `NVWriteDacWriteAddr`, `NVWriteDacData`, and `NVReadDacData`. The exported setup routine is `NVCommonSetup()`. Internal helpers include `NVIsConnected()` for analog detection, `NVSelectHeadRegisters()` for per-head pointer selection, `nv4GetConfig()` and `nv10GetConfig()` for memory/clock/cursor limits.

## Control Flow

`NVCommonSetup()` allocates temporary var and monitor-spec structures, maps register-bank pointers into `struct nvidia_par`, derives `twoHeads`, scaler, PLL, vsync, and blending capabilities, identifies mobile chip IDs, reads architecture-specific memory/clock configuration, selects head 0, unlocks VGA, creates I2C buses, and performs display detection. Single-head flow probes connector 1 for EDID or falls back to current hardware programming. Dual-head flow inspects output routing, analog presence, slaved flat-panel/TV bits, temporarily selects heads, probes EDID on both connectors, chooses a compatible monitor/head, applies forced flatpanel/CRTC parameters if provided, and selects final head registers. It then records panel width/height/syncs for flat panels, copies chosen monitor specs into `info->monspecs`, computes dithering/LVDS state, frees temporary EDID/monitor allocations, and returns.

## State and Persistence Behavior

The function fills nearly all hardware topology fields in `struct nvidia_par`: register pointers, `twoHeads`, `fpScaler`, `twoStagePLL`, `WaitVSyncPossible`, `BlendingPossible`, `RamAmountKBytes`, `CrystalFreqKHz`, `MinVClockFreqKHz`, `MaxVClockFreqKHz`, `CURSOR`, `IOBase`, `FlatPanel`, `Television`, `CRTCnumber`, `fpWidth`, `fpHeight`, `fpSyncs`, `FPDither`, and `LVDS`. It also stores parsed EDID monitor specs in `info->monspecs`; mode databases are later consumed and freed by `nvidia_set_fbinfo()`.

## Dependencies and Integration Points

The file depends on VGA constants, PCI config reads, NVIDIA raw MMIO helpers, `nv_i2c.c`, `nv_of.c`, fbdev EDID parsing, and the register layout used by `nv_hw.c` and `nvidia.c`. `nvidiafb_probe()` calls `NVCommonSetup()` before framebuffer mapping and initial mode selection.

## Risks and Edge Cases

Display detection mixes EDID, current register state, analog load detection, laptop chip heuristics, and user-forced options; ambiguous hardware can choose the wrong head or output. Some PCI config helper calls assume specific host bridge slots for nForce memory detection. OF/I2C EDID failures are tolerated but reduce mode validation quality. Temporary monitor specs are shallow-copied into `info->monspecs`, so ownership of mode databases must be handled carefully by later cleanup.

## Test Signals

Test single-head CRT, single-head DFP, dual-head CRT/DFP combinations, forced `flatpanel` and `forceCRTC`, `reverse_i2c`, OF EDID fallback, mobile chips with no detected output, LVDS/TMDS detection, and nForce memory-size paths. Monitor-spec mode databases should be valid through initial mode selection and freed once.
