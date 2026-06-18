# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmware.h

Purpose: Defines VMware hypervisor command constants and inline hypercall helpers for x86 guests, including I/O-port, `vmcall`, `vmmcall`, TDX, and high-bandwidth transfer variants.

Important APIs/types/functions: Constants include `VMWARE_HYPERVISOR_PORT`, `_PORT_HB`, `VMWARE_HYPERVISOR_MAGIC`, command IDs such as `GETVERSION`, `GETHZ`, `GETVCPU_INFO`, and `STEALCLOCK`, and `VMWARE_CMD_MASK`. External fallbacks are `vmware_hypercall_slow()` and `vmware_tdx_hypercall()`. Inline helpers `vmware_hypercall1/3/4/5/6/7()` cover low-bandwidth calls with different output sets. `vmware_hypercall_hb_out()` and `_hb_in()` perform high-bandwidth `rep outsb`/`rep insb` transfers.

Control flow: Low-bandwidth helpers first route TDX guests to `vmware_tdx_hypercall()`. Before alternatives are patched in built-in code, they use `vmware_hypercall_slow()`. Otherwise inline asm emits the `VMWARE_HYPERCALL` alternative sequence, selecting I/O port, `vmcall`, or `vmmcall` based on CPU features. High-bandwidth helpers always use I/O-port string instructions and save/restore frame pointer around `%bp` use.

State and persistence: No kernel state is stored here. Hypercalls read/write hypervisor state and optionally write output registers into caller-provided `u32 *` destinations.

Dependencies and integration points: Uses x86 cpufeatures, alternatives, stringify/asm helpers, TDX guest detection, and unwind hints. Integrated with VMware platform detection, paravirtual clock/steal-time code, and guest drivers.

Risks: Register ABI is strict. Output pointer arguments must be valid and non-null where asm writes them. High-bandwidth calls are documented as unsupported for encrypted-memory guests; callers must check memory-encryption attributes. Early boot before alternatives patching must take the slow path.

Test signals: VMware guest boot tests, hypervisor version and clock commands, TDX guest hypercall tests, high-bandwidth transfer users, alternatives-patching coverage, and encrypted-memory guest negative tests.
