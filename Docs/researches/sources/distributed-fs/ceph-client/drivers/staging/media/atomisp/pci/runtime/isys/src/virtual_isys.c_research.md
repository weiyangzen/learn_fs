# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/virtual_isys.c

Purpose: builds virtual ISP2401 input-system stream handles and calculates hardware configs for CSI/pixelgen input ports, stream2mmio, IBUF controller, DMA, and metadata channels.

Important functions/state: public `ia_css_isys_stream_create`, `destroy`, and `calculate_cfg`; private resource acquire/release wrappers; channel/input-port creation/destruction; config calculators for PRBS, CSI frontend/backend, stream2mmio, IBUF, DMA, DMA ports; `calculate_stride`; and packet-type classification.

Control flow: stream creation zeroes the handle, sets metadata/id/linkage, allocates input-port resources, allocates main channel resources, then optionally allocates metadata channel. Failures unwind prior allocations. Config calculation fills channel config, optional metadata config, and input-port config, then marks stream/config valid.

State/persistence: stream handles contain allocated resource IDs and buffer addresses; global resource managers own allocation tables. Calculated configs are caller-owned and later programmed into input-system hardware.

Dependencies/integration: ISYS resource managers, CSI RX constants, input-system virtual stream structs, ISP vector/DDRx constants, and debug tracing.

Risks: broad manual unwind logic must remain exact to avoid leaked SIDs/IBUF/DMA/LUT entries. Metadata handling shares input-port/backend resources and changes stores-per-frame. Alignment/stride math must agree with `frame.c`/DMA expectations.

Test signals: create/destroy with sensor, PRBS, metadata on/off, resource exhaustion at each allocation step, offline vs online IBUF/DMA config, raw-packed destination stride, compression/custom data type backend config, and valid flags after calculation.
