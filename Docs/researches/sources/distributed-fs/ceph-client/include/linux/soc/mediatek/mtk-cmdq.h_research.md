# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-cmdq.h

Purpose: This MediaTek header exposes the Command Queue/GCE packet-building API used by display, multimedia, and power drivers to program hardware command buffers.

Important APIs/types/functions: It defines address helpers, SPR indices, `enum cmdq_logic_op`, `struct cmdq_operand`, `struct cmdq_client_reg`, and `struct cmdq_client`. Enabled builds export mailbox client creation/destruction, packet create/destroy, register writes by subsystem or physical address, masked writes, secure-register read/write helpers, memory move, wait/acquire/clear/set event, polling, logic/assign operations, address polling, absolute/relative jumps, and end-of-command. Disabled builds return `-EINVAL`, `-ENOMEM`, or no-op stubs as appropriate.

Control flow: A driver creates a CMDQ mailbox client, allocates a packet, appends write/poll/event/logic/jump commands, submits through the mailbox implementation, then destroys the packet and client. `cmdq_client_reg` lets consumers abstract MMIO versus physical-address command encoding.

State and persistence: Packets hold command-buffer state; GCE threads hold SPRs, events, and execution state. Hardware register writes persist in target IP blocks.

Dependencies and integration: Includes mailbox client and MediaTek CMDQ mailbox definitions. Integrates with DRM display pipelines, MMSYS, mutex, power domains, and multimedia engines.

Risks and test signals: Command encoding mistakes can write wrong registers or hang a GCE thread. Event waits can deadlock if producers are missing. Test disabled stubs, packet buffer sizing, masked writes, event sequencing, timeout/error paths, and display atomic commits using CMDQ.
