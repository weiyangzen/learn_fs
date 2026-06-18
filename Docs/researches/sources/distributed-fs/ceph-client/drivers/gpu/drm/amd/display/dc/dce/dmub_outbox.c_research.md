# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_outbox.c

Purpose: enables DMUB outbox1 notifications from firmware to the host CPU.

Important function: `dmub_enable_outbox_notification()` constructs a `DMUB_CMD__OUTBOX1_ENABLE` command, sets payload bytes to the command body size, enables the flag, and sends it synchronously with `dc_wake_and_execute_dmub_cmd()`.

Control flow: the function is single-purpose. It zeroes a `union dmub_rb_cmd`, fills header type/subtype/payload, sets `enable=true`, and waits for command completion.

State and persistence: no software state is stored here. The persistent effect is a firmware/DMUB configuration bit enabling outbox notifications until firmware or device state changes.

Dependencies and integration: depends on `dc.h`, `dc_dmub_srv.h`, `dmub_outbox.h`, and `dmub_cmd.h`. It integrates with DMUB service initialization paths that need firmware-originated notifications.

Risks: there is no null-check for `dmub_srv` or failure handling beyond lower-layer command execution. Payload size must match the firmware command definition. Test signals include command construction, DMUB service initialization with outbox enabled, notification delivery to x86, and behavior when DMUB service is absent or not ready.
