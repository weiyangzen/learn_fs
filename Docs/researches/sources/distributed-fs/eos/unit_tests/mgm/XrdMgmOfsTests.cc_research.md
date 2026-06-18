# sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsTests.cc

Purpose: validates `eos::mgm::XrdMgmOfs::prepareOptsToString()` against XRootD prepare option bitmasks. The test is deliberately narrow and acts as a compatibility guard for string rendering used in logging, diagnostics, and prepare workflows.

Important APIs and types: `XrdMgmOfs`, XRootD `Prep_*` constants from `XrdSfs`, `XrdVersion.hh` version macros, and GoogleTest fixture `XrdMgmOfsTest`. Conditional coverage includes `Prep_CANCEL`, `Prep_QUERY`, and `Prep_EVICT` only when compiled with XRootD 4.10+ or 5+.

Control flow: the single `prepareOptsToString` test constructs one option mask at a time and asserts the exact comma-separated output. Priority-only flags render as `PRTY0` through `PRTY3`; non-priority flags implicitly include `PRTY0`.

State and persistence: no persistent state. The fixture has empty setup/teardown; all inputs are constants.

Dependencies and integration: this is a low-level MGM OFS compatibility test tied to XRootD option definitions. Failures signal drift between MGM stringification and XRootD prepare semantics.

Risks and test signals: the exact-string assertions are intentionally brittle. Adding or reordering rendered flags will fail tests even if behavior remains functionally equivalent. Version-gated cases risk coverage gaps on older build environments.
