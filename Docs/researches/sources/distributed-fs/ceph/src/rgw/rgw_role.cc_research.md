# sources/distributed-fs/ceph/src/rgw/rgw_role.cc

## Purpose
`rgw_role.cc` implements common IAM role metadata behavior shared by SAL backends. It formats and parses `RGWRoleInfo`, validates role input, constructs role ids/ARNs/creation timestamps, and mutates inline policies, trust policy, tags, and session duration before backend-specific persistence.

## Important APIs, Types, and Functions
`RGWRoleInfo::dump()` emits IAM-facing JSON fields, including tenant-qualified role name, trust policy, inline policies, managed policy ARNs, tags, description, account id, and max session duration. `decode_json()` reconstructs the same fields, splitting tenant from names that contain `$`.

`RGWRole::RGWRole(...)` initializes a role from request input, defaulting path to `/`, parsing tenant from the name, defaulting max session duration to 3600 seconds, and storing tags/trust policy/description. The id constructor initializes lookup-by-id objects. `validate_input()` enforces name/path lengths and regexes plus max-session duration bounds. `create()` validates input, generates a UUID id if absent, constructs `arn:aws:iam::<account-or-tenant>:role<path><name>`, fills an ISO-like creation timestamp, and calls virtual `store_info(exclusive=true)`.

Policy/tag helpers mutate `RGWRoleInfo`: `set_perm_policy()`, `get_role_policy_names()`, `get_role_policy()`, `delete_policy()`, `update_trust_policy()`, `set_tags()`, `get_tags()`, `erase_tags()`, and `update_max_session_duration()`.

## Control Flow
Request handlers generally obtain a backend role object through `Driver::get_role()`, call common mutators/validation, then call a virtual persistence method. Creation is the main full flow in this file: validate, choose/generate id, compute ARN and creation date, then store through the backend. Loads, deletes, and low-level stores are abstract virtual methods from the header.

## State and Persistence Behavior
`rgw_role.cc` only mutates the in-memory `RGWRoleInfo`; persistence is delegated to `store_info()`, `load_by_name()`, `load_by_id()`, and `delete_obj()` implemented by a SAL backend. Encoding in the header persists versioned role fields. `objv_tracker` and `mtime` are part of role state but not manipulated much here beyond setting `mtime` to a default construction value.

## Dependencies and Integration Points
The file depends on Ceph formatter/JSON/time utilities, UUID generation, RGW string helpers, zone services, managed policy structures, and SAL backend role implementations. It is used by IAM APIs such as CreateRole, PutRolePolicy, AttachRolePolicy-related metadata, tagging, and role listing.

## Risks
`std::stoull()` in constructors and `update_max_session_duration()` can throw on malformed input unless callers prevalidate. `get_role_policy_names()` applies `std::move()` to keys from a const map iteration, which is ineffective but surprising. `set_tags()` appends tags before checking the 50-tag limit; on failure the object remains mutated. Regexes must match AWS semantics closely, especially path formatting.

## Test Signals
Tests should cover valid/invalid role names and paths, session duration min/max and malformed strings, tenant extraction, ARN construction with account id versus tenant, UUID generation, creation timestamp format, inline policy CRUD, duplicate/many tags, JSON dump/decode round trip including managed policies, and backend store failure propagation from `create()`.
