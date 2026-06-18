# sources/distributed-fs/ceph-client/drivers/sh/intc/userimask.c

Purpose: optional hardware-assisted userspace interrupt masking support for supported SH interrupt blocks.

Important APIs and functions: `register_intc_userimask` maps a 4 KiB user-mask register page and records it globally. Sysfs attribute `userimask` under the `intc` bus root uses `show_intc_userimask` and `store_intc_userimask` to read/write the mask level, writing the required key byte and level field. `userimask_sysdev_init` creates the sysfs file late after the INTC bus exists.

Control flow: platform code registers the hardware address. Late init exposes sysfs. Userspace writes a level lower than the default INTC priority; the register then masks lower-priority hard IRQs for userspace driver scenarios.

State and dependencies: global `uimask` mapping and the `intc_subsys` bus root. Dependencies include MMIO, sysfs/device model, default priority from INTC core, and CPU support. Risks include only one global mapping, no unmap path, strict priority validation, direct raw register writes, and exposing a privileged tuning knob. Test signals are successful registration log, sysfs file creation, readback of written levels, rejection of invalid high levels, and hardware interrupt masking behavior.
