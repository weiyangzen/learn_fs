# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.cc

Purpose: Implements shared fixture infrastructure for QuarkDB namespace tests.
Important APIs/types/functions: `FlushAllOnConstruction`, `NsTests` constructor/destructor, `getContactDetails`, `getMembers`, `initServices`, service/view/qclient/flusher accessors, `shut_down_everything`, `createQClient`, `populateDummyData1`, and `cleanNSCache`.
Control flow: fixture reads QDB host/password env vars or `/etc/eos.keytab`, builds test config, flushes QDB with `FLUSHALL`, lazily initializes `QuarkNamespaceGroup`, configures services/views/flushers, initializes the hierarchical view, and tears services down on destruction.
State/persistence: owns test config, namespace mutex, optional size mapper, a QDB-flush guard, and the namespace group. QDB is reset per fixture construction.
Dependencies/integration: central integration point for qclient, namespace group, services, flusher, accounting views, and environment configuration.
Risks: `FLUSHALL` is destructive on the configured QDB; defaults target `localhost:9999`; reading `/etc/eos.keytab` can unexpectedly set a password; lazy initialization hides setup failures until first accessor.
Test signals: enables almost every integration test in this subset.
