# File Research: sources/block-storage/kvdo/vdo/super-block-codec.h

This header defines `struct super_block_codec`, which owns the component-data buffer, sector-scoped block buffer, and full-block encoded super-block memory. The block buffer wraps the first sector of the encoded block, matching the codec's torn-write avoidance design.

It declares initialization/destruction plus encode/decode functions. Callers fill or consume `component_buffer`; the codec handles the enclosing super-block header and checksum.
