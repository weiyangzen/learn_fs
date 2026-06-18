
# sources/distributed-fs/ceph-client/arch/x86/include/asm/emergency-restart.h

Purpose: declaration for immediate machine restart on x86.

Important APIs and control flow: declares `machine_emergency_restart()`, used by panic/reboot code when normal shutdown paths are unavailable or unsafe.

State, dependencies, and risks: state is hardware reset pathway outside this header. Dependencies include reboot implementation and platform reset mechanisms. Risks include failing to reset on some firmware/platforms or bypassing device quiesce intentionally. Test signals are reboot/panic tests and platform watchdog/reset coverage.
