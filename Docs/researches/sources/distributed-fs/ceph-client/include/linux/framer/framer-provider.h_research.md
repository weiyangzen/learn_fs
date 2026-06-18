# sources/distributed-fs/ceph-client/include/linux/framer/framer-provider.h

## Purpose
This header defines the provider-side API for the generic framer framework. Framer providers create framer devices, expose operations, register OF providers, and notify status changes.

## APIs, types, and control flow
`struct framer_ops` supplies init/exit, power on/off, optional get-status, set-config, get-config, flags, and owner. `FRAMER_FLAG_POLL_STATUS` asks the core to poll `get_status()` and notify consumers on change if hardware cannot interrupt. `struct framer_provider` stores provider device, module owner, list node, and `of_xlate()` callback. Provider helpers create/destroy framers, devm-create, simple OF translate, register/unregister providers, and notify status changes. When `CONFIG_GENERIC_FRAMER` is disabled, creation/register calls return `ERR_PTR(-ENOSYS)` and notification/destruction are no-ops.

## State and dependencies
Provider state includes registered provider list entries, module ownership, framer device private data via `framer_set_drvdata()`, and optional polling work managed by the core. Dependencies include the consumer `framer.h`, device tree phandles, modules, lists, and error-pointer conventions.

## Integration, risks, and tests
Hardware framer drivers implement this side. Risks include provider unregister while consumers hold framers, missing owner assignment, polling without `get_status`, failing to notify status changes, and disabled-config `ERR_PTR` handling. Tests should cover create/destroy, devm cleanup, OF translation, provider unregister, polling flag behavior, notifier delivery, and disabled stubs.
