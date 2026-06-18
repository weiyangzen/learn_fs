# sources/distributed-fs/ceph/src/mon/MonCap.cc

## Purpose

`MonCap.cc` implements parsing, formatting, encoding, merging, and enforcement for monitor capabilities. Monitor caps authorize service-level read/write/execute access, named command grants with argument constraints, profiles that expand into grants, fs-name restrictions, and network restrictions.

## Important APIs, Types, and Functions

The file implements stream output for `mon_rwxa_t`, `StringConstraint`, `MonCapGrant`, and `MonCap`; `MonCapGrant::parse_network()`, `expand_profile()`, `get_allowed()`, and `to_string()`; and `MonCap::is_allow_all()`, `set_allow_all()`, `is_capable()`, `encode()`, `decode()`, `dump()`, `generate_test_instances()`, `parse()`, `merge()`, and `to_string()`. The Boost Spirit `MonCapParser` grammar accepts blanket grants, service grants, profile grants, command grants with `with` argument constraints, optional network clauses, and fs-name clauses.

## Control Flow and State

Parsing fills a vector of `MonCapGrant` objects and clears all grants on parse failure. Each grant can hold service/profile/command/fs/network fields plus rwx bits and command argument constraints. `expand_profile()` lazily populates cached profile grants for profiles such as `read-only`, `read-write`, `mon`, `osd`, `mds`, `mgr`, bootstrap profiles, RBD profiles, crash, cephfs-mirror, and role-definer. `is_capable()` iterates grants, skips invalid or non-matching networks, short-circuits `allow *`, ORs allowed bits from matching grants, and succeeds when all operation-required read/write/exec bits are present.

Encoded state is only the original textual cap string, preserving compatibility and re-parsing on decode. `merge()` updates or appends single fs-name grants idempotently.

## Dependencies and Integration Points

Dependencies include Boost Spirit/Fusion/Phoenix, regex, network parsing/matching helpers, Ceph auth entity names, buffer encoding, formatter support, and debug logging. Monitor sessions call `is_capable()` through `MonSession` to authorize monitor services and commands, including command argument constraints for bootstrap and blocklist operations.

## Risks and Test Signals

Risks include grammar ambiguity, profile grants becoming stale as command names change, regex exceptions, invalid network clauses silently denying a grant, and text-only persistence accepting old syntax but losing structured validation until decode. `MonCapGrant::to_string()` uses `else if` for rwx bits and therefore is only suitable for simple fs-name grant rendering, not full service/profile/command caps. Tests should cover valid and invalid parse cases, quoting, network filters, exact/prefix/regex argument constraints, profile expansion, `config-key` blanket denial except `allow *`, fs-name merge idempotency, encode/decode reparsing, and negative authorization cases.
