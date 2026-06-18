# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_nic.c

Purpose: Provides LiquidIO NIC-facing helpers that convert network data and control operations into Octeon instruction queue submissions.

Important APIs, types, and functions: `octeon_alloc_soft_command_resp()` wraps a prebuilt `union octeon_instr_64B` in a soft command, adds response metadata (`rflag`, RDP, response pointer, status word), and sets expiry. `octnet_send_nic_data_pkt()` posts a data command with optional doorbell suppression for `xmit_more`. `octnic_alloc_ctrl_pkt_sc()` allocates a soft command for NIC control commands, copies/swaps the command payload, appends user-defined data, prepares an OPCODE_NIC control instruction, and initializes completion. `octnet_send_nic_ctrl_pkt()` gates control commands while offline, sends the soft command, optionally returns immediately for no-sleep multicast/devflags commands, otherwise waits for completion and runs a callback.

Control flow: Data packets are already encoded by `octeon_nic.h` helpers and go straight to `octeon_send_command()`. Control packets allocate from the soft-command pool, enter IQ 0, move through ordered response processing, then complete or time out.

State and persistence: Uses transient soft-command DMA buffers, command response lock/state, completion status, and caller-done lifetime markers. No durable persistence.

Dependencies and integration: Integrates `octeon_iq`, `response_manager`, `octeon_main` wait helpers, and LiquidIO firmware opcodes. It is called by netdev setup, ethtool, link, multicast, and feature-control code.

Risks: Offline gating permits only RX control, so callers must handle failures. Immediate-return control commands rely on response-manager cleanup after `caller_is_done`. Endian swapping of command and UDD payloads must match firmware contract.

Test signals: Control send success/failure, offline rejection, no-sleep command lifetime, response timeout, callback invocation, xmit_more doorbell behavior, and CN23XX vs CN6XXX response field placement.
