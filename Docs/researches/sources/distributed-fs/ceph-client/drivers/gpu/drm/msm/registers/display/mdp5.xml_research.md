# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp5.xml

## Purpose
This XML file is a Freedreno/Nouveau RNN register database for Qualcomm MDP5 display hardware. It imports shared display definitions from `display/mdp_common.xml` and copyright metadata, then describes the `MDP5` 32-bit register domain plus an empty `VBIF` placeholder. Its output is consumed by `gen_header.py` and related register-generation tooling to produce C register offsets, bit masks, enum values, and pack helpers used by the MSM DRM display driver.

## Important APIs, Types, And Data
The file defines display-facing enums such as `mdp5_intf_type`, `mdp5_intfnum`, `mdp5_pipe`, `mdp5_ctl_mode`, scale filters, cursor formats, writeback modes, and color/rotation enums. `MDP5_IRQ` models interrupt bits for writeback, ping-pong completion/read/write/auto-refresh, underrun, and vsync. Register arrays model hardware blocks: global `SMP_ALLOC_*`, `IGC`, `CTL`, `PIPE`, `LM`, `DSPP`, `PP`, `WB`, `INTF`, and `AD`. Several arrays use `doffsets` expressions such as `mdp5_cfg->pipe_vig.base[0]`, so generated accessors depend on runtime MDP5 configuration tables rather than hard-coded offsets alone.

## Control Flow, State, And Integration
There is no executable flow in the XML itself. The effective flow is parser-driven: imports are resolved, enums and bitsets are registered, then arrays/regs become generated `REG_MDP5_*` accessors and field macros. State represented here is volatile hardware state: scanout source addresses, layer mixer composition, control flush bits, timing generator settings, color-space conversion coefficients, cursor configuration, writeback destination addresses, SMP allocation, and interrupt status/enable/clear. Integration points are the MSM DRM MDP5 KMS path and generated headers expected by code that programs MDP5 blocks.

## Risks And Test Signals
The largest risks are incorrect offsets/bit positions and stale hardware assumptions. Comments mark uncertain areas, including IGC disable bits, CTL layer extension compatibility, `mdp5_format` as a TODO, and a `VBIF` placement question. Dynamic offsets must stay in sync with `mdp5_cfg` structures. Test signals are successful header generation, schema validation, successful MSM display modesets, no underrun/vsync IRQ regressions, cursor/writeback tests, and register traces matching downstream or hardware documentation.
