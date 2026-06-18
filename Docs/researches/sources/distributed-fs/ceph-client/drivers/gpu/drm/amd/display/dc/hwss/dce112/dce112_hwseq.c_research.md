# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c

Purpose: DCE 11.2 hardware sequencer shim. It reuses the DCE110 sequencer almost entirely but overrides display power-gating to use DCE11.2 register offsets and PTE initialization behavior.

Important APIs, types, and functions: `dce112_hw_sequencer_construct()` is the only exported function. Private support includes `struct dce112_hw_seq_reg_offsets`, `reg_offsets[]`, `HW_REG_CRTC()`, `dce112_init_pte()`, and `dce112_enable_display_power_gating()`. The PTE helper reads and updates `mmDVMM_PTE_REQ` fields for maximum PTE requests and horizontal-flip request chunking. The power-gating helper maps `PIPE_GATING_CONTROL_*` to BIOS `ASIC_PIPE_*` actions, calls `dc_bios->funcs->enable_disp_power_gating()`, clears `CRTC_MASTER_UPDATE_MODE`, and reinitializes PTE settings when not enabling power gating.

Control flow: construction calls `dce110_hw_sequencer_construct(dc)` first, inheriting the base DCE110 `dc->hwss` and private hook tables. It then replaces `dc->hwseq->funcs.enable_display_power_gating` with the DCE112 version. Runtime callers therefore follow the DCE110 mode-set flow but land in DCE112-specific power-gating/PTE code whenever a pipe is initialized, ungated, or gated.

State and persistence: persistent state is hardware register state and BIOS-controlled pipe power state. The helper deliberately repairs `CRTC_MASTER_UPDATE_MODE` after BIOS command-table calls because BIOS sets it to a non-driver default. No software state is stored beyond the inherited `dc`/pipe/link state.

Dependencies and integration points: depends on DCE110 HWSS, `dc_bios` command tables, `dm_read_reg()`/`dm_write_reg()`, DCE11.2 register definitions, and the private HW sequencer function table. It is selected by the DCE11.2 resource path to provide generation-correct power gating while preserving base behavior.

Risks and test signals: the risk is register-offset mismatch or BIOS side effects during pipe gating. Broken PTE chunk programming may appear as scanout/f flip corruption. Test signals include DCE11.2 boot, mode set, suspend/resume, pipe power-gating transitions, and confirming `CRTC_MASTER_UPDATE_MODE` is restored after BIOS calls.
