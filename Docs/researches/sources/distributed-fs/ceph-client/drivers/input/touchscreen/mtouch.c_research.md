<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mtouch.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mtouch.c

Purpose: serio driver for MicroTouch/3M RS-232 touchscreens using the Format Tablet protocol. It assembles serial bytes into fixed five-byte touch frames or delimited response frames and reports single-touch coordinates.

Important APIs/types/functions: `struct mtouch` stores input, serio port, parser index, byte buffer, and physical path. `mtouch_interrupt()` receives bytes from serio. `mtouch_process_format_tablet()` decodes five-byte data frames using status/touch bits and 14-bit coordinates. `mtouch_process_response()` consumes `0x01 ... 0x0d` response frames but does not interpret them. `mtouch_connect()` allocates and registers the input device; `mtouch_disconnect()` tears it down.

Control flow: the serio core matches `SERIO_RS232/SERIO_MICROTOUCH`, connect allocates state/input, opens the serio port, and registers input. Each received byte is appended to `data[idx]`. If the first byte has the tablet status bit, a five-byte frame reports X, inverted Y, and touch state. If the first byte starts a response, bytes are consumed until carriage return or max length. Unknown first bytes are logged and leave synchronization to future bytes.

State and persistence: state is only the in-progress packet index and buffer. No device configuration is sent and no persistent state is stored.

Dependencies/integration: depends on serio bus/protocol IDs, Linux input core, RS-232 transport, and standard module serio registration.

Risks and test signals: parser resynchronization is minimal; a bad first byte can cause repeated debug logs until `idx` is reset by a recognized path. Test noisy serial streams, incomplete frames, response overflow, disconnect while bytes arrive, Y inversion, and coordinate range calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mtouch.c -->
