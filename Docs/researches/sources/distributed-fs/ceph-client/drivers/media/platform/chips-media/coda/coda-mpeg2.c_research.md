# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-mpeg2.c

`coda-mpeg2.c` provides MPEG-2 helpers for profile/level control reporting and initial-header detection. `coda_mpeg2_profile()` maps profile IDs 5, 4, 3, 2, and 1 to V4L2 simple, main, SNR scalable, spatially scalable, and high profile enums. `coda_mpeg2_level()` maps level IDs 10, 8, 6, and 4 to low, main, high-1440, and high. Unknown values return `-EINVAL`.

`coda_mpeg2_parse_headers()` is used by the decoder bitstream padding path when the first buffer is shorter than 512 bytes. It recognizes a sequence header at the beginning of the buffer and an extension header either at byte 12 for a 22-byte compact form or at byte 76 for an 86-byte form with quantization matrix data, optionally followed by another start-code prefix.

The file is stateless and depends only on V4L2 MPEG-2 enums and CODA prototypes. It integrates with `coda-bit.c` padding and `coda-common.c` read-only profile/level control updates. The main risk is that it is a fixed-pattern recognizer, not a full MPEG-2 parser, so unusual valid streams may not be padded for sequence init. Test all mappings, both header lengths, start-code-prefix variants, rejection paths, and decoder startup with short first buffers.
