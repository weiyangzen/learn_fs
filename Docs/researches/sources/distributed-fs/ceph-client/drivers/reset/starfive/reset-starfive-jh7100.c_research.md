# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7100.c

Purpose: StarFive JH7100 reset provider front-end that maps reset assert/status registers and uses the common JH71x0 reset implementation.

Important APIs/types/functions: register offsets define four assert and four status banks. `jh7100_reset_asserted[]` records status bits whose asserted polarity is not inverted. `jh7100_reset_probe()` maps MMIO and calls `reset_starfive_jh71x0_register()` with assert base, status base, asserted-status table, and `JH7100_RSTN_END`.

Control flow: built-in platform probe binds `starfive,jh7100-reset`, registers the common controller, and suppresses bind attributes.

State and persistence: hardware registers store reset state; static status-polarity array captures SoC quirks.

Dependencies and integration: platform MMIO, JH7100 reset dt-bindings, common StarFive reset helper, reset framework.

Risks and test signals: status polarity table must match hardware exactly or polling can time out. Test all banks, status inversion exceptions, reset pulse operation, and resource mapping failure.
