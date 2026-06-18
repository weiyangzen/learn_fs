# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/Makefile

## Purpose

`ibmvscsi/Makefile` is the Kbuild fragment for IBM virtual SCSI drivers. It conditionally builds the classic IBM virtual SCSI adapter object and the IBM virtual Fibre Channel object based on kernel configuration symbols.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SCSI_IBMVSCSI) += ibmvscsi.o` adds the IBM virtual SCSI driver object when `CONFIG_SCSI_IBMVSCSI` is enabled as built-in or module.
- `obj-$(CONFIG_SCSI_IBMVFC) += ibmvfc.o` adds the IBM virtual Fibre Channel driver object when `CONFIG_SCSI_IBMVFC` is enabled.
- The file also carries the `GPL-2.0-only` SPDX tag expected by kernel source policy.

## Control Flow and State

There is no runtime control flow or persisted state in this file. Kbuild evaluates the `obj-*` assignments during kernel build generation and includes the requested objects in either built-in archives or module builds depending on each configuration symbol's value.

## Dependencies and Integration Points

The file integrates with the Linux kernel build system under `drivers/scsi/Makefile` and the Kconfig symbols that expose IBM virtual SCSI and IBM virtual Fibre Channel support. The actual driver behavior lives in the corresponding C sources; this Makefile only controls compilation inclusion.

## Risks

- Incorrect config symbol names would silently drop driver objects from builds.
- Adding multi-object drivers here would require converting each target to `<module>-y` style lists; the current two one-line targets assume single composite objects already defined by their source names.
- Build coverage depends on both symbols being tested as built-in and module where supported.

## Test Signals

- `make M=drivers/scsi/ibmvscsi` or an equivalent in-tree build with `CONFIG_SCSI_IBMVSCSI=m` should produce `ibmvscsi.ko`.
- A build with `CONFIG_SCSI_IBMVFC=m` should produce `ibmvfc.ko`.
- Built-in configurations should include the objects in the relevant `built-in.a` without missing-object Kbuild warnings.
