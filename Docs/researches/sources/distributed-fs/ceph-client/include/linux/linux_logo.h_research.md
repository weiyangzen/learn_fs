# sources/distributed-fs/ceph-client/include/linux/linux_logo.h

Purpose: declares the boot/framebuffer Linux logo data interface.

Important APIs and types: logo type constants identify mono, VGA16, CLUT224, and grayscale formats. `struct linux_logo` stores type, dimensions, CLUT size/pointer, and pixel data pointer. Externs name built-in logo assets, `fb_find_logo()` selects a logo by display depth, and optional `fb_append_extra_logo()` appends extra logos when configured.

Control flow: framebuffer console code selects a logo for the active depth and may append vendor/extra logos during boot display setup.

State and persistence: logo data is static const image data. Extra-logo registration affects in-memory boot display lists only.

Dependencies and integration points: depends on init annotations and framebuffer logo build options; integrates logo assets with fbdev boot rendering.

Risks and test signals: risks include missing externs for disabled assets, mismatched CLUT/data sizes, and extra-logo config stubs. Test boot logos at supported depths, config with/without extra logos, and asset linkage.
