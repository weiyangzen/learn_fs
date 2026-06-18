# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200wb.c

## Purpose
Implements G200WB support, including WB register defaults, 48 MHz reference PLL search/programming, BMC-synchronized device info, pipeline creation, and factory setup.

## Important APIs, types, and functions
- `mgag200_g200wb_init_registers()` writes WB DAC defaults and shared VGA registers; reused by EW3.
- `mgag200_g200wb_pixpllc_atomic_check()` searches m/n/p for a 150-550 MHz VCO.
- `mgag200_g200wb_pixpllc_atomic_update()` performs a retry loop that disables clocks, selects PLL set C, resets VREF, writes WB PLL registers, selects PLL for pixel/remote head, and polls vertical count for lock.
- `mgag200_g200wb_device_create()` creates the device with WB limits and BMC-aware output.

## Control flow
Factory setup writes PCI options, maps resources, initializes shared state with WB info/functions, writes registers, probes VRAM, configures KMS, creates primary plane/CRTC/VGA-BMC output, resets config, and starts polling. Atomic enable uses the common CRTC helper and WB PLL update.

## State and persistence
Device info limits max mode to 1280x1024, bandwidth 31877, and enables BMC synchronization. PLL values persist in CRTC state; lock retry state is local. Hardware remote-head clock and DAC PLL state persist after update.

## Dependencies and integration points
Exports init and PLL update for EW3. Uses shared KMS helpers and BMC VGA output.

## Risks
PLL update retries mutate CRTC register 0x1e on later attempts and does not report lock failure. BMC sync means modesets interact with remote console handshakes. The 1280x1024 cap must match hardware/BMC limitations.

## Test signals
WB hardware should validate 1280x1024 preferred paths, BMC scanout coordination, PLL lock under repeated modesets, EDID and no-EDID fallback, and remote-head clock restoration.
