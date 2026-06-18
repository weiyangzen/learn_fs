# sources/distributed-fs/orangefs/src/io/flow/flowproto-bmi-cache/module.mk.in

Purpose: build fragment for the BMI-cache flow protocol.

Important content: sets `DIR := src/io/flow/flowproto-bmi-cache` and adds `flowproto-bmi-cache-server.c` to `SERVERSRC`.

Integration: this protocol is server-only in the build, matching its Trove/cache server dependencies.

Risks/test signals: because the protocol is not added to `LIBSRC`, client/library builds will not include it. Build tests should verify server configurations define the matching static flowproto macro if this source is expected in `static_flowprotos`.
