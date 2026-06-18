<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resstats.cc

Purpose: implements counters, histograms, and printing for file/directory resolution and recoverable log statistics.

Important APIs/control flow: constructors zero counter structs or initialize log sizes. `logshiphisto::add/update/print` tracks shipped log byte sizes and max entries. `conflictstats::update`, `logsize::chgsize/report/print`, `varlhisto::countalloc/countdealloc/print`, and `logstats::print` maintain log behavior metrics. `resstats::precollect/postcollect/update/print` aggregates per-volume file and directory stats. `FindResStats` searches the global `ResStatsList`.

State/persistence: `ResStatsList` is a global in-memory list. Individual `resstats` objects are attached to volume logs (`vmrstats`) and updated during resolution/log operations; they are not independently persisted here.

Dependencies/integration: included by log spooling/truncation, file resolution, directory resolution, and volume-log recovery. Uses fd-based `write` output.

Risks/test signals: `logsize` constructor does not zero buckets; callers relying on clean histograms need object memory zeroed or constructor extended. `varlhisto::countdealloc` increments free count but not bucket decrements. Test printed stats after file resolve success/conflict, directory resolve, log allocation/free, admin growth, and periodic pre/post collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resstats.cc -->
