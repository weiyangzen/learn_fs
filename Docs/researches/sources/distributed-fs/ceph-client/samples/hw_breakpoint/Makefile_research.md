# sources/distributed-fs/ceph-client/samples/hw_breakpoint/Makefile

Purpose: builds the hardware breakpoint sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_HW_BREAKPOINT` to `data_breakpoint.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on perf hardware breakpoint support.

Risks: none in build file.

Test signals: enabling `CONFIG_SAMPLE_HW_BREAKPOINT` should compile the sample.
