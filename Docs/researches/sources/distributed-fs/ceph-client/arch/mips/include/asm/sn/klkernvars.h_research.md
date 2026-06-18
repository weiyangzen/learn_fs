<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klkernvars.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klkernvars.h

Purpose: Defines the SN kernel variables handoff block used to communicate mapped-kernel physical bases and NASIDs.

Important APIs/types/functions: Offsets `KV_MAGIC_OFFSET`, `KV_RO_NASID_OFFSET`, `KV_RW_NASID_OFFSET`, magic `KV_MAGIC`, and `kern_vars_t` with magic, read-only/read-write NASIDs, padding, and physical base addresses.

Control flow: Mapped-kernel setup reads the KLDIR kernel-vars block, verifies magic, and uses the RO/RW NASIDs and base addresses to translate mapped kernel addresses to physical/K0 addresses.

State and persistence: Persistent state is firmware/kernel handoff data for mapped-kernel placement.

Dependencies and integration points: Depends on SN types and is consumed by `mapped_kernel.h` and hub/node setup code.

Risks: Offsets are used by assembly or firmware, so layout changes can break mapped-kernel boot. Invalid NASIDs or bases corrupt address translation.

Test signals: Mapped-kernel boot on SN, magic validation, and address translation tests are useful.

Source read size: 29 lines, 614 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klkernvars.h -->
