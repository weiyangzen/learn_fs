# sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/kcomedilib_main.c

## Purpose
This file implements a small GPL-exported COMEDI kernel library for other kernel modules. It lets kernel code open COMEDI devices by `/dev/comediN`, safely close them, issue DIO configuration and bitfield instructions, find subdevices, and query channel counts.

## Important APIs, Types, And Functions
Exported APIs are `comedi_open_from()`, `comedi_close_from()`, `comedi_dio_get_config()`, `comedi_dio_config()`, `comedi_dio_bitfield2()`, `comedi_find_subdevice_by_type()`, and `comedi_get_n_channels()`. Internal helper `comedi_do_insn()` validates attachment, subdevice index, subdevice usability, chanlist, and busy state before dispatching `INSN_BITS` or `INSN_CONFIG`. Link tracking is handled by `kcomedilib_set_link_from_to()` and `kcomedilib_clear_link_from_to()` using `kcomedilib_to_from[COMEDI_NUM_BOARD_MINORS][COMEDI_NUM_BOARD_MINORS]`.

## Control Flow
`comedi_open_from()` parses `/dev/comediN`, obtains a COMEDI device reference, checks attachment under `attach_lock`, and records an open edge from one device minor to another. The edge insertion walks the reverse link graph under a mutex to reject loops and caps duplicate edge counts at 255. On failure the device reference is dropped. `comedi_close_from()` removes one edge and releases the device reference.

DIO helpers construct `struct comedi_insn` objects and call `comedi_do_insn()`. `comedi_dio_bitfield2()` additionally handles base-channel shifting for subdevices with up to 32 channels because most drivers ignore `insn->chanspec` for `INSN_BITS`. Query helpers use `attach_lock` to read subdevice metadata safely.

## State And Persistence
The main persistent state is the static link-count matrix, protected by `kcomedilib_to_from_lock`. It records concurrent kernel opens between COMEDI minors and prevents dependency cycles. Subdevice busy state is temporarily set in `comedi_do_insn()` while an instruction executes.

## Dependencies And Integration Points
The file depends on COMEDI core internals (`comedi_dev_get_from_minor`, `comedi_dev_put`, `comedi_check_chanlist`, subdevice callbacks, locks, and busy state) and exports symbols for GPL kernel modules. It integrates with standard COMEDI instruction semantics rather than user-space file descriptors.

## Risks And Edge Cases
The graph loop check assumes the existing matrix is loop-free. If callers mismatch `from` values between open and close, link counts can become inaccurate. `comedi_do_insn()` has comments noting incomplete lock and instruction-length checks. Only `INSN_BITS` and `INSN_CONFIG` are supported. Base-channel shifting in `comedi_dio_bitfield2()` is only corrected for `n_chan <= 32`.

## Test Signals
Useful tests include opening invalid names and minors, refusing open loops, duplicate open count saturation, close decrement behavior, DIO config/query dispatch, bitfield base-channel shifting, busy subdevice rejection, and attach/detach races around `attach_lock`.
