<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun55i-pck600.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun55i-pck600.c

Purpose: Allwinner PCK-600/PPU power-domain provider for sun55i A523 and sun60i A733 SoCs. It programs per-domain PPU policy/status registers and SoC-specific delay registers, then exports a onecell genpd provider.

Important APIs/types/functions: `sunxi_pck600_desc` carries domain names, count, delay offsets/values, and reset/clock requirements. `sunxi_pck600_pd` embeds `generic_pm_domain`. `sunxi_pck600_pd_set_power()` writes `PPU_PWPR` and polls `PPU_PWSR`; `sunxi_pck600_pd_setup()` writes delay-control registers; `sunxi_pck600_probe()` maps MMIO, enables clock/reset support, creates domains, and registers the provider.

Control flow: probe obtains compatible match data, allocates a flexible `sunxi_pck600` with all domains, maps one MMIO range, optionally obtains an exclusive released reset for A523, enables the controller clock, and initializes domains at `base + PPU_REG_SIZE * i`. Each domain is initialized as powered on (`pm_genpd_init(..., false)`) after delay setup. Provider registration failure unwinds initialized genpds.

State/persistence: hardware state lives in PPU policy/status registers. Software stores the mapped base per domain and the shared provider object. The controller delay registers are configured during probe and not persisted elsewhere.

Dependencies/integration: integrates with OF compatibles `allwinner,sun55i-a523-pck-600` and `allwinner,sun60i-a733-pck-600`, generic PM domains, clock framework, reset framework, MMIO polling, and DT power-domain consumers.

Risks: assumes domains are laid out in 0x1000 strides and that all domains accept the same delay programming. `readl_poll_timeout_atomic()` uses a 10 ms timeout; slow or clock-gated hardware can fail power transitions. A523 reset acquisition is retrieved but not explicitly asserted/deasserted in this driver.

Test signals: boot with each SoC compatible, verify `power_on`/`power_off` changes PWSR status, validate clock/reset DT bindings, and exercise each named consumer domain including GPU/PCIe/USB/video blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun55i-pck600.c -->
