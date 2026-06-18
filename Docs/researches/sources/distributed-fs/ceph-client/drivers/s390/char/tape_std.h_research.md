# sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.h

Purpose: declares standard tape command constants, sense-byte masks, common tape operation prototypes, and the small s390 tape-type enum.

Important APIs/types/functions: defines `MAX_BLOCKSIZE`, CCW opcodes including `READ_FORWARD`, `WRITE_CMD`, `WRITETAPEMARK`, `ASSIGN`, `LOCATE`, `MODE_SET_DB`, and `READ_BLOCK_ID`; defines sense masks such as `SENSE_WRITE_PROTECT`, `SENSE_DRIVE_ONLINE`, and `SENSE_RECORD_SEQUENCE_ERR`; declares all `tape_std_*` helpers.

Control flow: no executable flow; the constants drive request construction in `tape_std.c` and sense interpretation in `tape_3490.c`.

State and persistence: no state. Constants describe hardware command and status layout.

Dependencies and integration: included by tape core, standard command builder, and 3490 discipline; prototypes expect `struct tape_device` and `struct tape_request` from `tape.h`.

Risks: constants are hardware ABI; wrong values break real tape operations or error handling. `MAX_BLOCKSIZE` bounds IDAL buffer allocation and userspace-visible MTSETBLK behavior.

Test signals: compile-time consumers, tape command execution on supported hardware/emulation, sense-code injection against 3490 recovery, and MTSETBLK boundary tests.
