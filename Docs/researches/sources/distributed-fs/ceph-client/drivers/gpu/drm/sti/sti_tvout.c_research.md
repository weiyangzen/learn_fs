# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_tvout.c

Purpose: Implements the shared TVOUT glue block and creates the HDMI, HDA, and DVO encoders used by the output bridge drivers. It routes main/aux mixer output to VIP blocks, configures CSC matrices, sync sources, clipping/rounding/channel order, HD DAC power, and debugfs.

Important APIs/functions: `sti_tvout_probe()` maps `tvout-reg`, deasserts reset, and registers component ops. `sti_tvout_bind()` creates HDMI TMDS, HDA DAC, and DVO LVDS encoders with common encoder funcs and type-specific helper funcs. `tvout_preformatter_set_matrix()` writes BT.709 or BT.601 RGB-to-YCbCr matrices by mode height. `tvout_hdmi_start()`, `tvout_hda_start()`, and `tvout_dvo_start()` select sync source and VIP input for main/aux path, set color order, clipping, rounding, input format, and output-specific selection. Encoder enable helpers call those start functions; disable helpers clear VIP state and DAC power.

Control flow: TVOUT creates encoders first; separate bridge/component drivers later find encoders by type and attach connectors/bridges. Encoder helper enable is path-sensitive via `sti_crtc_is_main()`.

State/persistence: `struct sti_tvout` stores DRM device, register base, reset, encoder pointers, and debugfs registration flag. `struct sti_tvout_encoder` embeds each DRM encoder and back-pointer.

Dependencies/integration: Uses component framework, DRM encoder helpers, reset API, CRTC path selection, VTG sync ids, and output-specific bridge drivers. It is the glue between compositor mixer paths and physical outputs.

Risks/test signals: `sti_tvout_create_encoders()` assumes all three encoder allocations succeed before setting clone masks. HDA helper uses `.commit` while HDMI/DVO use `.enable`, reflecting older helper semantics. Test encoder creation failure handling, clone masks, main/aux routing for each output, VIP debugfs, CSC matrix choice at 720-line boundary, and DAC power-off on disable.
