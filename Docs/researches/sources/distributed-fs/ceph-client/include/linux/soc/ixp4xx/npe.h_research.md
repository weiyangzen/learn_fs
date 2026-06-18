# sources/distributed-fs/ceph-client/include/linux/soc/ixp4xx/npe.h

Purpose: This header defines the public API for IXP4xx Network Processing Engines, including register layout, handle structure, firmware loading, and message exchange.

Important APIs/types/functions: `struct npe_regs` describes NPE control/status/mailbox registers. `struct npe` carries ID, MMIO regs, and device state. `npe_name` indexes `npe_names`. APIs include `npe_running`, `npe_send_message`, `npe_recv_message`, `npe_send_recv_message`, `npe_load_firmware`, `npe_request`, and `npe_release`.

Control flow: A consumer requests an NPE by ID, loads firmware if needed, checks running state, exchanges mailbox messages, and releases the handle during teardown.

State and persistence: NPE firmware and runtime state live in the hardware engine. The handle tracks the selected NPE and mapped registers while requested.

Dependencies and integration: Integrates with IXP4xx Ethernet/crypto/network acceleration drivers, firmware loading, and platform MMIO code.

Risks and test signals: Firmware/message protocol mismatches can wedge the NPE. Test request/release reference handling, firmware load errors, message timeout paths, and packet processing on each engine.
