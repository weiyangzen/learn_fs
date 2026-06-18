## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_pfvf.c

Purpose: Implements Gen2 PF/VF mailbox communication over a shared 32-bit CSR, including interrupt mask management, send/receive encoding, compatibility behavior, and PF/VF ops initialization.

Important APIs/functions: `adf_gen2_init_pf_pfvf_ops()` and `adf_gen2_init_vf_pfvf_ops()` populate `adf_pfvf_ops`. Static helpers map PF and VF CSR offsets, enable/disable VF2PF interrupts, atomically disable pending VF interrupts, convert 16-bit messages between PF2VF and VF2PF halves, and track the Gen2 in-use pattern. `adf_gen2_pfvf_send()` serializes with a CSR mutex, writes message plus interrupt bit, polls for ACK, handles notification collisions, and retries. `adf_gen2_pfvf_recv()` validates the interrupt bit, ignores legacy non-system messages, decodes `pfvf_message`, conditionally clears in-use bits, and ACKs by clearing the local interrupt bit.

Control flow and state: The shared CSR carries both directions, so local and remote offsets determine ownership and ACK semantics. Persistent state is external: CSR mutexes, compatibility version, PF/VF info, and interrupt masks. Notification messages intentionally preserve the in-use marker to detect collisions.

Dependencies/integration: Depends on `adf_pfvf_msg`, PF/VF protocol helpers, CSR polling, mutexes, PMISC mapping, and SR-IOV conditionals. PF ops wire VF interrupt management; VF ops only need offset and send/recv hooks.

Risks and test signals: Collision handling, legacy compatibility, and interrupt-mask races are the main risks. Tests should stress simultaneous PF/VF notifications, ACK timeout/retry paths, legacy user message filtering, `disable_pending_vf2pf_interrupts()` races, and compat versions before/after fast ACK.
