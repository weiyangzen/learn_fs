# sources/distributed-fs/ceph-client/include/uapi/linux/phantom.h

Purpose: Defines ioctl ABI and register constants for the SensAble Phantom haptic device driver.

Important APIs/types/functions: Exports `struct phm_reg`, `struct phm_regs`, `PH_IOC_MAGIC`, legacy pointer-typed ioctls `PHN_GET_REG`, `PHN_SET_REG`, `PHN_GET_REGS`, `PHN_SET_REGS`, value-typed ioctls `PHN_GETREG`, `PHN_SETREG`, `PHN_GETREGS`, `PHN_SETREGS`, `PHN_NOT_OH`, control register constants, and `PHN_ZERO_FORCE`.

Control flow: Userspace reads or writes one register or a masked set of up to eight registers, optionally declares it is not OpenHaptics with `PHN_NOT_OH`, and uses control bits for amplifier switching, button status, and IRQ enablement.

State and persistence behavior: Runtime state lives in device registers and driver mode flags. `PHN_NOT_OH` changes driver update behavior to avoid unwanted device switch-offs for libphantom-style callers. Register values are hardware state, not file-backed persistence.

Dependencies and integration points: Depends on `<linux/types.h>` and ioctl macros from transitive UAPI context. Integrates with haptic device userspace libraries and the Phantom PCI/char driver.

Risks: The header contains both pointer-encoded and direct-struct ioctl variants, so compat handling is easy to get wrong. Register masks/counts must be bounded to eight values. Incorrect torque/control writes can affect physical haptic output.

Test signals: Exercise single and multi-register get/set paths, compare old and new ioctl encodings, test `PHN_NOT_OH` mode, validate mask/count bounds, read button/IRQ control state, and verify zero-force behavior.
