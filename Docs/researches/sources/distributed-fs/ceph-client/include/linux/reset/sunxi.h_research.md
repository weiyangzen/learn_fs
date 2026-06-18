# sources/distributed-fs/ceph-client/include/linux/reset/sunxi.h

Purpose: this header declares the early initialization hook for Allwinner sun6i reset support.

Important APIs/types/functions: it declares `void __init sun6i_reset_init(void);` and no other API.

Control flow: Allwinner platform initialization calls `sun6i_reset_init()` during early boot so reset providers are available before dependent devices probe.

State and persistence: no state is declared here. The implementation owns MMIO mappings and registered reset-controller state.

Dependencies and integration points: integrates with sunxi platform init and reset-controller provider/consumer flows.

Risks: because this is an early init hook, incorrect placement can leave consumers without reset providers. Test signals include sunxi boot, provider registration, DT reset lookup by consumers, and reset pulse behavior on affected SoCs.
