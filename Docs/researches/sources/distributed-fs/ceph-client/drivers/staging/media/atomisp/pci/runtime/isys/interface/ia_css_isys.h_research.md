# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/interface/ia_css_isys.h

Purpose: central public interface for CSS input-system initialization, RX configuration/IRQ handling, format conversion, virtual stream construction, and ISYS resource managers.

Important APIs/types: `ia_css_isys_init/uninit`, port conversion, CSI RX stream register/unregister, compressed/stream format conversion, alignment calculation, RX interrupt/configure functions, virtual stream create/destroy/calculate_cfg, and resource-manager init/acquire/release APIs for CSI RX LUTs, IBUF, DMA channels, and stream2mmio SIDs.

Control flow/state: callers initialize ISYS once, create/calculate streams, register them with CSI RX tracking, configure RX/virtual input-system blocks, then destroy streams and uninit resources.

Dependencies/integration: wraps `input_system.h`, stream/input port formats, `system_global.h`, and `ia_css_isys_comm.h`. Implemented across `isys_init.c`, `rx.c`, `virtual_isys.c`, and resource-manager files.

Risks: broad API exposes low-level resource acquisition and requires strict acquire/release pairing. Many implementation paths rely on assertions and static global resource tables.

Test signals: ISP2400 vs ISP2401 init, resource exhaustion/release, all MIPI format mappings, compression mappings, RX IRQ translation/clear, and virtual stream metadata paths.
