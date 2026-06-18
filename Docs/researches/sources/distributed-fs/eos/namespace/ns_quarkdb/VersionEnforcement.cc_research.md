# sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.cc

Purpose: checks that the connected QuarkDB cluster meets the minimum namespace backend version requirement.

Important APIs/types/functions: `enforceQuarkDBVersion(qclient::QClient*)` executes `quarkdb-version`, parses the reply into `qclient::QuarkDBVersion`, compares with target `0.4.2`, logs failures, and returns a boolean.

Control flow: synchronous qclient command waits on `.get()`, logs the reply, parses version text, rejects parse failures and versions older than target, otherwise returns true.

State and persistence: stateless; reads server version only.

Dependencies and integration: called during `QuarkNamespaceGroup::initialize` before successful backend startup.

Risks: assumes non-null reply with string fields; malformed or null replies may crash before parse failure handling. Startup blocks on qclient retry behavior. Target version is hard-coded.

Test signals: integration tests with mocked or real qclient version replies should cover accept/reject paths.
