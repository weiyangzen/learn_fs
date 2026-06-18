# sources/distributed-fs/coda/coda-src/util/histo.c

## Purpose
Implements numeric histograms with linear, log2, or log10 bucket layouts, summary statistics, and plotting text output.

## Important APIs, Types, And Functions
`InitHisto()` allocates and initializes buckets. `ClearHisto()` resets counts and sums. `UpdateHisto()` and `MUpdateHisto()` add samples. `PrintHisto()` prints mean/stddev/90% confidence interval and populated buckets. `PlotHisto()` emits a graph description with histogram points.

## Control Flow
Initialization validates limits and log constraints, derives bucket boundaries, allocates `histo` buckets, and calls `ClearHisto()`. Updates route values to underflow, overflow, or first bucket with `newval < hival`, updating count/sum/sum2 for in-range samples. Printing derives statistics from accumulated sums and emits textual ranges.

## State And Persistence
State is heap-allocated bucket arrays and counters in caller-owned `hgram`. There is no free function in this file, so callers must manage `hg->buckets` lifetime.

## Dependencies And Integration Points
Depends on `math.h`, `stdio`, `stdlib`, `coda_assert`, and `histo.h`. Used for performance or behavior distributions in diagnostics.

## Risks
`PlotHisto()` divides by `totalcount` without guarding zero populated buckets. Confidence factors index a static table for low degrees of freedom. Linear initialization does not reject nonpositive `bucketcount`. Updates use linear bucket search.

## Test Signals
Initialize valid/invalid linear/log histograms, add underflow/overflow/in-range samples, clear and reuse, print one and many samples, plot empty/nonempty histograms, and check bucket boundary inclusivity.
