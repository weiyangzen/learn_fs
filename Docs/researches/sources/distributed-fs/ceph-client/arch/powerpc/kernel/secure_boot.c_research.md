# sources/distributed-fs/ceph-client/arch/powerpc/kernel/secure_boot.c

Purpose: PowerPC secure-boot and trusted-boot status discovery from firmware device-tree properties.

Important APIs/types/functions: `get_ppc_fw_sb_node()`, `is_ppc_secureboot_enabled()`, `arch_get_secureboot()`, and `is_ppc_trustedboot_enabled()`.

Control flow: the helper first searches for an IBM secureboot-compatible node (`ibm,secureboot`, `ibm,secureboot-v1`, or `ibm,secureboot-v2`). Secure boot is enabled when that node has `os-secureboot-enforcing`; if absent, the root `ibm,secure-boot` property is read and values greater than one enable it. Trusted boot similarly checks `trusted-enabled` on the secureboot node, falling back to root `ibm,trusted-boot` greater than zero. Each public function logs enabled/disabled status.

State and persistence: no kernel state is stored; results are derived each call from the live device tree and returned as booleans.

Dependencies and integration points: integrates with generic Linux `arch_get_secureboot()` and PowerPC secure-boot consumers. Relies on OF node reference management and `linux/secure_boot.h` semantics.

Risks: firmware property naming/version differences directly affect security reporting. The fallback thresholds (`secure-boot > 1`, `trusted-boot > 0`) encode platform ABI assumptions; incorrect firmware values can under-report enforcement. Repeated calls log status each time.

Test signals: boot with secureboot v1/v2 nodes and legacy root properties, confirm `/sys/kernel/security` or module-signature policy consumers see expected `arch_get_secureboot()` results, and verify node reference handling with OF debug checks.
