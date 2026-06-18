# sources/distributed-fs/orangefs/src/io/flow/flowproto-template/module.mk.in

Purpose: build fragment for the example flow protocol.

Important content: sets `DIR := src/io/flow/flowproto-template` but comments out `LIBSRC` and `SERVERSRC` additions.

Integration: keeps the skeleton protocol out of production builds.

Risks/test signals: uncommenting requires first updating `flowproto-template.c` to the current `flowproto_ops` API. Build tests should verify template remains disabled in normal configurations.
