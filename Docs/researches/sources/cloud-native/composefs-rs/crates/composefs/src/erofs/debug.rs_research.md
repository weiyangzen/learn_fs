# sources/cloud-native/composefs-rs/crates/composefs/src/erofs/debug.rs

Purpose: Provides debug formatting and whole-image inspection for composefs EROFS images, including structure dumps, path attribution, padding/unknown-region reporting, and space statistics.

Important APIs and types: Exposes `dump_unassigned` and `debug_img`. Implements `Debug` for format headers, reader inodes, xattrs, directory blocks, and data blocks. Internal `SegmentType` and `ImageVisitor` classify and traverse image regions.

Control flow: `debug_img` opens an `Image`, uses `ImageVisitor::visit_image` to walk from the root inode iteratively, then emits all visited segments in offset order. The visitor records header, superblock, inodes, shared xattrs, inline and external directory blocks, and data blocks, deduplicating by byte offset to handle hardlinks and cycles. Gaps between known segments are dumped as zero padding or unknown hexdump. At the end it prints per-segment and padding transition size percentages.

State and persistence: All state is in-memory: visited segment map, traversal stack, path lists, and statistics maps. Output is written to the supplied writer; input image bytes are not modified.

Dependencies and integration: Depends on EROFS `format` and `reader` modules, `zerocopy::FromBytes`, and `anyhow`. Fuzz target `debug_image.rs` continuously tests this entry point against arbitrary data.

Risks: Debug code traverses untrusted image structures, so bounds checks in reader APIs are critical. The visitor includes conflict detection for overlapping segments but still must avoid excessive traversal; iterative stack avoids call-stack overflow. Debug output is not a stable machine API unless explicitly treated as such.

Test signals: Direct tests are absent, but `debug_image` fuzzing targets panic resistance. The implementation also contains comments referencing a prior recursion depth problem that was addressed by iterative traversal.
