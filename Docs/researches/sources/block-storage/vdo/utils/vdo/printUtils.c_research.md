# File Research: sources/block-storage/vdo/utils/vdo/printUtils.c

Formats sizes for display.

Key details:
- Defines binary KB/MB/GB/TB/PB constants.
- `getSizeString()` either formats the raw numeric size or delegates to human-readable formatting.
- `setReadablePrintString()` emits two-decimal suffix strings for P/T/G/M/K/B ranges.

Risk notes:
- Raw output uses `sprintf(printString, "%ld", size)` for `u64`, which is type-sensitive and not fully portable.
- Uses strict greater-than thresholds, so exactly `1 MB` is formatted as `1024.00K`, not `1.00M`.
