# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/luks.c

LUKS crypto-volume detector. It reads the primary header at offset zero, validates LUKS magic, and for LUKS2 also requires the header’s recorded offset to match the actual location. It emits magic, version, UUID, and for LUKS2 label plus `SUBSYSTEM`.

If no primary header is found and the probe is not in safeprobe mode, it scans known LUKS2 secondary header offsets using the reversed secondary magic. A separate OPAL probe detects LUKS2 headers whose subsystem is `HW-OPAL` only when the underlying drive reports itself locked through OPAL status; this allows reporting locked hardware-encrypted LUKS2 volumes despite later I/O errors.

The file deliberately does not verify LUKS2 header checksums or parse JSON metadata; it is focused on stable header identity and recovery-header discovery.
