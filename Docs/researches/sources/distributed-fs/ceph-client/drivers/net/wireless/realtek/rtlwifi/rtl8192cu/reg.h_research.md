
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/reg.h

Purpose: Reuses the RTL8192CE register definitions for the USB CU driver by including `../rtl8192ce/reg.h`.

Important APIs/types/functions: No local macros beyond the SPDX/header comments and include. All register names used by CU code, such as `REG_SYS_CFG`, `REG_APS_FSMCO`, `REG_RQPN`, `REG_BCN_CTRL`, descriptor status registers, and bit masks, come from the CE register header.

Control flow: Header only. Compile-time aliasing lets CU implementation share the same register symbolic names as CE.

State and persistence: No direct state. It defines the symbolic map for hardware register reads/writes throughout the CU module.

Dependencies/integration: Every CU file that includes `reg.h` depends on CE register definitions staying compatible with 8192CU. This mirrors the shared 8192C silicon register layout.

Risks: USB-specific registers and PCIe-specific registers share a namespace; relying on CE definitions requires care where transport-specific offsets differ. Any change to the CE reg header affects CU builds and runtime register programming.

Test signals: Build coverage and hardware register traces for CU init, endpoint mapping, USB power, LED, and TRX paths to confirm all imported addresses match USB silicon.
