<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.h

Purpose: Defines the internal BMI method contract and generic operation/address structures shared by all transports.

Important APIs, types, and functions: `struct bmi_method_ops` is the transport vtable: initialize/finalize, info, memory allocation, send/receive, list I/O, tests, context open/close, cancel, reverse lookup, and address range query. `struct bmi_method_addr` wraps method-specific address data. `struct bmi_method_unexpected_info` carries unexpected arrivals. `struct method_op` stores generic operation state: op id, send/recv direction, tag, error, size accounting, address, context, queue links, hash link, method-private data, list I/O fields, and event id. Constants include `BMI_MAX_CONTEXTS`, `BMI_MAGIC_NR`, and `BMI_METHOD_FLAG_NO_POLLING`.

Control flow and state: Header only, but it establishes queueable state used by both BMI core and methods. `method_op` instances move among method queues and are discoverable through the id generator.

Dependencies and integration points: Pulls in `quicklist`, `bmi-types`, and `pint-event`. Every BMI method must provide a compatible `bmi_method_ops` table and honor the semantics expected by `bmi.c`.

Risks and test signals: Optional vtable members are sometimes assumed present by top-level BMI calls, so method implementations need clear coverage for unsupported operations. `BMI_MAX_CONTEXTS` is fixed at 16. Tests should exercise method activation, context creation, list I/O, cancellation, and unsupported callback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.h -->
