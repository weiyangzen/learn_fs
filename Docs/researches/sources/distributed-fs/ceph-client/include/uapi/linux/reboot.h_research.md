<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/reboot.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/reboot.h

Purpose: defines magic values and command constants for the `reboot(2)` system call.

Important APIs and types: `LINUX_REBOOT_MAGIC1`, `LINUX_REBOOT_MAGIC2*` authenticate reboot calls. Command constants include restart, halt, CAD on/off, power off, restart2, software suspend, and kexec.

Control flow: privileged userspace calls `reboot(magic1, magic2, cmd, arg)`; the kernel validates magic values and capability, then dispatches to restart, halt, poweroff, CAD state change, kexec, or suspend logic.

State and persistence: reboot commands affect global system power/restart state. CAD setting and kexec image state are runtime; reboot/poweroff changes platform state and terminates current kernel state.

Dependencies and integration points: integrates with sys_reboot, init systems, kexec, hibernation, architecture restart/poweroff handlers, and watchdog/power-management code.

Risks and test signals: risks include accidental destructive reboot, wrong magic compatibility, privilege bypass, and command-specific arch/platform behavior. Test command validation, capability checks, restart2 argument handling, kexec loaded/unloaded paths, and CAD toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/reboot.h -->
