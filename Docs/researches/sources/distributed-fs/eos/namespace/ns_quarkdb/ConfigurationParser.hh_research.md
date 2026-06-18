# sources/distributed-fs/eos/namespace/ns_quarkdb/ConfigurationParser.hh

Purpose: parses a namespace configuration map into `QdbContactDetails`.

Important APIs/types/functions: `ConfigurationParser::parse` requires `qdb_cluster`, optionally reads `qdb_password`, fills `qclient::Members`, and throws `MDException(EINVAL)` on missing or unparsable cluster data.

Control flow: find mandatory cluster key, parse into members, optionally copy password, return contact details.

State and persistence: stateless parser; all output is in the returned value.

Dependencies and integration: uses qclient `Members`, `Options`, `Handshake`, `QdbContactDetails`, and EOS exception helpers. Similar parsing logic is also present in `QuarkNamespaceGroup::initialize`.

Risks: duplicated parsing logic can diverge from namespace group initialization. It does not validate password with the cluster, only stores it.

Test signals: configuration failure and success cases should be covered through namespace group/plugin initialization tests.
