<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c

Purpose: Gumstix AM200 EPD carrier support for a Metronome display controller attached to PXA25x GPIO and framebuffer memory.

Important APIs and functions: exposes `am200_init()` as the carrier hook called by `gumstix.c`. It registers a `metronomefb` platform device populated with `struct metronome_board`. Board callbacks include GPIO setup/cleanup, framebuffer setup, reset/standby controls, IRQ setup, wait functions, and panel type query. `panel_type` module parameter selects 6-inch, 8-inch, or 9.7-inch timing.

Control flow: `am200_init()` registers an FB notifier, configures PXA2xx MFP pins, requests the `metronomefb` module, allocates/adds the platform device, and calls `am200_presetup_fb()`. The notifier captures the host `pxafb` framebuffer when its adjusted geometry matches. Later `metronomefb` calls `am200_setup_fb()` to split the shared framebuffer into command, waveform, image, and checksum regions.

State and persistence: static `am200_board` stores host framebuffer pointers, waveform size, and panel dimensions; GPIO ownership and IRQ registration persist while the platform device exists. No nonvolatile storage.

Dependencies and integration: depends on Gumstix PXA25x board init, `pxa_set_fb_info()`, Linux framebuffer notifier chain, `metronomefb`, GPIO APIs, and PXA GPIO IRQ translation.

Risks and test signals: the notifier-based framebuffer sharing is marked FIXME and is fragile if another FB has matching geometry or if notifier ordering changes. Cleanup always frees RDY IRQ, so setup failure ordering matters. Test with panel sizes, FB registration/unregistration, RDY IRQ wakeups, and visible EPD update via `metronomefb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c -->
