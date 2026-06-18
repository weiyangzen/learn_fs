# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvsi.h

Purpose: Defines the Hypervisor Virtual Serial Interface packet format and library state used by hvc/tty serial console implementations.

Important APIs, types, and functions: Defines packet header types, control/query verbs, modem-control masks, `HVSI_MAX_OUTGOING_DATA`, `HVSI_VERSION`, packet structs (`hvsi_header`, `hvsi_data`, `hvsi_control`, `hvsi_query`, `hvsi_query_response`), `struct hvsi_priv`, and hvsilib open/close/read/write/establish/get/put APIs.

Control flow: The library buffers incoming bytes, parses packet headers and lengths, sends data/control/query packets through supplied `get_chars`/`put_chars` callbacks, negotiates protocol establishment, and exposes modem-control updates to tty code.

State and persistence: `struct hvsi_priv` stores input buffer cursor/length, sequence number, open/established/console flags, modem-control state, tty pointer, callbacks, and terminal number. It is runtime tty state only.

Dependencies and integration points: Integrates hvc console structures, tty state, pSeries hypervisor terminal I/O, and endian packet fields.

Risks: Packet lengths are small and must be validated against the 255-byte input buffer. Sequence numbers and establishment state affect protocol correctness. Modem-control masks are sparse.

Test signals: Protocol establishment, data packets at maximum payload, split/partial input packets, control/query responses, DTR changes, close protocol, and console versus normal tty open paths.
