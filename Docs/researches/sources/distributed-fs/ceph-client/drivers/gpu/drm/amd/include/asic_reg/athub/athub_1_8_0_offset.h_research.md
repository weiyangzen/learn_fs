# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_8_0_offset.h

## Purpose
This generated-style header defines register offsets and base-index selectors for the ATHUB 1.8.0 hardware block in AMDGPU. It does not define bitfields; it maps symbolic `reg*` names to register offsets within ATHUB address blocks and pairs each register with a `*_BASE_IDX` value so driver register helpers can choose the correct MMIO base.

The file covers three address blocks: `aid_athub_atsdec` at base address `0x3080`, `aid_athub_xpbdec` at base address `0x46000`, and `aid_athub_rpbdec` at base address `0x46200`.

## Important APIs, Types, and Macros
The exported API is a set of C preprocessor constants. Each register has a `regNAME` offset and a `regNAME_BASE_IDX` selector. Base index `0` is used for the ATSDEC block, while base index `1` is used for XPBDEC and RPBDEC registers in this header.

The ATSDEC block includes offsets for `ATC_ATS_CNTL` through `ATC_ATS_CNTL4`, miscellaneous and status controls, ATC performance counters, fault status registers `INFO` through `INFO4`, fault address/default-page registers, PCIe ATS/PASID/page-request controls, outstanding page request allocation, ATHUB command, per-VF ATS controls for VF 0-15, shared virtualization reset and active function ID, SDP port control, VMID/PASID mapping update status, VMID0-VMID15 PASID mappings, translation fault response control, VMID status, ATHUB miscellaneous and memory power controls, and IH credit.

The XPBDEC block includes router source aperture offsets, XDMA source apertures, router and XDMA destination maps, CLG configuration and extra/mask registers, LB and WCB status, host configuration, P2P BAR configuration and BAR0-BAR7, BAR setup and delta controls, peer system BAR0-BAR9, XDMA peer system BAR0-BAR3, clock gating, interface and pipe status/configuration, sub-block control, map invert flush LSB, performance knobs, sticky and sticky write-one-to-clear registers, miscellaneous config, readback variants of CLG extra/mask, GFX/MM match and mask registers, and GFX/MM unit-ID mapping registers.

The RPBDEC block includes passPW, block-level, tag, arbitration, BIF, performance counter, deinterleave/combine, VC switch, RPB performance counter low/high/config/result registers, ATS controls, and RPB SDP port control.

## Control Flow
There is no executable control flow. Consumers include this file to resolve symbolic register names into numeric offsets at compile time. Runtime control flow lives in the callers that issue MMIO reads/writes through AMDGPU register helper macros.

The source order is the logical register order within each address block. This helps pair offsets with matching shift/mask headers and supports generated table construction, but the C preprocessor does not impose runtime behavior.

## State and Persistence Behavior
The header has no software state or persistence. Its constants identify where persistent hardware state resides in the GPU MMIO register aperture. The actual state includes ATS/PASID enablement, fault logs, VMID mappings, per-VF ATS state, P2P routing windows, interface status, sticky status, performance counters, and RPB scheduling controls.

Incorrect offsets directly redirect register accesses to the wrong hardware location. That makes this header part of the persistence contract for reset, resume, VMID setup, virtualization setup, fault handling, and performance diagnostics on ATHUB 1.8.0 devices.

## Dependencies and Integration Points
This file has only an include guard and no C includes. It depends on sibling shift/mask headers for field definitions and on AMDGPU register access conventions that combine `reg*` offsets, `*_BASE_IDX` selectors, and mask/shift constants. It integrates with AMDGPU ASIC initialization, memory-management and address-translation paths, SR-IOV virtualization, PCIe ATS/PRI/PASID programming, XPB P2P routing, RPB queue/performance tuning, fault handling, and debug/performance counter tooling.

Compared with the ATHUB 1.0 mask file in this work item, this header represents a later hardware generation and only carries offsets. Correct driver use requires matching it with the ATHUB 1.8.0 shift/mask header, not with an older generation's field layout unless code has explicitly verified compatibility.

## Risks
The largest risk is offset/base-index drift. A wrong offset can make a valid register write hit an unrelated register, and a wrong base index can access the right offset in the wrong ATHUB address block. Either failure can break ATS setup, fault collection, SR-IOV VF control, P2P routing, or RPB scheduling in ways that are difficult to diagnose from software logs alone.

Generation skew is also important. The 1.8.0 ATSDEC block includes newer control and fault-info registers such as `ATC_ATS_CNTL2`, `ATC_ATS_CNTL3`, `ATC_ATS_CNTL4`, `ATC_ATS_MISC_CNTL`, and fault status `INFO3/INFO4`, while the VMID mapping list in this offset header runs through VMID15. Code shared with other ATHUB generations must not assume identical register presence or count.

## Test Signals
Useful signals include all-ASIC AMDGPU build coverage, generated-header consistency checks against the register database, register read/write smoke tests for base index 0 and 1, GPU reset and resume on ATHUB 1.8.0 hardware, ATS/PASID/PRI enablement tests, VMID mapping and invalidation tests, SR-IOV VF ATS control tests, fault injection with status/fault-address readback, XPB P2P/XDMA routing tests, sticky status write-one-to-clear checks, RPB performance counter readback, and tracing that confirms expected MMIO addresses are produced from `reg*` plus base index selection.
