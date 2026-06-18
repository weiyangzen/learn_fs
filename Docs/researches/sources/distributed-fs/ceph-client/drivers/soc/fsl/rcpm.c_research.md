
# sources/distributed-fs/ceph-client/drivers/soc/fsl/rcpm.c

## Purpose
Implements the Freescale/NXP QorIQ RCPM wakeup controller platform driver. During PM prepare it scans registered wakeup sources and ORs device-provided `fsl,rcpm-wakeup` bits into IPPDEXPCR wakeup registers, with DT and ACPI support.

## Important APIs, Types, and Functions
- `struct rcpm` stores wakeup cell count, IPPDEXPCR base, and endianness.
- `rcpm_pm_prepare()` is the key PM hook.
- `copy_ippdexpcr1_setting()` implements LS1021A erratum A-008646 workaround through SCFG spare register.
- `rcpm_probe()` maps registers, reads `little-endian` and `#fsl,rcpm-wakeup-cells`, and stores drvdata.

## Control Flow
On suspend prepare, the driver locks wakeup-source iteration, visits each wakeup source with a parent device, reads `fsl,rcpm-wakeup`, filters by phandle in DT mode, ORs all wakeup cells into a local setting array, unlocks, then writes nonzero settings to consecutive IPPDEXPCR registers using the configured endianness. For LS1021A register 1, it mirrors the written bits to SCFG spare register.

## State and Persistence
Runtime state is devm-managed mapping/configuration. Hardware wakeup register bits are OR-only by this driver and persist across suspend preparation until hardware/firmware clears or rewrites them.

## Dependencies and Integration Points
Depends on wakeup source core, OF/ACPI property APIs, platform resources, and optional LS1021A SCFG syscon node. Devices integrate by exposing `fsl,rcpm-wakeup` on their parent.

## Risks
- The driver only ORs bits and does not clear stale wakeup bits; platform firmware or other paths must manage clearing.
- `RCPM_WAKEUP_CELL_MAX_SIZE` bounds the stack arrays; larger DT values would overflow reads if not constrained by bindings.
- ACPI mode assumes only one RCPM controller.
- Missing or malformed wakeup properties are silently skipped.

## Test Signals
Suspend prepare with multiple wakeup sources, DT phandle filtering, little/big endian register writes, LS1021A erratum mirroring, malformed property lengths, ACPI probe, and large cell-count validation are important.
