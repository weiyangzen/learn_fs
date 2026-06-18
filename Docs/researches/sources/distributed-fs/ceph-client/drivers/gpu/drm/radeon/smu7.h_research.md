<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7.h

## Purpose
`smu7.h` defines shared packed SMU7 firmware ABI primitives for Radeon CI/KV-era power management. It provides common limits, DPM state constants, scratch-register bit layouts, the PID-controller structure, feature/handshake masks, the SMU7 firmware header layout, and display PHY configuration IDs used by the discrete and fusion SMU7 table headers.

## Important APIs, types, and definitions
- Context IDs: `SMU7_CONTEXT_ID_SMC` and `SMU7_CONTEXT_ID_VBIOS`.
- DPM table capacities: maximum VDDC, VDDCI, MVDD, VDDNB, graphics, memory, GIO, PCIe link, UVD, VCE, ACP, SAMU, and SMIO entries.
- DPM action constants: `DPM_NO_LIMIT`, `DPM_NO_UP`, `DPM_GO_DOWN`, `DPM_GO_UP`, and first-level constants for graphics/memory.
- Scratch B bitfields track target/current PCIe, UVD, VCE, ACP, and SAMU indices.
- `SMU7_PIDController` defines firmware PID control parameters for activity-based DPM loops.
- Feature masks indicate which DPM domains and controllers are configured; handshake masks disable MCLK/SCLK handshakes for ACP, UVD, and VCE.
- `SMU7_Firmware_Header` records digest, version, code sizes, entry point, and SRAM offsets for soft registers, DPM table, fan table, CAC tables, MC tables, fuse table, globals, and signature.
- `enum DisplayConfig` enumerates display PHY modes such as power-down, DisplayPort lane/rate combinations, HDMI, and LVDS.

## Control flow and integration points
The header contains no functions. `smu7_discrete.h` and `smu7_fusion.h` include it to share constants and structures. CI and KV DPM code uses these definitions when loading SMU firmware, locating firmware tables, populating DPM table domains, and interpreting scratch-register state.

## State and persistence behavior
The definitions describe state persisted in SMU firmware memory and scratch registers. The CPU writes firmware headers, tables, PID parameters, feature masks, and enabled-level masks into SMU-visible memory; firmware uses them to control clocks, voltage rails, PCIe links, and media blocks until reset or table reload.

## Dependencies and constraints
The file relies on SMU enum constants such as `SMU__NUM_SCLK_DPM_STATE`, `SMU__NUM_MCLK_DPM_LEVELS`, `SMU__NUM_LCLK_DPM_LEVELS`, and `SMU__NUM_PCIE_DPM_LEVELS` being defined by the including context. The duplicate context-ID defines are harmless but should not diverge. Packed layout is required for firmware ABI compatibility.

## Risks and test signals
Incorrect capacities, firmware-header offsets, or scratch bit masks can make table uploads corrupt adjacent firmware memory or misreport active DPM states. Test signals include CI/KV SMU firmware load, DPM table upload/readback, enabled-level masks matching expected domains, media block clock changes, PCIe level transitions, and suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/smu7.h -->
