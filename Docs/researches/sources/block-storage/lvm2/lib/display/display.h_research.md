# File Research: sources/block-storage/lvm2/lib/display/display.h

This header declares display and conversion helpers implemented by `display.c`. It includes metadata exports and LVM string helpers, then exposes functions for LV names, percentages, sector/MiB size formatting, and stripe area display.

The object display API covers PV, LV, and VG output variants: full, short, colon, and segment-oriented forms. It also declares simple enumerators for formats, segment types, and tags.

Conversion declarations include allocation policy string/char mapping, lock type string mapping, and percent-type string mapping. `display_name_error` is the central name validation diagnostic emitter, and `yes_no_prompt` is declared with a printf-format attribute for compile-time format checking.
