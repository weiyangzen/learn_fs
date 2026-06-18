<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw.h

Purpose: centralizes shared MEI wire protocol constants, HBM command IDs, version feature gates, extended-header formats, bus message headers, and host/firmware message structures used by all MEI backends and HBM code.

Important APIs and types: defines global timeouts, `HBM_MAJOR_VERSION`/`HBM_MINOR_VERSION`, feature-version constants for PGI, dynamic clients, immediate enum, disconnect-on-timeout, events, fixed-address clients, OS version, DMA rings, vtags, GSC, capabilities, and client DMA. It declares HBM command IDs, `enum mei_hbm_status`, connection/disconnection status enums, extended header types and structs (`mei_ext_hdr`, `mei_ext_meta_hdr`, vtag and GSC headers), `struct mei_msg_hdr`, and many packed HBM request/response structures such as host start/stop, enum, properties, client connect/disconnect, flow control, PG, notify, DMA setup, capability, and client DMA commands.

Control flow: not executable except inline helpers for extended-header traversal/length. Runtime code uses these layouts to serialize/deserialize all HBM and data messages. `mei_msg_hdr` drives common read/write slot framing, routing by host/ME addresses, completion bits, DMA ring flag, and extended-header flag.

State and persistence: no storage. It defines protocol bytes that are exchanged with firmware and therefore must stay stable.

Dependencies and integration: included by HBM, hardware backends, TXE regs, and common device/client code. It also includes public `<linux/mei.h>` for externally visible MEI structures.

Risks: packed wire layout changes are high risk because firmware consumes exact binary formats. Extended-header length is expressed in dwords and traversal assumes valid firmware lengths after interrupt-side validation. Version feature constants gate optional behavior; incorrect thresholds can enable unsupported protocol commands.

Test signals: build-time `BUILD_BUG_ON` size checks in HBM code, runtime HBM negotiation, vtag/GSC extended-header message tests, DMA-ring/client-DMA tests, and fuzz/fault injection of malformed message headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw.h -->
