<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/epapr_hcalls.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/epapr_hcalls.h

Purpose: Defines the ePAPR hypercall token and return-code ABI for PowerPC guests.

Important APIs/types/functions: `EV_*` hypercall numbers, vendor IDs, `EV_BYTE_CHANNEL_MAX_BYTES`, `_EV_HCALL_TOKEN()`, `EV_HCALL_TOKEN()`, and ePAPR return codes `EV_SUCCESS` through `EV_BUFFER_OVERFLOW`.

Control flow: Guests compose hypercall tokens from vendor ID and call number, issue the hypercall through architecture code, and interpret numeric return codes.

State and persistence: No state owned; constants describe hypervisor interface state and error outcomes.

Dependencies and integration points: Used by KVM paravirtual code, ePAPR guests, byte channels, interrupt-controller calls, and idle/doorbell paths.

Risks: Token encoding and return codes are ABI. Incorrect vendor IDs collide with private hypercalls.

Test signals: KVM/ePAPR guest boot, byte-channel tests, interrupt hcall tests, and headers compile under GPL/BSD consumers.

Source read size: 99 lines, 4274 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/epapr_hcalls.h -->
