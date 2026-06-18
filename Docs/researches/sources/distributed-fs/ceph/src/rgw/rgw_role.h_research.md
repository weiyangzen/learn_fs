# sources/distributed-fs/ceph/src/rgw/rgw_role.h

## Purpose
`rgw_role.h` defines the IAM role metadata record and the abstract SAL role interface. It separates common IAM role validation/mutation logic from backend persistence, while preserving Ceph encoding compatibility for stored role objects.

## Important APIs, Types, and Functions
`RGWRoleInfo` contains id, name, path, ARN, creation date, trust policy, inline permission policies, managed policies, tenant, description, max session duration, tags, object version tracker, mtime, and account id. Its encoder is at struct version 4: older versions lack tenant, max session duration, account id, description, and managed policies. JSON helpers are declared for admin/API formatting.

`rgw::sal::RGWRole` owns a protected `RGWRoleInfo info` and declares backend virtuals: `load_by_name()`, `load_by_id()`, `store_info()`, and `delete_obj()`. Common methods validate max session duration and input, extract tenant from names, create roles, update trust policy, mutate inline policies/tags, and update max session duration. Constants define ARN prefix, max name/path lengths, and session duration bounds.

## Control Flow
Code constructs an `RGWRole` via driver factories either from request fields, an id, or existing `RGWRoleInfo`. Common methods mutate/validate the cached `info`, then backend virtuals persist or load it. Getters expose fields to IAM handlers and response formatters.

## State and Persistence Behavior
Persistent state is represented by `RGWRoleInfo` encoding. Versioned decode protects rolling upgrades by only reading newer fields when present. `RGWObjVersionTracker` supports optimistic concurrency in backend stores but is not encoded in `RGWRoleInfo`; it is runtime metadata alongside `mtime`.

## Dependencies and Integration Points
The header depends on Ceph encoding, JSON, time, async yield, RGW common identities, and `rgw_iam_managed_policy.h`. `Driver::get_role()` in `rgw_sal.h` returns concrete implementations of this interface.

## Risks
The interface exposes mutable `RGWRoleInfo& get_info()`, so callers can bypass validation. Decode compatibility means defaults for missing fields must remain safe. `set_tags()` and other common mutators do not persist automatically; callers must remember to call `store_info()`.

## Test Signals
Tests should exercise encode/decode across struct versions, JSON decode with tenant-qualified names, validation boundary constants, virtual backend contract for exclusive store, and mutation methods followed by backend persistence.
