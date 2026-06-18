
# sources/distributed-fs/ceph-client/arch/x86/include/asm/coco.h

Purpose: x86 confidential-computing vendor and encryption-mask interface.

Important APIs and control flow: `enum cc_vendor` identifies none, AMD, or Intel. With `CONFIG_ARCH_HAS_CC_PLATFORM`, global `cc_vendor` and `cc_mask` are exported; `cc_get_mask()`, `cc_set_mask()`, `cc_mkenc()`, `cc_mkdec()`, and `cc_random_init()` support address encryption-bit conversion and random initialization. Without support, vendor is none, mask is zero, conversions are identity, and random init is a no-op.

State, dependencies, and risks: state is global confidential-computing vendor/mask configuration. Dependencies include platform detection, memory encryption code, and random initialization. Risks include applying the wrong C-bit mask to physical addresses, changing mask too late, and identity stubs hiding missing platform support. Test signals are SEV/TDX boot, encrypted/decrypted mapping tests, and guest memory acceptance paths.
