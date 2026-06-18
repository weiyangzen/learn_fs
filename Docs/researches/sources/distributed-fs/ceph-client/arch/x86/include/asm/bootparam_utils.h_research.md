
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bootparam_utils.h

Purpose: boot parameter sanitizer for bootloaders that fail to zero unknown fields.

Important APIs and control flow: `sanitize_boot_params()` checks `boot_params->sentinel`; when set, it creates a zeroed static scratch object, copies only known-safe fields listed through `BOOT_PARAM_PRESERVE()`, then overwrites the original structure. The preserve list includes screen/APM/tboot/IST/disk/system/EFI/e820/EDD/secure boot/header and confidential-computing blob fields.

State, dependencies, and risks: state is the incoming `struct boot_params`. Dependencies are boot parameter layout and `offsetof`/field sizes. Risks include missing a field that a broken bootloader validly initialized, preserving a field that should be cleared, and static scratch lifetime in unusual reentry contexts. Test signals include kexec/bootloader compatibility tests and boot logs with sentinel-triggered sanitization.
