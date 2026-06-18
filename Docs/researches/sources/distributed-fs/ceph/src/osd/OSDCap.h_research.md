# sources/distributed-fs/ceph/src/osd/OSDCap.h

## Purpose
`OSDCap.h` declares the OSD capability data model and authorization API. It represents authenticated-user OSD caps as grants with allow masks, class/method permissions, pool/namespace/tag/object match constraints, optional network restrictions, and named profiles. The comments define the supported user-facing cap model and warn that `*` caps imply full administrative message permissions and should be reserved for monitors and OSDs.

## Important APIs, Types, and Functions
Capability bits are `OSD_CAP_R`, `OSD_CAP_W`, `OSD_CAP_CLS_R`, `OSD_CAP_CLS_W`, `OSD_CAP_X` as combined class read/write, and `OSD_CAP_ANY` for `*`. `osd_rwxa_t` wraps an 8-bit mask with assignment and conversion helpers.

`OSDCapSpec` stores either an allow mask or an explicit `class_name`/`method_name` permission. `allow_all()` identifies `OSD_CAP_ANY`.

`OSDCapPoolNamespace` stores an optional pool name and optional namespace. It declares `is_match` and `is_match_all`.

`OSDCapPoolTag` stores an application metadata predicate (`application`, `key`, `value`) and declares tag matching against nested application metadata maps. It is adapted with `BOOST_FUSION_ADAPT_STRUCT` so the Qi parser in `OSDCap.cc` can populate it directly.

`OSDCapMatch` combines pool/namespace constraints, pool tag constraints, and object prefix constraints. Its constructors support tag-only, pool/namespace-only, pool-prefix, pool-namespace-prefix, app tag, and namespace-tag forms. It declares `is_match` and `is_match_all`.

`OSDCapProfile` stores a profile name and optional pool/namespace scope. `is_valid()` is a simple non-empty-name check.

`OSDCapGrant` combines a match, spec, profile, optional textual and parsed network, network prefix, network validity, and cached `profile_grants`. It declares `set_network`, `allow_all`, `is_capable`, `expand_profile`, and `to_string`.

`OSDCap` is the top-level vector of grants. It declares `allow_all`, `set_allow_all`, `parse`, `merge`, `to_string`, and the operation-level `is_capable` check. The inline stream operator renders it as `osdcap` plus the grants vector.

## Control Flow
The declared authorization flow is hierarchical. An `OSDCap` contains grants; each `OSDCapGrant` either evaluates its direct match/spec/network or delegates to expanded profile grants. A direct grant matches request context using `OSDCapMatch`, checks read/write intent against `OSDCapSpec::allow`, and evaluates class operation permissions against `OpInfo::ClassInfo`. The top-level `OSDCap::is_capable` returns true when the grant set collectively authorizes the operation.

Parsing is declared on `OSDCap` but implemented in `OSDCap.cc`; it fills the grant vector from the textual grammar. `merge` is declared for applying another parsed one-grant cap into an existing cap set. `set_allow_all` is the imperative shortcut for replacing current grants with unrestricted access.

## State and Persistence Behavior
The header defines only in-memory structures. No encoding/decoding or ObjectStore persistence is declared here. Persistent cap storage elsewhere is expected to be textual and parsed into these structures. The important state-bearing fields are the ordered `grants` vector, cached profile expansions in each grant, textual plus parsed network representation, `network_valid`, and optional namespace values that distinguish absent namespace constraints from an explicit empty namespace.

## Dependencies and Integration Points
`OSDCap.h` depends on Ceph base types (`include/types.h`), OSD operation class metadata (`osd/osd_op_util.h`), `entity_addr_t` for client/network checks, Boost.Optional for optional namespaces, Boost.Fusion for parser struct adaptation, and standard containers/streams.

It is included by `OSDCap.cc` for implementation, monitor/auth code for validating and updating cap strings, OSD monitor code for checking whether caps imply writable OSD access, and OSD operation authorization code that needs `OSDCap::is_capable`.

## Risks
Because this header is the authorization contract, small semantic changes have security impact. Distinguishing absent namespace from explicit empty namespace is important. `OSD_CAP_X` is not an independent bit; it is the union of class read and class write. `OSD_CAP_ANY` is `0xff`, so callers must use `allow_all()` or bit checks consistently. Profile validity is name-only, so unknown profile names can exist structurally but expand to no grants. Network restrictions carry both original string and parsed state; callers must preserve both when rendering, auditing, or evaluating.

Constructor overloads for `OSDCapMatch` are convenient but easy to misuse because several accept strings with different meanings. The top-level `merge` contract is not a general cap union; implementation assumes a one-grant incoming cap and has specialized tag behavior.

## Test Signals
Header-level test signals include compile coverage for all constructor forms, stream rendering of all declared types, parser population of `OSDCapPoolTag` through Boost.Fusion adaptation, `allow_all` behavior for unrestricted direct and profile grants, namespace absent versus empty versus wildcard behavior, network-set construction, `set_allow_all` replacement semantics, and `merge` precondition enforcement with one-grant inputs.
