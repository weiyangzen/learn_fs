# sources/distributed-fs/ceph/src/osd/OSDCap.cc

## Purpose
`OSDCap.cc` implements parsing, rendering, matching, profile expansion, network restriction, capability merging, and authorization checks for Ceph OSD capability strings. It turns monitor/auth cap text such as `allow rwx pool foo`, `allow class rbd metadata_list`, `allow *`, `profile rbd`, or app-tag grants into `OSDCap` objects that can be checked against pool, namespace, object, class-operation, application metadata, and client address.

## Important APIs, Types, and Functions
Stream operators render `osd_rwxa_t`, `OSDCapSpec`, `OSDCapPoolNamespace`, `OSDCapPoolTag`, `OSDCapMatch`, `OSDCapProfile`, and `OSDCapGrant`. Match helpers include `OSDCapPoolNamespace::is_match`, `OSDCapPoolNamespace::is_match_all`, `OSDCapPoolTag::is_match`, `OSDCapPoolTag::is_match_all`, `OSDCapMatch::is_match`, and `OSDCapMatch::is_match_all`.

Grant-level logic is in `OSDCapGrant::set_network`, `allow_all`, `is_capable`, `expand_profile`, and `to_string`. Cap-level logic is in `OSDCap::allow_all`, `set_allow_all`, `is_capable`, `parse`, `merge`, and `to_string`.

`OSDCapParser` is a Boost.Spirit Qi grammar. It defines quoted and unquoted strings, optional pool and namespace clauses, object prefixes, application tags, wildcard/all spelling, rwx/class-read/class-write specs, explicit class/method specs, profile specs, optional `network` clauses, grant separators, and the top-level cap.

## Control Flow
Authorization starts at `OSDCap::is_capable`, which creates a `class_allowed` vector sized to the operation's class calls, then scans grants in order. A single grant that accepts the whole operation returns success.

`OSDCapGrant::is_capable` first rejects invalid or nonmatching network restrictions with `parse_network`/`network_contains`. Profile grants recurse through cached `profile_grants`. Non-profile grants then require the pool/namespace/tag/object match to pass. Read and write intent are checked against `OSD_CAP_R` and `OSD_CAP_W`. If the op invokes classes, `allow *` immediately succeeds; otherwise each class call can be allowed by an explicit `allow class <class> [method]` spec or by class read/write bits (`x`, `class-read`, `class-write`) only when `OpInfo::ClassInfo::allowed` says the class is eligible. Every class call must become allowed for the grant to pass.

Parser control flow accepts either `allow <capspec> <match>`, `allow <match> <capspec>`, or `profile <name> ...`, each with optional `network`. Grants are separated by semicolons or commas. `OSDCap::parse` requires the entire input to be consumed and clears all grants on failure so partially parsed privileges are not retained.

Profile expansion is deterministic. `read-only` expands to read on the profile pool/namespace. `read-write` expands to read/write. `rbd` adds special `rbd_info`, `rbd_children`, `rbd_mirroring`, `rbd metadata_list`, and full rwx grants for the profile pool/namespace. `rbd-read-only` adds `rbd metadata_list`, read plus class-read, and `rbd child_attach`/`child_detach` for `rbd_header.` objects.

`OSDCap::merge` is specialized for a one-grant incoming cap, primarily app-tag capability updates. It updates an existing grant with the same app/key/value when the allow mask differs, keeps idempotent matches unchanged, or appends a new tag grant otherwise.

## State and Persistence Behavior
This file does not persist data directly. It mutates in-memory `OSDCap::grants`, `OSDCapGrant::profile_grants`, parsed network fields, and grant allow masks. Persistence is indirect: monitor/auth code stores cap strings and uses this parser and `to_string`/`merge` behavior when validating or updating OSD caps.

Important state invariants are that failed parses leave `grants` empty; profile grants are expanded and cached inside the grant at construction; `network_valid` records whether the textual network parsed; and cap checks accumulate class-call permissions across grants through one shared `class_allowed` vector during an `OSDCap::is_capable` call.

## Dependencies and Integration Points
The implementation depends on Boost.Spirit Qi/Phoenix/Fusion for parsing, Boost string predicates for namespace wildcard matching, Ceph debug/config headers, `include/ipaddr.h` for network parsing and containment, `OSDCap.h` for data structures, and `osd_op_util.h` through `OpInfo::ClassInfo`.

Monitor integration is visible in `AuthMonitor.cc`, which parses OSD caps and merges cap updates, and `OSDMonitor.cc`, which parses OSD caps to reason about writable OSD permissions. At runtime the OSD operation path can use `OSDCap::is_capable` to decide whether a client operation over a pool/namespace/object/class set is authorized.

## Risks
Authorization risks center on parser ambiguity and match semantics. The grammar accepts both capspec-before-match and match-before-capspec forms, optional fields, wildcards, quoted empty namespaces, namespace suffix `*`, and tag wildcards; regressions here can silently broaden or narrow permissions. Namespace wildcard matching treats a namespace ending in `*` as a prefix match. Object prefix uses `object.find(prefix) == 0`, so empty or poorly quoted prefixes matter.

Class authorization is subtle because explicit class/method grants and class read/write bits interact with `classes[i].allowed`; bugs can over-permit class execution or deny valid RBD workflows. `OSDCap::is_capable` keeps `class_allowed` across grants, so multiple grants may collectively satisfy class calls, while read/write checks are still per matching grant. `OSDCap::merge` only compares tag fields and ignores other match dimensions, with an in-code TODO for cases such as `allow rw tag cephfs *`.

Network restrictions fail closed when parsing fails, but incorrect network parsing, address family handling, or missing client address propagation would affect access. `to_string` is lossy for profiles, networks, object prefixes, pool/namespace matches, class-name specs, and some class-write formatting choices, so it should not be treated as a canonical serializer for every parsed cap form.

## Test Signals
Tests should cover successful and failed parse strings; full-consumption parse failures; `allow *` and `allow all`; all rwx/class-read/class-write combinations; capspec-before-match and match-before-capspec forms; quoted pool/object/tag values; empty namespace quotes; namespace prefix wildcard; object prefix matching; pool tag wildcard key/value cases; profile expansion for read-only, read-write, rbd, and rbd-read-only; network allow/deny and invalid networks; explicit class/method grants; multi-class operations satisfied by one or more grants; `merge` idempotent/update/append behavior; and failure clearing existing grants.
