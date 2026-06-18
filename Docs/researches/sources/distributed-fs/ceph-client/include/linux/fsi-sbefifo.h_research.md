# sources/distributed-fs/ceph-client/include/linux/fsi-sbefifo.h

Purpose: declares the FSI SBEFIFO client interface for sending big-endian command streams to IBM Self-Boot Engine FIFO devices and parsing command status.

Important APIs and types: command constants cover OCC SRAM put/get and SBE FFDC retrieval; `SBEFIFO_MAX_FFDC_SIZE` caps failure data capture size. `sbefifo_submit()` sends a `__be32` command buffer and returns a `__be32` response buffer with in/out length. `sbefifo_parse_status()` validates response status for a command and returns payload length.

Control flow: a client builds a command stream, submits it to the target device, then calls the status parser to separate protocol status from payload bytes. OCC transport code can use this lower layer for OCC SRAM commands.

State and persistence: no persistent kernel state is declared. The device/firmware FIFO state is external and transient across command execution.

Dependencies and integration points: depends on `struct device` and big-endian integer types; integrates with FSI SBEFIFO drivers and OCC/diagnostic clients.

Risks and test signals: risks include incorrect response length units, endian mistakes, not bounding FFDC retrieval, and command/status mismatch. Tests should cover successful commands, status error responses, malformed short responses, max FFDC reads, and concurrent or timeout behavior in provider code.
