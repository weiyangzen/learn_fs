# sources/distributed-fs/ceph-client/drivers/firmware/efi/test/efi_test.h

Purpose: Defines the userspace ABI for the EFI runtime test driver. It documents the packed request structures and ioctl command numbers used by `/dev/efi_test`.

Important APIs/types/functions: ABI structures include `efi_getvariable`, `efi_setvariable`, `efi_getnextvariablename`, `efi_queryvariableinfo`, `efi_gettime`, `efi_settime`, `efi_getwakeuptime`, `efi_setwakeuptime`, `efi_getnexthighmonotoniccount`, `efi_querycapsulecapabilities`, and `efi_resetsystem`. IOCTLs use `_IOW`, `_IOR`, and `_IOWR` with command group `p` and numbers `0x01` through `0x0C`.

Control flow: No executable flow. `efi_test.c` copies these packed structures from userspace and dispatches based on the ioctl definitions.

State and persistence behavior: No state is stored here. The structs expose pointers to status fields and runtime-service inputs that can cause persistent EFI variable writes, time changes, or resets when consumed by the driver.

Dependencies and integration points: Depends on `linux/efi.h` for EFI types. Any userspace test program must match these layouts exactly, including pointer width and packed layout of the running kernel ABI.

Risks and test signals: ABI changes would break existing test tools. Packed pointer-containing structs make 32-bit compatibility and native word-size assumptions important. Test signals include ioctl compilation against this header, native userspace round trips, and compat-mode review if the driver is exposed on mixed ABI systems.
