# sources/distributed-fs/ceph-client/arch/arm/kernel/reboot.h

Purpose: declares restart/shutdown helpers shared by ARM kernel files that need to stop or restart the machine.

Important APIs/types/functions: small header exposing reboot-related prototypes, notably soft restart integration used by stacktrace/reboot users.

Control flow: no runtime flow.

State and persistence: no state.

Dependencies and integration: included by reboot-adjacent ARM kernel files to avoid local extern declarations.

Risks: because it is tiny, main risk is prototype drift from implementation. Test signals are compile coverage of files including it and reboot/kexec runtime paths.
