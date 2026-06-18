# sources/distributed-fs/ceph-client/include/soc/microchip/mpfs.h

Purpose: declares Microchip PolarFire SoC system-controller message structures and optional sys-controller, flash, and reset-controller APIs.

Important APIs and types: `struct mpfs_mss_msg` describes a mailbox transaction with opcode, command size/data, response pointer, mailbox offset, and response offset. `struct mpfs_mss_response` holds status, response words, and response size. When `CONFIG_POLARFIRE_SOC_SYS_CTRL` is enabled, APIs perform blocking transactions, get the sys-controller handle, and get flash. When MPFS clock and reset controller configs are enabled, `mpfs_reset_controller_register()` registers reset support; otherwise a stub returns success.

Control flow: clients acquire the system controller, prepare mailbox command/response buffers and offsets, perform blocking transactions to MSS firmware, and optionally register reset control from the clock driver.

State and persistence: runtime state includes sys-controller client handles, mailbox firmware state, response buffers, flash handle, and reset regmap state. Firmware/flash contents persist outside this header.

Dependencies and integration points: depends on OF device, regmap, and MTD/reset/clock users. Integrates MPFS MSS services with platform drivers.

Risks and test signals: risks include absent fallback declarations for disabled sys-controller users, mismatched reset stub signature versus enabled signature, mailbox offset/size errors, blocking transaction hangs, and firmware status misinterpretation. Test sys-controller probe, transaction success/failure/timeouts, flash access, reset registration across config matrices, and invalid command sizes.
