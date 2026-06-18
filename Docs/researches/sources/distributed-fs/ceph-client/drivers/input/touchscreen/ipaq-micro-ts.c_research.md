<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ipaq-micro-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ipaq-micro-ts.c

Purpose: platform input driver for the iPAQ H3600 Atmel micro companion touchscreen subdevice. It exposes the companion chip's touchscreen messages as a simple single-touch `input_dev` with `ABS_X`, `ABS_Y`, and `BTN_TOUCH` ranges fixed to 0..1023.

Important APIs/types/functions: `struct touchscreen_data` stores the input device and parent `struct ipaq_micro`. `micro_ts_receive()` is the registered MFD callback and decodes 4-byte big-endian coordinate reports or zero-length release reports. `micro_ts_toggle_receive()` installs or removes `micro->ts` and `micro->ts_data` under `micro->lock`. `micro_ts_open()`, `micro_ts_close()`, `micro_ts_suspend()`, and `micro_ts_resume()` control callback registration, while `micro_ts_probe()` allocates and registers the input device.

Control flow: probe obtains the parent `ipaq_micro`, allocates state and input device, sets capabilities, registers the device, and stores driver data. The input open path enables message delivery; each MFD touchscreen message reports coordinates and touch state, then syncs. Close and suspend unregister the callback; resume reacquires the input mutex and only re-enables delivery when userspace has the input device open.

State and persistence: there is no persistent storage. Runtime state is limited to the input device and callback pointers in the shared `ipaq_micro` object. The callback pointer lifetime is protected by a spinlock, while input open/suspend coordination uses the input core mutex on resume.

Dependencies/integration: depends on the `ipaq-micro` MFD parent for transport and locking, Linux input core, platform driver binding `ipaq-micro-ts`, PM helpers, and big-endian coordinate decoding.

Risks and test signals: callback deregistration must race safely with parent MFD message dispatch and suspend. Test open/close cycles, suspend while open, resume while closed, zero-length release frames, malformed nonzero lengths, and removal of the parent MFD while the input node is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ipaq-micro-ts.c -->
