# sources/distributed-fs/ceph-client/tools/mm/slabinfo-gnuplot.sh

Purpose: Converts repeated `slabinfo -X` samples into gnuplot-friendly intermediate files and PNG graphs for slab totals, loss, and size trends.

Important APIs and functions: `do_preprocess` extracts top slab-by-loss, slab-by-size, and total memory/loss series. `do_slabs_plotting` plots stacked size/loss bars for one preprocessed slab file. `do_totals_plotting` overlays memory usage/loss time series for one or more totals files. `parse_opts` selects preprocess, totals, or slabs mode and image/range options.

Control flow: Options set mode, size, and sample range. Preprocess mode loops over raw slabinfo samples and creates `basename-slabs-by-loss`, `basename-slabs-by-size`, and `basename-totals`, then plots each. Plot modes consume already-preprocessed files directly.

State and persistence behavior: Writes intermediate text files and PNGs in the current directory. It does not modify source sample files.

Dependencies and integration points: Expects output format from `slabinfo -X`; relies on bash arrays, grep, awk, wc, basename, and `gnuplot`.

Risks: Parsing is tightly coupled to headings and column positions. Backtick command substitutions around pipelines are unnecessary and may obscure errors. Output filenames are derived from basenames and can collide. Optional getopts declarations use `r::`/`s::`, so missing argument handling is shell/getopts-dependent.

Test signals: Use fixture `slabinfo -X` samples with multiple records, range and size options, totals comparison, empty files, and absent gnuplot.
