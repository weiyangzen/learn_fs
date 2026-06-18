<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/misc_44x.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/misc_44x.S

Purpose: implements low-level PPC44x byte I/O helpers that temporarily switch data accesses to address space 1.

Important APIs/types/functions: global symbols `as1_readb` and `as1_writeb` are declared in `44x.h`. Both save MSR, set `MSR_DS`, synchronize, perform `lbz` or `stb`, restore MSR, and return.

Control flow: callers pass an MMIO byte address, the helper switches data-space context only for the single byte load/store, then restores the original MSR with sync/isync barriers around transitions.

State and persistence: temporarily mutates MSR data-space bit; no persistent software state. The write helper has hardware MMIO side effects.

Dependencies and integration: depends on PPC assembly macros, MSR bit definitions, and board code that needs AS1 access.

Risks and test signals: missing barriers or failure to restore MSR would corrupt later memory accesses; arguments follow PowerPC ABI registers. Test AS1 read/write users on 44x hardware and inspect disassembly for correct clobber expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/misc_44x.S -->
