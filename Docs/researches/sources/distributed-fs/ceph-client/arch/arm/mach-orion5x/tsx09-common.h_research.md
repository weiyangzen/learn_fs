<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.h

Purpose: declaration header for QNAP TS-x09 common board support.

Important APIs/types: declares `qnap_tsx09_power_off()`, `qnap_tsx09_find_mac_addr(u32 mem_base, u32 size)`, and the exported `struct mv643xx_eth_platform_data qnap_tsx09_eth_data`.

Control flow and integration: board-specific TS-x09 setup files include this header to reuse the shared UART PIC poweroff path and MAC scan logic before registering Orion Ethernet.

State and persistence: this header owns no state; it exposes the platform-data object whose `mac_addr` may be filled from flash by the C file.

Dependencies: includes no external headers directly in this file, so consumers must already have or indirectly receive `u32` and `struct mv643xx_eth_platform_data` declarations.

Risks and test signals: compile coverage should catch missing type includes in consumers. Runtime test signals come from the C implementation: MAC log output and successful board poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.h -->
