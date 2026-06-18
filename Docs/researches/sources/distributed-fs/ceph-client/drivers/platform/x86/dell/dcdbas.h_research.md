# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.h

Purpose: Shared firmware ABI definitions for DCDBAS and Dell SMBIOS SMM.

Important APIs/types/functions: SMI limits/constants, host-control action/type constants, port constants, `SMI_CMD_MAGIC`, `SMM_EPS_SIG`, packed `struct smi_cmd`, `struct apm_cmd`, `struct smm_eps_table`, `struct smi_buffer`, and SMI helper declarations.

Control flow/state/persistence: Header-only. Structures are written into DMA or firmware-provided buffers and consumed by firmware.

Dependencies/integration: Included by `dcdbas.c` and `dell-smbios-smm.c`.

Risks/test signals: Packing and field order are firmware ABI. Test through successful SMM calls and host-control operations; any structural edit needs firmware ABI review.
