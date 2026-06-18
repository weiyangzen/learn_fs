<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.cc -->
# sources/distributed-fs/eos/mgm/EosCtaReporter.cc

Purpose: Implements RAII-style EOS-to-CTA report generation. Reporter objects collect ordered key/value fields during an operation and emit one ampersand-separated record when the reporter is destroyed.

Important APIs/types/functions: `EosCtaParamMap` maps every `EosCtaReportParam` enum to the external log key string. Static `DEFAULT_PARAMS` vectors define the base fields and per-report extensions for prepare requests, WFE events, evict commands, file deletion, and file creation. `ioStatsWrite()` sends the generated record to `gOFS->mIoStats->WriteRecord()` when I/O statistics are available. `EosCtaReporter::generateEosReportEntry()` serializes `mParams` in `std::map` order using the enum ordering, and the constructors prepopulate default fields with empty strings.

Control flow: Construction sets the writer callback, inserts base defaults, then derived constructors insert report-specific defaults. Callers add values through header-defined `addParam()` overloads. Destruction in the base class triggers `generateEosReportEntry()` if the object is still active; the move constructor transfers parameters/callback and disables the moved-from instance. The generated string is built as `key=value&key=value...` and sent through the callback.

State and persistence behavior: State is per-object only: `mParams`, `mWriterCallback`, and `mActive`. There is no durable storage in this file; persistence is delegated to `Iostat::WriteRecord()` or to a caller-supplied callback such as PrepareManager's log bridge.

Dependencies and integration points: The implementation depends on `mgm/ofs/XrdMgmOfs.hh` for global `gOFS`, `mgm/iostat/Iostat.hh`, and `mgm/EosCtaReporter.hh`. WFE code creates WFE/file creation/deletion reporters, admin evict creates evict reporters, and bulk prepare manager uses `EosCtaReporterPrepareReq` with an explicit writer callback.

Risks: Values are not URL-escaped, so `&`, `=`, or newlines in paths/errors can corrupt downstream parsing unless producers sanitize them. `EosCtaParamMap.at()` throws if a new enum is added without a map entry. Destructor-triggered logging can throw through a destructor if the callback or map lookup fails, which is risky during stack unwinding. The static vectors are mutable globals rather than `const`. Test signals should include deterministic field ordering, moved reporter single-emission behavior, null `mIoStats`, callback capture behavior, and fields containing delimiter characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.cc -->
