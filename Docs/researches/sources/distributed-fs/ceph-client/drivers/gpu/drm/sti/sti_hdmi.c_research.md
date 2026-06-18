# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.c

Purpose: Implements HDMI output as a DRM bridge/connector with HPD, EDID/DDC, infoframes, audio codec integration, CEC notifier updates, clock programming, PHY control, interrupts, and debugfs.

Important APIs/functions: `sti_hdmi_probe()` allocates the bridge, obtains DDC adapter, maps `hdmi-reg`, selects PHY ops from OF match data, gets `pix`, `tmds`, `phy`, and `audio` clocks, initializes HPD/waitqueue/IRQ/reset, and registers component ops. `sti_hdmi_bind()` finds the TMDS encoder, attaches the bridge, creates an HDMI-A connector with DDC, adds a colorspace property, registers `hdmi-codec`, initializes audio infoframe state, registers CEC notifier, and enables default interrupts. Bridge `mode_set`, `pre_enable`, and `disable` program rates, PHY, active area, interrupts, config bits, infoframes, audio, software reset, and teardown.

Control flow: IRQ top half reads/clears status and wakes the thread. Threaded IRQ updates HPD, emits DRM HPD events, wakes waiters for SW reset/PLL lock, and logs audio underruns. EDID modes are read through DRM EDID helpers and update CEC physical address. Audio callbacks configure N, channel-valid bits, infoframe, mute flat masks, and ELD access.

State/persistence: `struct sti_hdmi` stores current mode, register base, clocks, IRQ status, PHY ops, HPD/enabled flags, wait event, DDC adapter, colorspace, audio params, connector pointer, notifier, and bridge.

Dependencies/integration: Uses DRM bridge/connector/EDID/property helpers, Linux HDMI infoframe helpers, CEC notifier, sound `hdmi-codec`, local TX3G4C28 PHY ops, and VTG coordinate helpers.

Risks/test signals: Pre-enable sets `enabled = true` before PHY start failure and does not unwind clocks on failure. Infoframe register loops step by four but compare against word-count-like constants, so boundary review is important. Test HPD IRQ, EDID failure, color-space property updates, DVI vs HDMI config, audio channel counts/rates, CEC physical address invalidation, bridge disable cleanup, and debugfs infoframe dumps.
