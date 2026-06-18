# File Research: sources/block-storage/lvm2/lib/format_text/text_import.h

## Summary
Small import header exposing the shared segment-area parser.

## API Surface
Declares `text_import_areas(struct lv_segment *seg, const struct dm_config_node *sn, const struct dm_config_value *cv, uint64_t status)`, used by segment-type import handlers to parse area arrays from text metadata.

## Risks And Invariants
The function expects the segment’s area count to be established before import and consumes config values as name/offset pairs.
