# File Research: sources/block-storage/kvdo/vdo/time-utils.c

This file implements `current_time_us()`, returning realtime wall-clock microseconds by calling `current_time_ns(CLOCK_REALTIME)` and dividing by `NSEC_PER_USEC`.

The file includes assertion/string/time headers and kernel delay/time headers, but the only runtime behavior is the wall-clock microsecond helper.
