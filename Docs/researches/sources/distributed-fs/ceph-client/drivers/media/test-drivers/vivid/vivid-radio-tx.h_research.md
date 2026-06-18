# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-tx.h

Purpose: declares Vivid radio transmitter file and ioctl operations.

Important APIs and types: declarations cover RDS `write`, `poll`, `VIDIOC_G_MODULATOR`, and `VIDIOC_S_MODULATOR` handlers.

Control flow: radio TX file-operation and ioctl tables call these functions for userspace interaction.

State and persistence: no header-owned state. Implementation mutates TX fields and shared RDS generator state in `struct vivid_dev`.

Dependencies and integration points: requires V4L2 file, poll, and modulator types from including contexts.

Risks: the header does not expose shared frequency helpers; users must combine it with `vivid-radio-common.h`.

Test signals: compile coverage and radio transmitter write/modulator ioctl tests validate this boundary.
