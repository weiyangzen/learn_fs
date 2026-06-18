# sources/distributed-fs/ceph-client/security/landlock/audit.h

## Purpose

`audit.h` defines the compact request structure and logging entry points used by Landlock enforcement code. It also provides no-op stubs when audit support is disabled.

## Important APIs, Types, and Functions

`enum landlock_request_type` classifies ptrace, filesystem topology, filesystem access, network access, abstract Unix socket scope, and signal scope denials. `struct landlock_request` carries mandatory LSM audit data, either a fixed denying layer or access bits, optional layer masks, optional compact deny masks, and optional-access metadata. `landlock_log_denial()` and `landlock_log_drop_domain()` are exported internally.

## Control Flow

Enforcement hooks populate a stack `landlock_request` only when they need to log. With `CONFIG_AUDIT=n`, inline stubs make these calls compile away.

## State and Persistence Behavior

The request is transient stack state. Persistent audit-related state is in domain hierarchy structures declared elsewhere.

## Dependencies and Integration Points

The header depends on Linux audit/LSM audit types and Landlock access and credential types. It is included by filesystem, network, task, domain, and object lifetime code.

## Risks and Test Signals

Callers must set a consistent combination of `layer_plus_one`, `access`, `layer_masks`, and `deny_masks`; `audit.c` warns on invalid combinations. Build-test audit on/off and exercise every request type.
