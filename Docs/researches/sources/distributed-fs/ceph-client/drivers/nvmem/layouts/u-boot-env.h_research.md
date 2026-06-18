# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/u-boot-env.h

Purpose: Small shared header for U-Boot environment layout parsing.

Important APIs/types/functions: defines `enum u_boot_env_format` with `U_BOOT_FORMAT_SINGLE`, `U_BOOT_FORMAT_REDUNDANT`, and `U_BOOT_FORMAT_BROADCOM`; declares `u_boot_env_parse(struct device *, struct nvmem_device *, enum u_boot_env_format)`.

Control flow: there is no runtime flow; it is a compile-time contract between the layout parser and providers that need to parse the same image formats.

State/persistence: no state. The enum values are used as OF match data cast through pointer-sized fields.

Dependencies/integration: included by the layout driver and MTD-backed `u-boot-env` provider. It assumes the including translation unit has visible declarations for `struct device` and `struct nvmem_device`.

Risks: enum ordering is part of the local match-data convention, so changing it would alter existing compatible handling unless all users are updated together.

Test signals: compile coverage for both users and format-specific parser tests cover this header's contract.
