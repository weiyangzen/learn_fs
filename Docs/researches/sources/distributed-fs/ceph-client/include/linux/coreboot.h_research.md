## sources/distributed-fs/ceph-client/include/linux/coreboot.h

Purpose: This header defines coreboot table structures and helpers used by Linux drivers to consume firmware-provided coreboot metadata.

Important APIs, types, and functions: `cb_u64` is a 4-byte-aligned 64-bit type matching table layout. Tags include `CB_TAG_FRAMEBUFFER` and `LB_TAG_CBMEM_ENTRY`. Structures include `coreboot_table_entry`, `lb_cbmem_ref`, `lb_cbmem_entry`, and `lb_framebuffer`. Framebuffer orientation constants cover normal, bottom-up, left-up, and right-up. `LB_FRAMEBUFFER_HAS_LFB(fb)` and `LB_FRAMEBUFFER_HAS_ORIENTATION(fb)` use `offsetofend` to check whether a variable-sized framebuffer table is large enough to include fields.

Control flow: Consumers parse coreboot table entries by tag and size, then cast to the matching structure only after checking size for optional fields. Framebuffer consumers use the helper macros before reading linear framebuffer or orientation data.

State and persistence: The header maps firmware table bytes; it declares no mutable state. The persistent data is firmware-provided memory made available during boot/platform probing.

Dependencies and integration points: It depends on compiler alignment attributes, `stddef.h`, types, coreboot table scanning, framebuffer/simplefb setup, and platform drivers for CBMEM.

Risks and test signals: Risks include unaligned 64-bit access, reading optional fields when `size` is too small, tag mismatch, and endian/layout assumptions. Test signals include booting on coreboot hardware, fuzzing/truncating table entries, framebuffer orientation tests, and alignment-sensitive architecture builds.
