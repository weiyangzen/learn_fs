# sources/distributed-fs/ceph-client/include/linux/pse-pd/pse.h

Purpose: defines the Power Sourcing Equipment controller interface for Ethernet PoDL and Clause 33 PoE/PSE management, including driver callbacks, ethtool status/config structures, power-budget support, IRQ notification helpers, and consumer APIs used by PHY/network code.

Important APIs and types: status/config types include `pse_control_config`, `pse_admin_state`, `pse_pw_status`, `pse_ext_state_info`, `pse_pw_limit_ranges`, and `ethtool_pse_control_status`. `struct pse_controller_ops` declares mandatory and optional per-PI callbacks for admin state, power detection, extended state, class, actual power, enable/disable, voltage, power limit, priority, and requested power. `struct pse_pi`, `struct pse_controller_dev`, `struct pse_irq_desc`, and `struct pse_ntf` model controller state, PIs, IRQ mapping, and notifications. Public APIs include `pse_controller_register()`, `devm_pse_controller_register()`, `devm_pse_irq_helper()`, `of_pse_control_get()`, `pse_control_put()`, ethtool get/set helpers, and type tests.

Control flow: a PSE controller driver fills `pse_controller_dev` and ops, registers it, optionally installs IRQ helper mapping, and exposes PSE controls referenced by PHY/device tree. Network ethtool paths acquire a `pse_control`, query status, enable/disable, adjust power limit, or set priority. Static budget evaluation can use PI priorities, requested power, and allocated power maintained by core logic.

State and persistence: state includes registered controller lists, requested PSE controls, PI device-tree mapping, regulator devices, admin-state shadowing, priority and allocated power fields, IRQ FIFO notifications, and hardware PSE state. Configuration affects hardware power delivery but is not inherently persistent across reset.

Dependencies and integration points: depends on ethtool UAPI/netlink enums, PHY devices, regulator framework, kfifo, workqueues, device tree, netlink extack, and controller drivers. It integrates Ethernet PHY management with PoE/PSE hardware.

Risks and test signals: risks include unit confusion between uA/mW, missing mandatory ops, IRQ notification races, incorrect PI-to-hardware matrix mapping, unsafe power-budget allocation, and disabled `CONFIG_PSE_CONTROLLER` callers mishandling `-EOPNOTSUPP`. Test ethtool netlink get/set paths, OF phandle lookup/refcounting, IRQ event mapping, static budget priority behavior, power limit range allocation/freeing, and no-PSE builds.
