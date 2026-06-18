# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-platform.c

## Purpose

`sp-platform.c` is the ACPI/OF platform-bus frontend for AMD CCP/SP devices, mainly non-PCI environments such as ARM64 Seattle.

## Important APIs, Types, And Functions

Public functions are `sp_platform_init()` and `sp_platform_exit()`. Driver callbacks are `sp_platform_probe()`, `sp_platform_remove()`, and optional PM suspend/resume handlers. Helpers include `sp_get_acpi_version()` and `sp_get_irqs()`. `struct sp_platform` tracks DMA coherency and IRQ count.

## Control Flow

Probe allocates common and platform-private state, selects vdata from OF or ACPI match, maps resource 0, checks DMA support and coherency, sets `sp->axcache`, configures a 48-bit DMA mask, obtains one or two IRQs, stores driver data, and calls `sp_init()`. Remove calls `sp_destroy()`. PM delegates to common SP suspend/resume.

## State And Persistence Behavior

Per-device platform state persists in `sp->dev_specific`. Coherency determines the AXCACHE attribute used by CCP hardware operations. There is no PSP vdata in this platform table, so this path is CCP-focused.

## Dependencies And Integration Points

It depends on platform device resources, ACPI ID `AMDI0C00`, OF compatible `amd,ccp-seattle-v1a`, DMA attribute APIs, common SP core, and CCP platform vdata.

## Risks And Test Signals

Risks include incorrect DMA coherency handling, missing second IRQ on platforms that need it, unsupported DMA silently failing probe, and vdata mismatch between ACPI and OF. Test ACPI and DT probe, coherent and non-coherent DMA operation, single/shared IRQ versus dual IRQ, suspend/resume, and remove.
