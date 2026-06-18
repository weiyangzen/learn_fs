# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-ctrl.c

Purpose: `hda-ctrl.c` contains generic HDA controller reset, capability discovery, PP capability control, clock/power gating, chip initialization, and chip stop logic for SOF HDA platforms.

Important APIs: exported functions include `hda_dsp_ctrl_link_reset()`, `hda_dsp_ctrl_get_caps()`, `hda_dsp_ctrl_ppcap_enable()`, `hda_dsp_ctrl_ppcap_int_enable()`, `hda_dsp_ctrl_clock_power_gating()`, and `hda_dsp_ctrl_init_chip()`. `hda_dsp_ctrl_stop_chip()` is a common stop helper used by suspend/remove paths.

Control flow: reset writes `SOF_HDA_GCTL_RESET` and polls for entry or exit. Capability discovery performs a reset cycle, then walks the HDA linked-list capability pointer, recording PP, SPIB, DRSM, GTS, and multi-link capability BARs into `bus` and `sdev->bar[]`. Chip init enables codec wake, disables miscellaneous clock gating, clears wake/interrupt/stream status, resets the HDA controller, accepts unsolicited responses, optionally detects codecs, initializes command I/O, enables controller/global interrupts, programs the position buffer, resets multi-link LOSIDV state, and marks `bus->chip_init`. Stop disables stream and controller interrupts, clears status, stops command I/O, disables position buffer, and clears `chip_init`.

State and persistence behavior: persistent runtime state includes capability remap pointers, `bus->chip_init`, codec mask, position-buffer registers, command I/O state, and PCI gating bits. `hda->l1_disabled` affects whether DMI L1 state is re-enabled by clock/power gating.

Dependencies and integration: this file depends on HDA register helpers, codec helper functions, multi-link helpers, PCI update wrappers, and SOF stream lists. It imports HDA multi-link and codec namespaces.

Risks and test signals: reset and capability discovery order is hardware sensitive. Risks include failing to clear stale interrupts, programming position buffers while invalid, or enabling L1 against prior policy. Test signals are successful capability BAR discovery, stable codec detection after reset, no interrupt storms during init/stop, correct runtime suspend/resume chip_init transitions, and multi-link SoundWire/HDA link enumeration.
