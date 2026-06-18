# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pmt.h

## Purpose

`xe_pmt.h` defines BMG PMT discovery and telemetry offsets, including package/card energy fields, module and G-state residencies, and PCIe link residency counters.

## Important APIs, Types, and Definitions

- Base offsets: `BMG_PMT_BASE_OFFSET`, `BMG_DISCOVERY_OFFSET`, `BMG_TELEMETRY_BASE_OFFSET`, and `BMG_TELEMETRY_OFFSET`.
- Discovery/energy: `PUNIT_TELEMETRY_GUID`, `BMG_ENERGY_STATUS_PMT_OFFSET`, `ENERGY_PKG`, and `ENERGY_CARD`.
- Residency offsets: `BMG_MODS_RESIDENCY_OFFSET`, `BMG_G2_RESIDENCY_OFFSET`, `BMG_G6_RESIDENCY_OFFSET`, `BMG_G7_RESIDENCY_OFFSET`, `BMG_G8_RESIDENCY_OFFSET`, `BMG_G10_RESIDENCY_OFFSET`, and PCIe L0/L1/L1.2 offsets.

## Control Flow

No local control flow is present. PMT/telemetry code uses the constants to locate PMT discovery data and read 64-bit telemetry fields at the specified offsets.

## State and Persistence Behavior

The represented state is live telemetry exposed through a PMT aperture. Energy and residency counters change over time and may roll over; consumers own sampling and delta calculation.

## Dependencies and Integration Points

It includes `xe_regs.h` for `SOC_BASE` and `XE_REG`. It integrates with BMG telemetry/hwmon and power-management diagnostics.

## Risks and Edge Cases

- Offsets are BMG-specific and must be platform-gated.
- `ENERGY_PKG`/`ENERGY_CARD` are 64-bit masks over a combined telemetry value; consumers must use 64-bit reads and fields.
- Counter rollover and units are not described in this header.

## Test Signals

Signals include PMT GUID discovery, nonzero or changing energy counters under load, residency counter movement across power states, and correct PCIe residency reporting.
