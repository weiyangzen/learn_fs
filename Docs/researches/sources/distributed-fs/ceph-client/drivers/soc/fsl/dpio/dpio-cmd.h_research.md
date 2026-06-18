# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-cmd.h

Purpose: DPAA2 Management Complex wire command definitions for DPIO objects.

Important APIs/types/macros: defines DPIO API version 4.2, command ID encoding through `DPIO_CMD()`, command IDs for open/close/enable/disable/get-attr/reset/stashing-destination/API-version, and packed command/response parameter layouts `dpio_cmd_open`, `dpio_rsp_get_attr`, and `dpio_stashing_dest`.

Control flow and integration: included by `dpio.c` and `dpio-driver.c` so MC commands are encoded consistently. The response layout maps MC words to `struct dpio_attr` fields in host endian form.

State and persistence: no state; it defines the serialized command ABI between kernel and MC firmware.

Dependencies and risks: depends on `linux/fsl/mc.h` command header conventions and little-endian MC fields. Risks are ABI drift from MC firmware or incorrect field sizes/masks, especially `DPIO_CHANNEL_MODE_MASK` and portal offset fields.

Test signals: successful `dpio_get_api_version()`, `dpio_get_attributes()` returning sane portal offsets/version/clock, and MC command failures when IDs or versioning mismatch.
