# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dm_helpers.h

## Purpose
Declares helper callbacks that Display Manager supplies to Display Core. These functions form the OS/DRM integration boundary for EDID, AUX/I2C, MST, GPU memory allocation, DMUB commands, panel settings, link detection, debug state, and display-policy queries.

## Important APIs, Types, And Functions
Major groups include GPU memory allocation/free, EDID parsing/reading, DP branch and DPCD read/write helpers, I2C submission, MST payload/topology manager operations, DSC enable and hblank reduction writes, fused I/O, DMUB AUX/config sync, periodic detection, panel setting initialization/override, MCCS/DDC helpers, test pattern handling, DCN clock programming, DMUB outbox interrupt control, timeout notification, adaptive sync type, S-BIOS EDID, fullscreen/HDR queries, and SMU timeout detection through `IS_SMU_TIMEOUT()`.

## Control Flow
The header has no implementations. Display Core calls these declarations from link detection, MST allocation, HDCP, DMUB service, clock managers, panel code, and debug/test paths. The actual control flow is implemented in AMDGPU DM helper source files.

## State And Persistence
State lives in the provider layer and objects passed through `dc_context`, `dc_link`, `dc_stream_state`, `dc_sink`, payload structures, and DMUB command buffers. GPU memory helpers return CPU-visible pointers and physical addresses whose lifetime is controlled by matching free calls.

## Dependencies And Integration Points
Includes `dc_types.h` and `dc.h`, and forward-declares MST, AUX, and config status types. It bridges Display Core to DRM connector/EDID logic, AUX/I2C transactions, MST topology manager, DMUB firmware, ACPI/SBIOS, SMU timeout reporting, and policy state from the display manager.

## Risks
This is a high-blast-radius interface: wrong return values or lifetime handling can break detection, mode validation, MST payload allocation, DSC enablement, DMUB commands, and clock programming. Several helpers are synchronous and timeout-sensitive. GPU memory allocation must use correct type/alignment and be paired with free. Boolean failure often forces fallback behavior rather than hard errors, so missing diagnostics can mask integration bugs.

## Test Signals
Test via EDID read/parse, DPCD read/write, I2C/DDC, MST start/stop/allocation/ACT, DSC enable, DMUB command execution including timeout paths, GPU memory allocation/free under clock managers, panel setting override, periodic detection toggles, adaptive sync/HDR/fullscreen queries, and DP compliance test pattern handling.
