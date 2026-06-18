# sources/distributed-fs/ceph-client/drivers/firmware/google/framebuffer-coreboot.c

Purpose: Converts a coreboot framebuffer table entry into a platform framebuffer device when Linux did not already receive usable `screen_info`.

Important APIs/types/functions: `framebuffer_parent_pci_dev()` tries to identify an enabled display PCI device owning the framebuffer resource. `framebuffer_probe()` validates the `lb_framebuffer`, builds a memory resource, chooses either `coreboot-framebuffer` platform data for DRM corebootdrm or legacy `simple-framebuffer` data, and registers the platform device.

Control flow: The driver binds to `CB_TAG_FRAMEBUFFER`. Probe first exits if sysfb already handles screen info, then rejects empty or invalid physical addresses. It sizes the resource from `y_resolution * bytes_per_line`, finds an optional PCI parent, and registers the platform device with the framebuffer table payload or simplefb-compatible geometry.

State and persistence behavior: The driver creates a child platform device and holds a temporary PCI device reference while registering. It does not own the framebuffer memory contents.

Dependencies and integration points: Integrates the coreboot bus, PCI, sysfb, platform devices, simplefb format tables, and optionally DRM corebootdrm. Downstream display drivers consume the registered platform device.

Risks and test signals: Geometry and format matching must be exact for simplefb fallback. Resource overflow or invalid firmware dimensions could produce bad reservations. Test on coreboot systems with and without `screen_info`, with DRM corebootdrm enabled and disabled, and verify parent PCI reference release.
