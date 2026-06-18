# sources/distributed-fs/ceph-client/arch/sh/include/asm/Kbuild



Source read size: 6 lines, 170 bytes.



Purpose: SH asm header export/generation manifest for Kbuild.

Important APIs/types/functions: generates `syscall_table.h` and delegates several headers to generic implementations: `kvm_para.h`, `mcs_spinlock.h`, `parport.h`, and `text-patching.h`.

Control flow: during header generation Kbuild emits generated syscall table headers and creates generic wrapper links as needed.

State and persistence: build-time generated headers only.

Dependencies and integration points: affects users of architecture asm headers, syscall table generation, and generic kernel facilities.

Risks and test signals: missing generated or generic headers break architecture builds and exported UAPI assumptions. Test `headers_install` and SH defconfig builds.
