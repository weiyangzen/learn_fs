# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-rx.h

Purpose: declares Vivid radio receiver file and ioctl operations.

Important APIs and types: declarations cover RDS `read`, `poll`, frequency band enumeration, hardware seek, tuner get, and tuner set operations.

Control flow: the Vivid radio RX video_device ioctl/file-operation tables reference these functions.

State and persistence: no header-owned state. Implementations read and mutate radio RX fields in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 tuner/frequency/file/poll types from including contexts.

Risks: this header exposes only operation functions; lifecycle and shared frequency handling live elsewhere, so callers must compose it with `vivid-radio-common.h`.

Test signals: compile coverage and V4L2 radio receiver ioctl/read tests validate the declarations.
