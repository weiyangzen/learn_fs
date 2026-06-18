# sources/distributed-fs/ceph-client/include/linux/secure_boot.h

Purpose: `secure_boot.h` provides a small architecture hook for querying platform secure boot status.

Important APIs/types/functions: `arch_get_secureboot()` is declared when `CONFIG_HAVE_ARCH_GET_SECUREBOOT` is enabled and otherwise returns false inline. The API returns true only when platform secure boot is enabled; disabled or unsupported platforms report false.

Control flow: Security or integrity code calls `arch_get_secureboot()` during policy setup or runtime decisions. The architecture implementation supplies firmware-specific detection; the generic fallback avoids conditional compilation at call sites.

State and persistence behavior: The header owns no state. The returned value reflects platform firmware or architecture state and is expected to be stable after boot.

Dependencies and integration points: It depends on architecture support and integrates with lockdown, module signature policy, kexec restrictions, and integrity subsystems that may strengthen policy under secure boot.

Risks: A false fallback means generic callers must not treat false as proof that the platform lacks secure boot support unless the architecture config is known. Architecture implementations must avoid late firmware calls that can sleep or fail unpredictably in early boot.

Test signals: Build with and without `CONFIG_HAVE_ARCH_GET_SECUREBOOT`, boot secure-boot enabled and disabled systems, and verify downstream policy decisions such as lockdown/module-loading behavior.
