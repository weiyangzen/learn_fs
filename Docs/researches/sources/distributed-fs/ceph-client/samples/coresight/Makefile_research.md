# sources/distributed-fs/ceph-client/samples/coresight/Makefile

Purpose: builds the CoreSight syscfg sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_CORESIGHT_SYSCFG` to `coresight-cfg-sample.o` and adds an include path for `drivers/hwtracing/coresight`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on CoreSight syscfg internal headers being available in the kernel source tree.

Risks: include path reaches into driver internals, so sample build is sensitive to CoreSight header movement.

Test signals: enabling `CONFIG_SAMPLE_CORESIGHT_SYSCFG` should compile `coresight-cfg-sample.ko`.
