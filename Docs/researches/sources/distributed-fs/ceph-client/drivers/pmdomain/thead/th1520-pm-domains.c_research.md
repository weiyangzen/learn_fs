<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/th1520-pm-domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/thead/th1520-pm-domains.c

Purpose: TH1520 AON-backed power-domain controller. It exposes firmware-managed domains to genpd and creates auxiliary devices for GPU power sequencing and reboot support.

Important APIs/types/functions: `struct th1520_power_domain` binds a genpd to an AON resource ID and channel. `th1520_pd_ranges` maps DT power IDs to AON resources and disables AUDIO due to a firmware crash risk. `th1520_pd_power_on/off()` call `th1520_aon_power_update()`. `th1520_pd_xlate()` maps phandle resource IDs to domains. `th1520_pd_pwrseq_gpu_init()` creates `pwrseq-gpu` auxiliary device if `reset-names` contains `gpu-clkgen`; `th1520_pd_reboot_init()` creates a reboot auxiliary device.

Control flow: probe initializes the AON channel, allocates a onecell domain array sized to the binding enum, creates all non-disabled domains initially off, powers them off via firmware, registers the genpd provider, then registers optional auxiliary devices. Error paths delete provider, remove genpds, and deinit AON.

State/persistence: power state is in AON firmware; driver state is devm-allocated domain objects and the AON channel. AUDIO is intentionally never represented to consumers.

Dependencies/integration: uses `linux/firmware/thead/thead,th1520-aon.h`, `dt-bindings/power/thead,th1520-power.h`, auxiliary bus, genpd onecell provider, and DT compatible `thead,th1520-aon`.

Risks: disabled slots leave NULL entries in the onecell array; `th1520_pd_xlate()` must skip them. Initial power-down of all manageable domains may surprise firmware/bootloader users if a consumer is missing. The AUDIO firmware bug is encoded as policy and should remain documented in bindings/tests.

Test signals: verify all binding IDs translate except AUDIO, GPU pwrseq auxiliary appears only with the reset name, reboot auxiliary registers, and firmware failures unwind without leaked provider state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/th1520-pm-domains.c -->
