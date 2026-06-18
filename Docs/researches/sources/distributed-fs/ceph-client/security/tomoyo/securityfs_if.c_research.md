# sources/distributed-fs/ceph-client/security/tomoyo/securityfs_if.c

## Purpose

This file exposes TOMOYO's securityfs control interface under `/sys/kernel/security/tomoyo/` and implements the special `self_domain` file for reading or manually changing the current task's TOMOYO domain.

## Important APIs, types, and functions

The key externally used function is `tomoyo_interface_init()`, registered as TOMOYO's `initcall_fs`. File operation handlers include `tomoyo_write_self`, `tomoyo_read_self`, `tomoyo_open`, `tomoyo_release`, `tomoyo_poll`, `tomoyo_read`, and `tomoyo_write`. `tomoyo_check_task_acl()` validates manual domain transition ACLs. `tomoyo_create_entry()` creates typed securityfs files using `i_private` keys.

## Control Flow

`tomoyo_interface_init()` exits early if TOMOYO is disabled or not yet attached to the kernel domain. It creates the `tomoyo` securityfs directory, adds query, policy, audit, stat, profile, manager, version, process status, and `self_domain` files, then loads built-in policy. Generic file operations forward to TOMOYO control-buffer helpers. `tomoyo_write_self()` copies a user domain string, normalizes it, validates domain syntax, checks `task manual_domain_transition` permission under the read lock, assigns or finds the new domain, and swaps the current task's domain reference counts.

## State and Persistence

Securityfs dentries persist after initialization. Manual domain transitions mutate the current task's `tomoyo_task.domain_info` pointer and atomic user counts. Policy data and control buffer state are managed by common TOMOYO code; this file only routes file operations to it.

## Dependencies and Integration Points

It depends on Linux securityfs, TOMOYO control I/O helpers, domain assignment, request initialization, ACL checks, line normalization, and path/domain validators. The created files are the user-space policy management ABI.

## Risks and Test Signals

Risks include permissive `0666` `self_domain` relying entirely on TOMOYO ACL checks, partial read offsets, domain reference count imbalance, securityfs creation failures not being checked, and user input size handling. Tests should cover securityfs file presence, read/write behavior, invalid domains, denied and allowed manual transitions, concurrent transitions, and policy load ordering.
