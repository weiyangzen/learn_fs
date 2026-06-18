# sources/cloud-native/containers-storage/pkg/system/meminfo_solaris.go

Purpose: implements Solaris memory and swap statistics retrieval through cgo.

Important APIs, types, and functions: C helpers for swap table allocation and kernel page lookup, `getTotalMem`, `getFreeMem`, `ReadMemInfo`, and `getSysSwap`.

Control flow: total/free memory come from `sysconf`. Kernel pages are read through kstat and subtracted from total. Swap stats use `swapctl` to count/list entries, iterate entries, accumulate total/free disk blocks, and free allocated C memory.

State and persistence: reads OS kernel and swap state; no mutation.

Dependencies and integration points: depends on cgo, `fmt`, and `unsafe`; links `kstat`. Selected on `solaris && cgo`.

Risks and edge cases: C helper error paths in `getPpKernel` can leak kstat handles. `getSysSwap` returns block counts scaled by disk blocks per page, which should be reviewed for byte-unit consistency against `MemInfo`.

Test signals: no Solaris tests in requested files.
