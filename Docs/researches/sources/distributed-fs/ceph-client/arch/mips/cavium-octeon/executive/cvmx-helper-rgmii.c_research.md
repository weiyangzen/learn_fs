# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-rgmii.c

## Purpose
Probes, enables, loops back, reads link status, and changes link settings for RGMII/GMII/MII ports.

## Important APIs, Types, And Functions
Functions include `__cvmx_helper_rgmii_probe()`, `cvmx_helper_rgmii_internal_loopback()`, `__cvmx_helper_rgmii_enable()`, `__cvmx_helper_rgmii_link_get()`, and `__cvmx_helper_rgmii_link_set()`.

## Control Flow
Probe interprets `GMXX_INF_MODE` by model to return port count. Enable configures ASX RX/TX masks, pass1 errata or preamble handling, pause timing, clock delays, common GMX setup, GMX port enables, and ASX/GMX interrupts. Link set disables RX and PKO queue scheduling, waits for GMX idle, programs duplex/speed/clocks, then restores queues, backpressure, RX, and enable state.

## State, Persistence, And Dependencies
State is in GMX, ASX, PKO, and debug CSRs. Stack-saved QoS/backpressure state is restored after speed changes.

## Integration Points
Used by the helper coordinator for RGMII and GMII modes; relies on board link status and PKO queue helpers.

## Risks
Changing speed without true idle can lock GMX. Board link fallback is deprecated. Mode misclassification can configure the wrong interface type.

## Test Signals
Verify port counts, packet flow after enable, GMX clock changes for 10/100/1000, queue QoS restoration, and ASX/GMX error interrupts.
