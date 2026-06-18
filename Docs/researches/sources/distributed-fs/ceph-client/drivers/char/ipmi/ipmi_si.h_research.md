# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si.h

Purpose: This header is the internal contract between IPMI SI discovery/probe code and the base SI transport engine. It describes SI types, address spaces, register I/O callbacks, IRQ setup hooks, and add/remove/init/shutdown entry points for KCS, SMIC, BT, and platform-specific SI providers.

Important APIs, types, and functions: `enum si_type` names invalid, KCS, SMIC, and BT state-machine types. `enum ipmi_addr_space` distinguishes I/O port and memory-mapped register spaces. `struct ipmi_match_info` carries SI type matches. `struct si_sm_io` provides `inputb`/`outputb` callbacks, register mapping metadata, address source/info, setup/cleanup callbacks, IRQ callbacks, slave address, match info, and backing device. Externs include `ipmi_si_add_smi`, `ipmi_si_irq_handler`, IRQ helper functions, removal helpers, hardcode/hotmod/platform init and shutdown functions, optional PCI/LS2K/PARISC hooks, and generic port/memory setup.

Control flow: Discovery modules fill a `struct si_sm_io`, then call `ipmi_si_add_smi`. The SI engine chooses low-level KCS/SMIC/BT handlers, calls `io_setup`, probes the BMC, registers the SMI with the core message handler, and uses the callbacks in this structure for every state-machine byte access and IRQ lifecycle operation.

State and persistence behavior: The header itself is stateless. Runtime state is carried by each `si_sm_io` instance and copied into `struct smi_info` in `ipmi_si_intf.c`. Address source and address info become visible through sysfs and `ipmi_get_smi_info`.

Dependencies and integration points: It includes IPMI public headers, interrupt support, and platform-device support. It is consumed by SI core, hardcode/hotmod/platform discovery, LS2K, PCI, PARISC, and low-level I/O setup code.

Risks and edge cases: The state machine assumes `inputb`/`outputb` implement IPMI register semantics correctly, including regspacing/regsize/regshift handling. Optional setup functions must fill cleanup callbacks to avoid leaks. Conditional hooks compile to no-ops when platform support is disabled, so callers depend on the header's stubs for init/shutdown ordering.

Test signals: Compile configurations with and without PCI, LS2K, and PARISC; add SMIs using I/O and memory spaces; IRQ setup and cleanup; removal by device and by address/type; and `get_smi_info` propagation of source metadata.
