# sources/distributed-fs/ceph-client/tools/testing/selftests/memory-hotplug/config

Purpose: kernel config fragment for memory hotplug tests.

Important APIs/types/functions: requests memory hotplug, hotremove, notifier error injection, and the memory notifier error injection module.

Control flow: none.

State and persistence: build configuration only.

Dependencies and integration points: enables sysfs memory block state changes and debugfs notifier injection used by the script.

Risks: test coverage still requires actual removable memory blocks.

Test signals: configured kernels should expose memory block `state`/`removable` and notifier error injection.
