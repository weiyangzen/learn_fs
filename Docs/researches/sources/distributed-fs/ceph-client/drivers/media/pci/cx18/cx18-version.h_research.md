# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-version.h

Centralizes cx18 driver identity macros: `CX18_DRIVER_NAME` is `"cx18"` and `CX18_VERSION` is `"1.5.1"`.

It has no runtime state or control flow. Integration is through module metadata, logs, or user-visible driver identification.

Risk is stale version/name reporting after code changes. Test signals are compile coverage and module/device information exposing the expected name/version.
