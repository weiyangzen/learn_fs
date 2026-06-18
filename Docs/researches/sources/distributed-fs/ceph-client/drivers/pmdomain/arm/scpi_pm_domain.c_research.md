# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/scpi_pm_domain.c

Purpose: legacy SCPI generic power-domain provider for SCP firmware controlled device power states.

Important APIs/types/functions: `struct scpi_pm_domain` wraps genpd with `scpi_ops` and domain ID. `enum scpi_power_domain_state` maps ON to 0 and OFF to 3. `scpi_pd_power()` sets and verifies state; `scpi_pd_power_on/off()` are genpd callbacks; `scpi_pm_domain_probe()` registers a onecell provider from DT `num-domains`.

Control flow: platform probe obtains global SCPI ops, validates DT node and firmware power-state callbacks, reads `num-domains`, allocates domain arrays, creates a named genpd for each index, initializes all as off from genpd's reference-count perspective regardless of firmware state, and registers the onecell provider.

State and persistence: software state is per-domain index and SCPI ops pointer. Firmware owns actual power state. Genpd intentionally starts off to avoid Linux turning off firmware-enabled domains it did not request.

Dependencies/integration: depends on legacy SCPI protocol ops, OF platform matching `arm,scpi-power-domains`, DT `num-domains`, and generic PM domains.

Risks: SCPI power state values are not fully standardized; this driver hardcodes ON=0 and OFF=3. `of_genpd_add_provider_onecell()` return value is ignored, so provider registration failures are not propagated. Verification returns a boolean mismatch as an integer error, which may not preserve firmware error detail after set succeeds but get disagrees.

Test signals: probe defers until SCPI ops are ready, DT `num-domains` creates the expected slots, power set/get works with firmware state values, consumers resolve all indices, and provider registration failures should be caught by boot logs or follow-up checks.
