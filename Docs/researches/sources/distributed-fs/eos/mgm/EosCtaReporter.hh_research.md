<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.hh -->
# sources/distributed-fs/eos/mgm/EosCtaReporter.hh

Purpose: Defines the public reporting API used by MGM CTA workflows to emit structured audit/report records for prepare, WFE, evict, file deletion, and file creation events.

Important APIs/types/functions: `EosCtaReportParam` is the authoritative enum of supported report fields; comments state that parameter order follows enum order and that `SEC_APP` should remain last by convention. `EosCtaReporter` is the protected base class with chainable `addParam()` overloads for numeric/string/bool/C-string values. Derived reporter types are `EosCtaReporterPrepareReq`, `EosCtaReporterPrepareWfe`, `EosCtaReporterEvict`, `EosCtaReporterFileDeletion`, and `EosCtaReporterFileCreation`.

Control flow: Users instantiate a concrete reporter, call `addParam()` as the operation progresses, and rely on the virtual destructor to emit the record. Copying and assignment are disabled; moving is allowed only through the protected move constructor so containers can transfer reporters without double-emitting. Derived constructors are responsible for adding their default parameter sets.

State and persistence behavior: The report is accumulated in `std::map<EosCtaReportParam, std::string> mParams`, which gives stable enum-ordered serialization. The writer callback abstracts persistence, defaulting to the implementation's I/O-stat writer. The object lifecycle itself is the transaction boundary: destruction means "finalize and write".

Dependencies and integration points: This header depends only on standard containers/callbacks and `mgm/Namespace.hh`, so CTA-aware managers can include it cheaply. It is integrated by `bulk-request/prepare/manager`, WFE archive workflows, and admin evict command code.

Risks: Destructor side effects make reporting easy to forget in tests and hard to suppress on exceptional paths. `std::to_string()` in the templated overload excludes types that need custom formatting and can surprise for char-like values. No API validates that required fields were filled before emission. Since ordering and external key names are split between this header and the `.cc` map, enum additions require coordinated updates. Good tests should assert per-derived default coverage, bool formatting, move semantics in STL containers, and behavior when a caller omits fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.hh -->
