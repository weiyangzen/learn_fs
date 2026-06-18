# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_ppsmc.h

## Purpose
`smu7_ppsmc.h` defines the SMU7 powerplay SMC mailbox command and event ID namespace. It is the command contract used by the host driver to ask SMU firmware to initialize, upload tables, enable/disable features, adjust DPM and fan policy, query telemetry, and access secure register operations.

## Important APIs, Types, And Constants
- Defines response/status values such as success/failure/unknown-command style mailbox responses.
- The core `PPSMC_MSG_*` range includes initialization, DPM table loading, fan control, voltage and clock DPM enable/disable, UVD/VCE/ACP/SAMU/PCIe DPM controls, thermal controls, power limits, CAC/telemetry queries, and overdrive/fan target controls.
- Later ranges include BACO, VddGfx, microcode/VBIOS loading, DRAM address handoff, DMCU PSR, clock-gating, metadata, telemetry calibration, AVFS, AGM/PSM/VFT, CU power gating, DIDT/EDC/FFC/zero RPM, secure SRBM read/write, and generic address/data access.
- `typedef uint16_t PPSMC_Msg` establishes command ID width.
- Event status masks include thermal, regulator-hot, and DC events.

## Control Flow And Data Flow
Host control flow writes a `PPSMC_Msg` plus any argument to the SMC mailbox registers, waits for a response, and interprets firmware status. Data paths frequently require setup through table-memory addresses or prior soft-register writes before issuing commands such as table load, DPM enable, AVFS enable, or telemetry query.

## State And Persistence
The header stores no state. The message IDs mutate firmware runtime state when sent: enabling controllers, changing fan limits, loading tables, toggling AVFS/clock gating, updating power limits, or reading status. Persistence is firmware/session scoped unless command effects are backed by board policy elsewhere.

## Dependencies And Integration Points
- Used by all SMU7-family discrete/fusion implementation files that send SMC messages.
- Integrates with the table layouts in `smu7*.h`, `smu7*_discrete.h`, and later SMU72-SMU75 headers.
- Secure SRBM and address/data messages bridge powerplay with protected register access.

## Risks
- Command IDs are firmware ABI. Reusing an ID for a different semantic breaks every firmware version expecting the old command.
- Some commands are only valid on specific ASIC/firmware generations; callers must gate by firmware capability.
- Address high/low handoff commands must match DMA address width and ordering.
- Misspelled names such as calibration variants should not be "fixed" without checking external users and firmware symbols.

## Test Signals
- Build-time references should resolve to the intended IDs.
- Runtime mailbox tests: command accepted response, table load succeeds, telemetry commands return sane values, unsupported commands are handled gracefully, and feature toggles produce expected firmware state.
