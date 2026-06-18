# sources/distributed-fs/eos/mgm/proc/user/Whoami.cc

Purpose: implements `ProcCommand::Whoami()`, returning the caller's virtual identity in monitoring or human-readable form.

Important APIs and types: reads `mgm.option`, uses fields from `pVid` such as uid/gid, allowed UID/GID sets, auth protocol, sudo flag, host, domain, geolocation, key, fullname, federation, email, and optional token dump.

Control flow: option `m` emits compact key/value fields for UID, allowed UIDs, GID, allowed GIDs, authz, and sudo. Default output formats identity details, host/domain, auth key redaction for non-sss protocols, optional profile fields, and token dump if present.

State and persistence: read-only except stats.

Dependencies and integration: exposes the resolved identity object used by all other proc commands, making it a diagnostic integration point for auth mapping and token scope.

Risks: monitoring output intentionally omits host/geolocation, while human output may reveal PII such as fullname and email. Token dumps are included in default output with secret suppression controlled by `Dump(true, false)`. Tests should cover empty allowed UID/GID sets, sudo flag, sss versus oauth key redaction, optional PII fields, token-authenticated identities, and monitoring output grammar.
