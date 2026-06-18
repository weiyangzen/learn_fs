# sources/distributed-fs/orangefs/src/io/flow/module.mk.in

Purpose: build fragment for the core flow subsystem.

Important content: sets `DIR := src/io/flow`, adds `flow.c` and `flow-ref.c` to both `LIBSRC` and `SERVERSRC`, and comments out `flow-queue.c`.

Integration: core flow APIs are compiled for both library and server; endpoint-pair mapping support is available; disabled queue code matches the apparent missing queue-link drift.

Risks/test signals: if queue-based scheduling is needed, `flow-queue.c` must be reconciled with `flow_descriptor`. Build tests should verify static protocol fragments provide the concrete ops referenced by compile-time macros.
