# sources/distributed-fs/ceph-client/samples/hung_task/Makefile

Purpose: builds the hung task sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_HUNG_TASK` to `hung_task_tests.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on sample Kconfig and debugfs APIs used by the module.

Risks: none in the Makefile; module is intentionally disruptive at runtime.

Test signals: enabling `CONFIG_SAMPLE_HUNG_TASK` builds `hung_task_tests.ko`.
