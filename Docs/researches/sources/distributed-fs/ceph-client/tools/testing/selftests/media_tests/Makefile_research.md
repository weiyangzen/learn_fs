# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/Makefile

Purpose: builds media controller and video device manual stress tools.

Important APIs/types/functions: adds `-I../ $(KHDR_INCLUDES)`, declares `TEST_GEN_PROGS := media_device_test media_device_open video_device_test`, and includes `../lib.mk`.

Control flow: build-only; the generated programs require explicit device arguments at runtime.

State and persistence: none.

Dependencies and integration points: Linux media and V4L2 uapi headers.

Risks: shell helper scripts in the folder are not listed as `TEST_PROGS` here, so they are auxiliary/manual unless invoked externally.

Test signals: successful compilation of three tools.
