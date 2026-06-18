# sources/distributed-fs/ceph-client/include/linux/comedi/comedilib.h

Purpose: This header exposes a small in-kernel Comedi library API for opening Comedi devices and performing simple digital I/O operations.

Important APIs/types/functions: APIs are `comedi_open_from`, inline `comedi_open`, `comedi_close_from`, inline `comedi_close`, `comedi_dio_get_config`, `comedi_dio_config`, `comedi_dio_bitfield2`, `comedi_find_subdevice_by_type`, and `comedi_get_n_channels`.

Control flow: Kernel users open a fake `/dev/comediN` path, use the returned `struct comedi_device` for DIO config/bitfield operations or subdevice discovery, then close it. Inline wrappers pass `-1` as the caller source to the `_from` variants.

State and persistence behavior: Open/close manipulate Comedi device references/use counts in the implementation. DIO calls mutate subdevice channel direction or state. The header itself stores no state.

Dependencies and integration points: It forward-declares `struct comedi_device` and integrates in-kernel consumers with Comedi core without going through userspace file descriptors.

Risks: The path parser expects `/dev/comediN`-style names. Callers must close opened devices. DIO operations require valid subdevice and channel numbers and an attached device.

Test signals: In-kernel Comedi users, open/close refcount tests, invalid path tests, DIO config/bitfield tests, and subdevice discovery checks validate behavior.
