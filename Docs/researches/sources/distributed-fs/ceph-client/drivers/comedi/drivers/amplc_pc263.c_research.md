# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc263.c Research

Implements a legacy Comedi driver for the Amplicon PC263 16-channel reed-relay output board.

`pc263_do_insn_bits()` updates relay outputs through two byte registers and returns the software state. `pc263_attach()` requests a 2-byte I/O region, allocates one DO subdevice, initializes its metadata, and reads the initial relay state. `pc263_boards[]` and `amplc_pc263_driver` provide manual attach metadata.

Attach validates the configured base address, creates a single `COMEDI_SUBD_DO`, and reads both relay output bytes into `s->state`. Instruction writes use `comedi_dio_update_state()` and only write hardware when requested bits changed. Relay state persists in hardware and Comedi subdevice state; there is no interrupt, command, or reset path.

Dependencies are legacy Comedi APIs, raw I/O ports, and `comedi_legacy_detach`. Risks are small but include base-region configuration, byte ordering for channels 0-7 versus 8-15, and preserving initial relay state. Tests should cover attach region validation, initial state readback, masked bit updates, output byte ordering, and no unintended writes when the mask is zero.
