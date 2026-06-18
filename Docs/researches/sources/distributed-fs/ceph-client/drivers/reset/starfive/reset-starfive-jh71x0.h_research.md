# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.h

Purpose: local header declaring the common StarFive JH71x0 reset registration helper.

Important APIs/types/functions: `reset_starfive_jh71x0_register()` takes device, OF node, assert/status MMIO bases, optional asserted-status table, reset count, and owner module pointer.

Control flow: no runtime flow; JH7100 and JH7110 front-ends include this header and call the helper from probe.

State and persistence: no state in the header.

Dependencies and integration: relies on declarations of `struct device`, `struct device_node`, and `struct module` from including C files; links SoC front-ends to common implementation.

Risks and test signals: signature drift breaks both front-ends at compile time. Compile coverage for both SoC drivers is the main signal.
