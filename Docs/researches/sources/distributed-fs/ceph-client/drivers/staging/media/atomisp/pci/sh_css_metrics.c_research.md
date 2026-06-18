# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.c

Purpose: `sh_css_metrics.c` implements lightweight frame and program-counter metrics for CSS binaries. It can count processed frames and, when enabled, build ISP/SP PC histograms of run versus stall samples for the active binary.

Important APIs/types/functions: exported global `sh_css_metrics` holds the binary metrics list and frame counters. `sh_css_metrics_start_frame()` increments frame count. `sh_css_metrics_enable_pc_histogram()` toggles sampling. `sh_css_metrics_start_binary()` selects the current binary histograms, allocates arrays sized by `ISP_PMEM_DEPTH` and `SP_PMEM_DEPTH`, and links the binary metrics into the global list. `sh_css_metrics_sample_pcs()` reads ISP PC and sink registers and updates histogram buckets. Helpers `clear_histogram()`, `make_histogram()`, and `insert_binary_metrics()` manage arrays and list insertion.

Control flow and state: the file maintains static `pc_histogram_enabled`, `isp_histogram`, and `sp_histogram`. Sampling is a no-op unless enabled. Starting a binary sets the active histogram pointers and lazily allocates bucket arrays. ISP sampling updates `msink[pc]` by bitwise-and, classifies stalls when sink is not `0x7FF`, and increments `stall` or `run`. SP sampling code is compiled but disabled by `&& 0`.

Dependencies and integration: it uses SP/ISP control register accessors and internal CSS metrics structures from `sh_css_metrics.h`. Higher-level code can call start-frame/start-binary/sample around pipeline execution to collect diagnostics.

Risks: `make_histogram()` can partially allocate `run` or `stall` then fail on a later array, leaving non-null partial state with `length == 0`; later calls return early if `run` is set, so allocation failure handling is weak. `insert_binary_metrics()` asserts `*l`, yet callers pass `&sh_css_metrics.binary_metrics`, which can be NULL initially; depending on assert behavior this may be wrong. PC values read from hardware are used as array indices without bounds checks. Histogram arrays are never freed in this file.

Test signals: diagnostic tests should enable/disable histograms, start first and repeated binaries, simulate allocation failures, and sample boundary PC values. Static/dynamic analysis should check list insertion with an initially empty list and out-of-range PC reads. Runtime debug output should show frame counts and nonzero run/stall buckets when sampling is active.
