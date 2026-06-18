# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_dvo.c

Purpose: Implements the DVO/LVDS bridge and connector side of the STI display pipeline. It attaches to the LVDS encoder created by TVOUT, configures DVO clocks, AWG sync generation, LUT byte routing, and optional panel modes.

Important APIs/functions: `sti_dvo_probe()` allocates a DRM bridge, maps `dvo-reg`, gets `dvo_pix`, `dvo`, and optional parent clocks, parses `sti,panel`, and registers component ops. `sti_dvo_bind()` finds the LVDS encoder, adds/attaches the bridge, creates an LVDS connector, and attaches it to the encoder. `sti_dvo_set_mode()` copies the mode, selects main/aux parent clocks from the encoder CRTC mixer, sets clock rates, and selects `rgb_24bit_de_cfg`. `sti_dvo_pre_enable()` generates AWG code, enables clocks/panel, writes LUT routing, and enables the formatter; disable reverses this.

Control flow: The bridge mode-set chooses clock parents/rates before pre-enable writes hardware. Connector detect lazily resolves the DRM panel and reports connected only when found. Mode validation checks rounded pixel-clock tolerance.

State/persistence: `struct sti_dvo` persists current mode, clocks, panel reference, selected config, bridge, encoder pointer, and enabled flag. Debugfs exposes DVO registers and AWG microcode.

Dependencies/integration: Uses DRM bridge/connector/panel helpers, STI AWG utilities, TVOUT-created LVDS encoder, mixer identity for main/aux clock parent selection, and OF panel lookup.

Risks/test signals: `panel_node` is put immediately after parsing yet reused later, which is lifetime-sensitive. Clock enable errors are logged but do not abort pre-enable. Test panel detect, mode validation tolerance, bridge enable/disable, AWG generation failure, main/aux path clock-parent selection, and debugfs microcode dump.
