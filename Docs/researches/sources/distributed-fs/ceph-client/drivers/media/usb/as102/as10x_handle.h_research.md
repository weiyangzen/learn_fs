# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_handle.h

## Purpose
Declares the private bus-operation abstraction used by AS10x command and streaming code to stay independent of the concrete transport.

## Important APIs, types, and functions
`struct as102_priv_ops_t` contains callbacks for firmware packet upload, command send, command transfer, stream start/stop, target reset, register read/write, and endpoint 2 reads. It also defines register mode constants `REGMODE8`, `REGMODE16`, and `REGMODE32`.

## Control flow and state
No code runs here. At USB probe, `as102_dev_t.bus_adap.ops` is assigned to the USB implementation table. Higher-level AS102 code calls methods through this table for firmware, command, and stream operations.

## Dependencies and integration points
Forward-declares the bus adapter and device state, includes the command header, and is included by `as102_drv.h`. This is the integration boundary between AS10x protocol code and USB transport code.

## Risks and test signals
Risks are null optional callbacks and divergent semantics across possible transports. In this tree, USB supplies `upload_fw_pkt`, `xfer_cmd`, `as102_read_ep2`, `start_stream`, and `stop_stream`, while some callbacks remain unused. Test signals are all higher-level callers checking optional operations before use or being restricted to transports that supply them.
