# sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-flags.h

Purpose: extends UAPI x86 processor flag definitions with kernel-only masks for VM86 support and CR3 address/PCID/no-flush handling.

Important APIs, types, and functions: includes `uapi/asm/processor-flags.h` and `mem_encrypt.h`, defines `X86_VM_MASK` based on `CONFIG_VM86`, and defines `CR3_ADDR_MASK`, `CR3_PCID_MASK`, and `CR3_NOFLUSH` differently for 64-bit and 32-bit builds. Under PTI it defines `X86_CR3_PTI_PCID_USER_BIT`.

Control flow: no executable code. Macros are used by CR3 read/write and TLB context switching paths.

State and persistence: no state is owned. The masks interpret or construct CR3 register values.

Dependencies and integration points: depends on SME encryption bit clearing through `__sme_clr()`, physical page masks, PCID support, LAM/CR3 layout comments, VM86, and PTI address-space ID selection.

Risks: CR3 contains physical address bits, PCID, optional no-flush bit, SME encryption bit, and LAM mode bits. Incorrect masking can flush unexpectedly, fail to flush when required, switch to the wrong page table, or include encryption/metadata bits in a physical address.

Test signals: TLB context switch tests with PCID on/off, PTI user/kernel PCIDs, SME/SEV boot, VM86 builds, CR3 physical address readback, and no-flush behavior during address-space switches.
