# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/rx_csi_defs.h

Purpose: defines the CSI RX frontend register map, widths, lane-enable encodings, error-handling bits, interrupt bits, lane status bits, and packet/header bit positions.

Important APIs/types/functions: macros define register indices for enable, enabled lanes, error handling, status, lane HS/LP status, clock/data lane delay counters, register count calculation, lane-count encodings, error handling bits, IRQ bit numbers, and packet/header fields.

Control flow: no runtime flow. CSI RX host accessors use these constants to read and program frontend control/status registers.

State and persistence: constants only.

Dependencies and integration: included by `csi_rx_private.h` and tied to CSI frontend hardware.

Risks and test signals: IRQ definitions replace older Arasan frontend definitions, so mixed hardware paths can misinterpret status. Tests should verify lane-enable programming, delay counter access for each lane, and IRQ/status decoding during real or simulated CSI error injection.
