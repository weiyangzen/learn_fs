# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_drv.h

## Purpose
Defines the shared AS102 driver state, public registration functions, constants, and cross-file declarations used by the DVB glue and USB transport.

## Important APIs, types, and functions
`struct as10x_bus_adapter_t` contains the USB device, bus mutex, command token storage, transaction id `cmd_xid`, command/response pointers, and `as102_priv_ops_t` method table. `struct as102_dev_t` contains board name, bus adapter, kref, eLNA config, DVB adapter/frontend/demux/dmxdev, a timer handle, synchronization semaphore, DMA stream storage, stream count, and up to `MAX_STREAM_URB` URBs. It declares `as102_dvb_register()` and `as102_dvb_unregister()`.

## Control flow and state
This header structures the persistent device lifetime. The USB probe allocates `as102_dev_t`, initializes the bus adapter token pointers, USB device pointer, kref, and stream buffers. The DVB layer mutates `streaming` and DVB objects. The bus command lock serializes firmware and control traffic through the shared command/response buffers.

## Dependencies and integration points
Includes USB, DVB demux/frontend/dmxdev, `as10x_handle.h`, `as10x_cmd.h`, and `as102_usb_drv.h`. Exports `as102_usb_driver` for the module entry in `as102_drv.c` and `elna_enable` for frontend/stream control behavior.

## Risks and test signals
The shared command/rsp buffers make locking mandatory; any new caller must hold `bus_adap.lock`. Lifetime depends on kref and USB disconnect ordering. Test signals include no use-after-free under open file descriptors, correct URB array bounds using `MAX_STREAM_URB`, and clean unregister after active streaming.
