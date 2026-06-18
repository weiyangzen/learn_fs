# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.c

Purpose: low-level DPAA2 DPIO Management Complex command wrapper library.

Important APIs and functions: `dpio_open()` obtains an object token; `dpio_close()` releases it; `dpio_enable()`, `dpio_disable()`, and `dpio_reset()` send lifecycle commands; `dpio_get_attributes()` decodes portal offsets, portal ID, channel mode, priorities, QBMan version, and clock; `dpio_set_stashing_destination()` programs CPU cluster stashing; `dpio_get_api_version()` queries MC API version.

Control flow: each function builds `struct fsl_mc_command`, fills command header with `mc_encode_cmd_header()`, writes little-endian params where needed, calls `mc_send_command()`, and decodes response fields on success.

State and persistence: no local persistent state. Tokens returned by `dpio_open()` are used by callers as MC session state. Commands mutate DPIO object state in MC firmware/hardware.

Dependencies and integration: depends on `linux/fsl/mc.h`, `dpio.h`, and `dpio-cmd.h`. It is consumed primarily by `dpio-driver.c`.

Risks and test signals: risks include MC ABI field mismatch, endian errors, and callers using invalid tokens after close. Test signals are probe success through open/reset/get-attr/enable/close, API version matching expected 4.2, and failure handling from `mc_send_command()`.
