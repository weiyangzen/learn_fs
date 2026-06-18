<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppdev.h

Purpose: defines the Linux parallel-port userspace character-device ABI for claiming ports, data/control/status I/O, negotiation modes, IRQ/timeouts, and IEEE 1284 device ID retrieval.

Important APIs and types: mode constants include compatibility, nibble, byte, ECP, EPP, and vendor-specific flags. `struct ppdev_frob_struct` controls bit-mask updates, and ioctl constants such as `PPCLAIM`, `PPRELEASE`, `PPSETMODE`, `PPRDATA`, `PPWDATA`, `PPRCONTROL`, `PPFCONTROL`, `PPRSTATUS`, `PPNEGOT`, `PPGETTIME/PPSETTIME`, `PPGETMODES`, `PPGETPHASE`, `PPGETFLAGS/PPSETFLAGS`, and `PPGETDEVICEID` define the control surface.

Control flow: userspace opens `/dev/parportN`, claims exclusive access, selects protocol/mode, performs data/control/status operations or negotiation, and releases the port. Kernel parport code arbitrates claims and maps ioctls to hardware or parport driver methods.

State and persistence: state is transient per file/port claim: selected mode, phase, flags, timeout, IRQ use, and hardware register values. No durable state is stored by the header.

Dependencies and integration points: uses ioctl encoding and integrates with parport core, IEEE 1284 devices, printers, scanners, GPIO-like parallel hardware, and legacy userspace drivers.

Risks and test signals: risks include unsafe hardware access, missing `PPCLAIM`, ioctl size compatibility, timing-sensitive EPP/ECP negotiation, and concurrent access. Test claim/release exclusivity, mode negotiation, control-bit frobbing, timeout behavior, IRQ waits, and device-id retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppdev.h -->
