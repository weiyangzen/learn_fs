# File Research: sources/block-storage/util-linux/sys-utils/readprofile.c

This file implements `readprofile(8)`, a legacy reader for Linux kernel profiling data from `/proc/profile` correlated with `System.map`. It can display sampling step info, reset counters, set the profiling multiplier, print all symbols, print individual histogram bins, print per-function counters, and handle compressed `.gz` map files through a forked `zcat`.

The program reads the whole profile buffer as unsigned integers, optionally detects reversed byte order using a heuristic over high/low half-word usage, and treats `buf[0]` as the sampling step. It opens the requested map file or falls back from `/boot/System.map` to `/boot/System.map-$(uname -r)`.

Main processing finds `_stext`/`__stext`, then walks text symbols until `_etext`/`__etext`, accumulating profile bins whose addresses fall inside each function. It prints either per-bin counts or per-symbol totals and normalized counts per byte, then emits the final unknown bucket and total. Reset and multiplier writes use `/proc/profile` with root attempt via `setuid(0)`.
