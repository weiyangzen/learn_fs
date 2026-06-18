<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/Kbuild

**Purpose:** Declares generated and generic header exports for the MIPS asm include tree.

**Important APIs/types/functions:** `generated-y` lists generated syscall table and syscall count headers for n32, n64, and o32 ABIs. `generic-y` imports generic headers such as qspinlock, qrwlock, user, kvm_para, and text-patching.

**Control flow:** Kbuild uses this metadata when preparing architecture headers.

**State, dependencies, integration:** Integrates generated syscall headers with UAPI/build products and falls back to asm-generic implementations for selected facilities.

**Risks and test signals:** Missing generated headers break syscall builds; wrong generic fallback changes ABI-visible behavior. Test `headers_install` and full MIPS build for all three ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/Kbuild -->
