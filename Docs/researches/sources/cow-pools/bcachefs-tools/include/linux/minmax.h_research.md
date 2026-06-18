# File Research: sources/cow-pools/bcachefs-tools/include/linux/minmax.h

This header implements kernel min/max/clamp helpers with single-evaluation behavior and signedness-aware comparisons. It defines `min`, `max`, `umin`, `umax`, `min3`, `max3`, `min_t`, `max_t`, `min_not_zero`, `clamp`, `clamp_t`, and `clamp_val`.

It also provides array min/max helpers, range checks (`in_range32`, `in_range64`, `in_range`), `swap()`, and unsafe uppercase `MIN/MAX` macros for obvious constants. The comments explain the signed/unsigned rules and constant non-negative exceptions that avoid surprising comparison bugs.
