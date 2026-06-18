## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_pfvf.c

Purpose: Implements Gen4 PF-side PF/VF communication over dedicated PF2VM and VM2PF CSRs.

Important APIs/functions: `adf_gen4_init_pf_pfvf_ops()` installs PF operations. Offset helpers return `ADF_GEN4_PF2VM_OFFSET(i)` and `ADF_GEN4_VM2PF_OFFSET(i)`. Interrupt helpers enable, disable, and atomically disable pending VM2PF interrupts using `VM2PF_SOU`/`VM2PF_MSK`. `adf_gen4_pfvf_send()` encodes a message with a 6-bit type and 24-bit payload, writes it with `ADF_PFVF_INT`, and polls for the remote side to clear the interrupt bit. `adf_gen4_pfvf_recv()` reads the CSR, filters spurious interrupts, clears the interrupt bit to ACK, and decodes the generic message.

Control flow and state: A CSR mutex serializes sends. Unlike Gen2, Gen4 has separate PF2VM/VM2PF registers and no shared in-use half-word protocol. Interrupt mask state is maintained in PMISC registers.

Dependencies/integration: Depends on Gen4 hardware-data offsets, PF/VF utility encoding, PF protocol enablement, mutexes, and poll helpers. Only PF ops are provided in this file.

Risks and test signals: ACK timeout and interrupt-mask race behavior are the main risks. Tests should validate message encoding bounds, spurious interrupt handling, pending interrupt disabling under concurrent VF events, and communication behavior across all VFs.
