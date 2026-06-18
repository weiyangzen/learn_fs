# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-priv.h

Purpose: This private CEC core header shares internal macros and function prototypes among `cec-core.c`, `cec-adap.c`, and `cec-api.c`.

Important APIs, types, and functions: Macros include `dprintk()` for debug-level gated logging, `call_op()` and `call_void_op()` for registered-driver operation calls, `to_cec_adapter()` for devnode-to-adapter conversion, and `msg_is_raw()`. Prototypes cover monitor count helpers, debug status, adapter thread, adapter enable, internal physical/logical address setters, filehandle transmit, event queueing, and `cec_devnode_fops`.

Control flow and state: The macros centralize adapter-operation dispatch and ensure callbacks are skipped when the devnode is unregistered. The prototypes allow implementation files to call each other without exposing these helpers in public media headers.

State and persistence behavior: No state is stored here except the external `cec_debug` declaration. It shapes access to runtime adapter state through function boundaries.

Dependencies and integration points: Includes `<linux/cec-funcs.h>` and `<media/cec-notifier.h>`, and assumes public CEC structs are already available through included media headers in users. It is internal to the composite `cec.o`.

Risks and edge cases: `dprintk()` assumes a local variable named `adap`, so careless use in a scope without that symbol will not compile. `call_op()` returns `0` when a callback is absent or device is unregistered, which is correct for optional operations but can hide missing mandatory ops if misused.

Test signals: Compile coverage is the main signal. Runtime unregister tests should confirm callbacks stop after `devnode.unregistered` is set.
