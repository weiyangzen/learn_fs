<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/watchdog.h

Purpose: Solaris-compatible SPARC hardware-watchdog ioctl ABI.

Important APIs and control flow: includes generic Linux watchdog UAPI, then defines `WIOCSTART`, `WIOCSTOP`, and `WIOCGSTAT` plus status bits for freerun, expired, running, stopped, and serviced states.

State, dependencies, and risks: state is hardware watchdog timer enablement, expiry, and interrupt service status. Dependencies include Linux watchdog ioctl base and Sun board watchdog drivers. Risks are ABI overlap with generic watchdog commands and userspace relying on Solaris-compatible status bits. Test signals are watchdog start/stop/status ioctls, timeout expiry tests, and generic watchdog compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/watchdog.h -->
