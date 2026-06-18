# sources/distributed-fs/orangefs/src/io/flow/flowproto-dump-offsets/module.mk.in

Purpose: build fragment for the dump-offsets diagnostic protocol.

Important content: sets `DIR := src/io/flow/flowproto-dump-offsets` but comments out both `LIBSRC` and `SERVERSRC` additions for `flowproto-dump-offsets.c`.

Integration: confirms this diagnostic protocol is not built by default, consistent with source-level API drift.

Risks/test signals: uncommenting this fragment without updating the source will likely break builds. Build tests should keep it disabled unless a compatibility update is made.
