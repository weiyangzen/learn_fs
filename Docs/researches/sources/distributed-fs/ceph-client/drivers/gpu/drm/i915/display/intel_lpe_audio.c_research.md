# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.c

Purpose: implements the i915 bridge to the standalone HDMI/DP LPE audio platform driver on Atom-class platforms that lack the traditional HD-audio controller.

Important APIs/types/functions: `intel_lpe_audio_init()` detects and sets up the bridge, `intel_lpe_audio_teardown()` unregisters it, `intel_lpe_audio_irq_handler()` forwards display audio IRQs through a Linux IRQ descriptor, and `intel_lpe_audio_notify()` updates per-port ELD/link-clock/DP state and notifies the audio driver. Internal helpers create/destroy the `hdmi-lpe-audio` platform device, allocate IRQ descriptors, install an IRQ chip, and detect VLV/CHV systems without Atom HDAudio PCI devices.

Control flow: init detects Valleyview/Cherryview without matching HD-audio PCI IDs. Setup allocates a synthetic IRQ descriptor, installs a simple IRQ handler chip, creates a child platform device with IRQ and MMIO resources plus `intel_hdmi_lpe_audio_pdata`, marks it runtime-PM callback-free, and enables a VLV audio chicken bit. Display IRQ handling calls `generic_handle_irq()` for the allocated IRQ. Audio notify locks pdata, copies or clears ELD, pipe, link symbol clock, and DP-output flags for the port, unmutes or mutes the amplifier register, calls the platform driver's notification callback if present, and unlocks.

State and persistence behavior: runtime state lives in `display->audio.lpe.irq`, `display->audio.lpe.platdev`, platform device resources, and platform data copied at device registration. Per-port audio state is in platform data and protected by `lpe_audio_slock`. No durable persistence exists.

Dependencies and integration points: integrates i915 display audio register programming with the ALSA `hdmi-lpe-audio` platform driver, Linux platform device model, IRQ core, PCI resource BARs, runtime PM parentage, and Intel audio register definitions.

Risks: file documentation calls out platform-device lifetime risk if the audio module remains installed while i915 unregisters the child. `platform_device_register_full()` leaks its allocated DMA mask by platform core behavior, acknowledged in teardown. IRQ descriptor allocation and platform device registration must unwind correctly. Port indexing assumes ports B/C(/D) map to zero-based platform data entries. Notify must serialize register and pdata updates.

Test signals: VLV/CHV systems with and without HDAudio PCI device, platform device probe by ALSA driver, forwarded IRQ delivery, ELD updates on HDMI/DP plug/unplug, amp mute/unmute register writes, teardown with audio driver loaded/unloaded, and error paths for IRQ/platform allocation.
