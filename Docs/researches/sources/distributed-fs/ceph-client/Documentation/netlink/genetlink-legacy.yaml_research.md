# sources/distributed-fs/ceph-client/Documentation/netlink/genetlink-legacy.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/netlink/genetlink-legacy.yaml` is a YAML netlink specification for `genetlink-legacy.yaml` using protocol `netlink`. It documents the userspace/kernel ABI and feeds Linux netlink code-generation, validation, and documentation tooling.

## Important APIs, Types, and Functions
The schema/spec exports structured ABI metadata: 0 definitions, 0 attribute sets, 0 operations, and 0 multicast groups. Top-level keys are `$id`, `$schema`, `$defs`, `title`, `description`, `type`, `required`, `additionalProperties`, `properties`. Attribute sets describe binary payload layouts, types, enum bindings, nesting, display hints, policies, and generated C names. Operations describe command IDs, request/reply notifications, do/dump semantics, required attribute sets, and policy validation entry points.

## Control Flow
Control flow is generator-driven. YAML is parsed by the kernel netlink spec tooling, normalized into an internal family model, and emitted as UAPI documentation, C policy tables, op tables, enum/name helpers, or userspace helpers depending on the target. At runtime generated or hand-written family code receives netlink messages, validates attributes against policies, dispatches operations, fills replies, and emits multicast notifications according to this spec.

## State and Persistence Behavior
The file stores no runtime state. Its persistent state is ABI: family name, operation numbers, attributes, enum values, nesting relationships, multicast groups, and generated symbol names. Runtime state belongs to the associated kernel family such as sockets, objects, device instances, conntrack tables, devlink ports, or energy-model records.

## Dependencies and Integration Points
License/doc signal: not declared. Integration points include `tools/net/ynl`, YAML schema validation, generic netlink or raw netlink dispatch, generated policy arrays, generated userspace bindings, and subsystem-specific drivers or core code. The source has 482 lines; references and enum/value definitions must remain synchronized with the subsystem UAPI headers and implementation.

## Risks
Risks include ABI breakage from renumbering operations or attributes, mismatched attribute types between YAML and C code, underspecified nested policies, incorrect dump/do flags, missing admin-permission annotations, and generator drift where the spec validates but the family implementation accepts or emits a different shape. Large specs such as devlink also risk partial updates where a new command is added to C but not to YAML.

## Test Signals
Run the kernel YNL/netlink spec validation and generated-code build paths for this file, then exercise generated clients against a kernel with the target family loaded. Test malformed attributes, missing required attributes, dump pagination, multicast notification decoding, enum name round-trips, and compatibility of old userspace against newly generated policies.
