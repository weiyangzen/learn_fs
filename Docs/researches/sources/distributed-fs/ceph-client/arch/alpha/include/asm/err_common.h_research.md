# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/err_common.h

This header defines common Alpha error-log and machine-check packet constants. It provides SCB vector ids, machine-check disposition codes, error-log class/type ids, an `el_timestamp` union, and `struct el_subpacket` for system error, system event, halt, logout, Regatta, and raw packet headers.

There is no control flow. State is the layout of firmware/PAL error records parsed by machine-check handlers. Integration is with EV6/EV7/platform-specific error headers and machine-check code that walks logout frames. Risks are binary layout and bit-width drift; changing these structs can break decoding of firmware-provided records. Tests are machine-check parser builds, synthetic logout-frame decoding, and hardware/firmware error logs where available.
