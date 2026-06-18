# sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.h

Purpose: declares the bus-independent TEA5777 helper interface and state structure used by radio drivers that provide raw register transport.

Important APIs and types: `struct radio_tea5777_ops` contains `write_reg` and `read_reg` callbacks for the TEA5777 6-byte write and 3-byte read registers. `struct radio_tea5777` embeds V4L2 file/video/control state, current band/frequency/audmode, seek limits, read/write register caches, quirk flags, callback pointer, private data, and card/bus strings. Exported functions are `radio_tea5777_init`, `radio_tea5777_exit`, and `radio_tea5777_set_freq`.

Control flow: consumers allocate a containing device structure, fill `v4l2_dev`, `ops`, `private_data`, capability flags such as `has_am` and `write_before_read`, and identity strings, then call `radio_tea5777_init`. The helper registers the V4L2 radio node and later uses callbacks to program hardware. Consumers call `radio_tea5777_exit` during teardown.

State and persistence: all helper state is caller-owned and mutable at runtime. Cached register values and seek bounds are volatile and represent the last helper view of hardware.

Dependencies and integration points: includes V4L2 core headers and Linux radio frequency definitions. It is consumed by `radio-shark2.c` in this subset and can be reused by other bus wrappers.

Risks: the header exposes the full mutable helper structure rather than an opaque handle, so consumers can accidentally corrupt invariants. Fixed `card[32]` and `bus_info[32]` buffers require careful string copying. The defined `TEA575X_FMIF` and `TEA575X_AMIF` names are legacy/misleading for TEA5777.

Test signals: compile coverage for consumers, structure initialization by `radio-shark2.c`, callback invocation ordering, string truncation behavior, and helper init/exit under probe failure.
