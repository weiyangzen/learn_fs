# sources/distributed-fs/ceph-client/security/landlock/cred.h

## Purpose

`cred.h` defines Landlock's credential security blob and inline helpers to retrieve the current or target task domain, copy credential Landlock state, and detect whether a subject domain handles a requested mask.

## Important APIs, Types, and Functions

`struct landlock_cred_security` stores the enforced immutable `domain`. With audit, it also stores `domain_exec` and `log_subdomains_off`. `landlock_cred()` indexes the LSM credential blob. `landlock_cred_copy()` drops the destination domain, copies the source blob, and pins the source domain. `landlock_get_current_domain()`, `landlock_get_task_domain()`, and `landlocked()` are accessors. `landlock_get_applicable_subject()` returns a subject only if some domain layer handles the requested fs/net/scope masks and can report the youngest matching layer.

## Control Flow

Enforcement hooks call `landlock_get_applicable_subject()` before doing expensive checks. The function scans domain layers from newest to oldest and returns early when any requested bit is handled. If no domain or no handled bits exist, callers skip enforcement.

## State and Persistence Behavior

The blob is persistent per credential and points to reference-counted immutable rulesets. Audit bits persist until new exec or credential replacement.

## Dependencies and Integration Points

The header depends on ruleset, access, setup, credentials, RCU, and task structures. It is included by filesystem, network, task, audit, and setup code.

## Risks and Test Signals

Layer scanning order affects audit attribution for topology denials. Copy helpers must be used carefully to avoid dropping a live domain. Test nested domains, no-op masks, audit layer reporting, and concurrent task-domain reads under RCU.
