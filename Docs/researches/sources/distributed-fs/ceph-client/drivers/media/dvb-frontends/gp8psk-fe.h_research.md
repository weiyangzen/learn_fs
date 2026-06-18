# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.h

### Purpose
`gp8psk-fe.h` defines the Genpix command protocol constants, firmware revision helpers, parent operation callbacks, and frontend attach entry point.

### Important APIs, Types, And Functions
The header enumerates USB request IDs such as `TUNE_8PSK`, `GET_SIGNAL_LOCK`, `SET_LNB_VOLTAGE`, and `SEND_DISEQC_COMMAND`; configuration bit masks like `bmDCtuned`; advanced modulation IDs; `GP8PSK_FW_VERS()`; `struct gp8psk_fe_ops`; and `gp8psk_fe_attach()`.

### Control Flow
No executable control flow exists. The implementation uses these constants to form parent USB control transfers.

### State, Persistence, And Dependencies
No state is stored in the header. It depends on Linux integer types and a visible `bool` type in includers.

### Integration Points
USB bridge code includes this header to issue firmware commands and attach the demodulator frontend with transport callbacks.

### Risks
The command constants are a hardware/firmware ABI. Mismatched firmware revisions, wrong request directions, or incorrect modulation IDs directly break tuning and SEC control.

### Test Signals
Compile parent users, verify firmware version decoding, and test each command ID against known Genpix firmware revisions.
