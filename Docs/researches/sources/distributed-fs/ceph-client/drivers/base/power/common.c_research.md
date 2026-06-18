# sources/distributed-fs/ceph-client/drivers/base/power/common.c

## Purpose
Provides shared driver-core PM helpers for `dev->power.subsys_data` lifetime and device PM-domain attachment, list attachment, detachment, start, domain assignment, and performance-state requests.

## Important APIs, Types, And Functions
Exports `dev_pm_get_subsys_data()`, `dev_pm_put_subsys_data()`, `dev_pm_domain_attach()`, `dev_pm_domain_attach_by_id()`, `dev_pm_domain_attach_by_name()`, `dev_pm_domain_attach_list()`, `devm_pm_domain_attach_list()`, `dev_pm_domain_detach()`, `dev_pm_domain_detach_list()`, `dev_pm_domain_start()`, `dev_pm_domain_set()`, and `dev_pm_domain_set_performance_state()`. `struct pm_subsys_data` is reference-counted under `dev->power.lock` and initialized for PM clocks.

## Control Flow
Subsystem data acquisition allocates optimistically, takes the device power lock, either increments an existing refcount or installs a new object and initializes PM clock state, then frees unused allocation. PM-domain attach first rejects devices already in a domain, tries ACPI attach and generic PM domain attach, and records detach-power-off policy. List attach counts OF power domains or uses named entries, attaches virtual devices by ID/name, optionally installs required OPP configs, optionally creates runtime-PM device links, and rolls back all prior domains, links, and OPP tokens on failure. Devres list attach registers automatic detach.

## State And Persistence
State lives in `dev->power.subsys_data`, `dev->pm_domain`, `dev->power.detach_power_off`, `struct dev_pm_domain_list` arrays of attached devices/links/OPP tokens, and device links. No persistent storage is used.

## Dependencies And Integration
Integrates with ACPI PM, generic PM domains, OF `power-domains`, device links, OPP required devices, PM clock initialization, and driver-core callback recalculation through `device_pm_check_callbacks()`.

## Risks And Test Signals
Risks include racing PM callbacks during attach/detach, leaking virtual PM-domain devices or device links on partial failure, changing PM domains after a device is bound, and incorrect behavior when `PD_FLAG_NO_DEV_LINK`, `PD_FLAG_DEV_LINK_ON`, or `PD_FLAG_REQUIRED_OPP` are combined. Test signals include multi-domain OF devices, attach-by-name/id failures, devres cleanup, OPP token cleanup, and bound-device domain-change warnings.
