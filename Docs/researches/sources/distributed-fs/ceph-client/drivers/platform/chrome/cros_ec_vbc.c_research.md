<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_vbc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_vbc.c

## Purpose

This platform driver exposes the Chrome EC verified-boot NVRAM context to userspace through a binary sysfs attribute under the Chrome EC class device. It is a small bridge from sysfs reads/writes to `EC_CMD_VBNV_CONTEXT`.

## Important APIs, Types, And Functions

`vboot_context_read()` sends `EC_VBNV_CONTEXT_OP_READ` and returns the 16-byte `struct ec_response_vbnvcontext` block. `vboot_context_write()` accepts exactly the full context block and sends `EC_VBNV_CONTEXT_OP_WRITE`. `BIN_ATTR_RW(vboot_context, 16)` defines the binary attribute, and `cros_ec_vbc_probe()` creates the `vbc` sysfs group on the parent `struct cros_ec_dev` class device.

## Control Flow

The platform child named `cros-ec-vbc` probes after the Chrome EC MFD/device layer has a `cros_ec_dev` parent. Reads allocate a command buffer sized for the larger request/response payload, send the read operation through `cros_ec_cmd_xfer_status()`, copy the response block, and return its size. Writes validate that the supplied count is the full block size, populate `struct ec_params_vbnvcontext`, and send a no-response write command.

## State And Persistence

The driver keeps no cached vboot state. The persistent data is the EC-managed VBNV context. Every read fetches current EC contents; every write overwrites the entire block. Sysfs group lifetime is tied to platform-device probe/remove.

## Dependencies And Integration Points

It depends on the Chrome EC command ABI, `struct cros_ec_dev` parent data, and sysfs binary attributes. It is selected by the platform device ID `cros-ec-vbc`.

## Risks

The code ignores `pos` and `count` for reads and always returns the whole block, so partial sysfs binary reads rely on sysfs core behavior. Writes require exact full-size input and reject partial updates. Since VBNV affects verified boot, command failures or unintended writes can affect boot policy.

## Test Signals

Validate sysfs group creation/removal, 16-byte read size, exact-size write enforcement, EC command errors, and persistence of a written VBNV block across EC reads or reboot scenarios where firmware preserves VBNV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_vbc.c -->
