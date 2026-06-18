# sources/distributed-fs/ceph-client/arch/arm64/lib/copy_from_user.S

Purpose: implements `__arch_copy_from_user`, copying bytes from a user pointer into kernel memory and returning bytes not copied.

Important APIs/types/functions: `__arch_copy_from_user`, load/store wrapper macros, `USER_CPY` MOPS copy operations, included `copy_template.S`, and exception fixups `9996/9997/9998`.

Control flow: sets `end` and original source, then instantiates the common copy template with user loads and kernel stores. MOPS uses forward/main/end copy instructions when available. On success it returns zero. On faults it adjusts the destination pointer using MOPS residual state or copy-template fault labels, tries a single-byte load/store if no progress was made, then returns `end - dst`.

State and persistence: writes only copied bytes into kernel destination. No persistent state. Fault paths may leave a partially copied destination, consistent with raw usercopy semantics.

Dependencies/integration: used by raw copy-from-user machinery; depends on `asm-uaccess.h`, exception-table `EX_TYPE_UACCESS_CPY`, `copy_template.S`, cache-line alignment constants, and ARM64 MOPS alternatives.

Risks: user fault direction metadata must identify a read-side uaccess fault, otherwise kernel destination faults could be incorrectly fixed up. The final one-byte retry affects exact residual behavior. Overlap is not a supported contract for usercopy.

Test signals: full copy, zero-length copy, faults at first/middle/last byte, destination unchanged after first-byte fault, MOPS and generic paths, and hardened usercopy/KASAN interaction.
