# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-mfg-pmdomain.c

Purpose: MediaTek MFlexGraphics PM-domain driver for GPUEB-managed GPU power and frequency, currently matching `mediatek,mt8196-gpufreq`.

Important APIs, types, and functions: firmware ABI is defined by `enum mtk_mfg_ipi_cmd`, packed `struct mtk_mfg_ipi_msg`, sleep message, and packed OPP entry. `struct mtk_mfg` owns genpd, clocks, regulators, RPC/GPR/shared-memory mappings, mailbox channels, OPP arrays, and variant data. `mtk_mfg_eb_on()`/`mtk_mfg_eb_off()` sequence the embedded GPU controller. `mtk_mfg_send_ipi()` synchronously sends GPUEB mailbox commands. `mtk_mfg_init_shared_mem()`, `mtk_mfg_read_opp_tables()`, `mtk_mfg_attach_dev()`, and `mtk_mfg_set_performance()` bridge firmware OPPs into genpd/OPP consumers. It also registers read-only `gpu-core`/`gpu-stack` clocks and an nvmem cell `shader-present`.

Control flow: probe maps GPR/RPC MMIO and reserved shared memory, gets EB/GPU clocks and regulators, runs variant init to select the GHPM enable register, initializes genpd callbacks, sets up mailboxes, powers the GPU EB on, initializes shared memory, reads firmware OPP tables, publishes clock/nvmem providers, and finally publishes the genpd provider. Power-on enables regulators and clocks, powers EB, reads IPI magic, sends firmware power-control enable, and applies deferred genpd performance state. Power-off sends firmware power-control disable, powers EB off, disables clocks and regulators.

State and persistence behavior: persistent hardware/firmware state lives in GPUEB shared memory and RPC/GPR registers. Driver state includes OPP arrays read once at probe, mailbox response buffer, current genpd performance state, and registered dynamic OPPs per attached device. No disk persistence.

Dependencies and integration points: depends on mailbox channels `gpufreq` and `sleep`, reserved memory, GPUEB firmware ABI, regulators `core`, `stack`, `sram`, clocks `eb`, `core`, `stack0`, `stack1`, genpd, OPP, nvmem, and OF platform probing.

Risks: firmware ABI structs must not change. `mtk_mfg_send_ipi()` assigns the local `msg` pointer to RX data, so callers rely on return status rather than mutated original message contents. OPP attach uses `prev_o` without explicit initialization in the visible code, which is a correctness risk if not zeroed by compiler behavior. Power-off failure leaves resources enabled by design to avoid unsafe teardown. Shared-memory bounds in nvmem reject `offset + bytes >= size`, which disallows reading exactly the last word.

Test signals: probe on MT8196 should power EB, validate shared-memory magic, read nonzero OPP tables, register two clocks and `shader-present`, and attach dynamic OPPs to GPU consumers. Runtime tests should change genpd performance states, verify `GF_REG_FREQ_OUT_*`, suspend/resume EB, and fault-inject mailbox timeouts/firmware errors.
