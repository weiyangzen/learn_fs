# sources/distributed-fs/ceph-client/drivers/reset/starfive/Makefile

Purpose: Kbuild object selection for StarFive reset drivers.

Important APIs/types/functions: common `reset-starfive-jh71x0.o` is built for `CONFIG_RESET_STARFIVE_JH71X0`; SoC front-ends build `reset-starfive-jh7100.o` and `reset-starfive-jh7110.o`.

Control flow: no runtime behavior; Kbuild assembles common and SoC-specific objects based on config.

State and persistence: build graph state only.

Dependencies and integration: common object exports `reset_starfive_jh71x0_register()` used by both SoC drivers.

Risks and test signals: object selection must stay aligned with Kconfig selects or SoC drivers will miss common symbols. Test JH7100-only and JH7110-only builds.
