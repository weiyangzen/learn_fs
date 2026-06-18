# sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.h

Purpose: Private libthermal header exposing handler internals and low-level netlink helper prototypes to implementation files.

Important APIs/types/functions: `struct thermal_handler` stores status fields, `thermal_ops *`, a message pointer, three netlink sockets, and three callback objects. `struct thermal_handler_param` packages a handler plus user argument for callbacks. Declares subscribe/unsubscribe/connect/disconnect/send helpers.

Control flow: Implementation files include this header to access handler internals and pass handler-param bundles into libnl callbacks.

State and persistence: Defines process memory layout for the opaque public handler. Sockets and callbacks are owned by init/exit routines.

Dependencies/integration: Includes libnl headers for netlink/genl/mngt/ctrl and is paired with public `thermal.h`.

Risks: Because internals are shared across implementation files, lifecycle invariants are distributed. Fields `done`, `error`, and `msg` are present but not meaningfully used by the current low-level implementation. No ownership annotations for sockets/callbacks.

Test signals: Compile all thermal implementation files against this header; lifecycle behavior tested through thermal init/exit and netlink helper tests.
