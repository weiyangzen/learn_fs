# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_arm64.h

Purpose: Supplies arm64 implementations of the VMware hypercall/backdoor helpers used by `vmwgfx_msg.c`. It emulates VMware x86 I/O-port semantics through register conventions and a trap instruction sequence.

Important APIs/types/functions: Defines VMware port constants, hypervisor magic, high-bandwidth direction flags, and x86 I/O encoding constants for register `x7`. Inline helpers include `vmware_hypercall1()`, `vmware_hypercall5()`, `vmware_hypercall6()`, `vmware_hypercall7()`, shared `vmware_hypercall_hb()`, and direction-specific `vmware_hypercall_hb_out()`/`_in()`.

Control flow: Each helper loads arm64 registers `x0` through the needed argument count with magic, command, payload arguments, port number, cookies, and encoded I/O metadata. The inline assembly executes `mrs xzr, mdccsr_el0`, which the VMware hypervisor intercepts. Output registers are copied into caller-provided `u32 *` slots, matching the x86 helper API expected by common message code.

State and persistence: The header has no persistent state. It is active only when `__aarch64__` is defined and otherwise compiles to an empty include guard. All state is transient register input/output.

Dependencies and integration points: Used by `vmwgfx_msg.c` for RPCI and mksGuestStat hypercalls on arm64. It must remain API-compatible with `<asm/vmware.h>` on x86. Risks include register constraint mistakes, truncating 64-bit return registers into `u32` outputs, incorrect direction/port flag encoding, and sensitivity to compiler inline-asm behavior. Test signals: arm64 builds, RPCI open/send/receive/close, high-bandwidth in/out payloads, mksstat one-argument calls, and comparison with x86 behavior.
