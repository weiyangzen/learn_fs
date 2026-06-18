# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/owl-sps.c

Purpose: generic PM-domain provider for Actions Semi Owl S500, S700, and S900 Smart Power System power gates.

Important APIs/types/functions: `struct owl_sps_domain_info` describes name, request bit, ack bit, and genpd flags; `struct owl_sps_info` holds SoC domain tables; `struct owl_sps` owns MMIO base and `genpd_onecell_data`; `struct owl_sps_domain` wraps each `generic_pm_domain`. Runtime callbacks are `owl_sps_power_on()` and `owl_sps_power_off()`, both using `owl_sps_set_power()` and `owl_sps_set_pg()`. Probe is `owl_sps_probe()`, registered at `postcore_initcall()`.

Control flow: probe gets match data, allocates a flexible `owl_sps`, maps the SPS register resource with `of_io_request_and_map()`, prepares a onecell genpd provider, initializes each domain from the SoC table, and registers the provider. Genpd callbacks convert domain bit numbers to masks and call the shared helper. S500 has explicit ack bits and some CPU domains marked always-on; S700/S900 tables omit ack bits, leaving ack mask as bit 0 for entries without explicit ack, which is an important hardware-table detail.

State and persistence: per-domain software state is the genpd object plus static table pointer. Hardware state is SPS power-gate bits. No disk persistence.

Dependencies/integration: uses generic PM domains, OF match data, DT power binding indices for S500/S700/S900, early platform-driver registration, and `owl-sps-helper`.

Risks: table correctness is critical: request/ack bits and `GENPD_FLAG_ALWAYS_ON` prevent accidental CPU or fabric shutdown. The driver initializes all domains as powered off from genpd's reference perspective (`pm_genpd_init(..., false)` means not off), but actual hardware may differ. Lack of remove path is expected for early SoC provider but matters for hot-unbind assumptions.

Test signals: DT consumers can resolve each power-domain cell, power transitions return after ack, always-on CPU domains are not shut down, probe runs early enough for dependent devices, and S500/S700/S900 binding indices map to the intended names.
