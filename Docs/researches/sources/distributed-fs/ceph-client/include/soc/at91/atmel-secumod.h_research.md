# sources/distributed-fs/ceph-client/include/soc/at91/atmel-secumod.h

Purpose: defines the minimal Atmel security module register interface needed to check backup/security RAM readiness.

Important APIs and types: `AT91_SECUMOD_RAMRDY` is the RAM ready register offset and `AT91_SECUMOD_RAMRDY_READY` is the ready bit.

Control flow: platform or security-module code maps the syscon/MMIO region and polls or reads `RAMRDY` before using secure/backup RAM.

State and persistence: state is a hardware readiness bit. The header stores no software state and does not persist data.

Dependencies and integration points: uses `BIT()` from common kernel macros through includer context and integrates AT91 security/backup RAM drivers.

Risks and test signals: risks are missing the required include context for `BIT()`, using the RAM before readiness is asserted, and SoC variants with different offsets. Test compile in AT91 configs, boot-time RAM readiness polling, timeout/failure handling, and secure RAM access after readiness.
