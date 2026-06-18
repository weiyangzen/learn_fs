# sources/distributed-fs/eos/unit_tests/mgm/tgc/SmartSpaceStatsTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/tgc/SmartSpaceStatsTests.cc

Purpose: tests `SmartSpaceStats`, the TGC helper that obtains free-byte information for spaces, optionally through a configured script.

Important APIs and types: `SmartSpaceStats`, `DummyTapeGcMgm`, constructor/config methods, and `get`-style free-byte retrieval.

Control flow: constructor test verifies initial state. The no-script test obtains stats through default/dummy MGM behavior. The script-configured test sets a free-bytes script and verifies values are returned through that path.

State and persistence: state is in-memory configuration plus any dummy MGM counters. It does not persist results; it computes or fetches them per call.

Dependencies and integration: bridges TGC decision logic with MGM space statistics and optional external script configuration.

Risks and test signals: external-script execution is a production risk, but tests use controlled dummy behavior. Coverage should be supplemented by integration tests for script failures and parsing.
