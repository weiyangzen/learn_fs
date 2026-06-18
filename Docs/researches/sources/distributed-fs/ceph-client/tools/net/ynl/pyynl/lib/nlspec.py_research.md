# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/nlspec.py

Purpose: Provides the Python object model and resolver for YAML netlink specifications used by YNL generators, CLI validation, and the Python runtime.

Important APIs and types: Core classes include `SpecElement`, `SpecEnumEntry`, `SpecEnumSet`, `SpecAttr`, `SpecAttrSet`, `SpecStructMember`, `SpecStruct`, `SpecSubMessage`, `SpecSubMessageFormat`, `SpecOperation`, `SpecMcastGroup`, and `SpecFamily`. `SpecFamily` exposes parsed dictionaries for `attr_sets`, `sub_msgs`, `msgs`, `req_by_value`, `rsp_by_value`, `ops`, `ntfs`, `consts`, `mcast_groups`, and `kernel_family`.

Control flow: `SpecFamily` reads and validates the SPDX-tagged YAML spec, optionally validates it against a schema, initializes collections, and then resolves elements through an iterative `_resolution_list`. `resolve()` constructs constants, attribute sets, sub-messages, operations under either unified or directional enum models, request/response lookup maps, async notification maps, and multicast groups. `SpecOperation.resolve()` derives its attribute set directly or through a referenced notification target.

Dependencies and integration: Depends on PyYAML and lazily imports `jsonschema` only when schema validation is enabled. It is subclassed by `YnlFamily` in `ynl.py` and consumed by code/doc generators.

State and persistence: All state is in-memory representation of a spec. It does not write files or keep external handles open.

Risks: Resolution retries catch `KeyError` and `AttributeError`; a real bug can look like an unresolved dependency until no progress is made. Directional operation ID handling is subtle, especially notifications/events and request/reply value overrides. Attribute-set subsets merge dictionaries with `real_attr.yaml | elem`, so override precedence must remain intentional.

Test signals: Specs with and without schema validation, missing SPDX tag, unified and directional enum models, explicit operation values, excluded ops regexes, subset attribute sets, structs, flags/enums, sub-message selectors, notifications referencing other messages, multicast groups, and unresolved-reference failures.
