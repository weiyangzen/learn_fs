# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.h

## Purpose

This header declares the exported TPMI power-domain mapping helpers.

## Important APIs, Types, And Functions

It declares CPU/domain translation helpers: `tpmi_get_linux_cpu_number()`, `tpmi_get_punit_core_number()`, `tpmi_get_power_domain_id()`, `tpmi_get_power_domain_mask()`, and `tpmi_get_linux_die_id()`.

## Control Flow

Consumers call these helpers after the mapping module initializes and CPU online callbacks populate state.

## State And Persistence

No state is defined here; implementation state is in `tpmi_power_domains.c`.

## Dependencies And Integration Points

It includes `linux/cpumask.h` because one helper returns `cpumask_t *`. It is used by TPMI feature drivers that need P-unit domain to Linux topology translation.

## Risks

The prototype names the second argument of `tpmi_get_linux_cpu_number()` as `die_id`, while the implementation treats it as `domain_id`; this naming mismatch can confuse consumers.

## Test Signals

Compile consumers, namespace import/export checks, and semantic tests for package/domain/core lookups validate it.
