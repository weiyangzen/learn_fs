# sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.hh

Purpose: declares the QuarkDB version enforcement function.

Important APIs/types/functions: `bool enforceQuarkDBVersion(qclient::QClient *qcl)`.

Control flow: declaration only.

State and persistence: none.

Dependencies and integration: includes qclient version type and forward-declares `QClient`; used by namespace group initialization.

Risks: callers need a live, connected qclient and must handle a false result as startup failure.

Test signals: covered through namespace initialization/version-check tests.
