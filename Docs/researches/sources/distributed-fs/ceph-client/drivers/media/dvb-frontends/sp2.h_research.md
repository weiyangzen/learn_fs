<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.h

## Purpose
`sp2.h` is the public interface for boards integrating the CIMaX SP2/SP2HF Common Interface driver. It defines platform configuration and declares the EN50221 callback functions implemented by `sp2.c`.

## Important APIs, Types, And Functions
`struct sp2_config` supplies the `dvb_adapter`, a device-specific `ci_control` callback pointer, and a private callback context. The header declares the CA memory/control callbacks and slot operations that are also installed into `struct dvb_ca_en50221`: attribute memory read/write, CAM control read/write, reset, shutdown, transport-stream enable, and poll status.

## Control Flow
Board code passes `struct sp2_config` as I2C client platform data. During probe, `sp2.c` copies these fields into `struct sp2` and binds the declared functions into DVB CA core operations. External users generally do not call the functions directly except through the CA framework.

## State And Persistence
No state is stored in the header. The callback pointers and private context must remain valid for the lifetime of the I2C client and CA device.

## Dependencies And Integration Points
The header depends on `media/dvb_ca_en50221.h`. It is the contract between board-specific CI access code and the generic SP2 I2C driver.

## Risks And Test Signals
The untyped `void *ci_control` field hides the actual callback signature, so a board can compile with an incompatible pointer and fail at runtime. The API is single-slot oriented even though the hardware naming references module A/B. Test signals are successful platform-data handoff, CA callback invocation with the expected private pointer, and CAM transactions that match the board's low-level memory mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2.h -->
