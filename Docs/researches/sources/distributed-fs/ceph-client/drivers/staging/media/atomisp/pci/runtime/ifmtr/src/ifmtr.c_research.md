# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/ifmtr/src/ifmtr.c

Purpose: calculates and installs input formatter configuration for sensor/buffered sensor streams, handling crop, bayer-order correction, YUV/RGB/raw deinterleaving, two-PPC, and input-buffer layout.

Important functions/state: public bayer correction helpers and `ia_css_ifmtr_configure`; private `ifmtr_start_column`, `ifmtr_input_start_line`, and `ifmtr_set_if_blocking_mode`; global `ifmtr_set_if_blocking_mode_reset`.

Control flow: configuration derives cropped dimensions and input format from the binary or stream config, selects formatter index from MIPI port or memory mode, computes start line/column, left padding, vector counts, buffer widths, deinterleaving, offsets, and `input_formatter_cfg_t` for formatter A and optionally B. For real formatter configs it resets/programs blocking mode once and calls `sh_css_sp_set_if_configs`.

State/persistence: no per-stream heap state, but hardware/SP formatter config and the global reset guard persist beyond the call.

Dependencies/integration: uses ISP vector constants, input formatter hardware functions, stream/binary metadata, `sh_css_sp`, and input-buffer ISP definitions.

Risks: many format cases hand-tune vector math; unsupported or width-zero results return `-EINVAL`. Global blocking reset is noted as problematic when streams start sequentially. Two-PPC crop and left-padding math are high-risk for off-by-one Bayer/YUV alignment bugs.

Test signals: matrix of input formats, two-PPC on/off, copy vs normal binary, continuous vs offline, odd crop offsets, left padding `-1`, and verification of SP if-config contents.
