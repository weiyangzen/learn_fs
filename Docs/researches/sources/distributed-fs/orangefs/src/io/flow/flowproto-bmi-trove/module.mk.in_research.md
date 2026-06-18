# sources/distributed-fs/orangefs/src/io/flow/flowproto-bmi-trove/module.mk.in

Purpose: build fragment for the multiqueue BMI/Trove flow protocol.

Important content: sets `DIR := src/io/flow/flowproto-bmi-trove`, adds `flowproto-multiqueue.c` to both `LIBSRC` and `SERVERSRC`.

Integration: makes the protocol available to both library/client-side and server-side builds, with Trove-specific sections compiled conditionally by source macros.

Risks/test signals: build configurations must consistently define static-flowproto and Trove-support macros so `flow.c` can reference `fp_multiqueue_ops` and endpoint directions compile as expected. Build tests should cover client-only and server/Trove-enabled variants.
