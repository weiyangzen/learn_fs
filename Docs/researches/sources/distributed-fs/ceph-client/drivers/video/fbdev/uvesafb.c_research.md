# sources/distributed-fs/ceph-client/drivers/video/fbdev/uvesafb.c

## Purpose
`uvesafb.c` is a framebuffer driver for VBE 2.0+ graphics adapters that can execute real-mode VBE BIOS services through the userspace `v86d` helper. Unlike `vesafb`, it discovers VBE modes at runtime, can read EDID/DDC data, can set VBE modes after boot, exposes VBE metadata through sysfs, and optionally uses the protected-mode interface on 32-bit x86 for palette and panning operations.

## Important APIs, Types, And Functions
The driver registers a platform driver/device named `uvesafb` and exposes `fb_ops` entries for open/release, colormap handling, panning, blanking, `fb_check_var`, and `fb_set_par`. The connector path is built around `struct uvesafb_ktask`, `struct uvesafb_task`, `uvesafb_exec()`, `uvesafb_cn_callback()`, and the global `uvfb_tasks[]` table protected by `uvfb_lock`. VBE discovery and mode work is handled by `uvesafb_vbe_getinfo()`, `uvesafb_vbe_getmodes()`, `uvesafb_vbe_getedid()`, `uvesafb_vbe_getmonspecs()`, `uvesafb_vbe_init_mode()`, and `uvesafb_set_par()`. Sysfs attributes expose VBE version, modes, OEM strings, `nocrtc`, and the driver-level `v86d` helper path.

## Control Flow
Module initialization parses boot/module options, installs the connector callback, registers the platform driver, creates the synthetic platform device, and adds the `v86d` driver attribute. Probe allocates `fb_info`, performs VBE info/mode/EDID/state-size discovery through `v86d`, chooses an initial mode, allocates a cmap, reserves VGA I/O and framebuffer memory, maps the LFB write-combining, registers the fbdev, and creates device attributes. A mode change validates a requested resolution/depth against cached VBE mode info, optionally builds a VBE 3.0 CRTC block, asks the helper to invoke function `0x4f02`, and falls back to BIOS-default timings if custom timings fail.

## State And Persistence
Persistent state is kernel-resident: module parameters, `v86d_path`, cached VBE blocks/mode arrays in `struct uvesafb_par`, monitor specs, selected mode index, MTRR/write-combine cookie, original VBE state buffers, and a refcount that controls save/restore around first open and last release. The driver also persists user-visible state through registered framebuffer state and sysfs attributes. It does not write disk state.

## Dependencies And Integration Points
It depends on Linux fbdev, connector/netlink, platform devices, `call_usermodehelper()`, `v86d`, VBE structures from `<video/uvesafb.h>`, EDID helpers, VGA I/O on x86, memory resource management, and architecture write-combine helpers. It integrates with fbcon/userspace through `/dev/fb*`, sysfs, and module/boot options such as `scroll`, `mtrr`, `nocrtc`, `noedid`, `vbemode`, and `v86d`.

## Risks
The helper protocol is security-sensitive: replies require `CAP_SYS_ADMIN` and ack/sequence validation, but correctness depends on trusted `v86d` behavior and bounded connector payloads. Hardware mode switches can fail or leave display state inconsistent; fallback to default timings helps but does not cover every BIOS quirk. PMI code is limited to non-NX 32-bit x86. Global `uvesafb_ops` is mutated to disable blanking/panning, which is safe for a single synthetic device but would be fragile for multiple instances. Memory sizing, VBE string offsets, and mode tables depend on BIOS-reported data.

## Test Signals
Useful signals are successful `uvesafb` probe logs, a registered framebuffer, populated `/sys/.../vbe_*` attributes, working `fbset` mode changes, palette tests in 8 bpp, panning tests when PMI is enabled, blank/unblank behavior, module unload cleanup, and negative tests where `v86d` is missing, EDID is unavailable, custom CRTC timings fail, or memory reservation/ioremap fails.
