# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.c

## Purpose

`ufs-fault-injection.c` adds fault-injection knobs for testing UFS error and timeout paths.

## Important APIs, Types, and Functions

Public functions are `ufs_fault_inject_hba_init()`, `ufs_trigger_eh()`, and `ufs_fail_completion()`. Module parameters `trigger_eh` and `timeout` use `ufs_fault_ops`, `setup_fault_attr()`, and per-HBA `fault_attr` copies.

## Control Flow

Module parameter writes parse standard fault-injection tuples into static template attributes and preserve the input string for reads. HBA init copies templates into `hba->trigger_eh_attr` and `hba->timeout_attr`, and optionally creates debugfs attributes. Runtime callers ask `should_fail()` to decide whether to trigger error handling or fail completion.

## State and Persistence Behavior

State is runtime kernel module parameter strings plus per-HBA fault attributes. It is not persisted beyond module lifetime.

## Dependencies and Integration Points

It depends on `FAULT_INJECTION`, optional fault-injection debugfs, module parameters, and `struct ufs_hba` fields consumed by core error paths.

## Risks and Test Signals

Risks include malformed parameter strings, global templates being copied only at HBA init time, and accidentally enabling aggressive failures on production systems. Test signals include parameter read/write parsing, debugfs attribute creation, deterministic `should_fail()` behavior for interval/probability/times settings, and disabled-config stubs returning false.
