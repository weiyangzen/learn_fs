<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.hh -->
# sources/distributed-fs/eos/mgm/policy/Policy.hh

Source read size: 163 lines, 6887 bytes.

## Purpose

Declares the static MGM policy utility class that resolves storage layout, space, placement, conversion, local redirect, and policy proc command behavior.

## Important APIs, Types, and Functions

Important declarations include `GetLayoutAndSpace`, `GetPlctPolicy`, `RedirectStatus`, `RedirectLocal`, `ConversionPolicy`, `HasUpdConversion`, `HasReadConversion`, `UpdateConversion`, `ReadConversion`, `GetSpacePolicyLayout`, `Set/Ls/Rm/Get`, `IsProcConversion`, static policy key vectors, `GetDefaultSizeFactor`, and nested `RWParams`.

## Control Flow

The class is a namespace-like collection of static functions. `RWParams` derives app/user/group/read-write policy keys and orders key lookup from app-specific to user, group, and generic read/write keys.

## State and Persistence Behavior

The header declares static key lists but no mutable state. Policy state lives in EOS space config and namespace attributes read by the implementation.

## Dependencies and Integration Points

Depends on mapping, MGM scheduler placement enums, namespace container metadata, and XRootD env/string types. Used by open/create/read paths and proc/admin policy surfaces.

## Risks and Edge Cases

Because all APIs are static and accept mutable attr/env references, callers must document whether the view lock is already held and whether attrmap mutation is acceptable. The policy command management API is declared even though much of it is not implemented in the `.cc`.

## Test Signals

Compile consumers of every static API, unit-test `RWParams::getKeys`, and integration-test `GetLayoutAndSpace` with controlled env/attr/space configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.hh -->
