# File Research: sources/block-storage/libblkid-rs/src/tag.rs

Purpose: Implements tag iteration for devices and parsing of tag strings.

Key APIs:
- `BlkidTagIter`
- `parse_tag_string`

Implementation notes:
- `BlkidTagIter` owns the C iterator and ends it in `Drop`.
- Iterator items are `(String, String)` pairs.
- `parse_tag_string` calls libblkid to split a tag string into type and value.

Notable risks:
- `parse_tag_string` does not free `type_` and `value` returned through output pointers, which likely leaks libblkid-allocated strings.
- Iterator UTF-8 conversion failures are converted to `None`, making invalid data indistinguishable from end-of-iteration.
- `Iterator::next` asserts non-null pointers after a nonnegative return.
