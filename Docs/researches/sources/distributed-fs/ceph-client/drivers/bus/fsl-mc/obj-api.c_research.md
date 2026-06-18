# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/obj-api.c

Purpose: provides generic open, close, and reset wrappers for FSL MC object types. It lets drivers operate on many MC object classes without embedding object-specific command IDs in each caller.

Important APIs: `fsl_mc_obj_open()` maps an object type string such as `dpni`, `dpio`, `dpmcp`, or `dpdmai` to its open command ID, sends the open command, and returns the firmware token. `fsl_mc_obj_close()` sends generic close with a token. `fsl_mc_obj_reset()` sends generic reset with a token.

Control flow: `fsl_mc_get_open_cmd_id()` searches a static type-to-command table. Open encodes the selected command ID with no token, stores the object ID in little-endian command params, calls `mc_send_command()`, and reads the returned token from the header. Close/reset encode generic command IDs with the supplied token and send them.

State and persistence: no local persistent state. The returned token represents a firmware-side open object handle and remains valid until close/reset semantics are invoked by callers.

Dependencies and integration: depends on command IDs and `struct fsl_mc_obj_cmd_open` from `fsl-mc-private.h`, public command header helpers, and `mc_send_command()`. It is exported for MC client drivers and management paths that need generic object control.

Risks: type strings must match firmware object descriptors exactly; unknown types return `-ENODEV`. A leaked token means an object may stay open in MC firmware. Test signals include open/close/reset across every listed object type, unknown-type failure, token extraction, and MC status/error propagation.
